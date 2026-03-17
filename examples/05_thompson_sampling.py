"""
TendedLoop Arena — Thompson Sampling (Bayesian Bandit)

Implements a multi-armed bandit approach where each "arm"
is a parameter configuration. Uses Thompson Sampling with
Beta distributions to balance exploration and exploitation.

This is well-suited for Arena because:
- Data arrives slowly (real users, not simulations)
- We want to minimize regret (bad configs hurt real users)
- Thompson Sampling naturally handles uncertainty

Run:
    pip install tendedloop-agent numpy
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/05_thompson_sampling.py
"""

import logging
import os
import random

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")


# ─── Arm Definitions ───
# Each arm represents a different economy philosophy

ARMS = [
    {
        "name": "Balanced",
        "config": {"scanXp": 12, "feedbackXp": 15, "streakBonusPerDay": 6, "firstScanOfDayXp": 15},
        "description": "Slight boost across the board",
    },
    {
        "name": "Scan-Heavy",
        "config": {"scanXp": 18, "feedbackXp": 10, "streakBonusPerDay": 5, "firstScanOfDayXp": 20},
        "description": "Prioritize scanning volume",
    },
    {
        "name": "Quality-Focus",
        "config": {"scanXp": 8, "feedbackXp": 22, "photoXp": 15, "firstScanOfDayXp": 12},
        "description": "Reward quality feedback over quantity",
    },
    {
        "name": "Streak-Master",
        "config": {"scanXp": 10, "streakBonusPerDay": 10, "streakBonusCap": 60, "firstScanOfDayXp": 20},
        "description": "Heavy streak incentives for retention",
    },
    {
        "name": "Conservative",
        "config": {"scanXp": 10, "feedbackXp": 12, "streakBonusPerDay": 5, "firstScanOfDayXp": 12},
        "description": "Minimal changes from default",
    },
]


# ─── Thompson Sampling ───


class ThompsonSampler:
    """
    Beta-Bernoulli Thompson Sampling.

    Each arm has a Beta(alpha, beta) prior. We sample from each,
    pick the highest, play it, and update based on whether the
    composite metric improved.
    """

    def __init__(self, n_arms: int):
        # Start with uniform prior Beta(1, 1)
        self.alphas = [1.0] * n_arms
        self.betas = [1.0] * n_arms
        self.pulls = [0] * n_arms
        self.last_arm: int | None = None
        self.last_composite: float | None = None

    def select_arm(self) -> int:
        """Sample from each arm's posterior and pick the highest."""
        samples = [
            random.betavariate(self.alphas[i], self.betas[i])
            for i in range(len(self.alphas))
        ]
        chosen = max(range(len(samples)), key=lambda i: samples[i])

        print(f"  Thompson samples: {[f'{s:.3f}' for s in samples]}")
        print(f"  Selected arm {chosen}: {ARMS[chosen]['name']}")

        return chosen

    def update(self, arm: int, reward: bool):
        """Update the posterior for the played arm."""
        self.pulls[arm] += 1
        if reward:
            self.alphas[arm] += 1
        else:
            self.betas[arm] += 1

        win_rate = self.alphas[arm] / (self.alphas[arm] + self.betas[arm])
        print(f"  Updated arm {arm} ({ARMS[arm]['name']}): "
              f"{'win' if reward else 'loss'}, "
              f"win_rate={win_rate:.2f}, pulls={self.pulls[arm]}")

    def compute_composite(self, signals: Signals) -> float:
        """Compute a composite engagement score from signals."""
        freq = signals.metrics.get("SCAN_FREQUENCY")
        retention = signals.metrics.get("RETENTION_RATE")
        quality = signals.metrics.get("FEEDBACK_QUALITY")

        score = 0.0
        if freq and freq.confidence != "low":
            score += freq.value * 0.4  # Weight scan frequency
        if retention and retention.confidence != "low":
            score += retention.value * 10 * 0.35  # Scale retention to ~same range
        if quality and quality.confidence != "low":
            score += quality.value * 10 * 0.25  # Scale quality

        return score


# ─── Decision Logic ───

sampler = ThompsonSampler(n_arms=len(ARMS))


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """Thompson Sampling decision function."""
    composite = sampler.compute_composite(signals)
    print(f"\n  Composite score: {composite:.3f}")

    # Update previous arm based on whether composite improved
    if sampler.last_arm is not None and sampler.last_composite is not None:
        improved = composite > sampler.last_composite
        sampler.update(sampler.last_arm, reward=improved)

    # Select next arm
    arm_idx = sampler.select_arm()
    arm = ARMS[arm_idx]

    sampler.last_arm = arm_idx
    sampler.last_composite = composite

    return ConfigUpdate(
        economy_overrides=arm["config"],
        reasoning=f"Thompson Sampling: playing '{arm['name']}' — {arm['description']}",
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — Thompson Sampling Agent")
    print("=" * 43)
    print()
    print("Arms:")
    for i, arm in enumerate(ARMS):
        print(f"  [{i}] {arm['name']}: {arm['description']}")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print()

        agent.run(decide, poll_interval=120, max_iterations=50)

        # Print final arm statistics
        print("\nFinal arm statistics:")
        for i, arm in enumerate(ARMS):
            win_rate = sampler.alphas[i] / (sampler.alphas[i] + sampler.betas[i])
            print(f"  [{i}] {arm['name']}: pulls={sampler.pulls[i]}, "
                  f"win_rate={win_rate:.2f}, "
                  f"alpha={sampler.alphas[i]:.0f}, beta={sampler.betas[i]:.0f}")


if __name__ == "__main__":
    main()
