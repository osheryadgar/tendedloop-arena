# Lesson 8: Thompson Sampling — Bayesian Bandits

> **Time:** ~30 minutes | **Complexity:** Advanced
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Design a Beta-Bernoulli model for binary reward tracking and posterior updating
> 2. Construct a Thompson Sampling agent that explores through posterior randomness rather than explicit bonuses
> 3. Derive binary reward signals from continuous Arena metrics using threshold-based conversion

> **Example**: [`examples/05_thompson_sampling.py`](../examples/05_thompson_sampling.py)

## The Bayesian Perspective

UCB1 asks: "what's the highest the true mean could be?" (confidence bound).

Thompson Sampling asks: "what's the probability that each arm is the best?" (posterior sampling).

The algorithm is surprisingly simple:
1. For each arm, maintain a **belief distribution** over its true reward
2. **Sample** a value from each arm's distribution
3. Play the arm with the **highest sample**
4. **Update** the belief based on the observed reward

## Beta-Bernoulli Model

For binary rewards (good/bad outcome), the natural model is:

- **Prior**: Beta(1, 1) — uniform, no preference
- **After a success**: Beta(α+1, β) — shift toward higher values
- **After a failure**: Beta(α, β+1) — shift toward lower values

```python
# Sample from each arm's posterior
samples = [random.betavariate(alpha[i], beta[i]) for i in range(n_arms)]
chosen = argmax(samples)

# Update after observing outcome
if reward:
    alpha[chosen] += 1  # Success
else:
    beta[chosen] += 1   # Failure
```

### Visual Intuition

```
After 0 observations:  Beta(1,1) = flat line (complete uncertainty)
After 3 wins, 1 loss:  Beta(4,2) = peak around 0.67 (getting confident)
After 20 wins, 5 losses: Beta(21,6) = sharp peak at 0.77 (very confident)
```

Arms with few observations have **wide** distributions → high chance of being sampled high (exploration). Arms with many observations have **narrow** distributions → sampled near their true mean (exploitation).

**The magic**: exploration happens naturally through randomness, not through an explicit bonus term.

## Why Thompson Sampling Works Well in Practice

1. **Natural exploration schedule**: Uncertain arms get explored automatically
2. **Fast convergence**: Once an arm's distribution narrows, it's rarely sampled incorrectly
3. **Robust to noise**: The posterior naturally accounts for variance
4. **Minimal tuning**: The prior (Beta(1,1) = uniform) works well by default, unlike UCB1's `c` which needs calibration

## Converting Arena Rewards to Binary

Arena produces continuous metrics, but Beta-Bernoulli needs binary outcomes. The example converts using a simple threshold:

```python
# Did the composite score improve?
improved = composite > last_composite
if improved:
    alpha[arm] += 1
else:
    beta[arm] += 1
```

This is a simplification. More sophisticated approaches include:
- **Gaussian Thompson Sampling**: Use Normal distributions instead of Beta (handles continuous rewards directly)
- **Quantile thresholding**: "Success" = top 25% of observed rewards
- **Relative improvement**: "Success" = better than the running average

## Exercises

1. **Gaussian Thompson Sampling**: Replace Beta distributions with Normal(mean, 1/n). Sample from N(mean, 1/sqrt(n)) instead. Compare convergence.
2. **Prior sensitivity**: Start with Beta(10, 10) instead of Beta(1, 1). How does a strong prior affect early exploration?
3. **Arm similarity**: Create 5 arms where the best is only 5% better than the second-best. How many rounds until Thompson Sampling identifies it?

## Next

In [Lesson 9](09-contextual-bandits.md), we'll extend bandits to use **context** — the full signal vector — to make smarter arm selections.
