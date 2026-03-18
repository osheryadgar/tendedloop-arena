# Lesson 5: Multi-Objective Optimization

> **Time:** ~30 minutes | **Complexity:** Intermediate
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Compare weighted-score and Pareto-dominance approaches to multi-objective optimization
> 2. Analyze tradeoffs between competing engagement metrics using lever mappings
> 3. Differentiate between metric boosting and XP inflation and evaluate their effects

> **Example**: [`examples/03_multi_metric.py`](../examples/03_multi_metric.py)

## The Problem

Real gamification isn't one metric. You want:
- **High scan frequency** (users are active)
- **High retention** (users come back)
- **High feedback quality** (users provide useful data)
- **Reasonable streaks** (users build habits)

These objectives **compete**. Boosting scan XP increases frequency but may decrease quality (users scan without leaving feedback). Boosting streak rewards improves retention but inflates XP velocity.

## The Weighted Score Approach

The simplest multi-objective strategy: assign weights to each metric and optimize a composite score.

```python
TARGETS = {
    "SCAN_FREQUENCY":  {"target": 3.0, "weight": 0.35},
    "RETENTION_RATE":  {"target": 0.7, "weight": 0.30},
    "FEEDBACK_QUALITY": {"target": 0.5, "weight": 0.20},
    "STREAK_LENGTH":   {"target": 5.0, "weight": 0.15},
}
```

### Health Scores

For each metric, compute how close it is to its target:

```python
health = metric.value / target  # 1.0 = at target, <1.0 = below, >1.0 = above
```

### The Decision Rule

1. If all metrics are healthy (score >= 0.8), do nothing
2. Find the **worst** metric (lowest health score)
3. Boost the parameters that influence that metric
4. Simultaneously reduce parameters for overperforming metrics (save budget)

### Lever Mapping

The key insight is knowing which parameters affect which metrics:

```python
METRIC_LEVERS = {
    "SCAN_FREQUENCY":  ["scanXp", "firstScanOfDayXp", "scanDailyCap"],
    "RETENTION_RATE":  ["streakBonusPerDay", "streakBonusCap", "firstScanOfDayXp"],
    "FEEDBACK_QUALITY": ["feedbackXp", "photoXp", "feedbackDailyCap"],
    "STREAK_LENGTH":   ["streakBonusPerDay", "streakBonusCap"],
}
```

Notice `firstScanOfDayXp` appears in both SCAN_FREQUENCY and RETENTION_RATE — it's a lever that affects multiple metrics. This creates interdependencies that make the problem interesting.

## Code Walkthrough

The `decide()` function follows three steps:

```python
def decide(signals, current_config):
    # 1. Score every metric (0-1 scale, 1.0 = at target)
    health = compute_health_score(signals)

    # 2. If everything is healthy, do nothing
    if all(score >= 0.8 for score in health.values()):
        return None

    # 3. Find the worst metric, boost its levers
    worst = min(health, key=lambda m: health[m])
    boost = 1.20 if health[worst] < 0.5 else 1.12  # Stronger boost if critical

    changes = {}
    for lever in METRIC_LEVERS[worst]:
        changes[lever] = round(current_config[lever] * boost)

    # Bonus: reduce levers for overperforming metrics (save budget)
    for metric, score in health.items():
        if score > 1.3:  # 30%+ above target
            for lever in METRIC_LEVERS[metric]:
                if lever not in changes:
                    changes[lever] = round(current_config[lever] * 0.92)

    return ConfigUpdate(economy_overrides=changes, reasoning=f"Boosting {worst}")
```

The key insight: **boost the weakest metric** while **trimming the strongest**. This naturally balances resources across objectives.

### Decision Flow

```
Signals ──> Health Scores ──> Worst Metric ──> Lever Mapping ──> ConfigUpdate
              │                    │                │
              │  SCAN_FREQ: 0.7   │  Worst: 0.5    │  scanXp: +15%
              │  RETENTION: 0.9   │  (FEEDBACK)     │
              │  FEEDBACK:  0.5   │                 │  feedbackXp: +10%
              │  XP_VEL:    0.8   │                 │
```

## Tradeoff Management

The real challenge isn't boosting one metric — it's managing tradeoffs:

| Action | Scan Freq | Retention | Quality | XP Velocity |
|--------|-----------|-----------|---------|-------------|
| Increase scanXp | Up | Neutral | Down? | Up |
| Increase feedbackXp | Neutral | Neutral | Up | Up |
| Increase streakBonus | Neutral | Up | Neutral | Up |
| Decrease scanDailyCap | Down | Neutral | Up | Down |

**The XP velocity column** reveals a hidden constraint: almost every boost increases XP velocity. Unchecked, this leads to **XP inflation** — users earn so much XP that rewards lose meaning.

A production multi-metric agent should include XP_VELOCITY as a constraint, not just a metric to maximize.

## Exercises

1. **Add XP velocity constraint**: Modify the agent to reduce boosts when XP_VELOCITY exceeds a threshold.
2. **Pareto analysis**: Instead of the weighted sum, implement Pareto dominance — a config is only "better" if it improves at least one metric without worsening any other.
3. **Dynamic weights**: Adjust weights based on experiment phase (early: weight retention high; late: weight quality high).

## When to Use Multi-Objective

| Situation | Multi-Objective? | Why |
|-----------|-----------------|-----|
| Competing KPIs (engagement vs. quality) | **Yes** | Prevents optimizing one at the expense of others |
| Single clear target | No | Use PID (Lesson 4) — simpler |
| Unknown metric relationships | **Yes** | Health scores surface which metrics are lagging |
| Production deployment | **Yes** | Real systems always have multiple concerns |

## Next

In [Lesson 6](06-explore-exploit.md), we shift from continuous optimization to a fundamentally different question: which of several discrete strategies is best?
