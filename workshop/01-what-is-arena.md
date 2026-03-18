# Lesson 1: What is Multi-Agent Optimization?

> **Time:** ~25 minutes | **Complexity:** Beginner
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Describe the limitations of traditional manual gamification tuning
> 2. Explain the observe-decide-act-learn agent loop and its four stages
> 3. List the key advantages of multi-agent optimization over static A/B testing

## The Problem

Imagine you run a platform where users perform actions and earn rewards. But how many points should each action be worth? Should you reward streaks? How much?

Get it wrong and users disengage. Get it right and engagement soars. The problem: you don't know the right answer in advance, and it changes over time.

## The Traditional Approach

Traditionally, product managers make these decisions based on intuition, A/B tests, or competitive analysis. They set the values, ship them, and wait weeks to measure impact.

This approach has fundamental limitations:
- **Slow iteration** — weeks per change
- **Human bias** — anchoring to initial guesses
- **One-size-fits-all** — same config for all user segments
- **No adaptation** — values stay static as user behavior evolves

## The Arena Approach

Arena turns this into an **autonomous optimization problem**. Instead of a human deciding "scanXp should be 10," you write an **agent** that:

1. **Observes** real-time engagement metrics (scan frequency, retention, feedback quality)
2. **Decides** whether to adjust the economy based on what it sees
3. **Acts** by submitting new parameter values to the platform
4. **Learns** from the outcome and improves over time

Multiple agents can compete simultaneously, each controlling a different experiment variant. The platform measures which strategy produces the best outcomes with statistical rigor.

## Why Multi-Agent?

The "multi" in multi-agent is key. In a typical Arena experiment:

```
Variant A: Your Python rule-based agent
Variant B: Your colleague's LLM-powered agent
Variant C: A Bayesian optimization agent
Control:   No agent (default parameters, never changes)
```

Each agent independently optimizes its variant. The platform randomly assigns users to variants and measures outcomes. After the experiment, statistical tests reveal which approach worked best.

This is more powerful than traditional A/B testing because:
- Agents **adapt in real-time** (not static configs)
- You test **strategies**, not just parameter values
- Safety **guardrails** prevent any agent from harming users
- Complete **audit trails** explain every decision

## The Agent Loop

Every Arena agent follows the same fundamental cycle:

```
         ┌──────────┐
    ┌───>│ Observe  │───┐
    │    └──────────┘   │
    │                   v
┌───┴───┐         ┌─────────┐
│ Sleep │         │ Decide  │
└───┬───┘         └────┬────┘
    │                  │
    │    ┌──────────┐  │
    └────│   Act    │<─┘
         └──────────┘
```

- **Observe**: Read engagement signals (6 metrics with statistical confidence)
- **Decide**: Your strategy logic — should we change anything?
- **Act**: Submit new economy parameters (subject to safety guardrails)
- **Sleep**: Wait for the changes to take effect before measuring again

## What You'll Build in This Course

By the end of this course, you'll have built agents using:

| Approach | Key Idea |
|----------|----------|
| Rule-based | React to thresholds |
| PID control | Maintain a target value |
| UCB1 | Optimism under uncertainty |
| Thompson Sampling | Bayesian exploration |
| Contextual bandits | Context-dependent decisions |
| Bayesian optimization | Sample-efficient search |
| LLM reasoning | Natural language decision-making |
| Ensemble | Combine strategies adaptively |

You'll understand when to use each one and how to deploy them safely in production.

## Key Vocabulary

| Term | Meaning |
|------|---------|
| **Agent** | Autonomous program that optimizes a variant's economy |
| **Variant** | One arm of an experiment with its own config and user group |
| **Economy** | The XP reward structure (scanXp, streakBonus, etc.) |
| **Signals** | Real-time engagement metrics provided by the platform |
| **Guardrails** | Safety checks that prevent harmful changes |
| **Experiment** | A controlled trial comparing multiple variants |

## Your First API Call

Even before building an agent, you can observe what's happening:

```python
from tendedloop_agent import Agent
import os

with Agent(
    api_url=os.environ.get("ARENA_URL", "https://api.tendedloop.com"),
    strategy_token=os.environ["STRATEGY_TOKEN"],
) as agent:
    signals = agent.observe()
    print(f"Enrolled: {signals.enrolled}")
    print(f"Active today: {signals.active_today}")
    for name, metric in signals.metrics.items():
        print(f"  {name}: {metric.value:.2f} (confidence: {metric.confidence})")
```

This is the **observe** step. In [Lesson 3](03-your-first-agent.md), you'll add **decide** and **act**.

## Exercises

1. **Run the observe call** above. How many metrics do you see? What are their confidence levels?
2. **Check the scoreboard**: Add `print(agent.scoreboard())` to see all variants in your experiment. How many are there?
3. **Think about strategy**: Looking at the metrics and the economy parameters (Lesson 2 preview), which parameter would you adjust first to improve your primary metric? Write down your hypothesis before reading Lesson 3.

## Next

In [Lesson 2](02-the-arena-environment.md), we'll explore the Arena environment in detail — what signals you receive, what parameters you control, and how the safety system works.
