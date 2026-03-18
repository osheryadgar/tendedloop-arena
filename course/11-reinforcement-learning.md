# Lesson 11: Reinforcement Learning

> **Time:** ~25 minutes | **Complexity:** Advanced
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Integrate the ArenaEnv Gymnasium wrapper to frame gamification tuning as an MDP
> 2. Compose reward-shaping functions that balance multiple objectives without Goodhart's Law pitfalls
> 3. Adapt policy complexity to Arena's data-scarce environment constraints

> **Example**: [`examples/02_gymnasium_rl.py`](../examples/02_gymnasium_rl.py)

## RL in Arena

Reinforcement Learning frames Arena as a Markov Decision Process:
- **State**: Current signals (enrollment, activity, metrics)
- **Action**: Economy config changes
- **Reward**: Change in primary metric value
- **Episode**: One experiment lifetime

The `ArenaEnv` wrapper provides the standard Gymnasium interface:

```python
obs = env.reset()
for step in range(100):
    action = policy.select_action(obs)
    obs, reward, terminated, truncated, info = env.step(action)
```

## The Honest Truth About RL in Arena

RL is the most powerful approach in theory. In practice, it's the **hardest to make work** in Arena because:

1. **Data scarcity**: Arena produces ~1 sample per minute. RL algorithms like PPO need thousands.
2. **Delayed effects**: Changing scanXp today affects behavior over days, not seconds.
3. **Non-stationarity**: User behavior changes with weekday/weekend, holidays, onboarding waves.
4. **No simulator**: You can't reset the environment and replay. Each step is real.

**Recommendation**: Use RL when you have 100+ experiment days and can tolerate slow convergence. For shorter experiments, bandits or BO are more sample-efficient.

## Reward Shaping

The default reward is the delta in your primary metric. But raw deltas are noisy and may not capture what you want. Consider:

```python
# Simple delta (default)
reward = current_freq - previous_freq

# Normalized to target (more stable)
reward = -abs(target_freq - current_freq)  # Negative distance to target

# Multi-objective (weighted sum)
reward = 0.4 * freq_delta + 0.3 * retention + 0.2 * quality - 0.1 * xp_inflation
```

**Warning**: Reward shaping is an art. A poorly designed reward creates agents that optimize the reward without improving the actual objective (Goodhart's Law).

## Policy Design

The example uses a simple momentum policy. For production RL, consider:

| Approach | Complexity | Data Needs |
|----------|-----------|-----------|
| Linear policy | Low | ~50 steps |
| Tabular Q-learning | Low | ~200 steps |
| DQN (deep Q-network) | Medium | ~1000 steps |
| PPO/SAC | High | ~5000 steps |

**For Arena, start with the simplest policy that works.** A linear policy mapping observations to actions often outperforms complex networks given Arena's data constraints.

## Exercises

1. **Reward shaping**: Replace the raw delta reward with distance-to-target. Does the agent converge faster?
2. **Multi-metric reward**: Design a reward that balances scan frequency (weight 0.5) and retention (weight 0.5). What tradeoffs emerge?
3. **Offline RL**: Save all (observation, action, reward) tuples to a file. Train a policy offline using the logged data, then deploy it.

## Next

In [Lesson 12](12-llm-agents.md), we'll take a completely different approach — using a language model to reason about signals in natural language.
