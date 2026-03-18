# Build an Agent That Beats Your Classmates

> Part 10 of the [Arena Playbook](README.md) series

It's competition day. Four teams, four agents, one experiment. Your agent has been running for seven days. The scoreboard refreshes. You check your variant's scan frequency, retention rate, feedback quality. You're in second place. The team in first has a 0.3-point lead on the composite score. You have 48 hours left.

What do you do?

If you've followed this series, you have options. Rule-based agents (Post 2). PID control (Post 3). Multi-armed bandits and UCB1 (Post 4). Thompson Sampling (Post 6). LLM-powered agents (Post 7). Safety patterns to keep any of them from crashing (Post 8).

The question isn't which approach to use. The question is: which approach is right for *this moment* in *this experiment*? And the honest answer is that you don't know in advance. Nobody does.

So here's the strategy: use all of them. Let the data decide.

## The Ensemble: A Committee of Strategies

The idea behind an ensemble agent is simple. Instead of picking one strategy and hoping it's right, you run several strategies simultaneously. Each one proposes a parameter change. The ensemble picks which proposal to execute, observes the result, and gives more weight to strategies that produce good outcomes.

Over time, the winning strategy rises to the top. But if conditions change — say the user population shifts, or a competing agent adjusts their parameters — the ensemble can adapt by shifting weight to a different strategy.

The algorithm that makes this work is called Hedge (also known as Multiplicative Weights). Here's the entire idea in one paragraph:

Every strategy starts with equal weight. Each cycle, the ensemble randomly selects a strategy, with selection probability proportional to weight. It executes that strategy's proposed config change. Then it observes what happened to the composite score. If the score improved, the selected strategy's weight goes up. If it dropped, the weight goes down. The update rule is `weight *= exp(learning_rate * reward)`. That's it. Over dozens of cycles, strategies that consistently produce positive outcomes dominate the committee. Strategies that consistently fail get marginalized but never fully eliminated — because conditions might change.

## Three Sub-Strategies That Cover the Spectrum

A good ensemble needs diverse strategies. If all your sub-strategies are basically the same, you have a committee that always agrees — which is just a single strategy with extra overhead. You want strategies that *disagree* in interesting situations.

Here are three that work well together:

**Reactive** — the firefighter. It watches metric thresholds and reacts when something is clearly wrong. Scan frequency below 2.0? Boost scanXp by 20%. Retention tanking? Pump up the streak bonus. It's fast and targeted but can't handle subtle multi-metric tradeoffs.

```python
def reactive(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if freq and freq.value < 2.0:
        return {"scanXp": round(config["scanXp"] * 1.2)}
    elif freq and freq.value > 4.5:
        return {"scanXp": round(config["scanXp"] * 0.9)}
    return {}
```

**Conservative** — the accountant. It finds the weakest metric and nudges its lever up by 5%. Small moves, steady progress, hard to crash. It won't win any sprints, but it won't blow up on day one either.

```python
def conservative(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")
    factor = 0.95 if (freq and freq.value > 4.0) else 1.05
    return {
        "scanXp": round(config["scanXp"] * factor),
        "feedbackXp": round(config["feedbackXp"] * factor),
    }
```

**Bold** — the gambler. It identifies the weakest metric and throws a 30% boost at it. High risk, high reward. If it works, you jump ahead. If it doesn't, the ensemble will stop picking it.

```python
def bold(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")
    qual = signals.metrics.get("FEEDBACK_QUALITY")
    if freq and qual and freq.value < qual.value * 5:
        return {"scanXp": round(config["scanXp"] * 1.3)}
    else:
        return {"feedbackXp": round(config["feedbackXp"] * 1.3)}
```

These three disagree in exactly the right ways. When engagement is low, Reactive wants a targeted fix, Conservative wants a gentle nudge, and Bold wants a big swing. The ensemble tries all three over time and learns which philosophy works for your specific variant.

## The Strategy Behind the Strategy

Building the agent is half the battle. The other half is tournament meta-strategy — the decisions you make *about* your agent, not inside it.

**Start conservative.** The first 24-48 hours of an experiment are when the platform is collecting baseline data and your metrics have high uncertainty. This is not the time to make bold moves. The conservative sub-strategy should naturally dominate early because the ensemble won't have enough signal to justify risk.

**Let the ensemble learn.** The Hedge algorithm needs cycles to build up meaningful weight differences. If you keep tweaking your agent's code every few hours, you reset the learning. Resist the urge. Set the agent running, monitor the logs, and let the math work.

**Monitor the scoreboard — but don't panic.** Being in third place after two days means almost nothing. Metrics are noisy with small populations. A leading team might be overfitting to a random spike. Check the confidence intervals, not just the point estimates. If a metric says "low confidence," it's telling you that the number is essentially made up.

**If you're behind late in the game, shift bold.** With 24 hours left and a gap to close, you can increase the learning rate (eta) to make the ensemble adapt faster, or add a bias toward the bold sub-strategy. This is risky — but if you're already losing, risk is free.

**Always log your reasoning.** Your grade probably rewards explainability as much as raw performance. An agent that finishes second but has clean logs showing *why* it made each decision is more impressive than a first-place agent that's a black box.

## Practical Tips Before You Deploy

**Test against the sandbox first.** The Arena SDK has a local sandbox mode (`python -m tendedloop_agent demo`) that simulates metrics. Run your agent against it. Make sure it doesn't crash on missing metrics, unexpected confidence levels, or edge cases in the config ranges.

**Handle rejections.** The platform will reject config updates that violate parameter bounds (e.g., scanXp below 1 or above 50). Your agent needs to clamp values before submitting. A single unhandled rejection can stall your agent for a full cycle.

**Check the heartbeat.** If your agent process dies at 3 AM, you lose hours of optimization. Use the agent's built-in heartbeat monitoring, and consider running it on a server or cloud VM instead of your laptop.

**Don't change parameters every single cycle.** If the previous change hasn't had time to affect user behavior (it takes time for people to actually interact with the new config), you're just adding noise. The example agent polls every 90 seconds but only proposes changes when metrics actually warrant them.

## The Complete Agent

Here's a minimal but competition-ready ensemble agent. It's about 30 lines of actual logic, plus the sub-strategies above:

```python
import math, random, os
from tendedloop_agent import Agent, ConfigUpdate, Signals

STRATEGIES = [reactive, conservative, bold]
weights = [1.0, 1.0, 1.0]
eta = 0.3
last_score = None
last_pick = None

def composite(signals):
    s = 0.0
    freq = signals.metrics.get("SCAN_FREQUENCY")
    ret = signals.metrics.get("RETENTION_RATE")
    qual = signals.metrics.get("FEEDBACK_QUALITY")
    if freq and freq.confidence != "low": s += freq.value * 0.4
    if ret and ret.confidence != "low": s += ret.value * 10 * 0.35
    if qual and qual.confidence != "low": s += qual.value * 10 * 0.25
    return s

def decide(signals, config):
    global last_score, last_pick, weights
    score = composite(signals)

    # Update weights from last round
    if last_pick is not None and last_score is not None:
        delta = max(-1, min(1, score - last_score))
        weights[last_pick] *= math.exp(eta * delta)

    # Select strategy proportional to weights
    total = sum(weights)
    r = random.random() * total
    pick, cumul = 0, 0
    for i, w in enumerate(weights):
        cumul += w
        if r <= cumul:
            pick = i
            break

    proposal = STRATEGIES[pick](signals, config)
    changes = {k: v for k, v in proposal.items() if v != config.get(k)}
    last_score, last_pick = score, pick

    if not changes:
        return None
    return ConfigUpdate(
        economy_overrides=changes,
        reasoning=f"{STRATEGIES[pick].__name__} "
                  f"({weights[pick]/total*100:.0f}% weight): {changes}",
    )

TOKEN = os.environ["STRATEGY_TOKEN"]
with Agent(api_url="https://api.tendedloop.com", strategy_token=TOKEN) as agent:
    agent.run(decide, poll_interval=90, max_iterations=200)
```

That's your competition agent. Reactive handles emergencies, Conservative keeps things stable, Bold pushes for gains when there's room, and Hedge figures out which one to trust. The reasoning string in each ConfigUpdate means your logs tell a story.

## What You've Built

Take a step back and look at what you know now.

You started this series not knowing what a multi-armed bandit was. You've now built an ensemble agent that balances exploration and exploitation (Posts 4-6), uses control theory to avoid oscillation (Post 3), respects production safety constraints (Post 8), and is informed by the behavioral economics that power every real gamification system on the planet (Post 9).

The agent you just wrote isn't a toy. It's the same architecture that production recommendation systems, ad bidding platforms, and automated trading systems use: multiple strategies, weighted voting, online learning. The difference is that you built it in 30 lines of Python and can explain every piece of it.

That's not a class exercise. That's production AI.

## Go Deeper

This series gave you the essentials. If you want to keep going:

- The [Workshop](../workshop/README.md) has 15 hands-on lessons with exercises, covering everything from basic agents to hierarchical ensembles and production safety patterns.
- The [Strategic AI Course](../academic/strategic-ai.md) is a 14-week university course that goes deep on multi-agent systems, mechanism design, and game-theoretic foundations.
- The [Behavioral AI Course](../academic/behavioral-ai.md) covers 14 weeks of incentive design — prospect theory, temporal discounting, and the ethics of computational nudging.
- The [Examples](../examples/) directory has 13 complete agent implementations you can read, run, and remix.

Good luck in the tournament. Trust the ensemble. Log everything. And remember — the team that understands *why* their agent works will always beat the team that just got lucky.

---

*This is post 10 of the [Arena Playbook](README.md), a 10-part series on multi-agent AI for CS undergrads.*
