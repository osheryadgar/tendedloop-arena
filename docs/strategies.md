# Agent Strategy Guide

This guide covers different approaches to building Arena agents, from simple rules to advanced ML techniques.

## Choosing a Strategy

| Strategy | Best For | Data Needs | Complexity |
|----------|----------|-----------|-----------|
| Rule-based | Quick start, clear hypotheses | Low | Low |
| PID Controller | Maintaining a target metric | Low | Low |
| Multi-metric | Multiple objectives | Medium | Medium |
| UCB1 | Discrete arms, strong regret bounds | Medium | Medium |
| Thompson Sampling | Discrete arms, empirical performance | Medium | Medium |
| LLM-powered | Nuanced reasoning, exploration | Low | Medium |
| Contextual Bandit | Context-dependent arm selection | Medium | High |
| Bayesian Optimization | Sample-efficient continuous search | Medium | High |
| Ensemble | Combining multiple strategies | Medium | High |
| Gymnasium RL | Continuous optimization, long runs | High | High |

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

## Strategy 6: PID Controller

Use classic control theory to maintain a target metric. Define a setpoint (e.g., 3.0 scans/day), measure error each cycle, and adjust using proportional + integral + derivative terms.

```python
error = target - current_value
output = Kp * error + Ki * integral(error) + Kd * derivative(error)
new_scan_xp = round(scan_xp * (1 + output / 10))
```

**Pros:** No training data needed, works from cycle 1, well-understood, deterministic.
**Cons:** Single-metric (one PID per target), requires tuning Kp/Ki/Kd gains.

**Tips:**
- Start conservative: `Kp=0.5, Ki=0.05, Kd=0.1`
- Use anti-windup on the integral term to prevent oscillation
- The derivative term dampens overshoot but amplifies measurement noise

See: [`examples/06_pid_controller.py`](../examples/06_pid_controller.py)

## Strategy 7: UCB1 (Upper Confidence Bound)

The other classic bandit alongside Thompson Sampling. UCB1 is deterministic — it always picks the arm with the highest upper confidence bound:

```
UCB(arm) = mean_reward(arm) + c * sqrt(ln(total_pulls) / arm_pulls)
```

**Pros:** Deterministic, strong theoretical regret bounds, no randomness.
**Cons:** Discrete action space, can be slow to converge with many arms.

**Tips:**
- Use `c=1.0` for a good exploration-exploitation balance
- Lower `c` (0.5) for less exploration, higher `c` (2.0) for more
- Works best with 3-7 well-differentiated arms

See: [`examples/07_ucb1.py`](../examples/07_ucb1.py)

## Strategy 8: Contextual Bandit (LinUCB)

Unlike standard bandits that ignore context, LinUCB uses the full signal vector (enrollment, activity, experiment day) to make context-dependent decisions. Different arms may be best in different situations.

**Pros:** Learns that different configs work in different contexts, principled exploration.
**Cons:** Requires feature engineering, needs numpy, slower convergence than simple bandits.

**Tips:**
- Normalize context features to [0, 1]
- Include enrollment ratio, activity ratio, experiment progress as features
- Start with `alpha=1.5` and reduce as you get more data

See: [`examples/08_contextual_bandit.py`](../examples/08_contextual_bandit.py)

## Strategy 9: Bayesian Optimization

Sample-efficient black-box optimization using a Gaussian Process surrogate model. Ideal for Arena's slow feedback loop where each evaluation is expensive.

**Pros:** Finds good configs in very few iterations, handles continuous parameter spaces, principled exploration.
**Cons:** Scales poorly with many parameters (>10), needs numpy, computationally heavier per iteration.

**Tips:**
- Start with 5 random samples before fitting the GP
- Use Expected Improvement as the acquisition function
- Keep the search space to 3-5 parameters for best results
- For production use, consider scikit-optimize or BoTorch

See: [`examples/09_bayesian_optimization.py`](../examples/09_bayesian_optimization.py)

## Strategy 10: Ensemble (Strategy Committee)

Combine multiple sub-strategies using the Hedge (multiplicative weights) algorithm. Each strategy proposes a config, the ensemble picks the highest-weighted one, and weights are updated based on outcomes.

**Pros:** Robust — if one strategy fails, others take over. Adapts over time. Bring your own sub-strategies.
**Cons:** Only as good as the best sub-strategy. More complex to debug.

**Tips:**
- Use 3-5 diverse sub-strategies (don't duplicate similar approaches)
- Set `eta=0.3` for moderate adaptation speed
- Mix simple (rule-based) and complex (bandit) sub-strategies

See: [`examples/10_ensemble.py`](../examples/10_ensemble.py)

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
