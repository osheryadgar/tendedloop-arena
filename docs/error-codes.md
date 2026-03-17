# API Error Codes

When `agent.act()` is rejected or an API call fails, the response includes a `rejectionReason` or HTTP status code. This document lists all possible values and how to respond.

## Rejection Reasons (from `ConfigResult.rejection_reason`)

These are returned when `result.accepted == False`:

| Code | Meaning | How to Respond |
|------|---------|----------------|
| `CONTROL_VARIANT_IMMUTABLE` | Your variant is the control group — config changes are not allowed. | Check `info.is_control` before calling `act()`. Control variants should only observe. |
| `EXPERIMENT_NOT_RUNNING` | The experiment is not in `RUNNING` status (paused, completed, or draft). | Stop the agent loop. Call `info()` to check `experiment_status`. |
| `CIRCUIT_BREAKER_ACTIVE` | A key metric has degraded significantly since the last config change. The platform is protecting users by freezing config updates until metrics stabilize. | Wait for `next_allowed_update` before retrying. Do not attempt to circumvent. |
| `RATE_LIMITED` | You're updating config too frequently. Minimum interval is `update_interval_min` minutes. | Wait for `next_allowed_update`. Increase your `poll_interval`. |

> **Note:** Delta clamping is not a rejection. When a change exceeds `delta_limit_pct`, it is **accepted but clamped** — see [Clamping vs. Rejection](#clamping-vs-rejection) below.

## Client-Side Validation

`ConfigUpdate` validates on creation — before any API call:

| Constraint | Error | Example |
|-----------|-------|---------|
| `economy_overrides` must not be empty | `ValueError` | `ConfigUpdate(economy_overrides={})` |
| All values must be `int` or `float` | `TypeError` | `ConfigUpdate(economy_overrides={"scanXp": "ten"})` |
| All values must be >= 0 | `ValueError` | `ConfigUpdate(economy_overrides={"scanXp": -5})` |

These checks fail immediately with a clear exception — no API call is made.

## HTTP Status Codes

| Code | Meaning | Retried by SDK? |
|------|---------|-----------------|
| `200` | Success | N/A |
| `204` | Success (no content) | N/A |
| `400` | Bad request — invalid payload format | No |
| `401` | Invalid or expired strategy token | No |
| `403` | Experiment ended, paused, or token revoked. In `run()`, this stops the agent gracefully. | No |
| `404` | Unknown endpoint or variant not found | No |
| `429` | Server-side rate limit (distinct from Arena rate limiting) | No |
| `500` | Internal server error | **Yes** (up to `max_retries`) |
| `502` | Bad gateway (Cloud Run cold start) | **Yes** |
| `503` | Service unavailable | **Yes** |
| `504` | Gateway timeout | **Yes** |

## SDK Safety Behaviors

### HTTPS Enforcement

The SDK refuses to connect over plain HTTP to prevent credential leakage. Only `localhost` / `127.0.0.1` are allowed over HTTP (for local development). Attempting `http://api.example.com` raises `ValueError`.

### Automatic Retry

Transient errors (connection failures, timeouts, 5xx status codes) are retried with exponential backoff up to `max_retries` (default: 2). Client errors (4xx) are never retried.

### Consecutive Error Limit

`agent.run()` tracks consecutive errors. After 5 consecutive failures (API errors or exceptions in your `decide_fn`), the loop re-raises the last exception instead of continuing silently. A single successful cycle resets the counter.

## Handling in Your Agent

```python
result = agent.act(update)

if not result.accepted:
    reason = result.rejection_reason
    if reason == "CIRCUIT_BREAKER_ACTIVE":
        # Metrics degraded — wait and observe
        logging.warning(f"Circuit breaker active until {result.next_allowed_update}")
    elif reason == "RATE_LIMITED":
        # Too frequent — wait for next window
        logging.info(f"Rate limited, next update at {result.next_allowed_update}")
    elif reason == "CONTROL_VARIANT_IMMUTABLE":
        # Should not happen if you check is_control first
        logging.error("Agent assigned to control variant — cannot update config")
    elif reason == "EXPERIMENT_NOT_RUNNING":
        # Experiment is no longer running
        logging.warning("Experiment not running, stopping agent")
        agent.stop()
```

## Clamping vs. Rejection

Clamping is **not** rejection. When a change is clamped:
- `result.accepted` is `True`
- `result.applied_config` contains the clamped values
- `result.clamped_deltas` shows the difference

```python
result = agent.act(ConfigUpdate(
    economy_overrides={"scanXp": 100},  # +900% from default 10
    reasoning="Aggressive boost",
))
# result.accepted == True
# result.applied_config == {"scanXp": 15}  # Clamped to +50%
# result.clamped_deltas == {"scanXp": {"requested": 100, "applied": 15, "clamped": True}}
```

See also: [Guardrails](guardrails.md) | [Classroom Guide](classroom-guide.md) | [FAQ](faq.md)
