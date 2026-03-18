# Week 5: Parameterized Reward Systems

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture formalizes the Points-Badges-Leaderboards (PBL) framework as a parameterized reward system and shows why PBL alone is insufficient. We define the configuration vector theta, the objective function J(theta), and the constraint space that bounds feasible configurations. The key shift from Weeks 1-4 is from understanding *why* gamification works (behavioral foundations) to engineering *how* to tune it (parameterized systems). This is where the course becomes explicitly computational: given a parameterized reward system, how do we search the configuration space for optimal parameters?

## Key Concepts

### The PBL Framework Formalized

Points, Badges, and Leaderboards are the three most common gamification mechanics. Each can be formalized as a distinct reward signal:

**Points (XP):** A scalar accumulator that maps actions to numerical rewards.

```
XP(t) = XP(t-1) + sum_{a in actions(t)} R(a, theta)
```

where R(a, theta) is the reward function parameterized by theta. Points are the primary extrinsic signal. They are fungible (interchangeable), accumulable, and comparable. Their psychological effect is through operant conditioning (Week 6) and competence signaling (Week 2).

**Badges:** Predicate-triggered discrete rewards. A badge B_j is earned when condition C_j(state) becomes true:

```
earned(B_j, t) = I[C_j(state(t)) = true AND NOT earned(B_j, t-1)]
```

Badges differ from points in three important ways:
1. They are *non-fungible* (each badge is unique)
2. They are *one-time* (earning is irreversible)
3. Their value comes from *signaling* (display to self and others), not accumulation

Formally, badge conditions C_j define a set of achievement thresholds in the state space. The badge set B = {B_1, ..., B_m} partitions the achievement space into regions.

**Leaderboards:** Ordinal ranking functions over users.

```
rank(u, t) = |{u' in U : score(u', t) > score(u, t)}| + 1
```

Leaderboards convert absolute performance (XP) into relative position (rank). Their psychological effect operates through social comparison (Festinger, 1954 — covered in Week 8) and competition. Key design parameters include scope (global vs. local), reset period (weekly vs. monthly vs. never), and visibility (opt-in vs. default).

### Why PBL is Necessary but Not Sufficient

The "PBL critique" (Werbach, 2012; Bogost, 2011) argues that simply adding points, badges, and leaderboards to a system is shallow gamification — "chocolate-covered broccoli." The critique is valid but imprecise. We can formalize it:

PBL provides three reward signals. But engagement is a function of many more variables:

```
engagement = f(PBL_signals, autonomy, challenge_balance, social_connection,
               narrative, feedback_quality, progression_visibility, ...)
```

PBL addresses only the first argument. A system with optimal PBL parameters but no autonomy (mandatory participation), poor challenge balance (same difficulty for all users), and no social features will still fail.

The formal version: PBL spans a subspace of the full gamification design space. Optimizing within the PBL subspace finds a local optimum that may be far from the global optimum in the full space. However, PBL parameters are the most *tunable* (continuous, measurable, easy to A/B test), which is why they are the focus of automated optimization.

### The Configuration Vector

For a system like TendedLoop's Scout program, the tunable parameters form a vector:

```
theta = (theta_1, theta_2, ..., theta_d) in Theta subset of R^d
```

Arena defines d = 10 parameters:

| Index | Parameter | Type | Range | Behavioral effect |
|-------|-----------|------|-------|-------------------|
| 1 | scanXp | Continuous | [1, 100] | Base action reward |
| 2 | feedbackXp | Continuous | [1, 100] | Quality action reward |
| 3 | streakBonus | Continuous | [0, 50] | Consistency incentive |
| 4 | dailyXpCap | Discrete | [50, 1000] | Effort ceiling |
| 5 | levelThresholds | Function | O(n^k), k in [1, 3] | Progression curve |
| 6 | missionRewardXp | Continuous | [5, 200] | Goal-directed reward |
| 7 | badgeXp | Continuous | [0, 100] | Achievement reward |
| 8 | referralXp | Continuous | [0, 500] | Growth incentive |
| 9 | leaderboardScope | Categorical | {building, tenant, global} | Competition scope |
| 10 | capWindow | Categorical | {daily, weekly} | Cap reset period |

Not all parameters are continuously tunable. Some are categorical (leaderboardScope), some are functional (levelThresholds), and some have complex interactions (feedbackXp is only meaningful if feedback is enabled). The configuration space Theta is a mixed-type space, which complicates optimization.

### The Objective Function

The central optimization problem from Week 1, now made concrete:

```
J(theta) = sum_{i=1}^{6} w_i * M_i(theta, U, T)
```

where M_i are the six Arena metrics:
- M_1: scans per user per day (activity volume)
- M_2: feedback rate (quality signal)
- M_3: streak retention (consistency)
- M_4: XP velocity (progression speed)
- M_5: level distribution entropy (fairness/spread)
- M_6: churn rate (retention)

The weights w_i encode the designer's priorities. Different weight vectors produce different optimal configurations:

| Priority | w_1 | w_2 | w_3 | w_4 | w_5 | w_6 | Effect |
|----------|-----|-----|-----|-----|-----|-----|--------|
| Volume-first | 0.4 | 0.1 | 0.1 | 0.2 | 0.1 | 0.1 | Max scans (may sacrifice quality) |
| Quality-first | 0.1 | 0.4 | 0.1 | 0.1 | 0.1 | 0.2 | Max feedback (may reduce volume) |
| Retention-first | 0.1 | 0.1 | 0.3 | 0.1 | 0.1 | 0.3 | Min churn (may reduce peak engagement) |
| Balanced | 0.17 | 0.17 | 0.17 | 0.17 | 0.16 | 0.16 | Pareto-seeking (no single metric dominates) |

### The Constraint Space

Not all configurations are valid. Constraints arise from:

**Budget constraints:** Total XP awarded per period must be bounded to prevent inflation.

```
E[XP_awarded(theta, U, 1 day)] <= B
```

This expands to:
```
|U| * E[scans/user] * scanXp + |U| * E[feedbacks/user] * feedbackXp + ... <= B
```

**Fairness constraints:** The reward system should not systematically favor one user subgroup.

```
Var_{groups}[E[XP(theta) | group]] <= epsilon_fair
```

**Inflation constraints:** XP velocity should not exceed the progression system's capacity to absorb it.

```
XP_velocity(theta) <= C * levelGap_mean
```

where levelGap_mean is the mean XP gap between consecutive levels.

**Parameter coupling constraints:** Some parameters are not independent.

```
scanXp <= dailyXpCap  (otherwise a single scan hits the cap)
missionRewardXp >= scanXp  (missions should feel more rewarding than individual scans)
```

**Safety constraints (from Week 11 preview):**

```
|theta(t+1) - theta(t)| <= Delta_max  (delta clamping)
theta in [theta_min, theta_max]  (parameter bounds)
```

## Formal Models

### Model 1: Configuration Space Geometry

The feasible configuration space Theta_F is the intersection of all constraint sets:

```
Theta_F = Theta_budget intersect Theta_fair intersect Theta_inflate intersect Theta_couple intersect Theta_safe
```

Each constraint defines a region in R^d. The feasible set is their intersection, which may be non-convex (especially when coupling constraints involve nonlinear relationships).

The optimization problem is:

```
theta* = argmax_{theta in Theta_F} J(theta)
```

Because J is evaluated through simulation or real experiments (not a closed-form function), this is a **black-box optimization** problem. Standard approaches include:

1. **Grid search:** Evaluate J at a grid of points in Theta_F. Cost: O(n^d), where n is grid resolution and d = 10. Infeasible for d = 10.
2. **Random search:** Sample theta uniformly from Theta_F. Better than grid search in high dimensions (Bergstra & Bengio, 2012).
3. **Bayesian optimization:** Build a surrogate model (Gaussian process) of J(theta) and use acquisition functions to select the next theta to evaluate. Efficient for expensive-to-evaluate functions.
4. **Evolutionary strategies:** Population-based search that evolves theta toward high-J regions. CMA-ES is particularly effective for d = 10-50.
5. **Bandit methods:** Treat each configuration as an arm. Use UCB or Thompson sampling to allocate evaluation budget.

### Model 2: Multi-Objective Pareto Frontier

When multiple metrics matter and no single weighting is "correct," we seek the Pareto frontier:

```
theta is Pareto-optimal if there is no theta' such that
  M_i(theta') >= M_i(theta) for all i, and
  M_j(theta') > M_j(theta) for some j
```

The Pareto frontier in metric space is the set of all non-dominated configurations. The designer then selects from the frontier based on preferences.

For two metrics (activity and retention), the frontier is a curve in R^2. Typical shape: increasing activity past a threshold decreases retention (users burn out), creating a concave frontier.

### Model 3: Sensitivity Analysis

How sensitive is J to each parameter? The sensitivity index:

```
S_j = Var_{theta_j}[E_{theta_{-j}}[J(theta)]] / Var[J(theta)]
```

This is the Sobol sensitivity index. S_j measures the fraction of J's variance attributable to parameter theta_j alone. Parameters with high S_j are "leverage points" — small changes produce large engagement changes.

In a typical gamification system:
- dailyXpCap has high sensitivity (it bounds everything)
- leaderboardScope has low sensitivity (affects only competitive users)
- streakBonus has moderate sensitivity but high interaction effects (its impact depends on scanXp and dailyXpCap)

Total-order sensitivity (including interactions) is:

```
S_T_j = 1 - Var_{theta_{-j}}[E_{theta_j}[J(theta)]] / Var[J(theta)]
```

When S_T_j >> S_j, parameter j has strong interactions with other parameters.

## Worked Examples

### Example 1: Computing the Inflation Constraint

A system has 500 active users with average 4 scans/day and 60% feedback rate. Current config: scanXp = 10, feedbackXp = 15, streakBonus = 5 (average streak length 4 days), dailyXpCap = 100.

**Daily XP awarded (expected):**
```
XP_scan = 500 * 4 * 10 = 20,000
XP_feedback = 500 * 4 * 0.6 * 15 = 18,000
XP_streak = 500 * 5 * 4 = 10,000  (rough: 5 XP * avg streak of 4)
XP_total = 48,000 XP/day (before cap)
```

**Per-user before cap:** 48,000/500 = 96 XP/user/day. Since dailyXpCap = 100, most users are under the cap. But power users (8+ scans/day) would be capped.

**Level thresholds:** L(n) = 100 * n^1.5 for level n. The gap between levels:
```
L(2) - L(1) = 100*(2^1.5 - 1) = 100*(2.83 - 1) = 183
L(5) - L(4) = 100*(5^1.5 - 4^1.5) = 100*(11.18 - 8.0) = 318
L(10) - L(9) = 100*(31.62 - 27.0) = 462
```

**Inflation rate:** Average user earns ~96 XP/day. Level gaps grow from 183 (level 2) to 462 (level 10). Time to level up: 183/96 = 1.9 days (level 2), 462/96 = 4.8 days (level 10).

If this is too fast (users reaching max level in < 30 days), we have inflation. Solutions: increase level thresholds, reduce scanXp, or lower dailyXpCap.

### Example 2: Grid Search in 2D Subspace

Fix 8 of 10 parameters at their current values. Vary scanXp in {5, 10, 15, 20, 25} and dailyXpCap in {50, 75, 100, 150, 200}. Evaluate J(theta) for each of the 25 combinations (via simulation or A/B testing).

Results (hypothetical engagement score 0-100):

| | Cap=50 | Cap=75 | Cap=100 | Cap=150 | Cap=200 |
|---|--------|--------|---------|---------|---------|
| XP=5 | 42 | 48 | 50 | 51 | 51 |
| XP=10 | 55 | 63 | 68 | 70 | 70 |
| XP=15 | 58 | 67 | **73** | 72 | 71 |
| XP=20 | 54 | 64 | 71 | 69 | 66 |
| XP=25 | 48 | 58 | 65 | 62 | 58 |

The optimum is at (scanXp=15, dailyXpCap=100) with J=73. Note:
- Too-low XP (5) produces low engagement (insufficient extrinsic motivation)
- Too-high XP (25) also reduces engagement (XP inflation, reduced scarcity)
- Cap too low (50) frustrates power users; cap too high (200) removes scarcity
- The interaction: higher XP values make caps more binding, shifting the optimal cap upward

### Example 3: Bayesian Optimization Step

After 10 random evaluations of J(theta), we have a Gaussian process posterior. The GP predicts:

```
J_hat(theta) = mu(theta),  uncertainty = sigma(theta)
```

The UCB acquisition function selects the next point:

```
theta_next = argmax_{theta in Theta_F} [mu(theta) + kappa * sigma(theta)]
```

where kappa balances exploration (high uncertainty) vs. exploitation (high predicted engagement).

Suppose the GP posterior at two candidate points:
- Point A: mu = 70, sigma = 5 (near observed optimum, well-explored)
- Point B: mu = 60, sigma = 15 (unexplored region)

With kappa = 2: UCB(A) = 70 + 2*5 = 80, UCB(B) = 60 + 2*15 = 90.

The optimizer selects Point B — exploring the uncertain region. If B turns out to have J = 75, the GP updates and the next iteration may exploit near B. If B has J = 45, the GP learns to avoid that region.

This is the explore-exploit tradeoff applied to gamification parameter tuning. Each "evaluation" requires running an experiment (days or weeks), so sample efficiency matters enormously.

## Arena Connection

This week's content maps directly to the Arena platform:

**The 10 parameters** defined in this lecture are the Arena's exact configuration vector. Workshop Lesson 2 introduces each parameter, its range, and its behavioral interpretation.

**The objective function** J(theta) is computed from Arena's 6 metrics. The agent's job is to find theta* that maximizes J. Different weight vectors produce different agent strategies.

**Constraints** in Arena are enforced by the platform: parameter bounds, delta clamping (maximum per-tick change), and inflation limits. An agent that proposes a configuration violating constraints receives an error, and the previous configuration remains in effect.

**Search strategy:** The examples above (grid search, Bayesian optimization) are strategies an Arena agent might use. Grid search is wasteful (each tick is one evaluation opportunity, and experiments run for limited ticks). Bayesian optimization is more sample-efficient but requires the agent to maintain a model of J(theta). Workshop Lesson 5 introduces multi-objective optimization, where the agent must balance competing metrics.

The key insight for Arena agents: the configuration space is small enough (d = 10) that Bayesian optimization or evolutionary strategies can find good configurations within a few dozen evaluations, but each evaluation takes an entire experiment tick — so wasting evaluations on uninformative configurations is costly.

## Discussion Questions

1. **Compute:** Given a system with 3 parameters (scanXp in [5, 50], feedbackXp in [5, 50], dailyXpCap in [50, 500]) and the inflation constraint E[XP/user/day] <= 120, derive the feasible region Theta_F. If users average 5 scans/day with 50% feedback rate, which (scanXp, feedbackXp) pairs are feasible for dailyXpCap = 100?

2. **Design:** The PBL critique says "just adding points, badges, and leaderboards" is insufficient. But Arena only lets agents tune PBL-adjacent parameters. What gamification mechanics lie *outside* the Arena's parameter space? How would you extend the parameter vector to capture autonomy-supporting or relatedness-building mechanics?

3. **Ethical:** Sensitivity analysis reveals that dailyXpCap is the highest-leverage parameter. An aggressive agent might remove the cap entirely to maximize short-term engagement. Why is this a bad long-term strategy? Connect your answer to both XP inflation (this week) and the crowding-out effect (Week 2).

4. **Technical:** Bayesian optimization assumes the objective function J(theta) is smooth (modeled by a GP with a smooth kernel). Is this assumption valid for gamification? What would cause J to be discontinuous or multi-modal in theta-space?

## Further Reading

- Bergstra, J. & Bengio, Y. (2012). "Random Search for Hyper-Parameter Optimization." *JMLR*. Shows random search is more efficient than grid search in high dimensions — directly applicable to gamification parameter search.
- Snoek, J., Larochelle, H., & Adams, R.P. (2012). "Practical Bayesian Optimization of Machine Learning Hyperparameters." *NeurIPS*. The foundational paper on GP-based Bayesian optimization for expensive-to-evaluate functions.
- Bogost, I. (2011). "Gamification is Bullshit." *The Atlantic*. The strongest version of the PBL critique — important to understand what purely parametric gamification cannot achieve.
