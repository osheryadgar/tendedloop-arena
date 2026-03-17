# Agent Strategy Guide

This guide covers different approaches to building Arena agents, from simple rules to advanced ML techniques.

## Choosing a Strategy

| Strategy | Best For | Data Needs | Complexity |
|----------|----------|-----------|-----------|
| Rule-based | Quick start, clear hypotheses | Low | Low |
| Multi-metric | Multiple objectives | Medium | Medium |
| LLM-powered | Nuanced reasoning, exploration | Low | Medium |
| Thompson Sampling | Discrete config options | Medium | Medium |
| Gymnasium RL | Continuous optimization | High | High |

## Strategy 1: Rule-Based Thresholds

The simplest approach. Define target ranges for each metric and adjust when values fall outside.

```python
def decide(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if freq and freq.confidence != "low":
        if freq.value < 2.0:
            return ConfigUpdate(
                economy_overrides={"scanXp": round(config["scanXp"] * 1.15)},
                reasoning="Frequency below threshold",
            )
    return None
```

**Pros:** Simple, predictable, easy to audit.
**Cons:** Doesn't adapt to complex dynamics, can oscillate.

**Tips:**
- Use hysteresis (different thresholds for boosting vs. reducing) to prevent oscillation
- Always check confidence before acting
- Start with one metric, add more as you gain confidence

## Strategy 2: Multi-Metric Optimization

Weight multiple metrics and optimize a composite score. Useful when you care about engagement AND retention AND quality.

```python
WEIGHTS = {"SCAN_FREQUENCY": 0.35, "RETENTION_RATE": 0.30, "FEEDBACK_QUALITY": 0.20, "STREAK_LENGTH": 0.15}

def composite_score(signals):
    return sum(
        signals.metrics[m].value * w
        for m, w in WEIGHTS.items()
        if m in signals.metrics and signals.metrics[m].confidence != "low"
    )
```

**Pros:** Balances competing objectives.
**Cons:** Weight selection is subjective, may miss metric interactions.

See: [`examples/03_multi_metric.py`](../examples/03_multi_metric.py)

## Strategy 3: LLM-Powered Reasoning

Use a large language model (Claude, GPT) to analyze signals and propose changes with natural language reasoning.

**Pros:** Handles nuance, provides human-readable explanations, can reason about novel situations.
**Cons:** API costs, latency, potential hallucination.

**Tips:**
- Include current config AND signals in the prompt
- Ask for structured JSON output
- Log the LLM's reasoning in the `reasoning` field for audit
- Use a longer poll interval (5-10 min) to manage API costs

See: [`examples/04_llm_agent.py`](../examples/04_llm_agent.py)

## Strategy 4: Thompson Sampling (Bayesian Bandit)

Define a set of discrete "arms" (config presets) and use Thompson Sampling to explore and exploit.

**Pros:** Theoretically optimal exploration-exploitation tradeoff, handles uncertainty naturally, minimal regret.
**Cons:** Discrete action space (you predefine the options), slow convergence with many arms.

**Tips:**
- Start with 3-5 well-differentiated arms
- Each arm should represent a distinct "philosophy" (scan-heavy, quality-focused, etc.)
- Monitor win rates to understand which strategies work

See: [`examples/05_thompson_sampling.py`](../examples/05_thompson_sampling.py)

## Strategy 5: Gymnasium RL

Use the `ArenaEnv` wrapper with standard RL algorithms. The environment provides observations, your policy selects actions, and the reward is the delta in your primary metric.

**Pros:** Can learn complex, non-linear strategies, continuous action space.
**Cons:** Needs many iterations to converge (days/weeks of real data), sample inefficiency.

**Tips:**
- Start with simple policies (linear, momentum-based) before complex RL
- The real environment is very slow (minutes between steps, not milliseconds)
- Consider offline RL approaches that learn from logged data
- Use `primary_metric` carefully — it defines what "good" means

See: [`examples/02_gymnasium_rl.py`](../examples/02_gymnasium_rl.py)

## Common Patterns

### Confidence Gating

Always check data quality before acting:

```python
def decide(signals, config):
    metric = signals.metrics.get("SCAN_FREQUENCY")
    if not metric or metric.confidence == "low":
        return None  # Insufficient data
    if metric.sample_size < 20:
        return None  # Want more samples
    # ... proceed with decision ...
```

### Gradual Adjustment

Prefer small changes over large ones:

```python
# Good: 10-15% adjustments
changes["scanXp"] = round(current * 1.12)

# Bad: 2x jumps (will be clamped anyway)
changes["scanXp"] = current * 2
```

### Cooldown Periods

After making a change, wait for the effect to stabilize before changing again:

```python
class StatefulDecider:
    def __init__(self, cooldown_cycles=3):
        self.cycles_since_change = 0
        self.cooldown = cooldown_cycles

    def decide(self, signals, config):
        self.cycles_since_change += 1
        if self.cycles_since_change < self.cooldown:
            return None  # In cooldown
        # ... make decision ...
        self.cycles_since_change = 0
```

### Logging and Debugging

Use the reasoning field extensively:

```python
return ConfigUpdate(
    economy_overrides=changes,
    reasoning=f"[cycle={self.cycle}] freq={freq.value:.2f} (n={freq.sample_size}), "
              f"retention={ret.value:.2f}, composite={score:.3f}, "
              f"action: boost scanXp {old}→{new} (+{pct:.0f}%)",
)
```

The reasoning is stored in the decision audit log, viewable via `agent.decisions()` or the research dashboard.
