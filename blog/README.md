# Arena Playbook

A 10-part blog series on multi-agent AI — from zero to competing agent — for undergraduate CS students.

> Built on [TendedLoop Arena](https://github.com/osheryadgar/tendedloop-arena), the open-source SDK for multi-agent gamification research.

## The Series

| # | Post | What You'll Learn |
|---|------|-------------------|
| 1 | [Your Building Has a Problem Nobody's Telling You About](01-the-problem-nobody-tells-you.md) | Why AI agents beat humans at incentive optimization |
| 2 | [I Wrote My First AI Agent in 15 Lines of Python](02-first-agent-in-15-lines.md) | The observe-decide-act loop, your first running agent |
| 3 | [Why Your Agent Oscillates](03-why-your-agent-oscillates.md) | PID control — a 100-year-old fix for a modern problem |
| 4 | [The Explore-Exploit Dilemma](04-explore-exploit-dilemma.md) | Multi-armed bandits, Netflix, Tinder, and regret |
| 5 | [How Poker AI Beat 6 Pros](05-how-poker-ai-beat-6-pros.md) | Game theory, Nash equilibrium, and competitive agents |
| 6 | [Thompson Sampling: Learning by Guessing](06-thompson-sampling-learns-by-guessing.md) | Bayesian bandits — the 90-year-old algorithm that works |
| 7 | [What Happens When You Let GPT-4 Run Your Experiment](07-let-gpt-run-your-experiment.md) | LLM-powered agents — strengths, risks, and hybrids |
| 8 | [The 5 Ways Your Agent Can Break Production](08-five-ways-to-break-production.md) | Safety patterns every agent developer needs |
| 9 | [Why Duolingo's Streak System Works](09-duolingo-mathematical-autopsy.md) | Behavioral economics, loss aversion, and XP design |
| 10 | [Build an Agent That Beats Your Classmates](10-build-an-agent-that-wins.md) | Ensemble methods, tournament strategy, the final agent |

## How to Read

Each post is **self-contained** — read any one and get value. But they build on each other:

- **Posts 1-3**: Foundations (what Arena is, first agent, PID control)
- **Posts 4-6**: Algorithms (bandits, game theory, Bayesian methods)
- **Posts 7-8**: Production (LLM agents, safety)
- **Posts 9-10**: Mastery (behavioral science, competition)

## Try It Yourself

Every post includes runnable code. Start here:

```bash
pip install tendedloop-arena
python -m tendedloop_agent demo  # Local sandbox — no account needed
```

## Go Deeper

- [Workshop](../workshop/README.md) — 15 hands-on lessons with exercises
- [Strategic AI Course](../academic/strategic-ai.md) — 14-week university course on multi-agent systems
- [Behavioral AI Course](../academic/behavioral-ai.md) — 14-week course on incentive design
- [Examples](../examples/) — 13 complete agent implementations
