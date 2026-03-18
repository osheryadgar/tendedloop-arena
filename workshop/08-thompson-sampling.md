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

### Beta Distribution Shapes

```
Beta(1,1)         Beta(3,2)         Beta(10,3)        Beta(2,8)
  uniform          leaning right      confident right    confident left

  │  ──────        │     ╱╲          │        ╱╲       │  ╱╲
  │ │      │       │    ╱  ╲         │       ╱  ╲      │ ╱  ╲
  │ │      │       │   ╱    ╲        │      ╱    ╲     │╱    ╲
  │ │      │       │  ╱      ╲       │     ╱      ╲    │      ╲
  │ │      │       │ ╱        ╲      │    ╱        ╲   │       ╲
  └─┴──────┴──     └─────────────    └───────────────   └────────────
  0         1      0           1     0             1   0           1

"I know nothing"  "Probably good"   "Almost certain"  "Probably bad"
```

Each arm maintains its own Beta distribution. Sampling from it naturally balances exploration (wide distributions) and exploitation (peaked distributions).

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

## Code Walkthrough

### The Thompson Sampling Agent

The full pattern integrates Thompson Sampling with the Arena SDK:

```python
class ThompsonSampler:
    def __init__(self, arms, prior_alpha=1.0, prior_beta=1.0):
        self.arms = arms
        self.alphas = [prior_alpha] * len(arms)
        self.betas = [prior_beta] * len(arms)

    def select_arm(self):
        samples = [random.betavariate(a, b) for a, b in zip(self.alphas, self.betas)]
        return max(range(len(self.arms)), key=lambda i: samples[i])

    def update(self, arm_index, reward_binary):
        if reward_binary:
            self.alphas[arm_index] += 1  # Success
        else:
            self.betas[arm_index] += 1   # Failure
```

### The Decide Function

```python
def decide(signals, config):
    composite = compute_composite(signals)
    reward = 1 if composite > previous_composite else 0  # Binary

    sampler.update(current_arm, reward)
    new_arm = sampler.select_arm()

    return ConfigUpdate(
        economy_overrides=ARMS[new_arm],
        reasoning=f"Thompson selected arm {new_arm} (α={sampler.alphas[new_arm]}, β={sampler.betas[new_arm]})",
    )
```

The key insight: Thompson Sampling's `select_arm()` is a single line — `random.betavariate(α, β)` per arm. The simplicity is the strength.

This is a simplification. More sophisticated approaches include:
- **Gaussian Thompson Sampling**: Use Normal distributions instead of Beta (handles continuous rewards directly)
- **Quantile thresholding**: "Success" = top 25% of observed rewards
- **Relative improvement**: "Success" = better than the running average

## When to Use Thompson Sampling

| Situation | Thompson? | Why |
|-----------|----------|-----|
| Discrete config options | **Yes** | Each option is a natural "arm" |
| Want to minimize regret | **Yes** | Near-optimal Bayesian regret bounds |
| Need stochastic exploration | **Yes** | Unlike UCB1, randomly selects — prevents adversarial worst-cases |
| Continuous parameters | No | Use Bayesian Optimization (Lesson 10) |
| Many arms (>20) | Caution | Convergence slows — consider contextual bandits |
| Need deterministic decisions | No | Use UCB1 (Lesson 7) |

## Exercises

1. **Gaussian Thompson Sampling**: Replace Beta distributions with Normal(mean, 1/n). Sample from N(mean, 1/sqrt(n)) instead. Compare convergence.
2. **Prior sensitivity**: Start with Beta(10, 10) instead of Beta(1, 1). How does a strong prior affect early exploration?
3. **Arm similarity**: Create 5 arms where the best is only 5% better than the second-best. How many rounds until Thompson Sampling identifies it?

## Next

In [Lesson 9](09-contextual-bandits.md), we'll extend bandits to use **context** — the full signal vector — to make smarter arm selections.
