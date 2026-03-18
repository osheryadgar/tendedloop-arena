# Lesson 13: Ensemble Methods

> **Time:** ~30 minutes | **Complexity:** Advanced
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Assess when an ensemble approach outperforms a single-strategy agent
> 2. Justify the choice of learning rate (eta) based on experiment duration and reward noise
> 3. Critique sub-strategy diversity and identify correlated failure modes in ensemble design

> **Example**: [`examples/10_ensemble.py`](../examples/10_ensemble.py)

## The Meta-Strategy

You've now learned 8 different approaches. Which one should you use? The honest answer: **it depends on the experiment**. The ensemble approach says: let them compete and let the data decide.

## The Hedge Algorithm

Hedge (also called Multiplicative Weights) maintains a weight for each sub-strategy. On each round:

1. **Sample** a strategy proportionally to weights (weighted random)
2. **Execute** that strategy's proposal
3. **Observe** the outcome (composite score delta)
4. **Update** the selected strategy's weight

```python
# Update rule
weight[i] *= exp(eta * reward)
```

- Positive reward → weight increases → strategy gets selected more
- Negative reward → weight decreases → strategy gets selected less
- Over time, the best strategy dominates

### Why Stochastic Selection?

The example uses **random sampling** proportional to weights, not deterministic argmax. This matters because:
- Early bad luck shouldn't permanently kill a strategy
- Conditions change — a bad strategy might become good
- Stochastic selection maintains exploration

## Designing Sub-Strategies

The ensemble is only as good as its sub-strategies. Design them to be **diverse**:

```python
STRATEGIES = [
    reactive_strategy,      # React to thresholds (fast, simple)
    conservative_strategy,  # Small nudges (stable, safe)
    bold_strategy,          # Large shifts (high risk, high reward)
]
```

### The Three Sub-Strategies

Each sub-strategy encodes a different philosophy:

**1. Reactive** — threshold-based, like Lesson 3:
```python
def reactive_strategy(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if freq and freq.value < 2.0:
        return {"scanXp": round(config["scanXp"] * 1.15)}
    elif freq and freq.value > 4.0:
        return {"scanXp": round(config["scanXp"] * 0.9)}
    return None  # No change needed
```

**2. Conservative** — small incremental steps toward the weakest metric:
```python
def conservative_strategy(signals, config):
    # Find the weakest metric and nudge its lever up by 5%
    worst_metric, worst_value = None, float('inf')
    for name, m in signals.metrics.items():
        if m.confidence != "low" and m.value < worst_value:
            worst_metric, worst_value = name, m.value
    if worst_metric == "SCAN_FREQUENCY":
        return {"scanXp": round(config["scanXp"] * 1.05)}
    elif worst_metric == "RETENTION_RATE":
        return {"streakBonusPerDay": round(config.get("streakBonusPerDay", 5) * 1.05)}
    return None
```

**3. Bold** — large shifts toward high-reward configs:
```python
def bold_strategy(signals, config):
    # If things are going well, push harder. If not, pull back hard.
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if freq and freq.value > 3.0:
        return {"scanXp": round(config["scanXp"] * 1.3)}  # Big boost
    elif freq and freq.value < 1.5:
        return {"scanXp": max(5, round(config["scanXp"] * 0.7))}  # Big cut
    return None
```

### How the Ensemble Decides

```
                    ┌─── Reactive:   {scanXp: 12}  weight: 0.35
                    │
Signals ──> Ensemble┼─── Conservative: {scanXp: 11} weight: 0.45  ← Selected!
                    │
                    └─── Bold:       {scanXp: 15}  weight: 0.20

After observing the result:
  - If composite improved: winning strategy's weight increases
  - If composite dropped: winning strategy's weight decreases
  - Weights are renormalized (Hedge algorithm)
```

**Good ensemble properties:**
- Strategies should **disagree** in many situations
- Include at least one **conservative** strategy (safety net)
- Include at least one **aggressive** strategy (growth potential)
- Strategies should be **independent** (not correlated errors)

**Bad ensemble design:**
- All strategies do basically the same thing (no diversity)
- All strategies are aggressive (no safety net)
- Strategies share state or dependencies (correlated failures)

## The Learning Rate (eta)

`eta` controls how quickly the ensemble adapts:

| eta | Behavior | When to Use |
|-----|----------|-------------|
| 0.1 | Slow adaptation, stable weights | Long experiments, noisy rewards |
| 0.3 | Moderate (default) | Most situations |
| 1.0 | Fast adaptation, volatile weights | Short experiments, clear signal |

## Advanced: Hierarchical Ensembles

You can ensemble ensembles:

```
Top-level Ensemble
├── Bandit Ensemble (UCB1, Thompson, LinUCB)
├── Control Ensemble (PID, Multi-metric)
└── AI Ensemble (LLM, Bayesian Optimization)
```

Each sub-ensemble selects among its strategies, and the top-level ensemble selects among families. This is useful when you have many strategies and want to organize them.

## When to Use Ensembles

| Situation | Ensemble? | Why |
|-----------|----------|-----|
| Uncertain which strategy is best | **Yes** | The ensemble discovers it automatically |
| Different strategies work in different phases | **Yes** | Weights adapt as conditions change |
| Already built multiple agents | **Yes** | Combine them without choosing |
| Limited experiment time | No | Each cycle only tests one strategy — slow learning |
| Need simplicity | No | Ensembles add a layer of complexity |

## Exercises

1. **Add more strategies**: Add PID and Thompson Sampling as sub-strategies. Does the ensemble perform better with more options?
2. **Weight visualization**: Log the weight distribution over time. Plot it to see which strategies rise and fall.
3. **Adaptive eta**: Start with `eta=1.0` (fast learning) and decay to `eta=0.1` over time. Does this improve convergence?

## Next

In [Lesson 14](14-production-safety.md), we'll learn how to deploy agents safely in production with monitoring, alerting, and graceful degradation.
