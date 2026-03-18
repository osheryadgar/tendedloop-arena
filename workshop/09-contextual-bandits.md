# Lesson 9: Contextual Bandits — Using Context

> **Time:** ~35 minutes | **Complexity:** Advanced
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Design a feature vector from Arena signals with proper normalization for linear models
> 2. Construct a LinUCB agent that learns context-dependent arm-reward relationships
> 3. Optimize feature engineering by evaluating which context dimensions improve arm selection

> **Example**: [`examples/08_contextual_bandit.py`](../examples/08_contextual_bandit.py)

## The Limitation of Standard Bandits

UCB1 and Thompson Sampling learn: "Arm 2 is the best overall." But what if:
- Arm 2 is best on weekdays, Arm 3 is best on weekends?
- Arm 1 is best early in the experiment, Arm 4 is best later?
- Different arms work for different enrollment sizes?

Standard bandits ignore this **context**. Contextual bandits use it.

## LinUCB: Linear UCB with Context

LinUCB extends UCB1 by modeling the relationship between context and reward as **linear**:

```
expected_reward(arm, context) = theta_arm · context
```

Where `theta_arm` is a learned weight vector for each arm, and `context` is a feature vector extracted from the current signals.

### The Algorithm

For each arm, maintain:
- **A**: A `d×d` matrix (starts as identity) — captures feature correlations
- **b**: A `d×1` vector (starts as zeros) — captures feature-reward correlations

On each round:
```python
theta = A_inv @ b                           # Estimated reward weights
score = theta @ context                     # Predicted reward
bonus = alpha * sqrt(context @ A_inv @ context)  # Confidence bonus (like UCB)
play = argmax(score + bonus)                # Select arm
```

After observing reward:
```python
A[arm] += outer(context, context)  # Update feature correlations
b[arm] += reward * context          # Update feature-reward correlations
```

### Code Walkthrough

The LinUCB algorithm maintains a design matrix `A` and reward vector `b` per arm:

```python
class LinUCB:
    def __init__(self, n_arms, n_features, alpha=1.5):
        self.n_arms = n_arms
        self.alpha = alpha
        # Per-arm matrices
        self.A = [np.eye(n_features) for _ in range(n_arms)]
        self.b = [np.zeros(n_features) for _ in range(n_arms)]

    def select_arm(self, context):
        best_arm, best_ucb = 0, -float('inf')
        for i in range(self.n_arms):
            A_inv = np.linalg.inv(self.A[i])
            theta = A_inv @ self.b[i]
            # Predicted reward + exploration bonus
            ucb = theta @ context + self.alpha * np.sqrt(context @ A_inv @ context)
            if ucb > best_ucb:
                best_arm, best_ucb = i, ucb
        return best_arm

    def update(self, arm, context, reward):
        self.A[arm] += np.outer(context, context)
        self.b[arm] += reward * context
```

**Key insight**: `theta @ context` is the predicted reward (exploitation). `alpha * sqrt(context @ A_inv @ context)` is the confidence bonus (exploration). As more data arrives, `A` grows and `A_inv` shrinks — reducing exploration naturally.

## Feature Engineering

The quality of contextual bandits depends entirely on your features. The example extracts 6 features from Arena signals:

```python
features = [
    enrolled / 200,              # Enrollment scale (0-1)
    active_today / enrolled,     # Daily engagement ratio
    active_7d / enrolled,        # Weekly engagement ratio
    experiment_days / 30,        # Experiment progress
    scan_frequency / 5.0,        # Scan rate (normalized)
    retention_rate,              # Retention (already 0-1)
]
```

**Design principles:**
1. **Normalize to [0, 1]**: Linear models are sensitive to feature scale
2. **Use ratios over absolutes**: `active_today / enrolled` is more meaningful than raw `active_today`
3. **Include temporal features**: `experiment_days` lets the model learn time-dependent patterns
4. **Cap at 1.0**: Prevents outliers from dominating

## When Does Context Help?

Context helps when there's **heterogeneity** — when the best action depends on the situation.

| Scenario | Standard Bandit | Contextual Bandit |
|----------|----------------|-------------------|
| One arm is always best | Both work well | Slight overhead, same result |
| Best arm changes with enrollment | Misses the pattern | Learns the pattern |
| Best arm depends on experiment phase | Averages across phases | Adapts to each phase |
| All arms are context-independent | UCB1/TS is simpler | Unnecessary complexity |

**Rule of thumb**: If you suspect "it depends on the situation," try a contextual bandit.

## When to Use Contextual Bandits

| Situation | Contextual? | Why |
|-----------|------------|-----|
| Weekday/weekend patterns matter | **Yes** | Context encodes temporal features |
| Engagement varies with enrollment size | **Yes** | Population size as context feature |
| Early vs. late experiment behavior | **Yes** | Experiment day as context |
| Only one type of user population | No | Standard bandits are simpler |
| Very few observations (<30) | No | LinUCB needs enough data to learn the linear model |

> **Dependency note:** This example requires `numpy`. Install with `pip install tendedloop-arena[rl]`.

## Exercises

1. **Add time features**: Include hour-of-day and day-of-week as context features. Do certain arms perform better at certain times?
2. **Feature ablation**: Remove one feature at a time and compare performance. Which features matter most?
3. **More arms**: Add 3 more arms with different economy philosophies. Does LinUCB scale well to 7 arms?

## Next

In [Lesson 10](10-bayesian-optimization.md), we leave the discrete arm world and enter continuous parameter optimization with Bayesian Optimization.
