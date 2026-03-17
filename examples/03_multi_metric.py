"""
TendedLoop Arena — Multi-Metric Optimizer

Demonstrates balancing multiple objectives simultaneously.
This agent uses a weighted scoring system to decide which
parameters to adjust based on all available metrics.

Strategy:
  - Assign weights to each metric (what matters most?)
  - Compute a composite score
  - Adjust parameters that influence underperforming metrics
  - Back off parameters linked to overperforming metrics (avoid waste)

Run:
    pip install git+https://github.com/osheryadgar/tendedloop-arena.git
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/03_multi_metric.py
"""

import logging
import os

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")

if TOKEN == "strat_your_token_here":
    raise SystemExit(
        "Set STRATEGY_TOKEN env var before running.\n"
        "Get yours from Dashboard > Admin > Research > Experiments > Arena Manifest"
    )


# ─── Strategy Configuration ───

# Define your optimization targets and weights
TARGETS = {
    "SCAN_FREQUENCY": {"target": 3.0, "weight": 0.35},
    "RETENTION_RATE": {"target": 0.7, "weight": 0.30},
    "FEEDBACK_QUALITY": {"target": 0.5, "weight": 0.20},
    "STREAK_LENGTH": {"target": 5.0, "weight": 0.15},
}

# Which parameters influence which metrics
METRIC_LEVERS = {
    "SCAN_FREQUENCY": ["scanXp", "firstScanOfDayXp", "scanDailyCap"],
    "RETENTION_RATE": ["streakBonusPerDay", "streakBonusCap", "firstScanOfDayXp"],
    "FEEDBACK_QUALITY": ["feedbackXp", "photoXp", "feedbackDailyCap"],
    "STREAK_LENGTH": ["streakBonusPerDay", "streakBonusCap"],
}


# ─── Decision Logic ───


def compute_health_score(signals: Signals) -> dict[str, float]:
    """Compute per-metric health scores (0.0 = critical, 1.0 = at target, >1.0 = exceeding)."""
    scores = {}
    for metric_name, target_config in TARGETS.items():
        metric = signals.metrics.get(metric_name)
        if not metric or metric.confidence == "low":
            scores[metric_name] = 0.5  # Assume neutral if insufficient data
            continue
        scores[metric_name] = (
            metric.value / target_config["target"] if target_config["target"] > 0 else 1.0
        )
    return scores


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """Multi-metric weighted optimizer."""
    health = compute_health_score(signals)

    # Compute weighted composite score
    composite = sum(min(score, 1.5) * TARGETS[metric]["weight"] for metric, score in health.items())

    print(f"  Composite health: {composite:.2f}")
    for metric, score in health.items():
        status = "OK" if score >= 0.8 else "LOW" if score >= 0.5 else "CRITICAL"
        print(f"    {metric}: {score:.2f} [{status}]")

    # If everything is healthy, don't change anything
    if all(score >= 0.8 for score in health.values()):
        print("  All metrics healthy — holding steady")
        return None

    # Find the most underperforming metric (lowest health score)
    worst_metric = min(health, key=lambda m: health[m])
    worst_score = health[worst_metric]

    if worst_score >= 0.8:
        return None

    # Boost levers for the worst metric
    changes: dict[str, float] = {}
    levers = METRIC_LEVERS.get(worst_metric, [])

    # Stronger boost for more critical situations
    boost = 1.20 if worst_score < 0.5 else 1.12

    for lever in levers:
        current_val = current_config.get(lever)
        if current_val is not None:
            changes[lever] = round(current_val * boost)

    if not changes:
        return None

    # Also reduce levers for any overperforming metrics (save budget)
    for metric, score in health.items():
        if score > 1.3:  # Exceeding target by 30%+
            for lever in METRIC_LEVERS.get(metric, []):
                if lever not in changes:  # Don't conflict with boosts
                    current_val = current_config.get(lever)
                    if current_val is not None:
                        changes[lever] = round(current_val * 0.92)

    return ConfigUpdate(
        economy_overrides=changes,
        reasoning=f"Boosting {worst_metric} (score={worst_score:.2f}), composite={composite:.2f}",
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — Multi-Metric Optimizer")
    print("=" * 42)
    print()
    print("Targets:")
    for metric, config in TARGETS.items():
        print(f"  {metric}: {config['target']} (weight={config['weight']})")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print()

        agent.run(decide, poll_interval=60, max_iterations=100)


if __name__ == "__main__":
    main()
