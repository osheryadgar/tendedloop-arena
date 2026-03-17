# Lesson 3: Your First Agent

> **Example**: [`examples/01_quickstart.py`](../examples/01_quickstart.py)

## The Simplest Possible Agent

An Arena agent is just a function that takes signals and returns a config update (or `None` to skip):

```python
def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
```

That's it. The SDK handles everything else — heartbeats, polling, error recovery.

## Code Walkthrough

### 1. Connect to Arena

```python
from tendedloop_agent import Agent, ConfigUpdate, Signals

with Agent(api_url="https://api.tendedloop.com", strategy_token=TOKEN) as agent:
    info = agent.info()
    print(f"Variant: {info.variant_name}")
```

The `Agent` is a context manager. It opens an HTTP connection, and `info()` confirms you're connected and shows your variant's constraints.

### 2. Write the Decision Function

```python
def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    scan_freq = signals.metrics.get("SCAN_FREQUENCY")

    # Rule 1: Never act on low-confidence data
    if not scan_freq or scan_freq.confidence == "low":
        return None

    # Rule 2: Boost if engagement is low
    if scan_freq.value < 2.0:
        return ConfigUpdate(
            economy_overrides={"scanXp": round(current_config["scanXp"] * 1.15)},
            reasoning="Scan frequency low, boosting +15%",
        )

    return None  # Everything looks fine, do nothing
```

Three key patterns:
1. **Confidence gating** — always check before acting
2. **Incremental changes** — 15%, not 200%
3. **Clear reasoning** — stored in the audit trail

### 3. Run the Loop

```python
agent.run(decide, poll_interval=60, max_iterations=50)
```

This starts the automated cycle:
- Call `observe()` every 60 seconds
- Pass signals + current config to your `decide()` function
- If `decide()` returns a `ConfigUpdate`, call `act()`
- Background heartbeat thread runs automatically
- Stops after 50 iterations or if the experiment ends

## What Happens When You Run It

```
TendedLoop Arena — Quickstart Agent
====================================
  Variant:     Treatment-A
  Experiment:  XP Boost Test (RUNNING)
  Constraints: update every 60min, delta limit 50%

2026-03-17 10:00:00 Agent started for variant 'Treatment-A' in 'XP Boost Test'
2026-03-17 10:01:00   Skipping — insufficient data
2026-03-17 10:02:00   Skipping — insufficient data
2026-03-17 10:03:00   Metrics within acceptable range — no change
...
2026-03-17 11:04:00 Config accepted: scan frequency low (1.8/day)
2026-03-17 11:05:00   Metrics within acceptable range — no change
```

The agent polls every 60 seconds (the `poll_interval`), but can only submit changes every 60 *minutes* (the `updateIntervalMin` guardrail). Most cycles observe without acting. Notice the first cycles skip due to insufficient data — this is correct behavior. Patient agents outperform hasty ones.

## The Three Rules of Good Agents

From this simple example, three rules emerge:

**Rule 1: Wait for confidence.** Don't act on low-confidence data. You'll waste your rate-limited update slots on noise.

**Rule 2: Change incrementally.** 10-20% adjustments. The guardrails will clamp larger changes anyway, and small changes are easier to measure.

**Rule 3: Explain your reasoning.** The `reasoning` string is stored permanently in the decision audit log. Future-you (and your colleagues) will thank you.

## Exercises

The full `01_quickstart.py` already has retention logic and a high-frequency reduction. For these exercises, start from the simplified version above (frequency-only) and extend it:

1. **Add hysteresis**: Boost `scanXp` when frequency drops below 1.8, but only reduce it when frequency exceeds 4.5. This gap prevents oscillation around a single threshold.
2. **Add a cooldown**: After making a change, skip the next 3 cycles to let the effect stabilize before measuring again. (Hint: track `cycles_since_last_change` in a class.)
3. **Add a ceiling**: Don't boost `scanXp` above 25 — at some point, higher rewards cause inflation without improving engagement.

## Next

In [Lesson 4](04-feedback-loops.md), we'll replace these ad-hoc rules with a proper feedback controller using PID control theory.
