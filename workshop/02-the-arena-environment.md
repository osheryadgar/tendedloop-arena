# Lesson 2: The Arena Environment

> **Time:** ~30 minutes | **Complexity:** Beginner
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Identify the six engagement metrics and their confidence levels
> 2. List the ten economy parameters an agent can control
> 3. Explain the five sequential guardrails that constrain every agent action

## Overview

Before writing your first agent, you need to understand four things:
1. How to **authenticate** (get a strategy token)
2. What **signals** the platform gives you (your observations)
3. What **parameters** you can control (your actions)
4. What **guardrails** constrain your actions (the rules)

## Getting a Strategy Token

Every agent needs a `STRATEGY_TOKEN` — a variant-scoped bearer token that authenticates your agent and scopes it to one experiment variant.

### Path A: You received a token (student / team member)

Your experiment manager (instructor, research lead) gives you an **Arena Manifest** containing your token. Extract and set it:

```bash
export STRATEGY_TOKEN=strat_your_token_here  # From the Arena Manifest
```

That's it — skip to the next section.

### Path B: You're setting up the experiment yourself

1. Log in to the [TendedLoop Dashboard](https://app.tendedloop.com)
2. Navigate to **Admin > Research > Experiments**
3. Create a new experiment with **Agent Mode** enabled
4. Click the **"..."** menu on a treatment variant and select **"Download Manifest"**
5. The Arena Manifest JSON file contains your `strategyToken`

```bash
export STRATEGY_TOKEN=strat_your_token_here
```

> For details on experiment setup and distributing tokens to teams, see the [Classroom & Lab Guide](../academic/classroom-guide.md).

### What the Token Gives You

Each token is scoped to exactly one variant — your agent can only observe and modify its own variant. The scoreboard endpoint is the only way to see other variants' performance. Tokens expire when the experiment is archived.

## Signals: What You Can See

Every time you call `agent.observe()`, you get a `Signals` object with:

### Aggregate Counts

| Field | Description |
|-------|-------------|
| `enrolled` | Total users assigned to your variant |
| `active_today` | Users who scanned today |
| `active_7d` | Users active in the last 7 days |
| `total_scans` | All scans since experiment start |
| `experiment_days` | Days since experiment started |

### Six Metrics (with Statistical Context)

Each metric includes `value`, `std_dev`, `sample_size`, and `confidence`:

| Metric | What It Measures | Range |
|--------|-----------------|-------|
| `SCAN_FREQUENCY` | Scans per user per day | 0+ |
| `XP_VELOCITY` | XP earned per user per day | 0+ |
| `RETENTION_RATE` | % of users active in last 7 days | 0.0 - 1.0 |
| `MISSION_COMPLETION` | Completed / assigned missions | 0.0 - 1.0 |
| `STREAK_LENGTH` | Average current streak (days) | 0+ |
| `FEEDBACK_QUALITY` | % of scans that include feedback | 0.0 - 1.0 |

### Confidence Levels

```python
freq = signals.metrics["SCAN_FREQUENCY"]
if freq.confidence == "low":     # n < 10 — don't act on this
    pass
elif freq.confidence == "medium": # 10 <= n < 30 — directional only
    pass
elif freq.confidence == "high":   # n >= 30 — reliable for decisions
    pass
```

**Critical rule**: Never make decisions based on low-confidence data. This is the most common beginner mistake.

## Actions: What You Can Control

Your agent tunes the **gamification economy** — the reward structure that drives behavior:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `scanXp` | 10 | XP per QR code scan |
| `feedbackXp` | 15 | XP per feedback submission |
| `statusReportXp` | 20 | XP per status report |
| `issueReportXp` | 25 | XP per issue report |
| `photoXp` | 10 | XP per photo attachment |
| `firstScanOfDayXp` | 15 | Bonus for first scan each day |
| `streakBonusPerDay` | 5 | XP per consecutive active day |
| `streakBonusCap` | 50 | Max daily streak bonus |
| `scanDailyCap` | 20 | Max scans counted per day |
| `feedbackDailyCap` | 10 | Max feedback counted per day |

You don't need to set all of them. Only include the parameters you want to change — everything else inherits from the tenant's defaults.

### The Economy Resolution Chain

```
Global Defaults → Tenant Config → Your Variant Overrides → Final XP
```

If the tenant admin set `scanXp: 12` and your agent sets `scanXp: 18`, users in your variant earn 18 XP per scan. All other parameters stay at the tenant's values.

## Guardrails: The Safety System

Every `agent.act()` call passes through five sequential checks:

### 1. Control Variant Lock
The control group is **always immutable**. No agent can modify it. This ensures a clean baseline for statistical comparison.

### 2. Experiment Status Gate
Config updates are only accepted when the experiment is `RUNNING`. Draft, Paused, Completed, and Archived experiments reject all changes.

### 3. Circuit Breaker
A safety stop that freezes all agent updates. Can be triggered:
- **Manually** by a researcher
- **Automatically** when retention drops dangerously low

### 4. Rate Limiter
Agents can't update faster than `updateIntervalMin` (default: 60 minutes). This prevents:
- Users experiencing constant reward changes
- Rapid oscillation between configs
- Noisy measurements from too-frequent changes

### 5. Delta Clamping
The most important guardrail. It doesn't reject large changes — it **clamps** them:

```python
# If scanXp is currently 10 and deltaLimitPct is 50%:
agent.act(ConfigUpdate(economy_overrides={"scanXp": 100}))
# Result: accepted, but applied_config = {"scanXp": 15}  (clamped to +50%)
```

This means you can write aggressive strategies without fear — the platform will smooth out extreme proposals.

## Experiment Lifecycle

```
DRAFT → RECRUITING → RUNNING → COMPLETED → ARCHIVED
                      ↕
                    PAUSED
```

Your agent can only make changes during `RUNNING`. The platform manages all transitions.

## Putting It Together

Here's the complete flow of a single cycle:

```
1. agent.observe()          → Get Signals (6 metrics + counts)
2. Your decide() function   → Analyze signals, propose changes
3. agent.act(update)        → Submit through 5 guardrails
4. Platform applies config  → Users experience new XP values
5. Users interact           → Scans, feedback, streaks
6. Platform computes stats  → Updated metrics (5-min cache)
7. Back to step 1
```

## Exercises

1. **Read the signals**: Write a script that calls `agent.info()` and `agent.observe()`, and prints all available information in a readable format.
2. **Understand clamping**: If `deltaLimitPct=50` and the current `scanXp=10`, what's the maximum value you can set in one update? What about two consecutive updates? (Hint: delta clamping operates on the *current applied value*, so after the first update changes 10→15, the second update's 50% is relative to 15, not 10.)
3. **Think about timing**: Your agent's `poll_interval` (how often it checks signals) is 60 seconds. The signal cache refreshes every 5 minutes. The `updateIntervalMin` (how often the platform allows config changes) is 60 minutes. Given these three timers, how many poll cycles pass before (a) you see updated metrics after a change, and (b) you can submit another change?

## Next

In [Lesson 3](03-your-first-agent.md), you'll write your first agent and run it against a real experiment.
