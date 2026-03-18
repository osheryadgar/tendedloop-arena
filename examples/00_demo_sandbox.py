"""
TendedLoop Arena — Demo Sandbox

Run the local sandbox server, then run this agent against it.
No TendedLoop account needed!

Terminal 1:
    python -m tendedloop_agent demo

Terminal 2:
    python examples/00_demo_sandbox.py
"""

import logging
import os

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

# ─── Configuration ───

ARENA_URL = os.environ.get("ARENA_URL", "http://localhost:7860")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_demo_local")


# ─── Decision Logic ───


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """
    Simple threshold-based strategy for the demo sandbox.

    Rules:
    - Boost scan XP when frequency drops below 2.0/day
    - Reduce scan XP when frequency exceeds 4.0/day
    - Boost streak bonus when retention is below 60%
    - Boost feedback XP when quality is below 3.0
    """
    scan_freq = signals.metrics.get("SCAN_FREQUENCY")
    retention = signals.metrics.get("RETENTION_RATE")
    quality = signals.metrics.get("FEEDBACK_QUALITY")

    if not scan_freq:
        print("  [skip] No scan frequency data yet")
        return None

    if scan_freq.confidence == "low":
        print(f"  [skip] Low confidence (n={scan_freq.sample_size}), waiting for more data...")
        return None

    scan_xp = current_config.get("scanXp", 10)
    streak_bonus = current_config.get("streakBonusPerDay", 5)
    feedback_xp = current_config.get("feedbackXp", 15)

    changes: dict[str, float] = {}
    reasons: list[str] = []

    # Rule 1: Scan frequency tuning
    if scan_freq.value < 2.0:
        new_val = min(15, round(scan_xp * 1.15))
        if new_val != scan_xp:
            changes["scanXp"] = new_val
            reasons.append(
                f"scan freq low ({scan_freq.value:.2f}/day) -> boost scanXp to {new_val}"
            )
    elif scan_freq.value > 4.0:
        new_val = max(5, round(scan_xp * 0.9))
        if new_val != scan_xp:
            changes["scanXp"] = new_val
            reasons.append(
                f"scan freq high ({scan_freq.value:.2f}/day) -> reduce scanXp to {new_val}"
            )

    # Rule 2: Retention via streaks
    if retention and retention.value < 0.60:
        new_val = min(8, round(streak_bonus * 1.2))
        if new_val != streak_bonus:
            changes["streakBonusPerDay"] = new_val
            reasons.append(
                f"retention low ({retention.value:.0%}) -> boost streakBonus to {new_val}"
            )

    # Rule 3: Feedback quality
    if quality and quality.value < 3.0:
        new_val = min(22, round(feedback_xp * 1.1))
        if new_val != feedback_xp:
            changes["feedbackXp"] = new_val
            reasons.append(f"quality low ({quality.value:.2f}) -> boost feedbackXp to {new_val}")

    if not changes:
        print("  [hold] All metrics within acceptable range")
        return None

    return ConfigUpdate(economy_overrides=changes, reasoning="; ".join(reasons))


# ─── Main ───


def main():
    print()
    print("=" * 50)
    print("  TendedLoop Arena — Demo Sandbox Agent")
    print("=" * 50)
    print()
    print(f"  Server:  {ARENA_URL}")
    print(f"  Token:   {TOKEN[:12]}...")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN, heartbeat_interval=15) as agent:
        # Show variant info
        info = agent.info()
        print(f"  Variant:     {info.variant_name}")
        print(f"  Experiment:  {info.experiment_name} ({info.experiment_status})")
        print(f"  Config:      {info.current_config}")
        print(
            f"  Constraints: update every {info.update_interval_min}min, delta limit {info.delta_limit_pct}%"
        )
        print()

        # Check scoreboard
        scoreboard = agent.scoreboard()
        print("  Scoreboard:")
        for entry in scoreboard:
            role = "CONTROL" if entry.is_control else "TREATMENT"
            print(f"    {entry.variant_name:20s}  {role:10s}  enrolled={entry.enrolled_count}")
        print()

        # Run the observe-decide-act loop
        # In demo mode, the rate limit is 60s, so we poll every 65s
        print("  Starting agent loop (poll every 65s, 10 iterations)...")
        print("  " + "-" * 46)
        print()

        agent.run(decide, poll_interval=65, max_iterations=10)

    print()
    print("  Demo complete! Check the server terminal for the full request log.")
    print()


if __name__ == "__main__":
    main()
