"""
TendedLoop Arena — Gymnasium-Compatible RL Loop

Demonstrates using ArenaEnv with the standard reset/step interface
for integration with RL frameworks (Stable-Baselines3, RLlib, CleanRL).

This example uses a simple momentum-based policy. In practice,
replace it with your RL model of choice.

Run:
    pip install tendedloop-agent
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/02_gymnasium_rl.py
"""

import os
import random

from tendedloop_agent import ArenaEnv

# ─── Configuration ───

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")
MAX_STEPS = 100


# ─── Simple Policy ───
#
# Replace this with your RL model (PPO, DQN, SAC, etc.)
# This example uses a random walk with momentum — it increases
# parameters that correlated with positive reward.


class MomentumPolicy:
    """Random walk with momentum — increases params that correlate with reward."""

    def __init__(self):
        self.last_reward: float = 0.0

    def select_action(self, obs: dict) -> dict[str, float]:
        config = obs.get("config", {})

        scan_xp = config.get("scanXp", 10)
        feedback_xp = config.get("feedbackXp", 15)
        streak_bonus = config.get("streakBonusPerDay", 5)

        # If last action had positive reward, keep direction; else reverse
        momentum = 1.0 if self.last_reward >= 0 else -1.0

        # Add randomness for exploration
        noise = random.uniform(-0.05, 0.05)

        return {
            "scanXp": round(scan_xp * (1 + momentum * 0.1 + noise)),
            "feedbackXp": round(feedback_xp * (1 + momentum * 0.05 + noise)),
            "streakBonusPerDay": round(streak_bonus * (1 + momentum * 0.08 + noise)),
        }

    def update(self, reward: float):
        self.last_reward = reward


# ─── Main ───


def main():
    print("TendedLoop Arena — Gymnasium RL Loop")
    print("=" * 36)
    print()

    policy = MomentumPolicy()
    total_reward = 0.0

    with ArenaEnv(
        api_url=ARENA_URL,
        strategy_token=TOKEN,
        primary_metric="SCAN_FREQUENCY",
    ) as env:
        obs = env.reset()
        print(env.render())
        print()

        for step in range(MAX_STEPS):
            action = policy.select_action(obs)
            obs, reward, terminated, truncated, info = env.step(
                action,
                reasoning=f"Step {step + 1}: momentum-based exploration",
            )

            policy.update(reward)
            total_reward += reward

            # Log progress
            status = "accepted" if info.get("accepted") else f"rejected: {info.get('rejection_reason')}"
            scan_freq = obs.get("metric_scan_frequency", 0)
            print(f"  Step {step + 1:3d} | reward={reward:+.3f} | scans/day={scan_freq:.2f} | {status}")

            if terminated:
                print("\n  Experiment ended.")
                break

            if truncated:
                print("  (action truncated — will retry next step)")

        print(f"\n  Total reward: {total_reward:.3f} over {step + 1} steps")
        print(f"\n  Final state:")
        print(env.render())


if __name__ == "__main__":
    main()
