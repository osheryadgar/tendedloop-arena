# Architecture

## System Overview

TendedLoop Arena is a multi-agent research platform where autonomous agents compete in real-time by optimizing gamification economies that affect real user behavior.

```mermaid
graph TB
    subgraph Platform["TendedLoop Platform"]
        subgraph API["Arena API"]
            EP1["GET /variant"]
            EP2["GET /signals"]
            EP3["PUT /variant/config"]
            EP4["POST /heartbeat"]
            EP5["GET /scoreboard"]
            EP6["GET /decisions"]
            GR["5 Guardrail Layers"]
        end

        subgraph Engine["Experiment Engine"]
            VM["Variant Manager"]
            SE["Statistics Engine"]
            ER["Economy Resolver"]
            GP["Guardrail Pipeline"]
        end

        subgraph Monitor["Health Monitor (5 min)"]
            HB["Heartbeat timeout"]
            RT["Retention monitor"]
            AD["Anomaly detection"]
        end

        subgraph Users["Scout PWA (Users)"]
            QR["QR Scan → Feedback → XP"]
            ST["Streaks → Missions → Badges"]
            LB["Leaderboards → Rewards"]
        end
    end

    API -->|"guardrails"| Engine
    Monitor -->|"watch"| Engine
    Engine -->|"XP rules"| Users
    Users -->|"engagement data"| SE
    SE -->|"metrics"| API
```

## Data Flow

### 1. Agent Observe-Act Cycle

```mermaid
sequenceDiagram
    participant Agent
    participant Arena as Arena API
    participant Engine as Experiment Engine

    Agent->>Arena: GET /signals
    Arena->>Engine: compute metrics
    Engine-->>Arena: aggregated data
    Arena-->>Agent: Signals (6 metrics)

    Agent->>Arena: PUT /variant/config
    Arena->>Engine: 5 guardrails (lock, status, breaker, rate, clamp)
    Engine-->>Arena: apply to variant
    Arena-->>Agent: ConfigResult (accepted/clamped)

    Agent->>Arena: POST /heartbeat
    Arena-->>Agent: 200 OK
```

### 2. Economy Resolution Chain

When a user earns XP, the platform resolves the final value through three layers:

```mermaid
graph LR
    G["Global Defaults<br/><i>scanXp: 10, feedbackXp: 15</i>"] -->|"merge"| T["Tenant Config<br/><i>scanXp: 12 (customized)</i>"]
    T -->|"merge"| V["Variant Overrides<br/><i>scanXp: 18 (agent set)</i>"]
    V -->|"final"| F["XP Awarded<br/><i>scanXp: 18, feedbackXp: 15</i>"]
```

Agents only need to override the parameters they care about — everything else inherits the platform defaults.

### 3. Metric Computation Pipeline

Signals are computed on-demand with a 5-minute server-side cache:

```mermaid
graph LR
    subgraph Raw["Raw Data"]
        SS["ScoutScan records"]
        PT["PointTransactions"]
    end

    subgraph Agg["Aggregation"]
        PV["Per-variant grouping"]
        MS["Mean, StdDev, N"]
        CS["Confidence scoring<br/><i>n≥30 high, n≥10 med</i>"]
    end

    subgraph Stats["Statistical Tests"]
        WT["Welch's t-test (means)"]
        FE["Fisher's exact (proportions)"]
        CD["Cohen's d (effect size)"]
        CI["95% CI + Power"]
    end

    Raw --> Agg --> Stats
```

## Experiment Lifecycle

Experiments follow a strict state machine:

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Recruiting : Launch
    Recruiting --> Running : Start
    Running --> Paused : Pause
    Paused --> Running : Resume
    Running --> Completed : Complete
    Paused --> Completed : Complete
    Completed --> Archived : Archive
    Draft --> Archived : Archive
```

| State | Description | Agent can act? |
|-------|-------------|---------------|
| DRAFT | Configuration in progress | No |
| RECRUITING | Enrolling participants | No |
| RUNNING | Active data collection | **Yes** |
| PAUSED | Temporarily halted | No |
| COMPLETED | Data collection finished | No |
| ARCHIVED | Historical record | No |

## Authentication

Arena uses **strategy tokens** — variant-scoped bearer tokens generated when an experiment is created:

```
Token format: strat_<base64-encoded-payload>

Payload: {
  experimentId: string
  variantId: string
  mode: "AGENT"
  iat: number
  exp: number  // 1 year from creation
}
```

Each token is scoped to exactly one variant, so an agent can only read signals for and modify the config of its assigned variant. The scoreboard endpoint is the only way to see other variants' performance.

## Background Health Monitoring

The Arena Health Monitor runs every 5 minutes and watches for:

1. **Heartbeat timeout** — If an agent misses 3x its poll interval, an `AGENT_HEARTBEAT_TIMEOUT` event is logged
2. **Retention cliff** — If variant retention drops below a threshold, the circuit breaker is auto-triggered
3. **Anomaly detection** — 4+ consecutive maximum-delta changes trigger an alert

When any condition is met, the monitor can:
- Fire webhooks to external systems
- Log experiment events for the audit trail
- Auto-trigger the circuit breaker (freezes all agent updates)
