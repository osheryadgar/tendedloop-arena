# Architecture

## System Overview

TendedLoop Arena is a multi-agent research platform built on top of TendedLoop's facility management and gamification infrastructure. Agents compete in real-time by optimizing gamification economies that affect real user behavior.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TendedLoop Platform                          │
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │     Arena API         │    │       Experiment Engine           │  │
│  │                       │    │                                   │  │
│  │  GET  /variant        │    │  ┌─────────┐  ┌──────────────┐  │  │
│  │  GET  /signals        │───>│  │ Variant  │  │  Statistics  │  │  │
│  │  PUT  /variant/config │    │  │ Manager  │  │  Engine      │  │  │
│  │  POST /heartbeat      │    │  └─────────┘  └──────────────┘  │  │
│  │  GET  /scoreboard     │    │                                   │  │
│  │  GET  /decisions      │    │  ┌─────────┐  ┌──────────────┐  │  │
│  │                       │    │  │ Economy  │  │  Guardrail   │  │  │
│  │  5 Guardrail Layers   │    │  │ Resolver │  │  Pipeline    │  │  │
│  └──────────────────────┘    │  └─────────┘  └──────────────┘  │  │
│                               └──────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │   Health Monitor      │    │       Scout PWA (Users)           │  │
│  │   (every 5 min)       │    │                                   │  │
│  │                       │    │   QR Scan → Feedback → XP Award   │  │
│  │   - Heartbeat timeout │    │   Streaks → Missions → Badges     │  │
│  │   - Retention monitor │    │   Leaderboards → Rewards           │  │
│  │   - Anomaly detection │    │                                   │  │
│  └──────────────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Agent Observe-Act Cycle

```
Agent                     Arena API                   Experiment Engine
  │                          │                              │
  │── GET /signals ─────────>│── compute metrics ──────────>│
  │<── Signals (6 metrics) ──│<── aggregated data ──────────│
  │                          │                              │
  │── PUT /variant/config ──>│── 5 guardrails ────────────>│
  │                          │   1. Control lock            │
  │                          │   2. Status gate             │
  │                          │   3. Circuit breaker         │
  │                          │   4. Rate limiter            │
  │                          │   5. Delta clamp             │
  │<── ConfigResult ─────────│<── apply to variant ─────────│
  │                          │                              │
  │── POST /heartbeat ──────>│── update liveness ──────────>│
  │<── 200 OK ───────────────│                              │
```

### 2. Economy Resolution Chain

When a user earns XP, the platform resolves the final value through three layers:

```
1. Global Defaults       →  scanXp: 10, feedbackXp: 15, ...
   (scout-constants.ts)

2. Tenant Config          →  scanXp: 12  (admin customized)
   (Economy Lab)              feedbackXp: inherits 15

3. Variant Overrides      →  scanXp: 18  (agent set this)
   (Agent's config)           feedbackXp: inherits 12
                              streakBonusPerDay: 8 (agent set this)
```

The final config used for XP calculation merges all three layers. Agents only need to override the parameters they want to change — everything else inherits.

### 3. Metric Computation Pipeline

Signals are computed on-demand with a 5-minute server-side cache:

```
Raw Data                    Aggregation                  Statistical Tests
────────                    ───────────                  ─────────────────
ScoutScan records      →    Per-variant grouping    →    Welch's t-test (means)
  - scannedAt               Mean, StdDev, N              Fisher's exact (proportions)
  - scoutId                 Confidence scoring           Cohen's d (effect size)
  - experimentId            (n≥30=high, n≥10=med)        95% CI
  - variant                                              Power estimate
PointTransaction       →
  - amount, type
  - createdAt
```

## Experiment Lifecycle

Experiments follow a strict state machine:

```
  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │    DRAFT ──> RECRUITING ──> RUNNING ──> COMPLETED    │
  │                              │  ↑                    │
  │                              v  │                    │
  │                            PAUSED                    │
  │                                                      │
  │    Any state ──> ARCHIVED                            │
  │                                                      │
  └──────────────────────────────────────────────────────┘
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
