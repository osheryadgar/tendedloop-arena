# Lesson 14: Going to Production

> **Example**: [`examples/12_production_safety.py`](../examples/12_production_safety.py)

## The Gap Between Demo and Production

Every example so far works perfectly in a demo. Production is different:
- The API returns 429 (rate limited) and you didn't expect it
- Your experiment gets paused by a researcher while your agent is running
- A bug in your reward function causes 20 consecutive max-delta changes
- The circuit breaker fires at 3 AM and nobody notices

This lesson covers the patterns that bridge the gap.

## Pattern 1: Rejection Handling

The platform can reject your update for several reasons. Handle each:

```python
result = agent.act(update)
if not result.accepted:
    match result.rejection_reason:
        case "RATE_LIMITED":
            # Expected — wait until next_allowed_update
            monitor.record_rejection()
        case "CIRCUIT_BREAKER_ACTIVE":
            # Something is wrong — back off significantly
            monitor.record_rejection()
            # Consider entering a longer cooldown
        case "EXPERIMENT_NOT_RUNNING":
            # Experiment paused or completed — exit the loop
            break
        case "CONTROL_VARIANT_IMMUTABLE":
            # Misconfiguration — you have the wrong token
            raise RuntimeError("Agent assigned to control variant")
```

## Pattern 2: Cooldown After Rejection

Don't immediately retry after rejection. Implement a cooldown:

```python
class SafetyMonitor:
    def __init__(self, cooldown_cycles=3):
        self.cycles_since_reject = 999

    def record_rejection(self):
        self.cycles_since_reject = 0

    def should_skip(self) -> bool:
        return self.cycles_since_reject < self.cooldown_cycles

    def tick(self):
        self.cycles_since_reject += 1
```

After a rate-limit rejection, skip 3 cycles. After a circuit breaker, skip 10+.

## Pattern 3: Metric Drift Detection

If metrics swing wildly between cycles, something unusual is happening (holiday, outage, onboarding wave). Reduce your change magnitude:

```python
def check_drift(self, signals):
    for metric, value in current_metrics.items():
        prev = self.last_metrics.get(metric)
        if prev and prev > 0:
            drift = abs(value - prev) / prev
            if drift > 0.20:  # 20%+ swing
                return 0.5    # Dampen changes to 50%
    return 1.0  # Full magnitude
```

**The principle**: When the environment is unstable, be conservative.

## Pattern 4: Anomaly Self-Detection

Track your own decisions and flag anomalies. The `record_decision()` method stores whether each change was clamped by the platform:

```python
def record_decision(self, changes, clamped=False):
    self.decision_history.append({"changes": changes, "clamped": clamped})

    # Flag if the last 4 decisions were all clamped by guardrails
    recent = self.decision_history[-4:]
    if len(recent) >= 4 and all(d.get("clamped") for d in recent):
        logger.warning("4 consecutive clamped decisions — possible runaway")
        self.cycles_since_reject = 0  # Force cooldown
```

After `act()` returns, check `result.clamped_deltas` to determine if clamping occurred:

```python
was_clamped = bool(
    result.clamped_deltas
    and any(d.get("clamped") for d in result.clamped_deltas.values())
)
monitor.record_decision(update.economy_overrides, clamped=was_clamped)
```

The health monitor detects this server-side too, but client-side detection is faster and triggers an immediate cooldown.

## Pattern 5: Structured Logging

In production, print statements aren't enough. Use Python's logging module with structured data:

```python
import logging
logger = logging.getLogger("arena.production")

logger.info(
    "Config accepted",
    extra={
        "cycle": cycle,
        "changes": update.economy_overrides,
        "dampening": dampening,
        "drift": drift_pct,
    }
)
```

Ship logs to your observability stack (Datadog, Grafana, etc.) for dashboards and alerting.

## Pattern 6: Webhook Registration

Register webhooks to get notified of platform events:

```python
agent.register_webhook(
    url="https://your-server.com/arena-events",
    events=["circuit_breaker_triggered", "heartbeat_timeout"],
)
```

Wire this to your alerting (Slack, PagerDuty, email) so you know when something needs attention.

## Pattern 7: Custom Loop for Fine-Grained Control

For production, use your own loop instead of `agent.run()`:

```python
info = agent.info()
config = dict(info.current_config or {})

for cycle in range(1000):
    signals = agent.observe()
    update = decide(signals, config)

    if update:
        result = agent.act(update)
        if result.accepted and result.applied_config:
            config.update(result.applied_config)
        monitor.record_result(result.accepted, result.rejection_reason)

    time.sleep(60)
```

This gives you full control over error handling, logging, and recovery — things `agent.run()` handles generically.

## Production Checklist

Before deploying an agent to a real experiment:

- [ ] **Confidence gating**: Agent never acts on low-confidence data
- [ ] **Rejection handling**: All rejection types handled gracefully
- [ ] **Cooldown logic**: Backoff after rejections
- [ ] **Drift detection**: Dampening when metrics are volatile
- [ ] **Structured logging**: Every decision logged with context
- [ ] **Webhook alerting**: Circuit breaker and timeout events go to your on-call
- [ ] **Max iterations**: Agent stops eventually (no infinite loops)
- [ ] **Graceful shutdown**: Clean exit on SIGINT/SIGTERM
- [ ] **Monitoring dashboard**: Track cumulative reward, rejection rate, drift over time
- [ ] **Runbook**: Document what to do when the circuit breaker fires

## What You've Learned

Over 14 lessons, you've built agents using:

| Module | Approach | Key Insight |
|--------|----------|------------|
| Foundations | Rule-based | The observe-decide-act loop |
| Control | PID | Feedback loops and target tracking |
| Control | Multi-metric | Balancing competing objectives |
| Bandits | Explore-Then-Exploit | The explore-exploit dilemma |
| Bandits | UCB1 | Optimism under uncertainty |
| Bandits | Thompson Sampling | Bayesian posterior sampling |
| Bandits | LinUCB | Context-dependent arm selection |
| Optimization | Bayesian Optimization | Sample-efficient continuous search |
| RL | Gymnasium | State-action-reward framework |
| AI | LLM Agents | Natural language reasoning |
| Meta | Ensemble (Hedge) | Combining strategies adaptively |
| Production | Safety patterns | Monitoring, alerting, graceful degradation |

The right approach depends on your experiment:
- **Short experiment, few data points** → Bandits or BO
- **Long experiment, clear target** → PID
- **Multiple objectives** → Multi-metric or Ensemble
- **Need explanations** → LLM agent
- **No idea what works** → Ensemble of everything

Welcome to multi-agent gamification research.
