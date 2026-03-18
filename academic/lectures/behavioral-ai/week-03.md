# Week 3: Flow, Engagement, and Dynamic Difficulty

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture treats Csikszentmihalyi's Flow state as a formal optimization target for gamification systems. We model engagement as a function of the mismatch between challenge and skill, derive the conditions for maximal engagement (the "flow channel"), and show how Dynamic Difficulty Adjustment (DDA) can be framed as a PID control problem. The central engineering question becomes: how do we continuously adjust challenge to keep users in the flow channel as their skill evolves?

## Key Concepts

### Flow as an Optimization Target

Csikszentmihalyi (1990) identified Flow as a state of complete absorption in an activity, characterized by loss of self-consciousness, distortion of time perception, and intrinsic enjoyment. The psychological conditions for Flow are:

1. Clear goals
2. Immediate feedback
3. Balance between challenge and skill

Condition 3 is the one we can formalize and optimize. Let s(t) be a user's skill level at time t and d(t) be the difficulty (challenge level) of the task at time t. Flow occurs when:

```
|d(t) - s(t)| < epsilon
```

where epsilon is the "flow channel width." If d(t) >> s(t), the user experiences anxiety. If d(t) << s(t), the user experiences boredom. Both states lead to disengagement.

### The Engagement Surface

Engagement can be modeled as a function of two variables: challenge and skill. The canonical model is a 2D Gaussian centered on the diagonal d = s:

```
E(d, s) = E_max * exp(-(d - s)^2 / (2 * sigma^2))
```

where E_max is peak engagement (Flow state) and sigma controls the width of the flow channel. This produces the classic "flow channel" — a diagonal band in the challenge-skill space where engagement is high.

**Properties:**
- E(d, s) is maximized when d = s (perfect challenge-skill balance)
- E decreases symmetrically for both d > s (anxiety zone) and d < s (boredom zone)
- The flow channel width (2*sigma) varies by individual and task type

A more nuanced model uses an *asymmetric* Gaussian, since anxiety (d >> s) typically causes faster disengagement than boredom (d << s):

```
E(d, s) = E_max * exp(-(d - s)^2 / (2 * sigma_left^2))   if d < s  (boredom side)
         = E_max * exp(-(d - s)^2 / (2 * sigma_right^2))  if d >= s (anxiety side)
```

with sigma_left > sigma_right (users tolerate mild boredom longer than mild frustration).

### Skill Dynamics

Skill evolves over time as the user practices. A common model:

```
s(t+1) = s(t) + alpha * (d(t) - s(t))^+  * I[engaged(t)]
```

where alpha is the learning rate, (x)^+ = max(0, x) captures that skill only increases when the challenge exceeds current skill, and I[engaged(t)] is an indicator that the user was active (no learning when disengaged).

This creates a feedback loop: challenge affects engagement, engagement affects whether the user practices, practice affects skill, and skill affects the optimal challenge. The system is coupled and dynamic.

### Dynamic Difficulty Adjustment (DDA)

DDA is the automatic adjustment of challenge to maintain flow. In gamification, "difficulty" maps to task requirements, mission complexity, or the threshold for earning rewards.

The DDA problem: given observations of user behavior (action frequency, completion rate, time-to-complete), adjust d(t) to maintain E(d, s) near E_max.

This is a **control problem.** The plant is the user, the output is engagement (observed via behavioral proxies), the setpoint is E_max, and the control input is the difficulty d(t).

### PID Control for Engagement

A PID controller continuously adjusts challenge based on the engagement error:

```
e(t) = E_target - E_observed(t)
```

The control law:

```
d(t+1) = d(t) + K_p * e(t) + K_i * sum_{k=0}^{t} e(k) + K_d * (e(t) - e(t-1))
```

where:
- **K_p (Proportional):** Immediate response to engagement gap. If engagement is below target, increase difficulty (user may be bored) or decrease it (user may be frustrated). The sign depends on which side of the flow channel the user is on.
- **K_i (Integral):** Corrects for persistent engagement deficit. If engagement has been below target for many periods, the accumulated error drives a larger correction.
- **K_d (Derivative):** Dampens oscillation. If engagement is improving (error decreasing), reduce the correction to avoid overshooting.

**The direction ambiguity problem:** When engagement drops, we don't know if the user is bored (need to increase d) or frustrated (need to decrease d). A pure PID controller on engagement has a sign ambiguity. We resolve this by using additional signals:

- Completion rate > 90%: likely boredom -> increase d
- Completion rate < 50%: likely frustration -> decrease d
- Session length decreasing: frustration signal
- Action speed increasing (rushing): boredom signal

### Engagement Proxies in Non-Game Systems

In games, difficulty is explicit (enemy health, puzzle complexity). In gamification systems like feedback platforms, "difficulty" is more abstract:

| Gamification element | "Challenge" interpretation | "Skill" interpretation |
|---------------------|--------------------------|----------------------|
| Mission requirements | Number of scans required | User's scan habit strength |
| Badge conditions | Completion threshold | Progress toward badge |
| Leaderboard position | Rank to maintain/improve | Activity level relative to peers |
| Streak maintenance | Consecutive days required | Reliability of daily engagement |

DDA in gamification means adjusting these thresholds dynamically. A user who easily completes 3-scan missions should be promoted to 5-scan missions. A user who struggles with daily streaks should receive more achievable targets (2-day streaks before 7-day streaks).

## Formal Models

### Model 1: The Flow Channel as a Region in Parameter Space

Define the flow channel formally. Let phi(u, t) = d(t) - s(u, t) be the challenge-skill gap for user u at time t.

The flow region F is:

```
F = { (d, s) : |d - s| < epsilon }
```

The fraction of a population in flow at time t:

```
FlowRate(t) = (1/|U|) * sum_u I[|phi(u, t)| < epsilon]
```

The DDA objective is to maximize the time-averaged FlowRate:

```
maximize  (1/T) * sum_{t=1}^{T} FlowRate(t)
subject to  d(t) in D  (feasible difficulty set)
            |d(t+1) - d(t)| <= Delta_max  (smoothness constraint)
```

The smoothness constraint prevents jarring difficulty jumps that break immersion.

### Model 2: Inverted-U Engagement Curve

An alternative to the Gaussian engagement model is the inverted-U (Yerkes-Dodson):

```
E(x) = 4 * E_max * x * (1 - x)
```

where x = d/(d + s) in [0, 1] normalizes the challenge-to-skill ratio. Peak engagement occurs at x = 0.5 (d = s). This quadratic model is simpler than the Gaussian and has a clean derivative:

```
dE/dx = 4 * E_max * (1 - 2x)
```

which is positive when x < 0.5 (increasing challenge helps) and negative when x > 0.5 (too much challenge hurts).

### Model 3: PID with Skill Estimation

Since skill s(t) is not directly observable, we must estimate it. A Bayesian skill estimator (similar to Elo or TrueSkill):

```
s_hat(t+1) = s_hat(t) + K * (outcome(t) - P_expected(t))
```

where outcome(t) in {0, 1} is task completion and P_expected(t) = sigmoid(s_hat(t) - d(t)) is the expected completion probability.

The PID controller then uses the estimated skill:

```
phi_hat(t) = d(t) - s_hat(t)
d(t+1) = d(t) + K_p * (phi_target - phi_hat(t))
```

where phi_target is slightly positive (challenge slightly exceeds skill, promoting growth and engagement).

### Model 4: Coupled Flow-Engagement Dynamics

Combining skill evolution, engagement, and difficulty adjustment into a dynamical system:

```
s(t+1) = s(t) + alpha * max(0, d(t) - s(t)) * E(d(t), s(t)) / E_max
d(t+1) = d(t) + K_p * (phi_target - (d(t) - s(t)))
E(t) = E_max * exp(-(d(t) - s(t))^2 / (2*sigma^2))
```

This is a 2D discrete dynamical system in (s, d). The fixed point is at d - s = phi_target with ds/dt = alpha * phi_target. The system converges if K_p is chosen appropriately (standard PID stability analysis applies).

## Worked Examples

### Example 1: PID Tuning for Mission Difficulty

A gamification system assigns missions with difficulty levels d in {1, 2, ..., 10}. A user starts with estimated skill s = 3. We observe their completion rate over time and adjust difficulty.

**PID parameters:** K_p = 0.5, K_i = 0.1, K_d = 0.2, phi_target = 0.5

Day 1: d = 3, user completes (outcome=1), P_expected = sigmoid(3-3) = 0.5.
- s_hat update: s_hat = 3 + 0.3*(1 - 0.5) = 3.15
- phi = d - s_hat = 3 - 3.15 = -0.15
- e = phi_target - phi = 0.5 - (-0.15) = 0.65
- d_new = 3 + 0.5*0.65 = 3.33 -> round to d=3

Day 2: d = 3, completes again. s_hat = 3.30, phi = -0.30, e = 0.80.
- d_new = 3 + 0.5*0.80 + 0.1*(0.65+0.80) + 0.2*(0.80-0.65) = 3 + 0.40 + 0.15 + 0.03 = 3.58 -> d=4

Day 3: d = 4, fails (outcome=0). P_expected = sigmoid(3.30 - 4) = 0.33.
- s_hat = 3.30 + 0.3*(0 - 0.33) = 3.20
- phi = 4 - 3.20 = 0.80, e = 0.5 - 0.80 = -0.30
- The negative error signal tells the PID to reduce difficulty.

The controller adapts, keeping the user near the flow channel.

### Example 2: Population-Level Flow Analysis

Model 100 users with skills drawn from N(5, 2^2) and a fixed difficulty d = 5 (no DDA).

```
FlowRate = (1/100) * |{u : |5 - s_u| < 1.5}|
```

For s ~ N(5, 4), P(|s - 5| < 1.5) = P(|Z| < 0.75) = 0.547.

So about 55% of users are in flow at any time with uniform difficulty. The other 45% are either bored (high skill) or frustrated (low skill).

With DDA that adjusts d_u for each user: if d_u = s_u + 0.5 (slight challenge), then FlowRate approaches 100% (all users are in flow with phi = 0.5, well within epsilon = 1.5).

The cost: DDA requires per-user difficulty adjustment, which means personalized missions/tasks rather than one-size-fits-all. This is the engineering tradeoff between population-level simplicity and individual-level optimization.

### Example 3: Stability Analysis of the Coupled System

Consider the linearized dynamics near the fixed point (s*, d*) where d* - s* = phi_target:

```
Delta_s(t+1) = (1 - alpha*E/E_max) * Delta_s(t) - alpha*E/E_max * Delta_d(t)  (approx.)
Delta_d(t+1) = K_p * Delta_s(t) + (1 - K_p) * Delta_d(t)
```

The Jacobian matrix J has eigenvalues that determine stability. For the system to converge to the flow channel without oscillation, we need |lambda_i| < 1 for all eigenvalues of J.

For K_p = 0.3 and alpha = 0.1, the eigenvalues are approximately 0.85 and 0.75 (both < 1), so the system is stable. For K_p = 1.5 (aggressive correction), eigenvalues can exceed 1, causing oscillation between too-easy and too-hard difficulty — a poor user experience.

**Design rule:** K_p should be less than 2/(1 + alpha) for stability. Overly aggressive PID tuning creates difficulty whiplash.

## Arena Connection

Arena's Workshop Lesson 4 introduces PID control for engagement targets. The specific connection:

**Arena metrics as engagement proxies:**
- scans/user/day maps to action rate (boredom signal if rising sharply without quality)
- feedback rate maps to task completion quality (frustration signal if dropping)
- streak retention maps to consistency (flow indicator if stable)

**Arena parameters as difficulty levers:**
- dailyXpCap: lower cap = harder to earn maximum XP = higher effective difficulty
- missionRewardXp: mission difficulty inversely proportional to XP reward per effort
- levelThresholds: steeper thresholds = harder progression = higher challenge

An Arena agent implementing DDA would:
1. Observe engagement metrics each tick
2. Estimate population skill level (from level distribution and XP velocity)
3. Compute the engagement error (actual vs. target)
4. Adjust parameters using a PID control law
5. Clamp adjustments to satisfy safety constraints (delta limits)

The PID controller in Lesson 4 does exactly this. The coefficients K_p, K_i, K_d become hyperparameters of the agent itself, forming a meta-optimization problem: what PID gains produce the best long-term engagement?

## Discussion Questions

1. **Compute:** A user has skill s = 7 and the engagement function is E(d, s) = 10 * exp(-(d-s)^2 / 8). The system uses a PID controller with K_p = 0.4, K_i = 0, K_d = 0, and phi_target = 1.0. If the current difficulty is d = 5, trace the system for 5 time steps. Does the system converge to the flow channel? How many steps does it take?

2. **Design:** In a facility feedback gamification system, what constitutes "difficulty"? Propose three difficulty dimensions that could be adjusted dynamically, and explain how you would measure each user's "skill" along that dimension using only behavioral data (no self-reports).

3. **Ethical:** DDA in games is generally considered benign (keep users entertained). DDA in gamification systems that drive real-world behavior (workplace feedback, health compliance) is more complex. If a system adjusts task difficulty to maximize engagement, is it manipulating employees? Where is the line between "helpful adaptation" and "dark pattern"?

4. **Technical:** The sign ambiguity problem (engagement drops — is it boredom or frustration?) is a fundamental limitation of scalar engagement signals. Propose a method using multiple behavioral signals to disambiguate the two states. What minimum set of signals would you need?

## Further Reading

- Hunicke, R. (2005). "The Case for Dynamic Difficulty Adjustment in Games." *ACM SIGCHI*. The foundational paper on DDA with a control-theoretic perspective.
- Lomas, J.D., et al. (2017). "Is Difficulty Overrated? The Effects of Choice, Novelty, and Suspense on Intrinsic Motivation in Educational Games." *CHI*. Challenges the simple difficulty-engagement model by showing that choice and novelty may matter more.
- Meder, B., et al. (2021). "Information-Theoretic Approaches to Difficulty Adjustment." *Frontiers in Psychology*. Uses information theory to formalize the concept of optimal difficulty, connecting to Bayesian models of learning.
