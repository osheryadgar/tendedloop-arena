# Week 7: Progression Systems and XP Economics

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture analyzes the mathematics of progression systems — how XP curves, level thresholds, currency sinks, and streak mechanics create the "feel" of a gamification economy. We derive why polynomial XP curves (especially O(n^1.5)) dominate real-world systems, formalize XP inflation as an economic phenomenon, and model streak retention probabilistically. The central theme is that progression systems are economic systems: they have supply (XP generation), demand (XP sinks), and inflation dynamics that must be managed.

## Key Concepts

### XP Curves: The Level Threshold Function

The level threshold function L(n) defines the total XP required to reach level n. This single function determines the *feel* of progression: how fast early levels fly by, how slowly late levels grind, and whether the system "respects" user effort.

Three canonical families:

**Linear: L(n) = a * n**

```
L(1) = a, L(2) = 2a, ..., L(10) = 10a
Level gap: L(n+1) - L(n) = a  (constant)
```

Each level requires the same additional effort. This sounds fair but *feels* wrong — level 10 should feel like more of an achievement than level 2. Linear curves make high levels feel cheap.

**Polynomial: L(n) = a * n^k**

```
Level gap: L(n+1) - L(n) = a * ((n+1)^k - n^k) ~ a * k * n^(k-1)
```

The gap grows polynomially. For k = 2: L(n) = a*n^2, gaps grow linearly (each level requires n more XP than the last). For k = 1.5: gaps grow as sqrt(n), a gentler increase.

**Exponential: L(n) = a * c^n**

```
Level gap: L(n+1) - L(n) = a * c^n * (c - 1) ~ a * (c-1) * c^n
```

Gaps grow exponentially. Level 20 requires c times more additional XP than level 19. This creates an extreme late-game grind where levels become effectively unreachable.

### Why O(n^1.5) Dominates

Most successful gamification systems use k between 1.2 and 2.0, with k = 1.5 being the most common. The reason is a balance between three competing requirements:

**Requirement 1: Early momentum.** New users should level up quickly to experience progression and competence (SDT, Week 2). This favors low k (fast early levels).

**Requirement 2: Late-game meaning.** High levels should feel like genuine achievements. This favors high k (hard late levels).

**Requirement 3: Sustainable pacing.** If a user maintains constant daily activity, the time between levels should grow at a manageable rate — not so fast that users feel stuck, not so slow that levels feel meaningless.

For constant daily XP rate r, the time to reach level n is:

```
T(n) = L(n) / r = a * n^k / r
```

Time between levels n and n+1:

```
Delta_T(n) = (a/r) * ((n+1)^k - n^k) ~ (a/r) * k * n^(k-1)
```

For k = 1: Delta_T is constant (~2 days per level). Levels come too easily.
For k = 2: Delta_T grows linearly (~n days per level). Level 20 takes 20 days. Level 50 takes 50 days. This is steep.
For k = 1.5: Delta_T grows as sqrt(n). Level 4 takes ~2 days, level 9 takes ~3 days, level 16 takes ~4 days, level 25 takes ~5 days. This is the "Goldilocks" growth rate — perceptible but not crushing.

**Derivation of the "just right" k:**

User perception of progress follows Weber-Fechner law: perceived effort is proportional to log(actual effort). For progression to feel "linear" in perception:

```
perceived_gap(n) = log(Delta_T(n)) = log(k * n^(k-1)) = log(k) + (k-1)*log(n)
```

For perceived gap to grow slowly: we want k-1 to be small but positive. k = 1.5 gives perceived gap growing as 0.5*log(n) — half the rate of actual gap growth. This feels like "appropriately increasing challenge."

### XP Inflation Analysis

XP inflation occurs when the rate of XP entering the economy exceeds the rate at which the progression system absorbs it. Formally:

**XP supply (inflow):**
```
S(t) = |U(t)| * E[XP/user/day]
```

This depends on the number of active users and the per-user XP generation rate (determined by scanXp, feedbackXp, streakBonus, etc.).

**XP demand (absorption capacity):**
```
D(t) = sum_u (L(level_u + 1) - XP_u)  (total XP needed for all users to reach next level)
```

**Inflation rate:**
```
I(t) = S(t) / D(t) - 1
```

When I(t) > 0, the economy is inflationary: users level up faster than the system intends, levels lose meaning, and the endgame arrives prematurely. When I(t) < 0, the economy is deflationary: users feel stuck, progression stalls, and engagement drops.

**Steady-state analysis:** In steady state, the average user is at level n* where inflow equals absorption:

```
E[XP/user/day] = (L(n*+1) - L(n*)) / target_days_per_level
```

For L(n) = 100*n^1.5 and E[XP/user/day] = 80, target 3 days per level:

```
100*((n*+1)^1.5 - n*^1.5) = 80 * 3 = 240
(n*+1)^1.5 - n*^1.5 = 2.4
```

Solving numerically: n* is approximately 7. Users stabilize around level 7, where the level gap matches their earning rate. Beyond level 7, progression slows (each level takes more than 3 days), which feels like hitting a wall.

### Currency Sinks

Currency sinks are mechanisms that remove XP (or other currency) from the economy, counteracting inflation. Common sinks:

**Consumption sinks:** Users spend XP on cosmetic items, streak freezes, or other purchases. The XP leaves the economy permanently.

```
XP_net(t) = XP_earned(t) - XP_spent(t)
```

For inflation control, we need E[XP_spent] to scale with E[XP_earned].

**Decay sinks:** XP gradually decays if not used (depreciation).

```
XP(t+1) = (1 - delta) * XP(t) + XP_earned(t)
```

This is aggressive and often feels punitive. Rarely used for total XP; sometimes used for "current XP" (spendable balance) vs. "total XP" (lifetime earned, never decreasing).

**Reset sinks:** Periodic resets (weekly leaderboards, seasonal ranks) remove accumulated position. XP isn't lost, but the *advantage* of accumulated XP is reset.

**Level-gated sinks:** Higher levels unlock more expensive items, creating proportionally larger sinks for high-level users.

The sink design problem: remove enough XP to prevent inflation, but not so much that users feel their effort is wasted. Formally:

```
minimize  |I(t)|  (drive inflation toward zero)
subject to  perceived_fairness(sink) >= f_min
            user_satisfaction(sink) >= s_min
```

### Streak Mechanics: Retention as a Function of Streak Length

Streaks create a self-reinforcing engagement loop. Define:

```
P(retain | streak_day = k) = probability user is active tomorrow given current streak of k days
```

Empirically, this function typically has two regimes:

**Habit formation phase (k < k*):**
```
P(retain | k) = p_0 + (p_max - p_0) * (1 - exp(-k / tau_habit))
```

Retention increases as the streak grows, reflecting habit formation. The time constant tau_habit is typically 14-30 days (consistent with habit formation literature).

**Plateau phase (k >= k*):**
```
P(retain | k) = p_max - epsilon * (k - k*)^+
```

After the habit is formed, retention plateaus and may slightly decline due to fatigue or loss of novelty.

**The streak paradox:** Longer streaks increase tomorrow's retention but also increase the *cost* of breaking the streak (prospect theory, Week 4). At very long streaks, the psychological cost of a break becomes so high that users experience anxiety, which can paradoxically cause them to pre-emptively quit ("I'll lose my streak eventually, so I'll stop now on my own terms").

Formally, the probability of *voluntary churn* due to streak anxiety:

```
P(voluntary_quit | k) = sigmoid((k - k_threshold) / tau_anxiety)
```

The effective retention combines organic retention and voluntary churn:

```
P(active_tomorrow | k) = P(retain | k) * (1 - P(voluntary_quit | k))
```

This produces a hump-shaped curve: retention increases with streak length up to a point, then decreases as streak anxiety dominates. The optimal streak system keeps users below k_threshold, perhaps through streak freezes or "streak milestones" that lock in achievement (converting loss-framed streak into gain-framed milestone).

### Diminishing Marginal Utility Formalized

The marginal utility of the n-th unit of XP is:

```
MU(n) = U(n) - U(n-1)
```

For concave utility functions (standard assumption in economics and verified for gamification rewards):

```
U(XP) = XP^alpha,  alpha in (0, 1)
MU(n) = n^alpha - (n-1)^alpha ~ alpha * n^(alpha-1)
```

MU is decreasing in n. The 100th XP feels worth less than the 10th.

**Implication for level design:** If L(n) grows faster than 1/MU(n), the perceived time between levels grows. If L(n) grows slower than 1/MU(n), the perceived time shrinks (levels feel easier as you progress — the opposite of what designers want).

For L(n) = a*n^k and MU(n) ~ n^(alpha-1):

```
Perceived level gap ~ (L(n+1) - L(n)) * MU(XP) ~ n^(k-1) * n^(alpha-1) = n^(k+alpha-2)
```

For perceived gap to be constant (each level "feels" equally hard): k + alpha = 2. With alpha = 0.88 (from prospect theory estimates): k = 1.12. With alpha = 0.5 (stronger diminishing returns): k = 1.5. This provides another derivation of why k = 1.5 is common — it compensates for diminishing marginal utility of XP.

## Formal Models

### Model 1: XP Economy as a Dynamical System

Define the economy state as the distribution of users across levels: N(n, t) = number of users at level n at time t.

The flow equation:

```
N(n, t+1) = N(n, t) + N(n-1, t) * P(level_up | n-1, theta) - N(n, t) * P(level_up | n, theta) - N(n, t) * P(churn | n)
```

where P(level_up | n, theta) = P(earning L(n+1) - L(n) XP before churning | at level n with config theta).

In steady state: inflow = outflow + churn for each level. The steady-state distribution N*(n) tells us where users "pile up." If N*(n) is concentrated at low levels, the economy is deflationary (users can't progress). If spread uniformly, it is well-calibrated. If concentrated at max level, it is inflationary (too easy).

**Level distribution entropy:**
```
H = -sum_n (N*(n)/|U|) * log(N*(n)/|U|)
```

High entropy means users are spread across levels (healthy). Low entropy means they are clustered (pathological — either all stuck at level 1 or all at max level).

### Model 2: Streak Survival Analysis

Model streak duration as a survival process. Let T be the random variable "streak length at break."

The survival function:

```
S(k) = P(T > k) = product_{j=1}^{k} P(retain | j)
```

Using the habit formation model:

```
S(k) = product_{j=1}^{k} [p_0 + (p_max - p_0)(1 - exp(-j/tau))]
```

Taking logs:

```
log S(k) = sum_{j=1}^{k} log[p_0 + (p_max - p_0)(1 - exp(-j/tau))]
```

The hazard rate (instantaneous probability of breaking at day k):

```
h(k) = 1 - P(retain | k) = 1 - p_0 - (p_max - p_0)(1 - exp(-k/tau))
```

For early k: h(k) is high (habit not formed). For large k: h(k) approaches 1 - p_max. If p_max = 0.95, the long-run daily break probability is 5%, giving an expected max streak of 1/0.05 = 20 days.

### Model 3: Optimal XP Curve Given User Distribution

Given a population with daily XP earning distribution X ~ F(x) (where F depends on theta), choose the level curve L(n) to maximize level distribution entropy H.

The optimization:

```
maximize  H(L) = -sum_n P(user at level n | L) * log P(user at level n | L)
subject to  L(n+1) > L(n) for all n  (monotonicity)
            L(1) = L_min  (entry threshold)
            L(N_max) = L_max  (cap)
```

This is a functional optimization over L(.). The solution depends on F(x): if users have high-variance XP earning, levels need wider gaps to separate them. If low-variance, narrower gaps suffice.

For XP earnings approximately lognormal (common in practice): L(n) ~ exp(n/c) places levels at equal intervals on the log-XP scale, matching the lognormal distribution's natural scale. But this is exponential in n, which creates grinding. The polynomial compromise L(n) = n^k approximates this for moderate k and a limited number of levels.

## Worked Examples

### Example 1: Deriving Level Thresholds

Design a 10-level system where users earning 80 XP/day take approximately:
- Level 1-3: 1 day each (onboarding)
- Level 4-6: 3 days each (engagement)
- Level 7-9: 7 days each (investment)
- Level 10: 14 days (mastery)

Required XP gaps: 80, 80, 80, 240, 240, 240, 560, 560, 560, 1120

Cumulative: L = [80, 160, 240, 480, 720, 960, 1520, 2080, 2640, 3760]

Fit L(n) = a * n^k:
- L(1) = a = 80 => a = 80
- L(10) = 80 * 10^k = 3760 => 10^k = 47 => k = log(47)/log(10) = 1.67

So L(n) = 80 * n^1.67 fits the designed progression. Let us verify intermediate levels:
- L(5) = 80 * 5^1.67 = 80 * 14.6 = 1168 (designed: 720). The power law over-estimates.

The mismatch shows that a pure polynomial does not perfectly match the three-phase design (fast/medium/slow). In practice, many systems use piecewise curves or lookup tables rather than a single formula.

### Example 2: XP Inflation Scenario

A system launches with 100 users, scanXp = 10, feedbackXp = 15, average 5 scans/day at 60% feedback rate, and L(n) = 100*n^1.5.

**Month 1:** 100 users, E[XP/user/day] = 5*10 + 5*0.6*15 = 50 + 45 = 95.

Users reach level 5 after L(5)/95 = 100*11.18/95 = 11.8 days. By day 30, average user is around level 7-8.

**Month 3:** Word of mouth brings 200 more users. Now 300 users. The 100 original users are at level 12-15. New users start at level 1.

The level distribution has two peaks: new users (level 1-3) and veterans (level 12-15). Entropy is moderate (bimodal).

**Month 6:** The designer adds daily missions (missionRewardXp = 50) to boost engagement. E[XP/user/day] jumps to 145.

Veterans now level up 50% faster. Within weeks, many reach level 20. The gap L(21) - L(20) = 100*(21^1.5 - 20^1.5) = 100*(96.2 - 89.4) = 680. At 145 XP/day, this takes 4.7 days — still reasonable.

But at level 30: L(31) - L(30) = 100*(172.5 - 164.3) = 820. At 145/day = 5.7 days. The system can handle level 30.

**Inflation check:** Is 145 XP/day too fast? Level 30 takes 100*30^1.5/145 = 100*164.3/145 = 113 days from level 0. That is about 4 months — reasonable for a long-term system.

### Example 3: Streak Bonus Optimization

Find the optimal streakBonus that maximizes 30-day retention.

**Model:** P(active on day t | streak = k) = 0.5 + 0.4*(1 - exp(-k/10)). Streak bonus = b * k XP. Users have a quit threshold: if the subjective loss from streak break exceeds 150 (prospect theory units), they experience anxiety and P(voluntary_quit) = 0.3.

Subjective loss at streak k: lambda * (sum_{j=1}^{k} b*j)^beta = 2.25 * (b*k*(k+1)/2)^0.88

For b = 5: loss at k = 14: 2.25 * (5*14*15/2)^0.88 = 2.25 * (525)^0.88 = 2.25 * 308 = 693. This exceeds 150 at k around 5-6. Users experience streak anxiety early.

For b = 1: loss at k = 14: 2.25 * (1*14*15/2)^0.88 = 2.25 * (105)^0.88 = 2.25 * 72.6 = 163. Just over threshold. Users can build longer streaks before anxiety kicks in.

For b = 2: loss at k = 14: 2.25 * (2*14*15/2)^0.88 = 2.25 * (210)^0.88 = 2.25 * 136 = 306. Threshold crossed around k = 9.

**Optimal b:** We want the anxiety threshold to be hit around k = 21 (3 weeks, when the habit is already formed and retention is high). Setting 2.25 * (b*21*22/2)^0.88 = 150:

```
(b * 231)^0.88 = 66.7
b * 231 = 66.7^(1/0.88) = 66.7^1.136 = 102.5
b = 0.44
```

So a streak bonus of about 0.5 XP per streak day keeps the anxiety threshold at 3 weeks, allowing habits to form before loss aversion becomes counterproductive. This is much lower than the typical "generous" streak bonus of 5-10 XP — a quantitative argument for restrained streak rewards.

## Arena Connection

XP economics is central to Arena optimization:

**Level distribution entropy** is one of Arena's 6 measured metrics. An agent that inflates XP (high scanXp, high feedbackXp, no cap) will see users cluster at high levels, reducing entropy. An agent that deflates XP will see users stuck at low levels, also reducing entropy. The optimal configuration produces a spread distribution.

**XP velocity** tracks how fast users accumulate XP. Rapid velocity means fast level-ups but also rapid inflation. Workshop Lesson 5 (Multi-Objective) teaches agents to balance XP velocity against other metrics.

**Streak retention** is directly measured. The streak bonus parameter controls the strength of the streak incentive. The worked example above suggests that smaller streak bonuses may produce better long-term retention by avoiding streak anxiety — a non-obvious insight that an agent must learn.

**Currency sinks in Arena:** Arena does not have explicit currency sinks, but the level threshold function serves as an implicit sink: the faster users earn XP, the faster they need to earn more. An agent can make the sink "deeper" by choosing steeper level curves (higher k in n^k), but this risks frustrating users.

The meta-lesson: XP economics is not just about setting reward values; it is about designing a self-regulating economic system where supply (XP generation) and demand (XP absorption by the progression system) stay in balance. An Arena agent that understands this will outperform one that simply maximizes XP output.

## Discussion Questions

1. **Compute:** A system uses L(n) = 200*n^1.5 and users earn 120 XP/day on average. Compute the days required to reach each level from 1 to 10. At what level does the time between levels exceed 7 days? If the designer wants no level to take more than 7 days, what is the maximum number of levels the system can support?

2. **Design:** TendedLoop's Scout program uses a 10-level system. Propose a currency sink mechanism that is appropriate for a enterprise context (not a game). The sink should feel natural, not punitive, and should scale with user level. How would you formalize the constraint "feels natural"?

3. **Ethical:** The streak anxiety analysis shows that strong streak bonuses can cause psychological distress. Some jurisdictions have begun regulating "dark patterns" in digital products. Should streak mechanics with loss-aversion properties be classified as dark patterns? What would a formal test look like (beyond subjective judgment)?

4. **Technical:** The XP economy model treats users as independent agents. In reality, leaderboards create strategic interactions: one user's XP velocity affects another user's rank. How does this social coupling change the inflation analysis? Can two users have different "inflation experiences" in the same economy?

## Further Reading

- Schell, J. (2019). *The Art of Game Design: A Book of Lenses* (3rd ed.), Ch. 12-14. Comprehensive treatment of progression and economy design from a game designer's perspective.
- Castronova, E. (2005). *Synthetic Worlds: The Business and Culture of Online Games*. Pioneering economic analysis of virtual economies — the formal inflation models originate here.
- Hamari, J. (2017). "Do Badges Increase User Activity? A Field Experiment on the Effects of Gamification." *Computers in Human Behavior*. Empirical evidence on badge effects with a formal analysis of the "novelty vs. sustained" engagement debate.
