# Week 2: Motivation Theory for Reward Function Design

> Behavioral AI: Computational Gamification & Engagement

## Overview

This lecture formalizes motivation theory as a foundation for reward function design. Self-Determination Theory (SDT) provides the psychological framework; we translate it into a utility model where intrinsic and extrinsic motivation interact, sometimes synergistically and sometimes destructively. The central result is the crowding-out effect: there exists a critical reward level beyond which adding extrinsic incentives *decreases* total motivation. Understanding this boundary is essential for anyone designing or optimizing reward systems.

## Key Concepts

### Self-Determination Theory as a Utility Model

Ryan and Deci (2000) identify three innate psychological needs that drive intrinsic motivation:

- **Autonomy:** The need to feel volitional, that one's actions are self-endorsed
- **Competence:** The need to feel effective, to master challenges
- **Relatedness:** The need to feel connected to others

In SDT, intrinsic motivation is highest when all three needs are satisfied. We formalize this as a utility function over the three need-satisfaction levels:

```
U_intrinsic(a, c, r) = a^alpha * c^beta * r^gamma
```

where a, c, r in [0, 1] represent autonomy, competence, and relatedness satisfaction respectively, and alpha, beta, gamma > 0 are elasticity parameters. The Cobb-Douglas form captures the key SDT insight: the needs are *complementary*, not substitutable. If autonomy drops to zero, intrinsic motivation collapses regardless of competence or relatedness.

**Alternative formulation (additive with minimum):**

```
U_intrinsic = min(a, c, r) * (w_a * a + w_c * c + w_r * r)
```

The min() term enforces the "weakest link" property: a deficiency in any need suppresses the overall utility.

### Intrinsic vs. Extrinsic Motivation: The Combined Utility

Total motivation for a task is a function of both intrinsic and extrinsic components:

```
U_total = w_i(R) * U_intrinsic + w_e(R) * U_extrinsic(R) - cost(effort)
```

where R is the extrinsic reward magnitude and w_i(R), w_e(R) are weight functions that depend on R. The crucial insight is that w_i is *not constant* with respect to R. As extrinsic rewards increase, the weight on intrinsic motivation can decrease.

If w_i and w_e were constant, the problem would be trivial: just increase R. But SDT and decades of empirical evidence show that w_i(R) is a decreasing function of R for certain task types (interesting tasks where intrinsic motivation is already present).

### Cognitive Evaluation Theory (CET)

CET, a sub-theory of SDT, explains *when* external rewards undermine intrinsic motivation:

1. **Informational aspect:** Rewards that signal competence ("you earned this because you did well") *support* intrinsic motivation by satisfying the competence need.

2. **Controlling aspect:** Rewards that feel coercive ("do this to get paid") *undermine* intrinsic motivation by threatening the autonomy need.

The net effect depends on which aspect is more salient. Formally:

```
Delta_a(R) = info(R) - control(R)
```

where info(R) is the competence signal and control(R) is the autonomy threat. When Delta_a < 0, the reward undermines intrinsic motivation.

**Key empirical findings formalized:**
- Expected, tangible, contingent rewards (typical XP systems) tend to be controlling: Delta_a < 0
- Unexpected, verbal rewards tend to be informational: Delta_a > 0
- Performance-contingent rewards are more controlling than completion-contingent ones

### The Overjustification Effect

The overjustification effect occurs when extrinsic rewards cause a person to attribute their behavior to the reward rather than to intrinsic interest. Once the reward is removed, motivation drops *below* the original baseline.

Formally, let U_intrinsic^0 be the baseline intrinsic motivation (no extrinsic reward). After exposure to reward R for duration T, the new intrinsic motivation is:

```
U_intrinsic^post(R, T) = U_intrinsic^0 * exp(-delta * R * T)
```

where delta > 0 is the attribution decay rate. This exponential decay model captures the finding that longer exposure to higher rewards produces deeper intrinsic motivation loss.

The practical implication for gamification: if you introduce XP for an activity users already enjoy, then later remove the XP, engagement may drop below the pre-XP baseline. This is not hypothetical — it is one of the most replicated findings in motivation psychology.

### The Crowding-Out Threshold

Combining the components, we can find the reward level R* where total motivation is maximized:

```
U_total(R) = w_i(R) * U_intrinsic + R - cost
```

where w_i(R) = 1 - sigma * R for a linear crowding model (sigma is the crowding-out coefficient).

Taking the derivative and setting to zero:

```
dU_total/dR = -sigma * U_intrinsic + 1 = 0
R* is the boundary where crowding begins to dominate
```

For the linear model, if sigma * U_intrinsic > 1, then the optimal reward is R* = 0 (don't add extrinsic rewards at all). If sigma * U_intrinsic < 1, there exists a finite optimal R*.

This gives us a decision rule: **measure intrinsic motivation before adding gamification.** If users already find the task inherently engaging, adding XP may hurt.

## Formal Models

### Model 1: Linear Crowding

```
U_total(R) = (1 - sigma * R) * U_i + R - c
```

Parameters:
- U_i: intrinsic utility of the task (measured or estimated)
- sigma: crowding coefficient (how much each unit of reward reduces intrinsic weight)
- c: effort cost

Optimal reward:

```
dU/dR = -sigma * U_i + 1 = 0
=> No interior optimum in the linear model (corner solution)
=> R* = 0 if sigma * U_i > 1 (high intrinsic + high crowding)
=> R* = R_max if sigma * U_i < 1 (low intrinsic or low crowding)
```

The linear model is too simple — it predicts either zero or maximum reward, with nothing in between.

### Model 2: Nonlinear Crowding (Gneezy-Rustichini)

Gneezy and Rustichini (2000) showed that small rewards can be *worse* than no reward. We model this with a non-monotonic total utility:

```
U_total(R) = U_i * exp(-sigma * R) + eta * ln(1 + R) - c
```

The first term is intrinsic utility with exponential crowding. The second term is extrinsic utility with diminishing returns (log). Taking the derivative:

```
dU/dR = -sigma * U_i * exp(-sigma * R) + eta / (1 + R) = 0
```

This has an interior solution when the exponential decay of intrinsic utility is balanced by the marginal gain from extrinsic reward. The solution R* depends on the ratio U_i / eta (intrinsic-to-extrinsic sensitivity).

**Key prediction:** For moderate U_i and sigma, there is a "valley" in U_total: small rewards (R just above 0) produce lower total utility than R = 0. You must offer *enough* reward to compensate for the crowding-out, or offer none at all. This matches Gneezy and Rustichini's empirical finding with Israeli daycare fines.

### Model 3: SDT Need-Satisfaction Dynamics

Model how gamification mechanics affect the three SDT needs over time:

```
a(t+1) = a(t) + delta_a * (choice(t) - control(t))
c(t+1) = c(t) + delta_c * (mastery(t) - frustration(t))
r(t+1) = r(t) + delta_r * (social(t) - isolation(t))
```

where choice(t) is the degree of user autonomy in the gamified interaction, control(t) is the perceived controlling pressure of the reward, mastery(t) is the competence signal from task completion, and so on.

Gamification mechanics affect these dynamics differently:

| Mechanic | Autonomy | Competence | Relatedness |
|----------|----------|------------|-------------|
| Mandatory daily quests | -- | + | 0 |
| Skill badges | 0 | ++ | 0 |
| Leaderboards | 0 | +/- | +/- |
| Free choice of missions | ++ | 0 | 0 |
| Team challenges | - | + | ++ |

A well-designed gamification system maintains positive dynamics across all three needs. An over-optimized system that maximizes short-term engagement through controlling mechanics (mandatory streaks, loss framing) may produce high initial engagement followed by collapse when autonomy reaches zero.

## Worked Examples

### Example 1: Computing the Crowding-Out Threshold

A facility feedback system has users who find the act of reporting issues moderately satisfying (U_i = 3, on a 0-10 scale). The crowding coefficient is estimated at sigma = 0.15 (from a pilot study comparing XP vs. no-XP conditions). Effort cost c = 1.

Using the nonlinear model with eta = 2:

```
U_total(R) = 3 * exp(-0.15R) + 2 * ln(1 + R) - 1
```

Evaluate at key points:
- R = 0: U = 3 * 1 + 0 - 1 = 2.0
- R = 2: U = 3 * 0.74 + 2 * 1.10 - 1 = 2.42
- R = 5: U = 3 * 0.47 + 2 * 1.79 - 1 = 3.00
- R = 10: U = 3 * 0.22 + 2 * 2.40 - 1 = 4.46
- R = 20: U = 3 * 0.05 + 2 * 3.04 - 1 = 5.24
- R = 50: U = 3 * 0.001 + 2 * 3.93 - 1 = 6.86

In this case, there is no valley — the extrinsic gain always outweighs crowding because U_i is moderate and eta is relatively high. But if U_i = 8 (highly intrinsically motivated users):

- R = 0: U = 8 - 1 = 7.0
- R = 2: U = 5.93 + 2.20 - 1 = 7.13
- R = 5: U = 3.78 + 3.58 - 1 = 6.36
- R = 10: U = 1.78 + 4.80 - 1 = 5.58

Now we see the valley: adding R = 5 XP *reduces* total utility from 7.0 to 6.36. The optimal strategy for highly intrinsically motivated users is either no reward (R = 0) or a very large reward (R > 20) that overwhelms the crowding effect.

### Example 2: Simulating a Heterogeneous Population

Simulate 100 users with heterogeneous intrinsic motivation (U_i drawn from Beta(2, 5) scaled to [0, 10]) under three reward policies:

- **No reward:** R = 0 for all users
- **Uniform reward:** R = 10 for all users
- **Adaptive reward:** R = max(0, 15 - 2*U_i) (less reward for more intrinsically motivated users)

For each user, compute U_total using the nonlinear model (sigma = 0.15, eta = 2, c = 1). The adaptive policy recognizes that high-U_i users should receive less extrinsic reward to avoid crowding-out, while low-U_i users need extrinsic motivation to engage at all.

Expected results: The adaptive policy produces the highest mean utility, but requires estimating each user's intrinsic motivation — a non-trivial inference problem (covered in Week 12, Personalization).

### Example 3: Overjustification Simulation

Model 50 users who initially perform a task with U_i = 5 (moderately interesting). Introduce R = 10 XP for 30 days, then remove it. Track U_intrinsic over time:

During reward phase (t = 1 to 30):
```
U_i(t) = 5 * exp(-0.01 * 10 * t) = 5 * exp(-0.1t)
```

At t = 30: U_i = 5 * exp(-3) = 0.25

After reward removal (t > 30):
```
U_total = U_i(30) - c = 0.25 - 1 = -0.75 (user quits)
```

The user's intrinsic motivation has been nearly destroyed. Recovery is slow (if it happens at all). This is why "just remove the gamification" is not a viable exit strategy once users have been exposed to strong extrinsic rewards.

## Arena Connection

Arena's economy parameters interact with motivation dynamics in specific ways:

- **scanXp and feedbackXp** are the primary extrinsic reward signals. Setting these too high for intrinsically motivated populations risks crowding-out.
- **dailyXpCap** can be interpreted through CET: a cap signals "you've done enough" (informational/competence) but also "we're controlling your rewards" (controlling/autonomy). The net effect depends on framing.
- **streakBonus** introduces a loss aversion dynamic (Week 4) that primarily operates through extrinsic motivation channels.
- **Missions** can support autonomy (user chooses which mission) or undermine it (mandatory daily missions). The mission design affects the autonomy parameter a(t).

An agent optimizing Arena parameters should model the intrinsic motivation of the user population. If the simulated population has high baseline engagement (suggesting intrinsic motivation), the agent should avoid dramatically increasing XP values. This is a non-obvious insight: sometimes the optimal move is to *reduce* rewards.

Assignment 1 asks you to formalize this: find the reward level R* that maximizes total engagement for a population with known intrinsic motivation distribution.

## Discussion Questions

1. **Compute:** Given U_i = 6, sigma = 0.2, eta = 1.5, c = 0.5, find the reward level R* that maximizes U_total(R) = U_i * exp(-sigma * R) + eta * ln(1 + R) - c. Does a "valley" (where small rewards are worse than none) exist? At what sigma value does the valley appear?

2. **Design:** You are building a gamification system for hospital hand hygiene compliance. Healthcare workers generally believe hand hygiene is important (moderate-to-high intrinsic motivation). Based on the crowding-out model, should you use XP rewards? If so, what constraints on the reward level would you impose? What alternative gamification mechanics might support intrinsic motivation instead of competing with it?

3. **Ethical:** The overjustification model predicts that removing gamification can leave users *worse off* than if gamification had never been introduced. Does a gamification designer have an ethical obligation to plan for graceful degradation? What would that look like formally?

4. **Technical:** CET predicts that performance-contingent rewards are more controlling than completion-contingent rewards. In Arena, scanXp is completion-contingent (you get XP for scanning) while feedbackXp is performance-contingent (you get XP for providing quality feedback). How should this distinction affect the ratio scanXp/feedbackXp?

## Further Reading

- Deci, E.L., Koestner, R., & Ryan, R.M. (1999). "A Meta-Analytic Review of Experiments Examining the Effects of Extrinsic Rewards on Intrinsic Motivation." *Psychological Bulletin*. The definitive meta-analysis (128 studies) on when rewards help vs. hurt.
- Gneezy, U. & Rustichini, A. (2000). "A Fine is a Price." *Journal of Legal Studies*. The Israeli daycare study — introducing fines for late pickup *increased* lateness. Classic demonstration of crowding-out.
- Cerasoli, C.P., Nicklin, J.M., & Ford, M.T. (2014). "Intrinsic Motivation and Extrinsic Incentives Jointly Predict Performance." *Journal of Applied Psychology*. Modern meta-analysis showing the interaction (not just crowding) between intrinsic and extrinsic motivation.
