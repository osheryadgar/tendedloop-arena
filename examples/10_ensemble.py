"""
TendedLoop Arena — Ensemble Agent (Strategy Committee)

Combines multiple independent strategies and uses weighted voting
to select the best action each cycle. Each sub-strategy proposes
a config, and the ensemble picks the one with the highest weighted
score — where weights are updated based on each strategy's track record.

Why an ensemble:
  - No single strategy dominates in all situations
  - Early on, aggressive strategies explore; later, conservative ones stabilize
  - The ensemble adapts by upweighting strategies that produce better outcomes
  - It's a meta-strategy: bring your own sub-strategies

This example combines three sub-strategies:
  1. Reactive (rule-based thresholds)
  2. Conservative (small incremental changes)
  3. Bold (large shifts toward high-reward configs)

The weighting uses multiplicative weights update (Hedge algorithm):
  - Good outcomes → increase weight
  - Bad outcomes → decrease weight
  - Over time, the best strategy dominates

Run:
    pip install git+https://github.com/osheryadgar/tendedloop-arena.git
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/10_ensemble.py
"""

import logging
import math
import os
import random

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")

if TOKEN == "strat_your_token_here":
    raise SystemExit(
        "Set STRATEGY_TOKEN env var before running.\n"
        "Get yours from Dashboard > Admin > Research > Experiments > Arena Manifest"
    )


# ─── Sub-Strategies ───


def reactive_strategy(signals: Signals, config: dict) -> dict[str, int]:
    """React to metric thresholds with targeted boosts."""
    changes = dict(config)
    freq = signals.metrics.get("SCAN_FREQUENCY")
    ret = signals.metrics.get("RETENTION_RATE")

    if freq and freq.confidence != "low":
        if freq.value < 2.0:
            changes["scanXp"] = round(config.get("scanXp", 10) * 1.2)
        elif freq.value > 4.5:
            changes["scanXp"] = round(config.get("scanXp", 10) * 0.9)

    if ret and ret.confidence != "low" and ret.value < 0.5:
        changes["streakBonusPerDay"] = round(config.get("streakBonusPerDay", 5) * 1.25)

    return changes


def conservative_strategy(signals: Signals, config: dict) -> dict[str, int]:
    """Small 5% nudges — up if engagement is low, down if overspending."""
    freq = signals.metrics.get("SCAN_FREQUENCY")
    direction = 1.0  # Default: increase
    if freq and freq.confidence != "low" and freq.value > 4.0:
        direction = -1.0  # Reduce if engagement already high (save budget)

    factor = 1.0 + direction * 0.05
    return {
        "scanXp": round(config.get("scanXp", 10) * factor),
        "feedbackXp": round(config.get("feedbackXp", 15) * factor),
        "streakBonusPerDay": round(config.get("streakBonusPerDay", 5) * (1.0 + direction * 0.03)),
    }


def bold_strategy(signals: Signals, config: dict) -> dict[str, int]:
    """Aggressive shifts toward the highest-impact parameters."""
    freq = signals.metrics.get("SCAN_FREQUENCY")
    qual = signals.metrics.get("FEEDBACK_QUALITY")

    # Boost whichever metric is weakest
    if freq and qual and freq.confidence != "low" and qual.confidence != "low":
        if freq.value < qual.value * 5:  # Frequency is relatively weaker
            return {
                "scanXp": round(config.get("scanXp", 10) * 1.3),
                "firstScanOfDayXp": round(config.get("firstScanOfDayXp", 15) * 1.25),
            }
        else:
            return {
                "feedbackXp": round(config.get("feedbackXp", 15) * 1.3),
                "photoXp": round(config.get("photoXp", 10) * 1.25),
            }

    # Default: boost scan rewards
    return {"scanXp": round(config.get("scanXp", 10) * 1.25)}


# ─── Ensemble (Hedge Algorithm) ───

STRATEGIES = [
    {"name": "Reactive", "fn": reactive_strategy},
    {"name": "Conservative", "fn": conservative_strategy},
    {"name": "Bold", "fn": bold_strategy},
]


class Ensemble:
    """
    Multiplicative Weights (Hedge) ensemble over sub-strategies.

    Each strategy has a weight. The ensemble picks the strategy with
    the highest weight, executes its proposal, and updates weights
    based on the observed reward.

    eta: Learning rate. Higher = faster adaptation, less stability.
    """

    def __init__(self, n_strategies: int, eta: float = 0.3):
        self.n = n_strategies
        self.eta = eta
        self.weights = [1.0] * n_strategies
        self.selections = [0] * n_strategies
        self.cumulative_reward = [0.0] * n_strategies
        self.last_selected: int | None = None
        self.last_composite: float | None = None

    def select(self) -> int:
        """Select strategy by sampling proportionally to weights (Hedge)."""
        total = sum(self.weights)
        probs = [w / total for w in self.weights]

        # Weighted random selection — allows recovery from early bad luck
        r = random.random()
        cumulative = 0.0
        chosen = 0
        for i, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                chosen = i
                break

        self.selections[chosen] += 1
        return chosen

    def update(self, strategy_idx: int, reward: float):
        """Update weight using multiplicative update rule."""
        # Multiplicative weights: w_i *= exp(eta * reward_i)
        self.weights[strategy_idx] *= math.exp(self.eta * reward)
        self.cumulative_reward[strategy_idx] += reward

        # Normalize to prevent overflow
        max_w = max(self.weights)
        if max_w > 100:
            self.weights = [w / max_w for w in self.weights]

    def compute_composite(self, signals: Signals) -> float:
        """Composite engagement score."""
        score = 0.0
        freq = signals.metrics.get("SCAN_FREQUENCY")
        ret = signals.metrics.get("RETENTION_RATE")
        qual = signals.metrics.get("FEEDBACK_QUALITY")

        if freq and freq.confidence != "low":
            score += freq.value * 0.4
        if ret and ret.confidence != "low":
            score += ret.value * 10 * 0.35
        if qual and qual.confidence != "low":
            score += qual.value * 10 * 0.25

        return score


# ─── Decision Logic ───

ensemble = Ensemble(n_strategies=len(STRATEGIES))


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """Ensemble decision: select best strategy, execute its proposal."""
    composite = ensemble.compute_composite(signals)

    # Update previous selection based on outcome
    if ensemble.last_selected is not None and ensemble.last_composite is not None:
        delta = composite - ensemble.last_composite
        reward = max(-1.0, min(1.0, delta))  # Clamp to [-1, 1]
        ensemble.update(ensemble.last_selected, reward)

    # Select strategy
    idx = ensemble.select()
    strategy = STRATEGIES[idx]

    # Get proposal from selected strategy
    proposal = strategy["fn"](signals, current_config)
    # Only include parameters that differ from current config
    changes = {k: v for k, v in proposal.items() if v != current_config.get(k)}

    ensemble.last_selected = idx
    ensemble.last_composite = composite

    # Print status
    total_w = sum(ensemble.weights)
    pcts = [f"{w / total_w * 100:.0f}%" for w in ensemble.weights]
    labels = [f"{STRATEGIES[i]['name']}={pcts[i]}" for i in range(len(STRATEGIES))]
    print(f"\n  Weights: {' | '.join(labels)}")
    print(f"  Selected: {strategy['name']} | Composite: {composite:.3f}")

    if not changes:
        print(f"  {strategy['name']} proposes no changes")
        return None

    return ConfigUpdate(
        economy_overrides=changes,
        reasoning=f"Ensemble: '{strategy['name']}' ({pcts[idx]} weight) — {changes}",
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — Ensemble Agent (Strategy Committee)")
    print("=" * 55)
    print()
    print("  Sub-strategies:")
    for i, s in enumerate(STRATEGIES):
        print(f"    [{i}] {s['name']}")
    print(f"  Learning rate (eta): {ensemble.eta}")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print()

        agent.run(decide, poll_interval=90, max_iterations=60)

        # Final report
        total_w = sum(ensemble.weights)
        print("\nFinal strategy report:")
        print(f"  {'Strategy':<15} {'Weight':>8} {'Selected':>10} {'Cum.Reward':>12}")
        print(f"  {'-' * 15} {'-' * 8} {'-' * 10} {'-' * 12}")
        for i, s in enumerate(STRATEGIES):
            pct = ensemble.weights[i] / total_w * 100
            print(
                f"  {s['name']:<15} {pct:>7.1f}% {ensemble.selections[i]:>10} "
                f"{ensemble.cumulative_reward[i]:>12.3f}"
            )


if __name__ == "__main__":
    main()
