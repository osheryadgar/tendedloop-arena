# Safety Guardrails

Arena's safety system ensures that autonomous agents cannot harm user experience. Every config update passes through five sequential guardrails before being applied.

## The Five Guardrails

### 1. Control Variant Lock

The control variant in every experiment is **always immutable**. Any attempt to modify it returns:

```json
{
  "accepted": false,
  "rejectionReason": "CONTROL_VARIANT_IMMUTABLE"
}
```

This ensures there is always an unmodified baseline for statistical comparison.

### 2. Experiment Status Gate

Config updates are only accepted when the experiment status is `RUNNING`. All other states return:

```json
{
  "accepted": false,
  "rejectionReason": "EXPERIMENT_NOT_RUNNING"
}
```

### 3. Circuit Breaker

The circuit breaker is a safety stop that freezes all agent updates. It can be triggered:

- **Manually** — By a researcher via the dashboard or API
- **Automatically** — By the health monitor when retention drops dangerously

When active:

```json
{
  "accepted": false,
  "rejectionReason": "CIRCUIT_BREAKER_ACTIVE"
}
```

The circuit breaker must be explicitly reset by a researcher before updates resume.

### 4. Rate Limiter

Agents cannot update more frequently than `updateIntervalMin` (default: 60 minutes). This prevents:

- Rapid oscillation between configurations
- Users experiencing constant reward changes
- Statistical noise from too-frequent changes

```json
{
  "accepted": false,
  "rejectionReason": "RATE_LIMITED",
  "nextAllowedUpdate": "2025-01-15T10:30:00Z"
}
```

### 5. Delta Clamping

The most nuanced guardrail — rather than rejecting large changes, it **clamps** them to the allowed range. The maximum change per parameter per update is `±deltaLimitPct` (default: 50%) of the current value.

Example: if `scanXp` is currently 10 and `deltaLimitPct` is 50%:
- Requested: 100 → Applied: 15 (clamped to +50%)
- Requested: 2 → Applied: 5 (clamped to -50%)
- Requested: 12 → Applied: 12 (within range)

The response includes full visibility:

```json
{
  "accepted": true,
  "appliedConfig": {"scanXp": 15},
  "clampedDeltas": {
    "scanXp": {
      "previous": 10,
      "requested": 100,
      "applied": 15,
      "clamped": true,
      "deltaPercent": 50
    }
  }
}
```

## Guardrail Configuration

When creating an experiment, researchers set:

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `updateIntervalMin` | 60 | 5-1440 | Minimum minutes between updates |
| `deltaLimitPct` | 50 | 5-100 | Maximum % change per parameter |

Tighter constraints = safer but slower convergence. For early experiments, start conservative (60 min, 50%) and loosen as you build confidence.

## Automatic Health Monitoring

The Arena Health Monitor runs every 5 minutes and watches for:

| Condition | Detection | Action |
|-----------|-----------|--------|
| Agent heartbeat timeout | No heartbeat for 3x poll interval | Log event, fire webhook |
| Retention cliff | Variant retention < threshold | Auto-trigger circuit breaker |
| Anomaly pattern | 4+ consecutive max-delta changes | Log warning, fire webhook |

## Best Practices

1. **Start conservative** — Use default guardrails (60 min, 50%) for initial experiments
2. **Monitor early** — Watch the first few decisions closely via the dashboard
3. **Prepare a circuit breaker strategy** — Know when you'll pull the emergency stop
4. **Use reasoning strings** — Every `act()` call should include clear reasoning for the audit trail
5. **Handle rejections gracefully** — Your agent should expect and handle all rejection types
6. **Don't fight clamping** — If your changes are consistently clamped, your step size is too large
