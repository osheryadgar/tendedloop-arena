# I Wrote My First AI Agent in 15 Lines of Python

I was skeptical. An AI agent in 15 lines? That sounds like the kind of claim you see on a YouTube thumbnail right before someone spends 45 minutes installing dependencies.

But it's real. No ML experience needed. No GPU. No TensorFlow. Just `pip install` and 15 lines of Python that connect to a live system, read real-time metrics, make autonomous decisions, and modify a production gamification economy.

Let me show you.

## The Setup (2 Minutes)

You need two terminal windows. That's it.

**Terminal 1** starts the sandbox -- a local server that simulates the full TendedLoop Arena API with realistic metrics, all five safety guardrails, and stateful economy tracking:

```bash
pip install tendedloop-arena
python -m tendedloop_agent demo
```

You'll see something like:

```
Arena Sandbox running on http://localhost:7860
Experiment: Demo Experiment (RUNNING)
Variants: Control, Treatment-A
Waiting for agent connections...
```

**Terminal 2** is where your agent runs. Create a file called `my_agent.py` and let's build it together.

## The 15 Lines

Here's the complete agent. Read it once, then I'll break it down:

```python
from tendedloop_agent import Agent, ConfigUpdate, Signals

def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if not freq or freq.confidence == "low":
        return None                          # not enough data yet
    if freq.value < 2.0:
        new_xp = round(current_config["scanXp"] * 1.15)
        return ConfigUpdate(
            economy_overrides={"scanXp": new_xp},
            reasoning=f"Scan freq low ({freq.value:.1f}), boost to {new_xp}",
        )
    return None                              # metrics look healthy

with Agent(api_url="http://localhost:7860", strategy_token="strat_demo_local") as agent:
    agent.run(decide, poll_interval=65, max_iterations=10)
```

That's it. Save it, run it:

```bash
python my_agent.py
```

## Line by Line

Let's walk through every decision in this code.

**Line 1: The import.**

```python
from tendedloop_agent import Agent, ConfigUpdate, Signals
```

Three things: `Agent` manages the connection and the loop. `ConfigUpdate` is what you return when you want to change something. `Signals` is what the platform gives you -- engagement metrics with statistical confidence levels.

**Lines 3-13: The decision function.**

```python
def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
```

This is the only function you write. The SDK calls it automatically on every loop iteration. It receives two arguments: the current engagement signals and the current economy configuration. It returns either a `ConfigUpdate` (make a change) or `None` (do nothing).

The return type `ConfigUpdate | None` is the entire API surface of your agent's brain. That's a beautiful constraint. You don't manage HTTP connections, heartbeats, retries, or error handling. You just answer one question: *should I change anything right now?*

**Lines 4-6: The confidence gate.**

```python
freq = signals.metrics.get("SCAN_FREQUENCY")
if not freq or freq.confidence == "low":
    return None
```

This is the most important pattern in agent design. Every metric comes with a confidence level: `low`, `medium`, or `high`, based on sample size. If you act on low-confidence data, you're reacting to noise, not signal.

Think of it this way. If I tell you "your restaurant got a 2-star review," that means nothing -- it's one person. If I tell you "your restaurant has a 2-star average across 500 reviews," that's a crisis. Same number. Wildly different confidence.

**Lines 7-12: The action.**

```python
if freq.value < 2.0:
    new_xp = round(current_config["scanXp"] * 1.15)
    return ConfigUpdate(
        economy_overrides={"scanXp": new_xp},
        reasoning=f"Scan freq low ({freq.value:.1f}), boost to {new_xp}",
    )
```

If scan frequency is below 2.0 scans per user per day, bump the XP reward by 15%. The `reasoning` string is stored permanently in an audit log. Weeks later, you can go back and see exactly why your agent made every decision.

Why 15% and not 50%? Two reasons. First, small changes are easier to measure. If you change five parameters by 50% each and engagement goes up, you have no idea which change helped. Second, the platform's delta clamp guardrail will cap changes at 50% anyway. Working within that constraint voluntarily means your requested changes actually get applied as-is.

**Line 13: The intentional no-op.**

```python
return None  # metrics look healthy
```

This line is easy to skip over but it encodes a critical insight: **a good agent does nothing most of the time**. If scan frequency is at 3.0 and everything looks fine, the correct action is no action. Resist the urge to optimize what's already working.

**Lines 15-16: The loop.**

```python
with Agent(api_url="http://localhost:7860", strategy_token="strat_demo_local") as agent:
    agent.run(decide, poll_interval=65, max_iterations=10)
```

`Agent` is a context manager -- it opens and closes the HTTP connection cleanly. `agent.run()` starts the automated loop: observe, call your `decide()`, act if needed, sleep, repeat. The `poll_interval=65` means it checks every 65 seconds. The sandbox's rate limiter allows changes every 60 seconds, so 65 gives a comfortable margin.

## What You'll See

Run it and watch:

```
TendedLoop Arena — Agent Running
=================================
  Variant:     Treatment-A
  Experiment:  Demo Experiment (RUNNING)
  Constraints: update every 1min, delta limit 50%

2026-03-18 10:00:00   [skip] Low confidence (n=4), waiting for more data...
2026-03-18 10:01:05   [skip] Low confidence (n=8), waiting for more data...
2026-03-18 10:02:10   Scan freq low (1.8), boost to 12
                      Config accepted: scanXp 10 -> 12
2026-03-18 10:03:15   [hold] All metrics within acceptable range
2026-03-18 10:04:20   [hold] All metrics within acceptable range
2026-03-18 10:05:25   Scan freq low (1.9), boost to 14
                      Config accepted: scanXp 12 -> 14
2026-03-18 10:06:30   [hold] All metrics within acceptable range
...
```

Notice three things:

1. **The first two cycles do nothing.** The sample size is too small. This is correct behavior. Hasty agents waste their limited update slots on noise.

2. **Most cycles do nothing.** The agent observes that metrics are fine and returns `None`. No unnecessary changes.

3. **When it acts, it explains why.** Every change includes a reasoning string that goes into the permanent audit log.

## The Three Rules

From this minimal example, three rules of good agent design emerge:

**Rule 1: Check confidence before acting.** You have a limited number of update slots (rate-limited by the platform). Don't waste them on data you can't trust. When sample sizes are small, the right move is patience.

**Rule 2: Change one thing at a time.** Our agent only touches `scanXp`. It doesn't simultaneously adjust `streakBonusPerDay`, `feedbackXp`, and `scanDailyCap`. Why? Because if you change four things at once and engagement improves, you learn nothing about which change helped.

**Rule 3: Always explain why.** The `reasoning` parameter isn't optional decoration. It's the audit trail that lets you (and your teammates, and your professor) understand your agent's behavior after the fact. "Boost scanXp because I felt like it" is not a good reason. "Scan frequency at 1.8/day, below 2.0 threshold, boosting 15%" is.

## What Happens When Metrics Are Healthy

Here's a subtle test of agent quality: what does it do when everything is fine?

Our agent returns `None`. It does nothing. And that's the right answer.

This is harder than it sounds. There's a strong temptation to always be doing *something*. To tweak, optimize, explore. But in a system with real users, unnecessary changes introduce variance. If scan frequency is at 3.0 and users are happy, the best move is to leave them alone.

The technical term for this is "stability." A stable agent converges to a configuration and stays there until something actually changes. An unstable agent fidgets constantly and never lets the metrics settle long enough to measure.

## But What If It Oscillates?

Run the agent long enough and you'll notice a problem. When scan frequency drops below 2.0, the agent boosts XP. Frequency goes up. The agent stops boosting. Frequency drifts back down. The agent boosts again.

```
scanXp: 10 → 12 → 12 → 14 → 14 → 14 → 12 → 14 → 12 → 14
         ↑              ↑                   ↑         ↑
       boost          boost              reduce?    boost
```

This sawtooth pattern is annoying. It wastes update slots. It confuses users who see their XP rewards changing constantly. And it happens with every rule-based agent.

The fix is surprisingly elegant, and it comes from a 100-year-old formula originally designed for steering ships. That's the next post.

## Try It Yourself

Everything above runs locally with no account:

```bash
pip install tendedloop-arena
python -m tendedloop_agent demo
```

Then create `my_agent.py` with the 15-line code above and run it in a second terminal.

Challenges to try:

1. **Add a second metric.** Monitor `RETENTION_RATE` and boost `streakBonusPerDay` when retention drops below 60%.
2. **Add a ceiling.** Don't let `scanXp` go above 20, no matter what. What happens to the agent's behavior?
3. **Add a cooldown.** After making a change, skip the next 3 cycles to let the effect settle. (Hint: you'll need to turn `decide` into a method on a class so you can track state.)

When you're ready to run against a real experiment instead of the sandbox, just change the URL and token:

```python
with Agent(api_url="https://api.tendedloop.com", strategy_token="strat_YOUR_TOKEN") as agent:
    agent.run(decide, poll_interval=60, max_iterations=50)
```

Everything else stays the same. Same `decide()` function, same loop, same 15 lines.

---

*This is part 2 of the [TendedLoop Arena](https://github.com/osheryadgar/tendedloop-arena) blog series. [Part 1](/blog/01-the-problem-nobody-tells-you.md) covered the problem and architecture. Next up: why your agent oscillates and how PID control fixes it.*
