# Lesson 1: What is Multi-Agent Optimization?

## The Problem

Imagine you run a facility feedback app. Users scan QR codes, leave feedback, and earn XP points. But how much XP should a scan be worth? Should you reward streaks? How much?

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

## Next

In [Lesson 2](02-the-arena-environment.md), we'll explore the Arena environment in detail — what signals you receive, what parameters you control, and how the safety system works.
