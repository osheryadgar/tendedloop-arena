# Lesson 0: Roles and Setup

## Two Personas, One Platform

Arena has two distinct roles. You might play one or both — but understanding the separation is key to how the system works.

### The Experiment Manager

**Who**: Instructor, research lead, facility manager, or solo researcher.

**What they do**:
- Create experiments in the [TendedLoop Dashboard](https://app.tendedloop.com)
- Configure variants, guardrails, enrollment, and schedule
- Download Arena Manifests (one per variant) containing strategy tokens
- Distribute tokens to agent developers
- Monitor the experiment in real-time via the dashboard
- Trigger circuit breakers if something goes wrong
- Analyze results after the experiment completes

**Tools**: TendedLoop Dashboard (web UI). No code required.

### The Agent Developer

**Who**: Student, engineering team, ML researcher, or solo developer.

**What they do**:
- Receive a strategy token from the experiment manager
- Write an agent using the Arena SDK (this repo)
- Run the agent against their assigned variant
- Monitor their agent's performance via `agent.scoreboard()`
- Iterate on their strategy based on observed signals

**Tools**: Python + Arena SDK. No dashboard access needed.

### The 1:N Relationship

One experiment manager sets up the experiment. N agent developers each build agents for their assigned variants:

```
Experiment: "XP Optimization Study"
├── Control (no agent — immutable baseline)
├── Variant A → Token → Team Alpha (UCB1 agent)
├── Variant B → Token → Team Beta  (LLM agent)
├── Variant C → Token → Team Gamma (PID agent)
└── Variant D → Token → Team Delta (Bayesian Optimization)
```

Each team works independently. They can see the scoreboard (how all variants are performing) but can only modify their own variant's economy. The experiment manager sees everything and can intervene if needed.

### Solo Mode

If you're a solo researcher, you wear both hats:
1. Create the experiment in the dashboard (manager hat)
2. Download your variant's manifest
3. Write and run your agent (developer hat)
4. Monitor results in the dashboard (back to manager hat)

The course focuses on the **agent developer** role — that's where the SDK lives. For experiment setup, see the [Classroom & Lab Guide](../docs/classroom-guide.md).

## Setup for Agent Developers

Your experiment manager gives you:
1. A **strategy token** (`strat_...`) — your authentication credential
2. The **API URL** (usually `https://api.tendedloop.com`)
3. The **experiment brief** — what metric to optimize, any constraints

You need:
1. Python 3.10+
2. The Arena SDK

```bash
pip install git+https://github.com/osheryadgar/tendedloop-arena.git
```

Set your token:

```bash
export STRATEGY_TOKEN=strat_your_token_here
export ARENA_URL=https://api.tendedloop.com  # default
```

Verify your connection:

```python
from tendedloop_agent import Agent

with Agent(api_url="https://api.tendedloop.com", strategy_token="strat_...") as agent:
    info = agent.info()
    print(f"Connected! Variant: {info.variant_name}")
    print(f"Experiment: {info.experiment_name} ({info.experiment_status})")
    print(f"Constraints: update every {info.update_interval_min}min, delta ±{info.delta_limit_pct}%")
```

If this prints your variant name, you're ready to start [Lesson 1](01-what-is-arena.md).

## Setup for Experiment Managers

See the [Classroom & Lab Guide](../docs/classroom-guide.md) for:
- Creating experiments with agent mode
- Configuring guardrails for student safety
- Distributing manifests and tokens
- Monitoring and grading

## Next

[Lesson 1: What is Multi-Agent Optimization?](01-what-is-arena.md)
