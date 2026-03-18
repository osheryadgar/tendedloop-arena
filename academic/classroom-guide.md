# Classroom & Lab Guide

A guide for instructors, research leads, and experiment managers who want to run multi-agent experiments with teams of agent developers.

## Overview

You create the experiment infrastructure. Your students/teams write the agents. The platform handles safety, measurement, and statistical analysis.

```
You (Experiment Manager)
  │
  ├── Create experiment in Dashboard
  ├── Configure N+1 variants (N treatment + 1 control)
  ├── Set guardrails (how much freedom agents get)
  ├── Download N manifests
  ├── Distribute tokens to N teams
  │
  ├── Launch experiment → Start enrollment → Start running
  │
  ├── Monitor via Dashboard (real-time)
  │     ├── Scoreboard: which variant is winning?
  │     ├── Decision log: what did each agent do?
  │     ├── Health monitor: are agents alive?
  │     └── Circuit breaker: emergency stop
  │
  └── Complete experiment → Analyze results → Grade/publish
```

## Step 1: Create the Experiment

1. Log in to [app.tendedloop.com](https://app.tendedloop.com)
2. Navigate to **Admin > Research > Experiments**
3. Click **New Experiment**
4. In the experiment builder:
   - **Hypothesis**: What you expect to learn
   - **Primary metric**: What agents should optimize (e.g., SCAN_FREQUENCY)
   - **Variants**: Create N treatment variants + 1 control
   - **Toggle "Agent Mode"** for each treatment variant
   - **Enrollment**: How users are assigned to variants
   - **Schedule**: Start date and duration

## Step 2: Configure Guardrails

Guardrails control how much freedom agents have. For classroom use, start conservative:

| Parameter | Conservative (Classroom) | Standard (Research) | Aggressive (Advanced) |
|-----------|-------------------------|--------------------|-----------------------|
| `updateIntervalMin` | 120 | 60 | 5 |
| `deltaLimitPct` | 15 | 50 | 80 |

**Conservative** (recommended for first-time students):
- 120-minute update interval: agents can only change config once every 2 hours
- 15% delta limit: each change is very small, limiting damage from bugs

**Standard** (for experienced teams):
- 60-minute interval, 50% delta: the default balance

**Aggressive** (for advanced research):
- 5-minute interval, 80% delta: fast iteration, large changes, closer to real-time optimization

## Step 3: Distribute Tokens

After creating the experiment:

1. Click the **"..."** menu on each treatment variant
2. Select **"Download Manifest"**
3. Each manifest is a JSON file containing:
   ```json
   {
     "experimentId": "exp_...",
     "experimentName": "XP Optimization Study",
     "variantId": "var_...",
     "variantName": "Treatment-A",
     "strategyToken": "strat_...",
     "apiUrl": "https://api.tendedloop.com",
     "constraints": {
       "updateIntervalMin": 60,
       "deltaLimitPct": 50
     }
   }
   ```
4. Distribute one manifest per team. Each team extracts their `strategyToken` and `apiUrl`.

**Security**: Strategy tokens are scoped to one variant. A team cannot affect other teams' variants. Tokens expire when the experiment is archived.

## Step 4: Brief Your Teams

Give each team:

| Item | Description |
|------|-------------|
| Manifest file | Their variant's strategy token and constraints |
| Primary metric | What they should optimize (e.g., "maximize SCAN_FREQUENCY") |
| Experiment duration | How long they have (e.g., "2 weeks starting Monday") |
| Ground rules | Any additional constraints (e.g., "must explain every decision in the reasoning field") |
| SDK repo | `https://github.com/osheryadgar/tendedloop-arena` |
| Course | Point them to the [Multi-Agent Course](../workshop/README.md) |

### Suggested Team Brief Template

```
EXPERIMENT: XP Optimization Study
YOUR VARIANT: Treatment-B
YOUR TOKEN: strat_... (in attached manifest)

OBJECTIVE: Maximize SCAN_FREQUENCY while keeping RETENTION_RATE above 0.5

CONSTRAINTS:
- Update interval: 60 minutes
- Delta limit: ±50% per update
- Experiment runs: March 20 – April 3

DELIVERABLES:
1. Your agent code (Python)
2. A 1-page writeup: strategy, results, what you learned
3. Your decision audit log (from agent.decisions())

RESOURCES:
- SDK: pip install tendedloop-arena
- Course: https://github.com/osheryadgar/tendedloop-arena/tree/main/course
- Scoreboard: agent.scoreboard() shows all variants
```

## Step 5: Monitor the Experiment

While teams run their agents:

### Dashboard Monitoring
- **Experiment Monitor > Overview**: Enrollment, active users per variant
- **Experiment Monitor > Metrics**: Real-time metric comparison across variants
- **Experiment Monitor > Variants**: Per-variant config history and decision log
- **Experiment Monitor > Scouts**: Which users are in which variant

### Health Checks
- **Heartbeat status**: Are all agents alive? (Check every 5 minutes)
- **Decision log**: Are agents making reasonable changes?
- **Circuit breaker**: Available if a variant's metrics drop dangerously

### When to Intervene
- **Agent heartbeat timeout**: Contact the team — their agent may have crashed
- **Retention cliff**: If a variant's retention drops below 30%, consider the circuit breaker
- **Suspicious patterns**: 4+ consecutive max-delta changes suggest a bug

## Step 6: Analyze Results

After the experiment completes:

1. **Statistical comparison**: The platform computes Welch's t-test (continuous metrics) and Fisher's exact test (proportions) for each variant vs. control
2. **Effect sizes**: Cohen's d shows practical significance, not just statistical
3. **Decision audit**: Review each agent's decision log to understand *why* it performed as it did
4. **Data export**: Export raw scan data, point transactions, and metrics for custom analysis

## Grading Rubric (Suggestion)

| Criterion | Weight | What to Evaluate |
|-----------|--------|-----------------|
| Primary metric improvement vs. control | 30% | Did the agent actually improve engagement? |
| Strategy design and rationale | 25% | Is the approach well-reasoned? Does the writeup explain the "why"? |
| Code quality | 20% | Clean code, proper error handling, confidence gating |
| Reasoning quality in decision log | 15% | Are the `reasoning` strings informative and specific? |
| Adaptiveness | 10% | Did the agent react to changing conditions, or just repeat the same action? |

## Example Course Structures

### 2-Week Sprint (Undergraduate)
- Week 1: Lessons 1-5 (Foundations + Control). Each team builds a rule-based or PID agent.
- Week 2: Experiment runs. Teams monitor, iterate, and submit writeups.

### 4-Week Deep Dive (Graduate)
- Week 1: Lessons 1-5. Build rule-based agent.
- Week 2: Lessons 6-9. Switch to a bandit agent.
- Week 3: Lessons 10-12. Try Bayesian Optimization or LLM agent.
- Week 4: Lessons 13-14. Build an ensemble. Experiment runs.

### Research Lab (Ongoing)
- Each lab member picks a different strategy.
- Rotate variants each month.
- Track cumulative results across experiments.
- Publish findings on what strategies work in which conditions.

## FAQ

**Can teams see each other's code?**
That's up to you. Tokens are separate, so teams can't interfere with each other regardless. Sharing code is a pedagogical decision.

**What if a team's agent crashes?**
The variant stays at its last config. The team can restart their agent and it will resume from the current state. The dashboard shows heartbeat status.

**Can I run the experiment without real users?**
For a dry run, use the local sandbox: `python -m tendedloop_agent demo`. It simulates the full Arena API with realistic metrics, all 5 guardrails, and stateful economy tracking. Students can develop and test agents before connecting to a live experiment.

**How many teams can participate?**
One experiment supports up to 5 variants (4 treatment + 1 control). For more teams, create multiple experiments or have teams share variants in rounds.
