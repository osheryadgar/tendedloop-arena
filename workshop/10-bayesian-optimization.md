# Lesson 10: Bayesian Optimization

> **Time:** ~40 minutes | **Complexity:** Advanced
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Design a search space with parameter bounds suitable for Gaussian Process modeling
> 2. Derive the Expected Improvement acquisition function and explain its explore-exploit balance
> 3. Optimize continuous economy parameters sample-efficiently using the surrogate-acquisition BO loop

> **Example**: [`examples/09_bayesian_optimization.py`](../examples/09_bayesian_optimization.py)

## The Continuous Search Problem

Bandits choose between discrete arms. But what if you want to find the optimal `scanXp` value on a continuous range from 5 to 25? With bandits, you'd discretize into 20 options — wasteful. Bayesian Optimization (BO) handles continuous spaces natively.

## Why BO is Perfect for Arena

Arena's optimization problem has three properties that make BO ideal:

1. **Expensive evaluations**: Each config change takes minutes to show effects
2. **Low dimensionality**: 4-6 parameters to tune
3. **Noisy but smooth**: The reward function has structure (nearby configs → similar rewards)

BO is specifically designed for **sample-efficient optimization of expensive black-box functions**.

## How It Works

### 1. Surrogate Model (Gaussian Process)

A GP models the unknown reward function as a distribution over possible functions. Given observed (config, reward) pairs, it predicts:
- **Mean**: Expected reward at any untested config
- **Variance**: Uncertainty at that config

```
High mean + Low variance → Probably good (exploit)
Low mean + High variance → Uncertain, might be good (explore)
```

### 2. Acquisition Function (Expected Improvement)

EI asks: "How much improvement over the current best can we expect from this config?"

```python
EI(x) = E[max(f(x) - best_y, 0)]
```

- High EI near the current best (might improve slightly)
- High EI in unexplored regions (might be much better)
- Zero EI where we're confident the reward is low

### 3. The BO Loop

```
1. Start with N random configs (exploration phase)
2. Fit GP to all observed (config, reward) pairs
3. Find config that maximizes EI (acquisition optimization)
4. Evaluate that config in Arena
5. Observe reward, add to dataset
6. Back to step 2
```

## The Search Space

Define bounds for each parameter:

```python
PARAMS = {
    "scanXp":          (5, 25),    # XP per scan
    "feedbackXp":      (8, 30),    # XP per feedback
    "streakBonusPerDay": (3, 15),  # Daily streak bonus
    "firstScanOfDayXp":  (8, 25), # First-scan bonus
}
```

BO normalizes these to [0, 1] internally and searches over the hypercube.

## Comparison with Other Approaches

| Method | Search Space | Convergence | Best For |
|--------|-------------|------------|----------|
| Grid Search | Discrete | O(n^d) evaluations | Small, known spaces |
| Random Search | Continuous | No learning between evals | Baselines |
| Bandits | Discrete arms | O(log T) regret over T rounds | Choosing between presets |
| **Bayesian Optimization** | **Continuous** | **Good configs in 10-50 evals** | **Tuning 4-10 params** |
| RL (Gymnasium) | Continuous | 1000+ steps to converge | Long-running experiments |

BO's sweet spot: **4-10 parameters, 20-50 evaluations, expensive objective**.

## Limitations

- **Scales poorly beyond ~10 parameters** (GP inference is O(n³))
- **Assumes smoothness** (nearby configs → similar rewards)
- **Cold start**: First N evaluations are random
- **Local optima**: EI can get stuck in local basins

## Exercises

1. **Larger search space**: Add `photoXp` and `scanDailyCap` to the search space. Does performance degrade with 6 parameters?
2. **More initial samples**: Try `N_INITIAL_RANDOM = 10` instead of 5. Does the GP fit better?
3. **Compare with random search**: Replace the BO suggestion with pure random configs. How many evaluations until random search finds a config as good as BO's best?

## Next

In [Lesson 11](11-reinforcement-learning.md), we'll use the Gymnasium interface for full reinforcement learning — the most powerful (but most data-hungry) approach.
