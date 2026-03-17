# Multi-Agent Gamification Research — Course

A hands-on course for building autonomous agents that optimize gamification economies using the TendedLoop Arena SDK.

## Prerequisites

- Python 3.10+
- Basic familiarity with APIs and data structures
- No ML/RL experience required (we build up from zero)

## Setup

```bash
pip install "tendedloop-agent[all] @ git+https://github.com/osheryadgar/tendedloop-arena.git"
export STRATEGY_TOKEN=strat_your_token_here
```

## Curriculum

### Module 1: Foundations

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [01](01-what-is-arena.md) | What is Multi-Agent Optimization? | — | The problem, why it matters, how Arena works |
| [02](02-the-arena-environment.md) | The Arena Environment | — | API, signals, guardrails, experiment lifecycle |
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
| [09](09-contextual-bandits.md) | Contextual Bandits — Using Context | `08_contextual_bandit.py` | LinUCB, feature engineering, context-dependent decisions |

### Module 4: Advanced Optimization

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [10](10-bayesian-optimization.md) | Bayesian Optimization | `09_bayesian_optimization.py` | Gaussian processes, acquisition functions, sample efficiency |
| [11](11-reinforcement-learning.md) | Reinforcement Learning | `02_gymnasium_rl.py` | Gymnasium interface, reward shaping, policy design |
| [12](12-llm-agents.md) | LLM Agents | `04_llm_agent.py` | Using language models for reasoning-based optimization |

### Module 5: Production & Meta-Strategies

| Lesson | Title | Example | What You Learn |
|--------|-------|---------|---------------|
| [13](13-ensemble-methods.md) | Ensemble Methods | `10_ensemble.py` | Hedge algorithm, combining strategies, meta-learning |
| [14](14-production-safety.md) | Going to Production | `12_production_safety.py` | Safety patterns, monitoring, observability |

## How to Use This Course

**Read then run.** Each lesson explains the theory, then walks through the example code. Run the example against a real experiment to see the concepts in action.

**Build incrementally.** Each module builds on the previous one. By Module 3, you'll understand why UCB1 is better than Explore-Then-Exploit. By Module 5, you'll know when to use which approach.

**Experiment.** The exercises at the end of each lesson suggest modifications. Try them — breaking things is the fastest way to learn.
