"""
TendedLoop Arena — Contextual Bandit (LinUCB) Agent

Linear Upper Confidence Bound algorithm that uses the full
signal context (enrollment, activity, experiment day) to make
context-dependent arm selections.

Unlike standard bandits (Thompson, UCB1) that ignore context,
contextual bandits learn that different configs work better
in different situations:
  - Early experiment (day 1-3): exploration-heavy arms win
  - Low activity day: high-reward arms are needed
  - Large enrollment: conservative arms are safer

The LinUCB formula:
  For each arm, maintain A_inv (inverse design matrix) and b (reward vector).
  Given context x:
    theta = A_inv @ b           (estimated reward coefficients)
    p = theta @ x + alpha * sqrt(x @ A_inv @ x)  (predicted reward + UCB)
  Select the arm with highest p.

Run:
    pip install "tendedloop-arena[rl] @ git+https://github.com/osheryadgar/tendedloop-arena.git"
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/08_contextual_bandit.py
"""

import logging
import os

import numpy as np

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")

if TOKEN == "strat_your_token_here":
    raise SystemExit(
        "Set STRATEGY_TOKEN env var before running.\n"
        "Get yours from Dashboard > Admin > Research > Experiments > Arena Manifest"
    )


# ─── Arm Definitions ───

ARMS = [
    {"name": "Balanced", "config": {"scanXp": 12, "feedbackXp": 17, "streakBonusPerDay": 7}},
    {"name": "Aggressive", "config": {"scanXp": 18, "feedbackXp": 22, "firstScanOfDayXp": 22}},
    {
        "name": "Streak-Heavy",
        "config": {"streakBonusPerDay": 12, "streakBonusCap": 65, "firstScanOfDayXp": 20},
    },
    {"name": "Quality-Focus", "config": {"feedbackXp": 25, "photoXp": 18, "issueReportXp": 30}},
]


# ─── LinUCB Algorithm ───


class LinUCB:
    """
    Linear Upper Confidence Bound contextual bandit.

    Args:
        n_arms: Number of arms.
        d: Dimensionality of context features.
        alpha: Exploration parameter. Higher = more exploration.
    """

    def __init__(self, n_arms: int, d: int, alpha: float = 1.0):
        self.n_arms = n_arms
        self.d = d
        self.alpha = alpha

        # Per-arm parameters: A (d x d identity), b (d x 1 zero)
        self.A = [np.eye(d) for _ in range(n_arms)]
        self.b = [np.zeros(d) for _ in range(n_arms)]
        self.pulls = [0] * n_arms

    def select_arm(self, context: np.ndarray) -> int:
        """Select arm with highest LinUCB score given context."""
        scores = []
        for i in range(self.n_arms):
            a_inv = np.linalg.inv(self.A[i])
            theta = a_inv @ self.b[i]
            # Predicted reward + exploration bonus
            pred = theta @ context
            exploration = self.alpha * np.sqrt(context @ a_inv @ context)
            scores.append(pred + exploration)

        chosen = int(np.argmax(scores))
        print(f"  LinUCB scores: {[f'{s:.3f}' for s in scores]}")
        print(f"  Selected: {ARMS[chosen]['name']} (score={scores[chosen]:.3f})")
        return chosen

    def update(self, arm: int, context: np.ndarray, reward: float):
        """Update arm's model with observed (context, reward) pair."""
        self.A[arm] += np.outer(context, context)
        self.b[arm] += reward * context
        self.pulls[arm] += 1


def signals_to_context(signals: Signals) -> np.ndarray:
    """
    Extract a feature vector from signals.

    Features (normalized to roughly [0, 1]):
      0: enrollment ratio (enrolled / 200, capped)
      1: daily activity ratio (active_today / enrolled)
      2: weekly activity ratio (active_7d / enrolled)
      3: experiment progress (days / 30, capped)
      4: scan frequency (value / 5, capped)
      5: retention rate (direct, already 0-1)
    """
    enrolled = max(signals.enrolled, 1)
    freq = signals.metrics.get("SCAN_FREQUENCY")
    ret = signals.metrics.get("RETENTION_RATE")

    return np.array(
        [
            min(signals.enrolled / 200, 1.0),
            min(signals.active_today / enrolled, 1.0),
            min(signals.active_7d / enrolled, 1.0),
            min(signals.experiment_days / 30, 1.0),
            min(freq.value / 5.0, 1.0) if freq and freq.confidence != "low" else 0.5,
            ret.value if ret and ret.confidence != "low" else 0.5,
        ]
    )


def compute_reward(signals: Signals) -> float:
    """Composite reward normalized to [0, 1]."""
    score = 0.0
    freq = signals.metrics.get("SCAN_FREQUENCY")
    ret = signals.metrics.get("RETENTION_RATE")
    qual = signals.metrics.get("FEEDBACK_QUALITY")

    if freq and freq.confidence != "low":
        score += min(freq.value / 5.0, 1.0) * 0.4
    else:
        score += 0.2
    if ret and ret.confidence != "low":
        score += ret.value * 0.35
    else:
        score += 0.15
    if qual and qual.confidence != "low":
        score += qual.value * 0.25
    else:
        score += 0.1

    return score


# ─── Decision Logic ───

N_FEATURES = 6
linucb = LinUCB(n_arms=len(ARMS), d=N_FEATURES, alpha=1.5)
last_arm: int | None = None
last_context: np.ndarray | None = None


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """LinUCB contextual bandit decision function."""
    global last_arm, last_context

    context = signals_to_context(signals)
    reward = compute_reward(signals)

    print(f"\n  Context: {[f'{x:.2f}' for x in context]}")
    print(f"  Reward:  {reward:.3f}")

    # Update previous arm with observed reward
    if last_arm is not None and last_context is not None:
        linucb.update(last_arm, last_context, reward)

    # Select next arm using context
    arm_idx = linucb.select_arm(context)
    arm = ARMS[arm_idx]

    last_arm = arm_idx
    last_context = context

    return ConfigUpdate(
        economy_overrides=arm["config"],
        reasoning=(
            f"LinUCB: '{arm['name']}' | context=[enroll={context[0]:.1f}, "
            f"activity={context[1]:.1f}, progress={context[3]:.1f}]"
        ),
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — Contextual Bandit (LinUCB)")
    print("=" * 46)
    print(f"  Features:    {N_FEATURES}")
    print(f"  Arms:        {len(ARMS)}")
    print(f"  Alpha:       {linucb.alpha}")
    print()
    for i, arm in enumerate(ARMS):
        print(f"    [{i}] {arm['name']}")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print()

        agent.run(decide, poll_interval=120, max_iterations=50)

        # Summary
        print("\nArm pull distribution:")
        for i, arm in enumerate(ARMS):
            bar = "#" * linucb.pulls[i]
            print(f"  {arm['name']:<15} [{linucb.pulls[i]:>3}] {bar}")


if __name__ == "__main__":
    main()
