"""
TendedLoop Arena — UCB1 (Upper Confidence Bound) Agent

Classic bandit algorithm that balances exploration and exploitation
by selecting the arm with the highest upper confidence bound.

UCB1 vs Thompson Sampling:
  - UCB1 is deterministic — given the same history, it always picks the same arm
  - Thompson Sampling is stochastic — it samples from posterior distributions
  - UCB1 has stronger theoretical regret bounds
  - Thompson Sampling often performs better empirically
  - Together they cover the two dominant approaches in bandit literature

The UCB formula:
  UCB(arm) = mean_reward(arm) + c * sqrt(ln(total_pulls) / arm_pulls)

  The first term exploits (pick arms with high average reward).
  The second term explores (pick arms with few pulls — high uncertainty).
  c controls the exploration-exploitation tradeoff.

Run:
    pip install git+https://github.com/osheryadgar/tendedloop-arena.git
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/07_ucb1.py
"""

import logging
import math
import os

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")


# ─── Arm Definitions ───
# Each arm is a distinct economy philosophy

ARMS = [
    {
        "name": "Default+",
        "config": {"scanXp": 12, "feedbackXp": 17, "streakBonusPerDay": 6},
        "description": "Slight uplift across the board",
    },
    {
        "name": "Scan Maximizer",
        "config": {"scanXp": 18, "firstScanOfDayXp": 22, "scanDailyCap": 25},
        "description": "Maximize scan volume",
    },
    {
        "name": "Quality First",
        "config": {"feedbackXp": 25, "photoXp": 18, "issueReportXp": 30},
        "description": "Reward detailed feedback over raw scans",
    },
    {
        "name": "Retention Engine",
        "config": {"streakBonusPerDay": 12, "streakBonusCap": 70, "firstScanOfDayXp": 25},
        "description": "Maximize daily return rate via streaks",
    },
    {
        "name": "Minimal Spend",
        "config": {"scanXp": 8, "feedbackXp": 10, "streakBonusPerDay": 4},
        "description": "Lowest viable rewards — test engagement floor",
    },
]


# ─── UCB1 Algorithm ───


class UCB1:
    """
    Upper Confidence Bound (UCB1) multi-armed bandit.

    Args:
        n_arms: Number of available arms.
        c: Exploration parameter. Higher = more exploration.
           sqrt(2) is the theoretically optimal value for [0,1] rewards.
           Use lower (0.5-1.0) for slower convergence environments like Arena.
    """

    def __init__(self, n_arms: int, c: float = 1.0):
        self.n_arms = n_arms
        self.c = c
        self.counts = [0] * n_arms  # How many times each arm was pulled
        self.rewards = [0.0] * n_arms  # Cumulative reward per arm
        self.total_pulls = 0
        self.last_arm: int | None = None
        self.last_composite: float | None = None

    def select_arm(self) -> int:
        """Select arm with highest UCB value."""
        # Play each arm once first (initialization phase)
        for i in range(self.n_arms):
            if self.counts[i] == 0:
                print(f"  UCB1: initializing arm {i} ({ARMS[i]['name']})")
                return i

        # Compute UCB for each arm
        ucb_values = []
        for i in range(self.n_arms):
            mean = self.rewards[i] / self.counts[i]
            exploration = self.c * math.sqrt(math.log(self.total_pulls) / self.counts[i])
            ucb = mean + exploration
            ucb_values.append(ucb)

        chosen = max(range(self.n_arms), key=lambda i: ucb_values[i])

        print(f"  UCB1 values: {[f'{v:.3f}' for v in ucb_values]}")
        print(f"  Selected arm {chosen}: {ARMS[chosen]['name']}")

        return chosen

    def update(self, arm: int, reward: float):
        """Update statistics for the pulled arm."""
        self.counts[arm] += 1
        self.rewards[arm] += reward
        self.total_pulls += 1

        mean = self.rewards[arm] / self.counts[arm]
        print(
            f"  Updated arm {arm} ({ARMS[arm]['name']}): "
            f"reward={reward:.3f}, mean={mean:.3f}, pulls={self.counts[arm]}"
        )

    def compute_composite(self, signals: Signals) -> float:
        """Weighted engagement score from signals."""
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

ucb = UCB1(n_arms=len(ARMS), c=1.0)


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """UCB1 decision function."""
    composite = ucb.compute_composite(signals)
    print(f"\n  Composite score: {composite:.3f}")

    # Update previous arm if we have history
    if ucb.last_arm is not None and ucb.last_composite is not None:
        # Reward = improvement in composite score (normalized to [0,1])
        delta = composite - ucb.last_composite
        reward = max(0.0, min(1.0, 0.5 + delta))  # Center at 0.5, clamp [0,1]
        ucb.update(ucb.last_arm, reward)

    # Select next arm
    arm_idx = ucb.select_arm()
    arm = ARMS[arm_idx]

    ucb.last_arm = arm_idx
    ucb.last_composite = composite

    return ConfigUpdate(
        economy_overrides=arm["config"],
        reasoning=f"UCB1: playing '{arm['name']}' — {arm['description']}",
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — UCB1 Agent")
    print("=" * 30)
    print(f"  Exploration constant c={ucb.c}")
    print()
    print("  Arms:")
    for i, arm in enumerate(ARMS):
        print(f"    [{i}] {arm['name']}: {arm['description']}")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print()

        agent.run(decide, poll_interval=120, max_iterations=50)

        # Final statistics
        print("\nFinal arm statistics:")
        print(f"  {'Arm':<20} {'Pulls':>6} {'Mean':>8} {'Total':>8}")
        print(f"  {'-' * 20} {'-' * 6} {'-' * 8} {'-' * 8}")
        for i, arm in enumerate(ARMS):
            pulls = ucb.counts[i]
            mean = ucb.rewards[i] / pulls if pulls > 0 else 0
            print(f"  {arm['name']:<20} {pulls:>6} {mean:>8.3f} {ucb.rewards[i]:>8.3f}")


if __name__ == "__main__":
    main()
