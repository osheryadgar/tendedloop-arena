"""
TendedLoop Arena — Quickstart Agent

A simple rule-based agent that adjusts economy parameters
based on real-time engagement signals. Great starting point
for understanding the observe-decide-act loop.

Run:
    pip install tendedloop-agent
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/01_quickstart.py
"""

import logging
import os

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

# ─── Configuration ───

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")


# ─── Decision Logic ───


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """
    Simple threshold-based strategy:
    - Boost scan XP when frequency drops below 2.0/day
    - Reduce scan XP when frequency exceeds 4.0/day (avoid overspend)
    - Boost streak bonus when retention is low
    """
    scan_freq = signals.metrics.get("SCAN_FREQUENCY")
    retention = signals.metrics.get("RETENTION_RATE")

    # Don't act on low-confidence data
    if not scan_freq or scan_freq.confidence == "low":
        print("  Skipping — insufficient data")
        return None

    scan_xp = current_config.get("scanXp", 10)
    streak_bonus = current_config.get("streakBonusPerDay", 5)

    changes: dict[str, float] = {}
    reasons: list[str] = []

    # Boost scan rewards if frequency is low
    if scan_freq.value < 2.0:
        changes["scanXp"] = round(scan_xp * 1.15)  # +15%
        reasons.append(f"scan frequency low ({scan_freq.value:.1f}/day)")
    elif scan_freq.value > 4.0:
        changes["scanXp"] = round(scan_xp * 0.9)  # -10%
        reasons.append(f"scan frequency high ({scan_freq.value:.1f}/day), reducing cost")

    # Boost streaks if retention is low
    if retention and retention.value < 0.5:
        changes["streakBonusPerDay"] = round(streak_bonus * 1.2)  # +20%
        reasons.append(f"retention low ({retention.value * 100:.0f}%)")

    if not changes:
        print("  Metrics within acceptable range — no change")
        return None

    return ConfigUpdate(
        economy_overrides=changes,
        reasoning="; ".join(reasons),
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — Quickstart Agent")
    print("=" * 36)
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        # Show variant info
        info = agent.info()
        print(f"  Variant:     {info.variant_name}")
        print(f"  Experiment:  {info.experiment_name} ({info.experiment_status})")
        print(f"  Constraints: update every {info.update_interval_min}min, delta limit {info.delta_limit_pct}%")
        print()

        # Run the automated loop (50 iterations, then stop)
        agent.run(decide, poll_interval=60, max_iterations=50)


if __name__ == "__main__":
    main()
