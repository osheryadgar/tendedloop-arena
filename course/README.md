# Multi-Agent Gamification Research — Course

A hands-on course for building autonomous agents that optimize gamification economies using the TendedLoop Arena SDK.

## Who Is This For?

This course is for **agent developers** — the people who write the code. You might be a student in a class, a researcher in a lab, or a solo developer running your own experiments.

If you're an **experiment manager** (instructor, research lead) setting up experiments for others, start with the [Classroom & Lab Guide](../docs/classroom-guide.md) instead.

> **Wearing both hats?** Read [Lesson 0: Roles and Setup](00-roles-and-setup.md) first — it explains the two personas and how they interact.

## Prerequisites

- Python 3.10+
- A **strategy token** (from your experiment manager, or self-provisioned via the [Dashboard](https://app.tendedloop.com))
- Basic familiarity with APIs and data structures
- No ML/RL experience required (we build up from zero)

## Setup

```bash
pip install git+https://github.com/osheryadgar/tendedloop-arena.git
export STRATEGY_TOKEN=strat_your_token_here  # From your experiment manager
```

For examples that use numpy or anthropic:
```bash
pip install "tendedloop-agent[all] @ git+https://github.com/osheryadgar/tendedloop-arena.git"
```

## Curriculum

### Lesson 0: Getting Started

| Lesson | Title | What You Learn |
|--------|-------|---------------|
| [00](00-roles-and-setup.md) | Roles and Setup | The two personas (manager vs. developer), connection verification |

### Module 1: Foundations

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [01](01-what-is-arena.md) | What is Multi-Agent Optimization? | — | The problem, why it matters, how Arena works |
| [02](02-the-arena-environment.md) | The Arena Environment | — | Tokens, signals, parameters, guardrails, lifecycle |
| [03](03-your-first-agent.md) | Your First Agent | `01_quickstart.py` | The observe-decide-act loop |

### Module 2: Classical Control

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [04](04-feedback-loops.md) | Feedback Loops and PID Control | `06_pid_controller.py` | Control theory applied to gamification |
| [05](05-multi-objective.md) | Multi-Objective Optimization | `03_multi_metric.py` | Balancing competing metrics |

### Module 3: Bandit Algorithms

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [06](06-explore-exploit.md) | The Explore-Exploit Dilemma | `11_explore_then_exploit.py` | The core tension in optimization |
| [07](07-ucb1.md) | UCB1 — Optimism Under Uncertainty | `07_ucb1.py` | Frequentist bandits, confidence bounds |
| [08](08-thompson-sampling.md) | Thompson Sampling — Bayesian Bandits | `05_thompson_sampling.py` | Posterior sampling, Beta-Bernoulli |
| [09](09-contextual-bandits.md) | Contextual Bandits — Using Context | `08_contextual_bandit.py` | LinUCB, feature engineering |

### Module 4: Advanced Optimization

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [10](10-bayesian-optimization.md) | Bayesian Optimization | `09_bayesian_optimization.py` | Gaussian processes, acquisition functions |
| [11](11-reinforcement-learning.md) | Reinforcement Learning | `02_gymnasium_rl.py` | Gymnasium interface, reward shaping |
| [12](12-llm-agents.md) | LLM Agents | `04_llm_agent.py` | Language model reasoning |

### Module 5: Production & Meta-Strategies

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [13](13-ensemble-methods.md) | Ensemble Methods | `10_ensemble.py` | Hedge algorithm, combining strategies |
| [14](14-production-safety.md) | Going to Production | `12_production_safety.py` | Safety patterns, monitoring, observability |

## How to Use This Course

**If you're a student with a token**: Start at [Lesson 0](00-roles-and-setup.md) to verify your setup, then proceed through the lessons in order.

**If you're a solo researcher**: Read [Lesson 0](00-roles-and-setup.md) to understand both roles, set up your experiment in the Dashboard, then work through the course as an agent developer.

**If you're an instructor**: See the [Classroom & Lab Guide](../docs/classroom-guide.md) for experiment setup, token distribution, and grading rubrics. Point your students at this course.

**Read then run.** Each lesson explains the theory, then walks through the example code. Run the example against a real experiment to see the concepts in action.

**Build incrementally.** Each module builds on the previous one. By Module 3, you'll understand why UCB1 is better than Explore-Then-Exploit. By Module 5, you'll know when to use which approach.

**Experiment.** The exercises at the end of each lesson suggest modifications. Try them — breaking things is the fastest way to learn.
