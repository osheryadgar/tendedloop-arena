# The 5 Ways Your Agent Can Break Production (and How to Prevent Each)

Your agent works in the sandbox. You've tested it for hours. The metrics go up, the rewards converge, the logs look clean. You deploy it to a real experiment with real users and go to bed feeling pretty good about yourself.

At 3 AM, it does something catastrophic.

Let me tell you about the agent that ran while everyone was sleeping.

## The Prelude

A team deployed a simple threshold agent to a production experiment. The logic was straightforward: if scan frequency drops below 2.0, boost `scanXp` by 15%. The agent observed, decided, acted. Textbook stuff.

But the agent never checked confidence levels. On a quiet Sunday night, with only 5 active users, the scan frequency metric read 0.8 with a sample size of 3. The agent saw 0.8, panicked, and cranked `scanXp` from 10 to 12. Next cycle, still low (because it's Sunday night and 5 people are asleep), so it boosted again. And again. By Monday morning, `scanXp` was at 45. Users were getting nearly five times the intended XP per scan. The team spent the next week trying to deflate the economy without tanking engagement.

This is Break 2, but I'm telling you about it first because every break in this post follows the same pattern: something that never happened in the sandbox happens in production, and the agent doesn't know how to respond.

Here are the five ways it happens and the fix for each.

## Break 1: The Oscillator

**The story.** You deploy a rule-based agent with two thresholds: if scan frequency drops below 2.0, increase `scanXp`; if it rises above 4.0, decrease it. In the sandbox, it converges nicely around 3.0 and stays there.

In production, something different happens. The agent boosts `scanXp` from 10 to 12. Users respond. Frequency jumps to 4.2. The agent cuts `scanXp` to 10. Frequency drops to 1.8. The agent boosts again. Back and forth, every cycle, forever. Users experience a reward structure that changes constantly, and they stop trusting the system.

**What went wrong.** The agent has no concept of settling time. It reacts to every signal immediately, creating a feedback loop faster than the user behavior can stabilize.

**The fix: cooldown periods.** After making a change, wait a minimum number of cycles before acting again. This gives the system time to reach a new equilibrium before measuring the effect.

```python
class SafetyMonitor:
    def __init__(self, cooldown_cycles=3):
        self.cycles_since_change = 999

    def can_act(self) -> bool:
        return self.cycles_since_change >= self.cooldown_cycles

    def record_action(self):
        self.cycles_since_change = 0

    def tick(self):
        self.cycles_since_change += 1
```

Three cycles of cooldown at 60-minute intervals means you wait at least 3 hours between changes. That's usually enough for user behavior to reflect the previous change.

## Break 2: The Confidence Ignorer

**The story.** This is the one from the prelude. The agent treated all data equally, whether it came from 500 users or 3. On Sunday nights, holidays, and during onboarding waves, the sample sizes were tiny. The metrics were noise. The agent treated them as signal.

**What went wrong.** The agent never looked at the `confidence` field on the metrics. Arena provides three levels -- `high`, `medium`, and `low` -- based on sample size and variance. Low confidence means "this number might be meaningless."

**The fix: confidence gating.** If the data isn't trustworthy, don't act on it. This is the single most important safety check you can add.

```python
def decide(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")

    # The most important two lines in production
    if not freq or freq.confidence == "low":
        return None  # Do nothing. Wait for better data.

    # ... rest of your strategy
```

Two lines. That's all it takes. And those two lines would have prevented the Sunday night XP inflation entirely. When I review student agents, this is the first thing I look for. If your agent doesn't gate on confidence, it's not ready for production. Full stop.

## Break 3: The Rate Limit Fighter

**The story.** A team set their agent's `poll_interval` to 10 seconds because "faster feedback means faster convergence." Their agent called `act()` every 10 seconds. The platform's `updateIntervalMin` was set to 60 minutes. So 99.7% of their updates were rejected with `RATE_LIMITED`. The agent logged 5,000 rejections per day, burned through its error budget, and the remaining 0.3% of accepted updates were essentially random because the agent had no awareness of which decisions actually went through.

**What went wrong.** The agent's polling frequency was wildly mismatched with the platform's rate limit. Polling every 10 seconds when you can only act every 60 minutes means you're doing 360 observations for every one action. That's not "fast feedback." That's noise.

**The fix: match your rhythm to the platform's.** Check the experiment's `updateIntervalMin` from `agent.info()` and set your `poll_interval` accordingly. A good rule of thumb: poll at 1-2x the update interval.

```python
info = agent.info()
min_interval = info.update_interval_min * 60  # Convert to seconds

# Poll slightly more often than the limit, but not absurdly
agent.run(decide, poll_interval=max(min_interval, 60))
```

If the platform says you can update every 60 minutes, poll every 60 minutes. You'll observe, decide, and act in sync with what the platform actually allows. No wasted calls, no rejection floods.

## Break 4: The Goodhart's Monster

**The story.** An agent was tasked with maximizing scan frequency. It did exactly that. It boosted `scanXp` to the platform's clamped maximum, set `firstScanOfDayXp` as high as guardrails allowed, and pushed `scanDailyCap` up so more scans counted. Scan frequency went from 2.0 to 6.5. Mission accomplished.

Except users were gaming the system. They'd scan the same QR code five times in a row, collect their XP, and leave. Feedback quality dropped to near zero. Retention started falling because the "game" felt hollow -- there was no reason to give thoughtful feedback when you could farm XP by repeatedly scanning the bathroom code.

The agent hit its target metric and destroyed the thing the metric was supposed to measure.

**What went wrong.** Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure." The agent optimized one number without any constraint on the other numbers that mattered.

**The fix: multi-objective constraints.** Never optimize a single metric. Always add secondary metrics as constraints, even if your primary goal is clear.

```python
def decide(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")
    quality = signals.metrics.get("FEEDBACK_QUALITY")
    retention = signals.metrics.get("RETENTION_RATE")

    # Primary goal: boost frequency
    if freq and freq.value < 2.0 and freq.confidence != "low":
        # But ONLY if quality and retention aren't suffering
        if quality and quality.value < 0.5:
            return None  # Quality is tanking, don't make it worse
        if retention and retention.value < 0.6:
            return None  # Retention is dropping, hold steady

        return ConfigUpdate(economy_overrides={"scanXp": round(config["scanXp"] * 1.1)})
    return None
```

The secondary metrics act as guard rails on your optimization. You can boost frequency all you want, as long as quality stays above 0.5 and retention stays above 0.6. The moment those constraints are violated, the agent backs off.

## Break 5: The Silent Crasher

**The story.** A team deployed their agent on a Friday afternoon and left for the weekend. Saturday morning at 2 AM, the Anthropic API returned a 500 error (it happens). The agent's LLM call raised an unhandled exception. The process crashed. The variant's economy config was stuck at whatever the last update was -- which happened to be an aggressive boost that was intended to be temporary, with a reduction planned for the next cycle.

For 36 hours, users in that variant experienced inflated rewards. Nobody knew until Monday morning.

**What went wrong.** The agent had no error recovery, no heartbeat monitoring, and no alerting. When it crashed, it crashed silently. The platform noticed the missing heartbeat and logged an event, but nobody was watching.

**The fix: the `agent.run()` consecutive error limit, plus alerting.**

The SDK's `agent.run()` method already handles this partially -- it tracks consecutive errors and stops after 5 in a row, raising the exception so your process manager can restart it. But you also need external monitoring.

```python
# Register a webhook for critical events
agent.register_webhook(
    url="https://your-server.com/arena-alerts",
    events=["circuit_breaker_triggered", "heartbeat_timeout"],
)
```

Wire that webhook to Slack, email, PagerDuty -- whatever your team uses. When the platform detects a heartbeat timeout (no agent heartbeat for 3x the poll interval), it fires the webhook. Someone gets paged. The agent gets restarted. The 36-hour silent failure becomes a 15-minute incident.

And if you're running a custom loop instead of `agent.run()`, add your own error tracking:

```python
consecutive_errors = 0
for cycle in range(1000):
    try:
        signals = agent.observe()
        update = decide(signals, config)
        if update:
            result = agent.act(update)
        consecutive_errors = 0  # Reset on success
    except Exception as e:
        consecutive_errors += 1
        logger.error(f"Cycle {cycle} failed: {e}")
        if consecutive_errors >= 5:
            raise  # Let the process manager handle it
    time.sleep(60)
```

## The Production Checklist

Before you deploy an agent to a real experiment, verify every item on this list. I'm serious. Print it out. Tape it to your monitor. Do not deploy until every box is checked.

1. **Confidence gating** -- agent never acts on `confidence == "low"` data
2. **Rejection handling** -- all four rejection types handled (`RATE_LIMITED`, `CIRCUIT_BREAKER_ACTIVE`, `EXPERIMENT_NOT_RUNNING`, `CONTROL_VARIANT_IMMUTABLE`)
3. **Cooldown logic** -- agent backs off after rejections, waits N cycles
4. **Drift detection** -- agent reduces change magnitude when metrics swing more than 20%
5. **Multi-objective constraints** -- agent monitors secondary metrics, not just the target
6. **Alerting** -- webhook registered for `circuit_breaker_triggered` and `heartbeat_timeout`
7. **Max iterations** -- agent eventually stops (no infinite loops)

Miss any one of these and you're building a production incident that just hasn't happened yet.

## Arena's Safety Net

Here's the good news. Even if your agent goes completely rogue, the platform has five guardrails that catch it:

1. **Control lock** -- the control variant is always immutable, ensuring you always have a clean baseline for comparison
2. **Status gate** -- changes are only accepted when the experiment is `RUNNING`, so a paused experiment can't be modified
3. **Circuit breaker** -- if retention drops dangerously, all agent updates are frozen automatically until a researcher manually resets it
4. **Rate limiter** -- agents can't update faster than `updateIntervalMin` (default 60 minutes), preventing rapid oscillation
5. **Delta clamping** -- changes larger than `deltaLimitPct` (default 50%) are automatically clamped, so your agent can't 10x a parameter in one step

These guardrails are sequential. Every `act()` call passes through all five, in order. Your agent's worst-case mistake is capped at a 50% change to any parameter, applied no more than once per hour, with an automatic emergency stop if things go south.

That's a pretty good safety net. But it's the net under the trapeze, not a substitute for knowing how to swing. The five breaks in this post are the ones that happen inside the guardrails -- where the platform lets your change through because it's technically within bounds, but the strategy behind it is flawed.

## The Takeaway

Production agents fail in predictable ways. The Oscillator, the Confidence Ignorer, the Rate Limit Fighter, Goodhart's Monster, and the Silent Crasher -- these aren't exotic edge cases. They're the five failure modes that every team hits on their first real deployment.

The fixes are not complicated. A cooldown counter. A confidence check. A matched poll interval. A secondary metric constraint. A webhook. Each one is a few lines of code. The hard part isn't writing them -- it's knowing they're necessary before you learn it the hard way at 3 AM.

Armed with these safety patterns, you're ready for the real challenge. In the next post, we'll reverse-engineer Duolingo's streak system and build an agent that replicates their approach.

---

*This is part 8 of the [TendedLoop Arena](https://github.com/osheryadgar/tendedloop-arena) blog series. Arena is an open-source platform for multi-agent gamification research. Star the repo if this was useful.*
