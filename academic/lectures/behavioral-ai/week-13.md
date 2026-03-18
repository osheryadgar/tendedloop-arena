# Week 13: Case Studies — Computational Analysis

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture applies the full toolkit developed in Weeks 1-12 to concrete gamification systems. Rather than descriptive case studies, we perform computational reverse engineering: extract parameters, model reward functions, simulate populations, and identify optimization objectives. The three cases — Duolingo (consumer), TendedLoop (enterprise), and agent-optimized systems (frontier) — span the spectrum from human-designed to AI-controlled gamification.

## Key Concepts

### Computational Case Study Methodology

A computational case study goes beyond description. The methodology:

1. **System decomposition.** Identify all gamification elements and their parameters. Output: a parameter vector $\boldsymbol{\theta}$.
2. **Reward function extraction.** Determine the mapping from user actions to rewards: $r: \mathcal{A} \times \Theta \to \mathbb{R}$.
3. **Behavioral modeling.** Model user response to the reward function. Estimate the engagement function $E(\boldsymbol{\theta}, \mathbf{u})$ where $\mathbf{u}$ is the user population characteristics.
4. **Objective inference.** From the observed $\boldsymbol{\theta}^*$ (the deployed configuration), infer the optimization objective by inverse optimization: "What objective function would a rational designer maximize to arrive at this configuration?"
5. **Simulation.** Simulate alternative configurations and predict engagement outcomes. Identify the sensitivity of the system to parameter perturbations.
6. **Critique.** Identify Goodhart risks, alignment failures, and potential improvements.

### Case Study 1: Duolingo XP Economy

Duolingo is the world's most successful gamification system by user count (~100M MAU). We reverse-engineer its economy.

**Parameter extraction.** From public documentation, user experimentation, and published papers (Settles & Meeder, 2016):

| Parameter | Value (approximate) | Category |
|-----------|---------------------|----------|
| Lesson XP | 10-20 per lesson | Base reward |
| Perfect lesson bonus | +5 XP | Quality incentive |
| Streak bonus | 2x XP multiplier at 7-day streak | Retention mechanic |
| Daily goal | 10/20/30/50 XP | Personalized targets |
| Streak freeze | 1 available (purchasable) | Loss aversion buffer |
| Leaderboard | 30 users, weekly reset | Social competition |
| League tiers | 10 tiers (Bronze to Diamond) | Progression system |
| Hearts (lives) | 5 per session (free tier) | Constraint |
| Gems (currency) | Earned through streaks/achievements | Secondary economy |

**Parameter vector:**
$$\boldsymbol{\theta}_{\text{Duo}} = (\text{lessonXP}, \text{perfectBonus}, \text{streakMultiplier}, \text{dailyGoal}, \text{freezeCount}, \text{leaderboardSize}, \text{leagueTiers}, \text{hearts}, \text{gemRate})$$

**Reward function.** For a user completing $k$ lessons on day $d$ with streak length $s$:

$$r(k, d, s) = \sum_{j=1}^{k} \left(\text{baseXP}_j + \text{perfectBonus}_j \cdot \mathbb{1}[\text{perfect}_j]\right) \cdot \text{streakMultiplier}(s)$$

where $\text{streakMultiplier}(s) = 1 + \mathbb{1}[s \geq 7] \cdot 1.0$ (doubles XP at 7+ days).

**Inferred optimization objective.** Duolingo's public metrics focus on DAU and retention. The inferred objective:

$$\max_{\boldsymbol{\theta}} \quad w_1 \cdot \text{DAU}(\boldsymbol{\theta}) + w_2 \cdot R_{14}(\boldsymbol{\theta}) - w_3 \cdot \text{Cost}(\boldsymbol{\theta})$$

where $R_{14}$ is 14-day retention and Cost includes server costs and content creation. The streak mechanic dominates retention (Duolingo's own A/B tests show streaks are the single most impactful feature).

**Critique.** Duolingo exhibits several Goodhart risks:
- Users "streak pad" by doing one easy lesson to maintain the streak without meaningful learning.
- The leaderboard creates a "lesson count" optimization that favors short, easy lessons over challenging material.
- Hearts (lives) on the free tier may cause anxiety and avoidance rather than engagement.

The misalignment: Duolingo optimizes DAU/retention (engagement), but the true objective is language learning. These can diverge — a user who does one easy lesson daily for streak maintenance has high retention but low learning.

### Case Study 2: TendedLoop Enterprise Gamification

TendedLoop's facility feedback platform (the Arena domain) represents enterprise gamification with fundamentally different constraints.

**Parameter extraction (Arena's 10 tunable parameters):**

| Parameter | Range | Purpose |
|-----------|-------|---------|
| scanXp | 1-50 | Base scan reward |
| feedbackXp | 1-100 | Feedback submission reward |
| streakBonus | 0-50 | Per-day consecutive streak bonus |
| dailyXpCap | 50-500 | Daily earning limit |
| levelThreshold | varies | XP needed per level |
| missionFrequency | 1-5/day | Mission generation rate |
| badgeThresholds | varies | Achievement triggers |
| referralBonus | 0-200 | Referral reward |
| qualityMultiplier | 1-3x | Bonus for detailed feedback |
| streakFreezeAllowed | 0-2 | Loss aversion buffer |

**Key differences from consumer gamification:**

1. **Involuntary population.** Employees do not choose to use the system; it is deployed by management. Engagement cannot be assumed — it must be earned.
2. **Non-anonymous impact.** Unlike Duolingo (where only the user is affected by their engagement), feedback quality affects facility operations, maintenance scheduling, and other employees' work environment.
3. **Small populations.** Typically 50-500 users per building, compared to millions for consumer apps. Statistical detection of effects requires larger relative effect sizes (Week 10).
4. **Institutional constraints.** Reward budgets may be limited. Aggressive gamification (dark patterns) risks employee backlash and HR complaints.

**Reward function:**

$$r(\text{scan}, \text{feedback}, d, s) = \min\left(\text{scanXp} \cdot n_{\text{scan}} + \text{feedbackXp} \cdot n_{\text{feedback}} + \text{streakBonus} \cdot s + r_{\text{mission}}, \; \text{dailyXpCap}\right)$$

The `dailyXpCap` acts as a hard constraint — it bounds the maximum daily reward, preventing both farming and inflationary spirals. The `qualityMultiplier` incentivizes detailed feedback (photos, comments), partially addressing the Goodhart risk of empty submissions.

**Optimization objective (inferred):**

$$\max_{\boldsymbol{\theta}} \quad w_1 \cdot \text{ScanRate} + w_2 \cdot \text{FeedbackQuality} + w_3 \cdot \text{Retention} \quad \text{s.t.} \quad \text{XpInflation} \leq I_{\max}, \; \boldsymbol{\theta} \in \Theta$$

The multi-objective nature — balancing scan volume, feedback quality, and retention — is what makes Arena experiments interesting. A single-objective agent can easily game one metric at the expense of others.

### Case Study 3: Agent-Optimized Systems

What happens when an AI agent controls the reward structure? This is the Arena's core research question.

**Phase 1: Static optimization.** The agent searches the parameter space offline (grid search, Bayesian optimization) and deploys a fixed configuration. This is equivalent to a well-designed A/B test — the agent selects the best variant and runs with it. No adaptation, no feedback loops.

**Phase 2: Adaptive optimization.** The agent observes user responses in real-time and adjusts parameters. This creates a feedback loop:

$$\boldsymbol{\theta}_{t+1} = \boldsymbol{\theta}_t + \eta \cdot \nabla_\theta \hat{E}(\boldsymbol{\theta}_t)$$

where $\hat{E}$ is estimated from recent data. The gradient is noisy and the objective is non-stationary (users adapt to the reward structure), creating a moving-target problem.

**Phase 3: Multi-agent dynamics.** Multiple agents compete on the same platform, each optimizing for their assigned user segment. Agent A's parameter changes affect Agent B's users through social comparison, shared leaderboards, and network effects. The system becomes a game between agents:

$$\boldsymbol{\theta}_A^* = \arg\max_{\boldsymbol{\theta}_A} E_A(\boldsymbol{\theta}_A, \boldsymbol{\theta}_B^*), \quad \boldsymbol{\theta}_B^* = \arg\max_{\boldsymbol{\theta}_B} E_B(\boldsymbol{\theta}_A^*, \boldsymbol{\theta}_B)$$

The Nash equilibrium of this agent game may not maximize total user welfare — a direct instance of the alignment problem (Week 11) at the agent level.

**What changes with AI control:**

1. **Speed of adaptation.** An AI agent can update parameters daily; a human designer updates quarterly. This allows faster convergence but also faster divergence into harmful configurations.
2. **Exploitation of subtlety.** An AI agent can discover non-obvious parameter combinations that exploit psychological vulnerabilities a human designer would not think to try. This is the "creative" risk of optimization.
3. **Accountability gap.** When the agent chooses a harmful configuration, the causal chain (agent code -> parameter update -> user behavior change -> harm) is harder to attribute than a human designer's deliberate choice.

## Formal Models

### Inverse Optimization for Objective Inference

Given observed parameters $\boldsymbol{\theta}^*$, infer the objective $f$ such that $\boldsymbol{\theta}^* = \arg\max_\theta f(\theta)$. Under a linear objective $f(\theta) = \mathbf{w}^T \mathbf{g}(\theta)$ where $\mathbf{g}$ maps parameters to metric values:

$$\text{Find } \mathbf{w} \geq 0 \text{ s.t. } \nabla_\theta (\mathbf{w}^T \mathbf{g}(\theta^*)) = 0 \text{ (KKT conditions)}$$

If $\mathbf{g}$ is differentiable and the Jacobian $\nabla_\theta \mathbf{g}(\theta^*)$ has full rank, the weights $\mathbf{w}$ are identifiable up to scaling. This formalizes "what is Duolingo optimizing?" as a well-posed mathematical problem.

### Comparative Economy Analysis

Define an economy similarity metric between two gamification systems. Let $\boldsymbol{\theta}_A$ and $\boldsymbol{\theta}_B$ be their parameter vectors, normalized to $[0, 1]$ on each dimension:

$$d(A, B) = \sqrt{\sum_k w_k (\hat{\theta}_{A,k} - \hat{\theta}_{B,k})^2}$$

where $w_k$ weights the importance of each parameter dimension. Parameters that exist in one system but not the other are handled by mapping to functional equivalents or treating as zero.

Applied to Duolingo vs. TendedLoop: high similarity on streak mechanics (both have streaks, freezes, bonus XP); low similarity on social mechanics (Duolingo has competitive leagues; TendedLoop has cooperative building-level goals); structural difference in the cap mechanism (Duolingo uses hearts to limit negative outcomes; TendedLoop uses dailyXpCap to limit positive outcomes).

## Worked Examples

### Example 1: Reverse-Engineering Duolingo's Streak Value

From public data: Duolingo reports that users with 7+ day streaks have 3x higher 30-day retention than users without. We estimate the implied value of the streak mechanic.

Let $R_0 = 0.20$ (base 30-day retention) and $R_s = 0.60$ (retention with streak). The lift is $\Delta R = 0.40$. If Duolingo has 100M MAU and average revenue per user is $r = \$0.50$/month, the streak mechanic's value:

$$V_{\text{streak}} = N \cdot \Delta R \cdot r = 10^8 \cdot 0.40 \cdot 0.50 = \$20M/\text{month}$$

This back-of-envelope calculation explains why Duolingo invests so heavily in streak features (notifications, freezes, streak rewards). Caveat: this is correlational, not causal — streak users may be inherently more motivated. The causal effect, estimated from A/B tests removing streaks (which Duolingo has run internally), is likely smaller but still substantial.

### Example 2: Simulating Arena Configurations

We simulate 200 users over 30 days under three configurations:

| Config | scanXp | feedbackXp | streakBonus | dailyXpCap |
|--------|--------|------------|-------------|------------|
| A (Conservative) | 5 | 10 | 5 | 100 |
| B (Aggressive) | 15 | 30 | 20 | 300 |
| C (Quality-focused) | 5 | 50 | 5 | 150 |

User model: each day, user $i$ scans with probability $p_i(r_{\text{scan}}) = \sigma(0.1 \cdot r_{\text{scan}} - 2 + \epsilon_i)$ where $\sigma$ is the logistic function and $\epsilon_i \sim N(0, 0.5)$ is individual variation. Feedback is submitted with probability $p_f = 0.3 \cdot p_i$ with quality proportional to $r_{\text{feedback}} / r_{\text{scan}}$ (ratio incentivizes quality when feedback is rewarded relatively more).

Simulated results (30-day averages):
- Config A: Scan rate 1.8/day, feedback quality 6.2/10, retention 55%
- Config B: Scan rate 3.4/day, feedback quality 4.1/10, retention 72%
- Config C: Scan rate 1.6/day, feedback quality 8.3/10, retention 48%

Config B wins on scan rate and retention but loses on quality. Config C wins on quality but has the lowest retention (the cap limits daily XP, reducing daily return motivation). This illustrates the multi-objective tradeoff that Arena agents must navigate.

### Example 3: Detecting Optimization Objective from Observed Behavior

An Arena agent deployed configuration $\boldsymbol{\theta}^* = (12, 25, 15, 200)$ over 4 weeks. We observe metric responses:

| Metric | Sensitivity to scanXp | Sensitivity to feedbackXp | Sensitivity to streakBonus | Sensitivity to cap |
|--------|----------------------|--------------------------|---------------------------|-------------------|
| Scan rate | +0.8 | +0.1 | +0.3 | +0.2 |
| Quality | -0.2 | +0.6 | 0.0 | -0.1 |
| Retention | +0.1 | +0.2 | +0.7 | +0.3 |

The Jacobian $\nabla_\theta \mathbf{g}$ at $\boldsymbol{\theta}^*$. The KKT condition $\nabla_\theta(\mathbf{w}^T \mathbf{g}) = 0$ gives:

$$0.8w_1 - 0.2w_2 + 0.1w_3 = 0, \quad 0.1w_1 + 0.6w_2 + 0.2w_3 = 0, \quad \ldots$$

Solving (with normalization $\sum w_k = 1$) yields approximately $w_1 = 0.45, w_2 = 0.15, w_3 = 0.40$. The agent is primarily optimizing for scan rate (45%) and retention (40%), with quality as a secondary concern (15%). This inverse analysis reveals the agent's implicit objective, which can then be evaluated against the researcher's intended objective.

## Arena Connection

Arena is itself the primary case study for this course:

- **Live parameter observation.** Students can observe how different agents configure the 10 parameters in real experiments and apply the inverse optimization methodology to infer agent objectives.
- **Comparative analysis.** Multiple agents running simultaneously on Arena provide natural comparisons — students can analyze which agent's implicit objective is most aligned with genuine user benefit.
- **Simulation vs. reality.** Students simulate populations under various configurations (Example 2) and can compare predictions against actual Arena experimental results. The gap between simulation and reality reveals model limitations.
- **Agent accountability.** When an Arena agent's configuration degrades a metric, the experimental log provides full traceability — every parameter change and its timestamp. This enables the causal chain analysis needed for accountability (Case Study 3).

## Discussion Questions

1. **Reverse engineering methodology.** Choose a gamification system you use daily (fitness app, productivity tool, social media). Apply the computational case study methodology: extract at least 8 parameters, write the reward function, and hypothesize the optimization objective. What data would you need to validate your hypothesis?

2. **Consumer vs. enterprise.** The Duolingo and TendedLoop case studies reveal fundamentally different design constraints. Formalize the differences as constraint sets on the optimization problem. Which constraints are harder to satisfy? What design choices become available when you relax enterprise constraints (e.g., allowing anonymous participation)?

3. **Agent discovery.** In Example 2, Config B maximizes scan rate and retention but degrades quality. A human designer might avoid this configuration because they understand the importance of quality. What prevents an AI agent from discovering and deploying such configurations? Are guardrails (Week 11) sufficient, or do we need something more fundamental?

4. **Economy evolution.** Both Duolingo and TendedLoop have evolved their gamification economies over time. What economic principles govern when to inflate (increase rewards), deflate (decrease rewards), or restructure (change the reward function entirely)? Draw parallels to monetary policy.

## Further Reading

- **Settles, B. & Meeder, B. (2016).** "A Trainable Spaced Repetition Model for Language Learning." *ACL.* Duolingo's published ML approach to learning optimization — reveals the intersection of pedagogy and gamification.
- **Hamari, J., Koivisto, J., & Sarsa, H. (2014).** "Does Gamification Work? — A Literature Review of Empirical Studies on Gamification." *HICSS.* Meta-analysis of 24 gamification studies — the evidence base for what actually works.
- **Azar, O. H. (2011).** "Relative Thinking Theory." *Journal of Socio-Economics.* Formal model of how users evaluate rewards relative to reference points — relevant to cross-system comparison.
