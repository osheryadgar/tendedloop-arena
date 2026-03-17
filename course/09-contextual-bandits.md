# Lesson 9: Contextual Bandits — Using Context

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

## Exercises

1. **Add time features**: Include hour-of-day and day-of-week as context features. Do certain arms perform better at certain times?
2. **Feature ablation**: Remove one feature at a time and compare performance. Which features matter most?
3. **More arms**: Add 3 more arms with different economy philosophies. Does LinUCB scale well to 7 arms?

## Next

In [Lesson 10](10-bayesian-optimization.md), we leave the discrete arm world and enter continuous parameter optimization with Bayesian Optimization.
