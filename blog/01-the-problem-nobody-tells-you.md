# Your Building Has a Problem Nobody's Telling You About

Let me tell you about a problem that costs companies millions of dollars a year, and almost nobody talks about it.

Picture this. You're a facility manager at a company with 2,000 employees across three buildings. You've got a cleaning crew, a maintenance team, and a budget that's somehow supposed to cover everything. On Monday morning you walk into the third-floor restroom and the soap dispenser has been empty since Friday. Nobody told you. Nobody filed a ticket. People just... stopped using that restroom.

This is the silent failure mode of every large facility. Research suggests that only about 20% of issues actually get reported. The other 80%? People work around them. They use a different restroom, a different kitchen, a different meeting room. The problems pile up invisibly until someone important notices, and by then the damage is done.

## The Feedback Gap

The traditional solution is suggestion boxes, annual surveys, or those little smiley-face kiosks near the elevator. But let's be honest: when was the last time you stopped to press a smiley face? These tools collect fragments, not signal.

Modern platforms like TendedLoop take a different approach. Stick a QR code on the soap dispenser. Someone scans it with their phone. Ten seconds later you know the soap is out. No app to install, no login, no friction. The scan goes straight to your dashboard.

But here's the twist. Getting people to scan that QR code is itself an engagement problem. You need to give them a reason. That's where gamification comes in: XP points for scanning, streak bonuses for scanning multiple days in a row, badges for thoroughness. And that raises a deceptively hard question:

**How much should a scan be worth?**

## Gamification Is an Optimization Problem

If you're a CS student, you might hear "gamification" and think of marketing fluff. Let me reframe it.

You have a reward function with ten tunable parameters: XP per scan, XP per feedback, streak bonus per day, daily caps, and more. You have six measurable outcomes: scan frequency, retention rate, feedback quality, XP velocity, mission completion, and streak length. Your job is to find the parameter configuration that maximizes engagement without overspending on rewards.

That's not a business problem. That's a constrained optimization problem. And it's a fascinating one because the "environment" is made of actual humans whose behavior changes in response to your parameters.

Set scan XP too low and nobody bothers scanning. Set it too high and people spam meaningless scans for points. Set the streak bonus just right and you create a habit loop that keeps people engaged for weeks. But "just right" is different for every building, every team, every season.

## Enter the Agents

What if you didn't have to guess? What if you wrote a piece of software that watched the engagement metrics in real-time, decided when to adjust the rewards, and then applied those changes automatically?

That's an **agent**. And that's what TendedLoop Arena is about.

Arena is a platform where autonomous agents compete to optimize gamification economies. You write a Python program. It connects to the platform. It gets real-time data about how users are engaging. It decides whether to change the reward structure. The platform applies those changes (with safety guardrails) and measures the results.

The core loop looks like this:

```
         +------------+
    +--->|  Observe   |---+
    |    +------------+   |
    |                     v
+---+---+          +-----------+
| Sleep |          |  Decide   |
+---+---+          +-----+-----+
    |                    |
    |    +------------+  |
    +----+    Act     |<-+
         +------------+
```

Let me make this concrete with a restaurant analogy. Think about a good waiter.

**Observe:** The waiter walks past your table and notices your water glass is empty and your plates are clean. That's signal.

**Decide:** Based on what they see, they decide you're probably ready for the check, but maybe they should offer dessert first. That's strategy.

**Act:** They come over, clear the plates, and ask if you'd like to see the dessert menu. That's the intervention.

**Sleep:** They give you five minutes to decide before coming back. That's the cooldown.

A bad waiter checks on you every 30 seconds (annoying) or never (neglectful). A good waiter observes the right signals, makes smart decisions, and acts at the right time. Your agent needs to do the same thing with engagement metrics instead of dinner plates.

## Why Multi-Agent?

Here's where it gets really interesting. Arena doesn't just run one agent. It runs several, simultaneously, on different user groups.

A typical experiment looks like this:

```
Variant A:  Your rule-based Python agent
Variant B:  Your friend's LLM-powered agent
Variant C:  A PID controller agent
Control:    No agent at all (default parameters, never changes)
```

Users are randomly assigned to variants. Each agent independently optimizes its group's reward structure. After a few weeks, statistical tests reveal which strategy actually worked best.

This is more powerful than traditional A/B testing for a crucial reason: you're not testing static configurations. You're testing **strategies**. Agent A might start aggressive and dial back. Agent B might be conservative for a week, then make one big move. Agent C might continuously adjust. The question isn't "is scanXp=12 better than scanXp=10?" It's "is the strategy of gradual escalation better than the strategy of patient observation?"

Four teams. Four strategies. One experiment. The best approach wins.

## The Safety Net

If you're thinking "wait, you're letting student code modify a production system?", that's a fair concern. Arena has five layers of guardrails that run on every action:

1. **Control Lock** -- the control variant can never be modified
2. **Status Gate** -- only running experiments accept changes
3. **Circuit Breaker** -- if engagement drops sharply, all changes are frozen
4. **Rate Limiter** -- you can only submit changes every N minutes
5. **Delta Clamp** -- changes larger than 50% get automatically clamped down

That last one is key. If your agent tries to set `scanXp` from 10 to 100, the platform won't reject it. It'll apply `scanXp = 15` (a 50% increase) and tell your agent exactly what happened. Your code gets feedback about what was actually applied versus what was requested.

You can't break things. You can only compete to make things better.

## What the Platform Measures

So your agent makes changes. How do you know if they worked? The platform continuously computes six engagement metrics for each variant:

| Metric | What it tells you |
|--------|------------------|
| **Scan Frequency** | How often users scan QR codes per day |
| **Retention Rate** | What percentage of users come back within 7 days |
| **Feedback Quality** | How many scans include actual written feedback |
| **XP Velocity** | How fast users accumulate points |
| **Mission Completion** | What fraction of assigned missions get done |
| **Streak Length** | How many consecutive days users stay active |

Each metric comes with a confidence level (low, medium, high) based on sample size. A smart agent checks confidence before acting. If you only have data from 5 users, any trend you see is probably noise. Wait for 30 users and the signal gets real.

This is one of the things that makes Arena interesting from a CS perspective: you're optimizing against noisy, delayed, human-generated feedback. It's not a clean loss function. It's not a simulation. It's messy, real-world signal that changes as humans learn and adapt to your changes.

## What You'll Need

The technical requirements are minimal:

- Python 3.10+
- `pip install tendedloop-arena`
- A strategy token (or just use the local sandbox -- no account needed)

The SDK handles HTTP connections, heartbeats, error recovery, and retry logic. You write one function: `decide(signals, config) -> ConfigUpdate | None`. The SDK calls it in a loop.

## Try It Right Now

Here's how you can see the agent loop in action locally, with no account and no setup beyond pip:

```bash
# Terminal 1: Start the sandbox (simulates the full Arena API)
pip install tendedloop-arena
python -m tendedloop_agent demo

# Terminal 2: Run a demo agent against it
python examples/00_demo_sandbox.py
```

The sandbox simulates realistic metrics, applies all five guardrails, and tracks your agent's economy changes statefully. You'll see your agent observe, decide, and act in real-time.

## What's Next

This is the first post in a three-part series. Here's the roadmap:

1. **This post** -- the problem, the approach, and the architecture
2. **Next post** -- you'll write your first agent in 15 lines of Python, and I'll walk through every line
3. **Post after that** -- your rule-based agent will oscillate (they all do), and I'll show you how a formula from 1922 fixes it

In the next post, you'll write your first agent in 15 lines of Python. No ML experience needed. No GPU. Just a function that reads numbers and returns a decision.

See you there.

---

*This is part 1 of the [TendedLoop Arena](https://github.com/osheryadgar/tendedloop-arena) blog series. Arena is an open-source platform for multi-agent gamification research. Star the repo if this was useful.*
