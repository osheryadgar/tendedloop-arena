# Multi-Agent Gamification Research — Workshop

A hands-on workshop for building autonomous agents that optimize gamification economies using the TendedLoop Arena SDK.

This workshop is the **practical implementation lab** for two theoretical courses:
- [Course A: Multi-Agent Systems](../academic/course-a-multi-agent-systems.md) — agent theory, game theory, bandits, RL
- [Course B: Computational Gamification](../academic/course-b-gamification-design.md) — reward modeling, behavioral economics, engagement optimization

You can also take this workshop **standalone** — it's self-contained with all the theory you need.

> **Total time:** ~7.5 hours of instruction (plus additional time for exercises and experimentation). Each lesson includes learning objectives, a time estimate, and a complexity rating (Beginner / Intermediate / Advanced).

## Who Is This For?

This workshop is for **agent developers** — the people who write the code. You might be a student in a class, a researcher in a lab, or a solo developer running your own experiments.

If you're an **experiment manager** (instructor, research lead) setting up experiments for others, start with the [Classroom & Lab Guide](../docs/classroom-guide.md) instead.

> **Wearing both hats?** Read [Lesson 0: Roles and Setup](00-roles-and-setup.md) first — it explains the two personas and how they interact.

## Prerequisites

- Python 3.10+
- A **strategy token** (from your experiment manager, or self-provisioned via the [Dashboard](https://app.tendedloop.com))
- Basic familiarity with APIs and data structures
- No ML/RL experience required (we build up from zero)

## Setup

```bash
pip install tendedloop-arena
export STRATEGY_TOKEN=strat_your_token_here  # From your experiment manager
```

For examples that use numpy or anthropic:
```bash
pip install "tendedloop-arena[all]"
```

### No Token? Use the Local Sandbox

You can try every example without a TendedLoop account using the built-in sandbox server:

```bash
# Terminal 1: Start the sandbox (simulates the full Arena API locally)
python -m tendedloop_agent demo

# Terminal 2: Run any example against it
export ARENA_URL=http://localhost:7860
export STRATEGY_TOKEN=strat_demo_local
python examples/00_demo_sandbox.py
```

The sandbox simulates all 5 guardrails, stateful economy tracking, and metrics that respond to config changes. Great for learning before connecting to a real experiment.

## Workshop Sessions (8 sessions)

Each session maps to specific topics from the theoretical courses. The "Course A/B" column shows which lectures provide the theoretical foundation.

### Session 1: Setup and Orientation

| Lesson | Title | Course A | Course B |
|--------|-------|---------|---------|
| [00](00-roles-and-setup.md) | Roles and Setup | — | — |
| [01](01-what-is-arena.md) | What is Multi-Agent Optimization? | Week 1: Agents | Week 1: Gamification as optimization |
| [02](02-the-arena-environment.md) | The Arena Environment | Week 1: Environments | Week 5: Parameterized rewards |

**Goal**: Everyone connected, tokens working, understand the system.

### Session 2: Your First Agent

| Lesson | Title | Example | Course A | Course B |
|--------|-------|---------|---------|---------|
| [03](03-your-first-agent.md) | Your First Agent | `01_quickstart.py` | Week 2: Decision theory | Week 5: Core mechanics |

**Goal**: Write and run a rule-based agent. Understand the observe-decide-act loop.

### Session 3: Control Theory for Engagement

| Lesson | Title | Example | Course A | Course B |
|--------|-------|---------|---------|---------|
| [04](04-feedback-loops.md) | PID Control | `06_pid_controller.py` | Week 2: Rational agents | Week 3: Flow & DDA |
| [05](05-multi-objective.md) | Multi-Objective Optimization | `03_multi_metric.py` | Week 4: Mechanism design | Week 9: Engagement metrics |

**Goal**: Maintain a target metric with PID. Balance competing objectives.

### Session 4: The Bandit Problem

| Lesson | Title | Example | Course A | Course B |
|--------|-------|---------|---------|---------|
| [06](06-explore-exploit.md) | Explore-Exploit Dilemma | `11_explore_then_exploit.py` | Week 5: Bandits intro | Week 6: Reward schedules |
| [07](07-ucb1.md) | UCB1 | `07_ucb1.py` | Week 5: UCB analysis | Week 10: A/B testing |

**Goal**: Understand the explore-exploit tradeoff. Implement UCB1.

### Session 5: Bayesian and Contextual Approaches

| Lesson | Title | Example | Course A | Course B |
|--------|-------|---------|---------|---------|
| [08](08-thompson-sampling.md) | Thompson Sampling | `05_thompson_sampling.py` | Week 6: Bayesian bandits | Week 6: Variable schedules |
| [09](09-contextual-bandits.md) | Contextual Bandits | `08_contextual_bandit.py` | Week 7: LinUCB | Week 12: Personalization |

**Goal**: Bayesian reasoning about uncertainty. Context-dependent decisions.

### Session 6: Advanced Optimization

| Lesson | Title | Example | Course A | Course B |
|--------|-------|---------|---------|---------|
| [10](10-bayesian-optimization.md) | Bayesian Optimization | `09_bayesian_optimization.py` | Week 10: GP & BO | Week 7: XP economics |
| [11](11-reinforcement-learning.md) | Reinforcement Learning | `02_gymnasium_rl.py` | Week 8-9: RL & MARL | Week 6: Reward shaping |

**Goal**: Sample-efficient continuous optimization. RL with real behavioral data.

### Session 7: AI Agents and Ensembles

| Lesson | Title | Example | Course A | Course B |
|--------|-------|---------|---------|---------|
| [12](12-llm-agents.md) | LLM Agents | `04_llm_agent.py` | Week 12: LLM agents | Week 12: Adaptive systems |
| [13](13-ensemble-methods.md) | Ensemble Methods | `10_ensemble.py` | Week 11: Hedge algorithm | Week 8: Social dynamics |

**Goal**: LLM-powered reasoning. Combine strategies with Hedge.

### Session 8: Safety, Competition, and Results

| Lesson | Title | Example | Course A | Course B |
|--------|-------|---------|---------|---------|
| [14](14-production-safety.md) | Going to Production | `12_production_safety.py` | Week 13: Safety & alignment | Week 11: Ethics & dark patterns |

**Goal**: Deploy safely. Present results. Compare agent performance across teams.

## All Lessons (Reference)

<details>
<summary>Click to expand full lesson list</summary>

| # | Title | Example |
|---|-------|---------|
| 00 | [Roles and Setup](00-roles-and-setup.md) | — |
| 01 | [What is Multi-Agent Optimization?](01-what-is-arena.md) | — |
| 02 | [The Arena Environment](02-the-arena-environment.md) | — |
| 03 | [Your First Agent](03-your-first-agent.md) | `01_quickstart.py` |
| 04 | [Feedback Loops and PID Control](04-feedback-loops.md) | `06_pid_controller.py` |
| 05 | [Multi-Objective Optimization](05-multi-objective.md) | `03_multi_metric.py` |
| 06 | [The Explore-Exploit Dilemma](06-explore-exploit.md) | `11_explore_then_exploit.py` |
| 07 | [UCB1 — Optimism Under Uncertainty](07-ucb1.md) | `07_ucb1.py` |
| 08 | [Thompson Sampling — Bayesian Bandits](08-thompson-sampling.md) | `05_thompson_sampling.py` |
| 09 | [Contextual Bandits — Using Context](09-contextual-bandits.md) | `08_contextual_bandit.py` |
| 10 | [Bayesian Optimization](10-bayesian-optimization.md) | `09_bayesian_optimization.py` |
| 11 | [Reinforcement Learning](11-reinforcement-learning.md) | `02_gymnasium_rl.py` |
| 12 | [LLM Agents](12-llm-agents.md) | `04_llm_agent.py` |
| 13 | [Ensemble Methods](13-ensemble-methods.md) | `10_ensemble.py` |
| 14 | [Going to Production](14-production-safety.md) | `12_production_safety.py` |

</details>

## How to Use This Workshop

**If you're a student with a token**: Start at [Session 1](00-roles-and-setup.md) to verify your setup, then follow the session schedule.

**If you're a solo researcher**: Read [Lesson 0](00-roles-and-setup.md) to understand both roles, set up your experiment in the Dashboard, then work through the sessions.

**If you're an instructor**: See the [Classroom & Lab Guide](../docs/classroom-guide.md) for experiment setup, token distribution, and grading. The [Academic Program](../academic/README.md) has full syllabi for the theoretical courses.

**Each session**: Read the lessons, run the examples, do the exercises. In a classroom setting, each session is a 2-3 hour lab with instructor support.
