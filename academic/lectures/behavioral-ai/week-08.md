# Week 8: Social Dynamics and Network Effects

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture formalizes social dynamics in gamification systems using game theory and utility theory. We model social comparison as a utility function where payoff depends on relative position, analyze leaderboard architectures through their psychological and strategic properties, and study network effects that determine whether a gamification system achieves viral growth or stalls. The key insight: social features transform a single-player optimization problem into a multi-agent game.

## Key Concepts

### Social Comparison as a Utility Function

Festinger (1954) proposed that humans evaluate themselves by comparison to similar others. We formalize this. Let user $i$ have absolute performance $x_i$ and let $\bar{x}_{-i}$ denote the mean performance of a reference group. A social utility function is:

$$U_i(x_i, \mathbf{x}_{-i}) = \alpha \cdot v(x_i) + \beta \cdot r(x_i, \mathbf{x}_{-i})$$

where $v(x_i)$ is intrinsic value from absolute performance, $r(x_i, \mathbf{x}_{-i})$ is relative value from social comparison, and $\alpha, \beta \geq 0$ weight the components. A purely "social" user has $\beta \gg \alpha$.

A common specification for $r$ uses rank:

$$r(x_i, \mathbf{x}_{-i}) = \frac{|\{j : x_j < x_i\}|}{N - 1}$$

This is the empirical CDF — the fraction of peers below user $i$. Note: rank is a zero-sum quantity. One user's gain in rank is another's loss. This has profound implications for system design.

**Upward vs. downward comparison.** Festinger distinguished two directions. Let $x_i^+$ be the nearest peer above and $x_i^-$ the nearest peer below. We can model asymmetric comparison:

$$r(x_i) = \gamma^+ \cdot (x_i - x_i^+) + \gamma^- \cdot (x_i - x_i^-)$$

Typically $|\gamma^+| > |\gamma^-|$ — the pain of being below a peer exceeds the pleasure of being above one (mirroring loss aversion from Week 4).

### Leaderboard Design and Strategic Effects

Leaderboards are the most common social mechanic. Different designs create different strategic games.

**Full ranking** shows all $N$ users ordered by score. This maximizes information but has a critical problem: users in the bottom quartile face consistent downward comparison, reducing motivation. Formally, if $U_i < 0$ when rank is below some threshold $k^*$, then fraction $(N - k^*)/N$ of users have negative utility from the leaderboard — they would prefer it did not exist.

**Relative leaderboard** shows only $k$ neighbors: the $k/2$ users directly above and below. This bounds the comparison set:

$$r_{\text{relative}}(x_i) = \frac{|\{j \in N_k(i) : x_j < x_i\}|}{k}$$

where $N_k(i)$ is $i$'s $k$-neighborhood. This keeps comparison tractable and prevents demoralization from extreme gaps.

**Percentile display** shows only $\text{percentile}(x_i) = \lceil 100 \cdot F(x_i) \rceil$ where $F$ is the empirical CDF. This removes individual comparisons entirely. The key property: percentile is monotone in $x_i$ but compresses the tails. Moving from 50th to 60th percentile requires less effort than moving from 90th to 95th (assuming normal-ish distributions). This naturally provides diminishing marginal returns on effort.

**Theorem (leaderboard impossibility).** No leaderboard design simultaneously satisfies: (1) full transparency (every user knows their exact rank), (2) positive utility for all users, and (3) truthful reporting (users have no incentive to manipulate). Proof sketch: full transparency plus positive utility requires all users to perceive themselves favorably, which contradicts the zero-sum nature of rank; relaxing truthfulness allows Sybil attacks.

### Competition vs. Cooperation: The Public Goods Game

Consider $N$ users who can contribute effort $e_i \in [0, E]$ to a shared resource (e.g., a collective feedback goal). Each unit of individual effort costs $c$ but the total pool $\sum e_j$ is multiplied by a factor $m > 1$ and distributed equally. User $i$'s payoff:

$$\pi_i = \frac{m \sum_{j=1}^{N} e_j}{N} - c \cdot e_i$$

**Nash equilibrium analysis.** The marginal return to $i$ from increasing $e_i$ by one unit is $m/N - c$. If $m/N < c$ (which holds when $N > m/c$), the dominant strategy is $e_i = 0$: free-riding. Yet if all contribute $E$, total surplus is $N(mE - cE) > 0$ when $m > c$. This is the classic social dilemma.

**Gamification solutions.** Adding recognition badges for top contributors, peer visibility of contributions, or threshold rewards (bonus triggered only when $\sum e_j > T$) can shift the equilibrium. The threshold mechanism is particularly powerful — it transforms the game into a coordination game where contributing is a best response if others contribute.

### Network Effects and Viral Coefficients

A gamification system exhibits network effects when user $i$'s utility increases with the number of active users: $\partial U_i / \partial N > 0$. This creates a positive feedback loop.

**Viral coefficient.** Let each active user invite $k$ others, and let $p$ be the conversion rate. The viral coefficient is $K = k \cdot p$. Starting from $N_0$ users, the steady-state population (for $K < 1$) is:

$$N_\infty = \frac{N_0}{1 - K}$$

For $K \geq 1$, growth is exponential (in the continuous limit, $dN/dt = (K-1) \cdot \lambda \cdot N$ where $\lambda$ is the invitation rate). In practice, $K$ degrades over time as the reachable network saturates.

**Referral mechanics.** A two-sided referral bonus gives reward $r_s$ to the sender and $r_r$ to the receiver. The optimal design balances acquisition cost against lifetime value (LTV):

$$\max_{r_s, r_r} \quad E[\text{LTV}(r_r)] \cdot p(r_s, r_r) - r_s - r_r$$

where $p(r_s, r_r)$ is the probability of successful conversion.

## Formal Models

### Agent-Based Social Dynamics Model

We simulate $N = 100$ users with heterogeneous social sensitivity:

$$\beta_i \sim \text{Uniform}(0, 1), \quad \alpha_i = 1 - \beta_i$$

Each period, user $i$ chooses effort $e_i$ to maximize expected utility given beliefs about others' effort. The dynamics follow a best-response process:

$$e_i^{t+1} = \arg\max_{e \in [0, E]} \left[ \alpha_i \cdot v(e) + \beta_i \cdot \hat{r}(e, \mathbf{e}_{-i}^t) - c(e) \right]$$

where $\hat{r}$ is the expected rank given current-period effort levels. In simulation, this converges to a heterogeneous equilibrium where high-$\beta$ users cluster near the top (effort arms race) and low-$\beta$ users settle at moderate effort.

### Leaderboard Churn Rate

Define churn as a user becoming inactive. Model the hazard rate:

$$h_i(t) = h_0 \cdot \exp(\delta_1 \cdot \Delta\text{rank}_i(t) + \delta_2 \cdot \text{gap}_i(t))$$

where $\Delta\text{rank}_i(t)$ is rank change since last period and $\text{gap}_i(t)$ is distance to the next rank above. Negative rank changes ($\delta_1 < 0$) and large gaps ($\delta_2 > 0$) increase churn. This proportional hazards model can be estimated from observational data.

## Worked Examples

### Example 1: Relative vs. Full Leaderboard

A gamification system has 500 users with XP scores $\sim \text{LogNormal}(\mu=7, \sigma=1.5)$. Under a full leaderboard, the bottom 50% see they are below the geometric mean and have $r < 0.5$. Under a relative leaderboard with $k=10$ neighbors, each user sees 5 above and 5 below, creating a local competition where they are always near the middle. Compute: the variance of the rank signal is $\text{Var}(r_\text{full}) = 1/12 \approx 0.083$ (uniform rank) vs. $\text{Var}(r_\text{relative}) \approx 0.083/50 = 0.0017$ (compressed by neighborhood size). The relative board provides less informative but less demoralizing signals.

### Example 2: Threshold Public Goods

A facility sets a monthly goal: if total feedback submissions exceed $T = 200$, all contributors share a bonus pool of $B = 1000$ XP. With $N = 50$ active users and cost $c = 5$ XP-equivalent per submission, the threshold requires $200/50 = 4$ submissions per user. The per-user payoff if the threshold is met: $1000/50 - 5 \cdot 4 = 20 - 20 = 0$. This is a knife-edge — increasing $B$ to $1500$ makes contribution strictly dominant ($30 - 20 > 0$), creating a cooperative equilibrium.

### Example 3: Viral Coefficient Calculation

A Scout referral system offers 50 XP to referrer and referree. Each active Scout invites $k = 3$ friends per month. With $p = 0.15$ conversion rate, $K = 0.45$. Starting from 100 Scouts: $N_\infty = 100 / (1 - 0.45) \approx 182$. To achieve $K \geq 1$, we need $p \geq 1/3$. A/B testing different referral rewards can estimate the $p(r_s, r_r)$ function and find the minimum reward that pushes $K$ above 1.

## Simulation Framework

### Agent-Based Model of Leaderboard Effects

To study the interaction between leaderboard design and population engagement, we define a discrete-time simulation.

**Setup.** $N = 200$ users. Each user $i$ has:
- Ability $\mu_i \sim \text{Normal}(50, 15)$ (latent skill)
- Social sensitivity $\beta_i \sim \text{Beta}(2, 5)$ (most users are moderately social)
- Effort cost function $c_i(e) = \kappa_i \cdot e^2 / 2$ where $\kappa_i \sim \text{Uniform}(0.5, 2.0)$

Each period, user $i$ chooses effort $e_i$ to maximize:

$$\Pi_i(e_i) = \alpha_i \cdot (\mu_i + e_i) + \beta_i \cdot r(e_i, \mathbf{e}_{-i}) - c_i(e_i)$$

where $r$ depends on the leaderboard design. Under full ranking: $r = \text{rank}_i / N$. Under relative ($k=10$): $r = \text{local\_rank}_i / k$. Under percentile: $r = \text{percentile}_i / 100$.

**Equilibrium computation.** For each design, iterate best responses until convergence ($\|\mathbf{e}^{t+1} - \mathbf{e}^t\| < \epsilon$). Record:
- Total engagement: $\sum_i e_i^*$
- Engagement inequality: Gini coefficient of $\{e_1^*, \ldots, e_N^*\}$
- Churn rate: fraction of users with $\Pi_i^* < 0$ (negative utility users would prefer to disengage)

**Expected results.** Full ranking maximizes total engagement but also maximizes inequality and churn. Relative leaderboards minimize churn but sacrifice total engagement. Percentile designs offer an intermediate point on the Pareto frontier.

## Arena Connection

TendedLoop Arena enables direct experimentation with social dynamics:

- **Leaderboard variants.** Arena's experiment engine can assign users to different leaderboard designs (full rank vs. relative vs. percentile) and measure the effect on the 6 engagement metrics. The `leaderboardEnabled` parameter (or custom variant config) controls visibility.
- **Scout referral system.** The Scout program's referral mechanics are a live instance of the viral coefficient model. Arena experiments can test different referral reward levels and measure $K$ directly from conversion data.
- **Public goods via collective missions.** Arena could model building-level challenges (threshold feedback targets) as a public goods game. The `dailyXpCap` parameter interacts with social dynamics: low caps compress the leaderboard (reducing rank variance), while high caps allow social differentiation.
- **Agent-based optimization.** Student agents on Arena implicitly compete — each variant's agent adjusts parameters for its population, creating an inter-agent social game on top of the intra-user social game. This is the multi-agent dimension explored further in Week 14.

## Discussion Questions

1. **Design tradeoff.** A leaderboard increases engagement for top performers but causes churn among bottom performers. Formalize this as a constrained optimization: $\max_{\text{design}} \sum_i \Delta\text{engagement}_i$ subject to $\max_i \Delta\text{churn}_i \leq \epsilon$. What leaderboard design solves this?

2. **Free-riding detection.** In a cooperative gamification system (team goals), how would you design an algorithm to detect free-riders without discouraging legitimate low-activity users? What features distinguish the two?

3. **Ethical tension.** Social comparison mechanics exploit psychological biases (status anxiety, FOMO). Is it ethical to deploy leaderboards that you know will cause negative utility for a subset of users, even if aggregate engagement increases? How does the answer change in enterprise (employee feedback) vs. consumer contexts?

4. **Network saturation.** The viral coefficient $K$ assumes a homogeneous network. In practice, early adopters are better connected than later adopters. Model $K(t)$ as a decreasing function and derive when growth stalls. What gamification interventions can counteract saturation?

## Further Reading

- **Lerner, B. & Tirole, J. (2002).** "Some Simple Economics of Open Source." *Journal of Industrial Economics.* Formalizes status incentives in contribution systems.
- **Zichermann, G. & Cunningham, C. (2011).** *Gamification by Design.* O'Reilly. Practical leaderboard design patterns (contrast with our formal analysis).
- **Jackson, M. O. (2008).** *Social and Economic Networks.* Princeton University Press. Network formation models relevant to viral gamification.
