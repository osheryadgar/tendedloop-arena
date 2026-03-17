# Frequently Asked Questions

## Getting Started

### How do I get a strategy token?

1. Log in to the [TendedLoop Dashboard](https://app.tendedloop.com)
2. Navigate to **Admin > Research > Experiments**
3. Create a new experiment with **Agent Mode** enabled
4. After creating the experiment, click the **"..."** menu and select **"Download Manifest"**
5. The manifest JSON file contains your `strategy_token`

### Can I run multiple agents for one experiment?

Each non-control variant in an AGENT-mode experiment gets its own strategy token. You can run a different agent (or the same agent with different strategies) for each variant. The control variant cannot be modified.

### What happens if my agent crashes?

The platform monitors agent heartbeats. If your agent stops sending heartbeats for 3x its poll interval, an event is logged. The variant's config stays at its last setting — it doesn't revert. Simply restart your agent and it will resume from the current state.

### Can I test my agent without affecting real users?

Not yet — Arena connects to real experiment data. We recommend:
1. Create a test experiment with a small enrollment (5-10 users)
2. Set tight guardrails (`updateIntervalMin=5`, `deltaLimitPct=10`)
3. Monitor closely via the dashboard

## Technical

### Why are my signals cached?

Signals are computed on-demand with a 5-minute server-side cache. This prevents database overload from frequent polling while ensuring data is reasonably fresh. Setting a poll interval less than 5 minutes won't give you fresher data.

### What happens when my config update is clamped?

Delta clamping adjusts your requested values to stay within the allowed range, but still applies the change. The response tells you exactly what happened:

```python
result = agent.act(ConfigUpdate(economy_overrides={"scanXp": 100}))
# result.accepted = True  (it was applied!)
# result.applied_config = {"scanXp": 15}  (clamped from 100 to 15)
# result.clamped_deltas = {"scanXp": {"requested": 100, "applied": 15, "clamped": True}}
```

### Why was my update rejected?

Check `result.rejection_reason`:

| Reason | Meaning | Action |
|--------|---------|--------|
| `CONTROL_VARIANT_IMMUTABLE` | You're trying to modify the control | This is by design — control is always static |
| `EXPERIMENT_NOT_RUNNING` | Experiment isn't in RUNNING state | Wait for the experiment to be started |
| `CIRCUIT_BREAKER_ACTIVE` | Safety stop is active | Contact the researcher to review and reset |
| `RATE_LIMITED` | Too many updates | Wait until `next_allowed_update` |

### What's the difference between `Agent` and `ArenaEnv`?

`Agent` is the core client — it provides direct access to all Arena API methods. Use it for rule-based agents, LLM agents, or custom loops.

`ArenaEnv` is a Gymnasium-compatible wrapper around `Agent`. It provides the standard `reset/step/render` interface expected by RL frameworks. Use it if you want to plug in Stable-Baselines3, RLlib, or similar.

### Can I use async/await?

The current SDK uses synchronous `httpx.Client`. For async use cases, you can wrap calls in a thread executor:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)

async def async_observe(agent):
    return await asyncio.get_event_loop().run_in_executor(executor, agent.observe)
```

A native async client is planned for a future release.

## Research

### How is statistical significance computed?

For continuous metrics (SCAN_FREQUENCY, XP_VELOCITY, STREAK_LENGTH): Welch's t-test with unequal variance assumption.

For proportion metrics (RETENTION_RATE, MISSION_COMPLETION, FEEDBACK_QUALITY): Fisher's exact test.

Effect sizes are reported as Cohen's d with 95% confidence intervals.

### How long should I run an experiment?

It depends on your sample size, expected effect size, and the metric you're optimizing. The experiment builder includes a power analysis that estimates days needed:

- **Small effect** (d=0.2): Requires large samples, weeks of data
- **Medium effect** (d=0.5): Moderate samples, 1-2 weeks
- **Large effect** (d=0.8): Small samples, days

Rule of thumb: plan for at least 2 weeks to allow behavioral patterns to stabilize.

### Can agents affect each other's results?

Agents only control their own variant's economy. Users are randomly assigned to variants and experience only their variant's config. Cross-contamination is minimized by:

1. Random assignment at enrollment
2. Variant-scoped economy resolution
3. Statistical tests that account for between-group variance

### How do I cite TendedLoop Arena?

```bibtex
@software{tendedloop_arena,
  title={TendedLoop Arena: Multi-Agent Gamification Research Platform},
  author={TendedLoop},
  year={2025},
  url={https://github.com/osheryadgar/tendedloop-arena}
}
```
