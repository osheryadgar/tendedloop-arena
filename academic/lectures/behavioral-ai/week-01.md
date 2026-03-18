# Week 1: Gamification as an Optimization Problem

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture establishes gamification as a computational optimization problem rather than a design exercise. We define the formal framework that the rest of the course builds upon: users are agents in a parameterized incentive environment, game mechanics are tunable variables, engagement is the objective function, and the designer's job is to find the configuration that maximizes engagement subject to constraints. By the end of this lecture, students should be able to write down a gamification system as an optimization problem.

## Key Concepts

### Gamification: A Computational Definition

The standard definition from Deterding et al. (2011) frames gamification as "the use of game design elements in non-game contexts." This is a design definition. We need a computational one.

**Computational definition:** Gamification is the design of a parameterized incentive environment E(theta) that maps user actions to reward signals, with the goal of maximizing a measurable engagement objective over a user population and time horizon.

The key shift is from "apply game elements" (a design heuristic) to "optimize reward parameters" (an engineering problem). This reframing opens the door to algorithms, measurement, and formal analysis.

### Users as Agents in an Incentive Environment

We borrow from the MDP formalism. A gamified system can be described as a tuple (S, A, T, R_theta):

- **S** = user state space (XP, level, streak count, badges earned, days active)
- **A** = action space (perform an action (scan, submit feedback, complete a task), refer a friend, log in)
- **T**: S x A -> S = state transition function (deterministic in most gamification systems)
- **R_theta**: S x A -> R = reward function parameterized by theta

The parameter vector theta contains the tunable knobs of the system. For a system like TendedLoop's Scout program, theta includes (scanXp, feedbackXp, streakBonus, dailyXpCap, levelThresholds, ...).

Unlike classical RL where the agent learns to maximize reward, here the *users* are the agents and the *designer* (or an AI) tunes R_theta to maximize a population-level objective.

### Parameterized Reward Systems

Every common game mechanic maps to a parameter:

| Mechanic | Parameter(s) | Type |
|----------|-------------|------|
| Points (XP) | Base XP per action | Continuous, R+ |
| Streaks | Bonus multiplier, reset penalty | Continuous |
| Levels | Threshold function L(n) | Function space |
| Daily caps | Max XP per day | Discrete, N |
| Badges | Unlock conditions | Predicate set |
| Leaderboards | Scope, reset period | Categorical |

The parameter vector theta lives in a configuration space Theta. Not all configurations are valid (e.g., dailyXpCap must exceed scanXp), so we have a feasible set Theta_F subset of Theta.

### The Optimization Framing

The central problem of computational gamification:

```
maximize    J(theta) = E[engagement(theta, U, T)]
subject to  theta in Theta_F
            cost(theta) <= B
            fairness(theta) >= f_min
```

where:
- J(theta) is the expected engagement over user population U and time horizon T
- Theta_F is the feasible parameter space
- B is a budget constraint (cost of rewards, XP inflation limits)
- f_min is a minimum fairness threshold (no subgroup should be systematically disadvantaged)

This is a stochastic optimization problem because user behavior is noisy and heterogeneous. The engagement function is typically not differentiable (users make discrete decisions), and evaluation requires simulation or real-world experimentation.

### Engagement as a Measurable Signal

Engagement is not a feeling; it is a measurable behavioral signal. We define engagement operationally through proxy metrics:

- **Activity rate**: actions per user per day (DAU actions)
- **Retention**: P(user active on day d | active on day 0)
- **Depth**: average actions per session
- **Consistency**: coefficient of variation of inter-action intervals
- **Quality**: fraction of actions that produce useful output (e.g., feedback with comments)
- **Growth**: new user acquisition rate (viral coefficient)

A composite engagement score combines these:

```
J(theta) = sum_i w_i * metric_i(theta)
```

where weights w_i reflect the designer's priorities. This is a multi-objective optimization problem, and different weight vectors produce different optimal configurations.

## Formal Models

### The Engagement Function

Let theta in R^d be the parameter vector with d tunable parameters. Let u in U be a user with type tau(u) drawn from a distribution over user types. Let t in {1, ..., T} be the time step (day).

The engagement of user u at time t under configuration theta is:

```
e(u, t, theta) = P(a(u,t) > 0 | theta) * E[q(a(u,t)) | a(u,t) > 0, theta]
```

where a(u,t) is the action count and q(.) is a quality function. The first term captures whether the user is active; the second captures how engaged they are when active.

Population engagement:

```
J(theta) = (1/|U|) * sum_{u in U} sum_{t=1}^{T} gamma^t * e(u, t, theta)
```

where gamma in (0, 1] is a discount factor reflecting the designer's time preference (do we care more about short-term activation or long-term retention?).

### Parameter Sensitivity

The gradient of engagement with respect to parameter theta_j:

```
dJ/d(theta_j) = (1/|U|) * sum_u sum_t gamma^t * de(u,t,theta)/d(theta_j)
```

In practice, this gradient is estimated empirically via A/B testing: perturb theta_j, measure the change in J, estimate the partial derivative. This is finite-difference optimization, and it is expensive (each evaluation requires running a real experiment).

### Constraint Formalization

**XP inflation constraint:** Total XP awarded per day should not exceed the system's capacity to absorb it:

```
E[XP_awarded(theta, U, 1 day)] <= C_inflate * sum_n (L(n+1) - L(n))
```

where L(n) is the XP threshold for level n and C_inflate is an inflation tolerance.

**Fairness constraint (demographic parity):** For user subgroups G_1, G_2:

```
|E[e(u, T, theta) | u in G_1] - E[e(u, T, theta) | u in G_2]| <= epsilon
```

This ensures no subgroup is systematically less engaged due to parameter choices (e.g., a daily cap that punishes high-frequency users from a particular demographic).

## Worked Examples

### Example 1: Two-Parameter Optimization

Consider a simple system with two parameters: scanXp (XP per primary action) and dailyCap (max XP per day). Users have heterogeneous scan rates drawn from Poisson(lambda) where lambda varies by user type.

**Setup:**
- Casual users: lambda = 2 scans/day
- Regular users: lambda = 5 scans/day
- Power users: lambda = 12 scans/day
- Population: 40% casual, 45% regular, 15% power

**Engagement model:** A user is "engaged" on day t if their earned XP exceeds their effort cost. Earned XP = min(scans * scanXp, dailyCap).

If scanXp = 10 and dailyCap = 80:
- Casual: E[XP] = min(2 * 10, 80) = 20
- Regular: E[XP] = min(5 * 10, 80) = 50
- Power: E[XP] = min(12 * 10, 80) = 80 (capped, losing 40 XP)

The cap constrains power users but doesn't affect casuals. If power users perceive unfairness (effort not rewarded), their retention drops. If there is no cap, XP inflation accelerates.

**Optimization:** Find (scanXp, dailyCap) that maximizes weighted retention across all groups subject to inflation rate <= 5% per week.

### Example 2: Engagement Time Series

Model a population of 100 users over 30 days under two configurations:

**Config A:** scanXp=10, streakBonus=0 (no streaks)
**Config B:** scanXp=8, streakBonus=5*streak_day (growing streak bonus)

Under Config A, daily engagement is i.i.d. with P(active) = 0.6 for each user each day. Under Config B, P(active on day t) depends on streak length:

```
P(active | streak=k) = 0.5 + 0.05 * min(k, 7)
```

So a 7-day streak raises P(active) from 0.5 to 0.85. But if a streak breaks, the user returns to baseline (or below, due to loss aversion — covered in Week 4).

After 30 days, Config B produces higher mean engagement (0.72 vs 0.60) but also higher variance and a bimodal distribution: users either maintain long streaks (high engagement) or repeatedly break streaks and churn. This tradeoff between mean engagement and engagement inequality is central to the course.

### Example 3: Mapping a Real System

Take Duolingo's XP system and map it to our framework:

- theta = (lessonXp=10, hardLessonXp=20, streakBonus=2x, dailyGoal={10,20,30,50}, leagueReset=weekly)
- S = (totalXp, streak, league, gems, hearts)
- A = (completeLesson, practiceSkill, doStory, useStreak freeze)
- Objective (inferred): maximize DAU/MAU ratio subject to lesson completion quality

This reverse-engineering exercise is a preview of Assignment 5 (Week 13).

## Arena Connection

TendedLoop Arena provides a concrete instance of this optimization framework. The Arena defines exactly 10 tunable parameters:

```
theta = (scanXp, feedbackXp, streakBonus, dailyXpCap,
         levelThresholds, missionRewardXp, badgeXp,
         referralXp, leaderboardScope, capWindow)
```

The 6 measured metrics (scans/user/day, feedback rate, streak retention, XP velocity, level distribution, churn rate) define the engagement signal J(theta). Workshop Lessons 1-2 introduce the platform and parameter space.

The key insight: Arena lets you run *real* optimization. Instead of simulating engagement, you deploy a configuration, observe real (simulated) users, and update. This is the loop that the course builds toward: formal model -> parameter selection -> deployment -> measurement -> update.

## Discussion Questions

1. **Formal:** Write down the optimization problem for a university course gamification system (attendance XP, quiz badges, leaderboard). What are the parameters, constraints, and objective? What makes this harder than a single-metric optimization?

2. **Design:** The engagement function J(theta) treats all users equally (average over population). Propose a modification that prioritizes retaining users who are about to churn. How does this change the optimal theta?

3. **Ethical:** If an AI agent optimizes theta to maximize DAU/MAU, it might discover that loss aversion mechanics (punishing streak breaks) are highly effective. Should there be constraints on *which* psychological mechanisms the optimizer can exploit? How would you formalize such constraints?

4. **Technical:** Why can't we simply use gradient descent on J(theta)? List three properties of the engagement function that make this a hard optimization problem.

## Further Reading

- Hamari, J., Koivisto, J., & Sarsa, H. (2014). "Does Gamification Work? -- A Literature Review of Empirical Studies on Gamification." *HICSS*. Meta-analysis covering 24 empirical studies.
- Liu, D., Santhanam, R., & Webster, J. (2017). "Toward Meaningful Engagement: A Framework for Design and Research of Gamified Information Systems." *MIS Quarterly*. Bridges IS theory and gamification.
- Seaborn, K. & Fels, D.I. (2015). "Gamification in Theory and Action: A Survey." *IJHCS*. Comprehensive taxonomy of game elements and outcomes.
