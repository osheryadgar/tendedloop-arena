# Week 6: Reinforcement Schedules and Reward Shaping

> Behavioral AI: Computational Gamification & Engagement

## Overview

This lecture formalizes operant conditioning — the oldest and most empirically validated theory of reward-driven behavior — as a computational framework for gamification design. We model Skinner's four reinforcement schedules mathematically, analyze their response rate and persistence properties, then connect to modern RL through Ng et al.'s reward shaping theorem. Finally, we model Eyal's Hook Model as a Markov chain, revealing how gamification systems create habitual behavior loops.

## Key Concepts

### Operant Conditioning as a Formal Reward Model

Skinner's operant conditioning framework describes how the *schedule* of reinforcement (when and how rewards are delivered) affects behavior more than the magnitude of the reward itself. This is a counterintuitive finding with deep implications for gamification: *how* you deliver XP matters more than *how much* XP you deliver.

The four canonical schedules are defined by two binary dimensions:

| | Ratio (action-based) | Interval (time-based) |
|---|---|---|
| **Fixed** | Fixed-Ratio (FR) | Fixed-Interval (FI) |
| **Variable** | Variable-Ratio (VR) | Variable-Interval (VI) |

Each schedule can be modeled as a reward function R: (action_count, time) -> {0, reward}:

**Fixed-Ratio (FR-n):** Reward after every n-th action.
```
R_FR(a) = reward * I[a mod n == 0]
```
Example: "Earn a badge after every 10 scans."

**Variable-Ratio (VR-n):** Reward after a random number of actions, with mean n.
```
R_VR(a) = reward * I[X_a = 1],  where X_a ~ Bernoulli(1/n)
```
Example: "Each scan has a 10% chance of earning a bonus badge."

**Fixed-Interval (FI-t):** Reward for the first action after every t time units.
```
R_FI(a, tau) = reward * I[tau >= t AND first_action_after(t)]
```
Example: "Daily login bonus — first scan each day earns 50 XP bonus."

**Variable-Interval (VI-t):** Reward for the first action after a random time interval with mean t.
```
R_VI(a, tau) = reward * I[tau >= T_k AND first_action_after(T_k)],  T_k ~ Exp(1/t)
```
Example: "Random surprise bonus — appears at unpredictable times for the next scan."

### Response Patterns by Schedule

Decades of behavioral research (animal and human) have established characteristic response patterns for each schedule:

**FR produces post-reinforcement pause:** After receiving a reward, there is a pause (the "FR break") before the next burst of activity. The pause length increases with n. Cumulative response curve has a "scalloped" shape: pause, burst, reward, pause.

**VR produces high steady-state response rate:** Because any action could be rewarded, there is no rational time to pause. VR produces the highest and most consistent response rate of all four schedules. This is why slot machines (VR schedule) are so compelling. Cumulative response curve is approximately linear with high slope.

**FI produces accelerating response near reward time:** Users learn the interval and accelerate their activity as the interval end approaches. Cumulative response curve is "scalloped" with acceleration.

**VI produces moderate steady-state response rate:** Similar to VR but lower, because the time uncertainty means intense responding doesn't help (the reward is time-gated, not action-gated). Cumulative response curve is approximately linear with moderate slope.

### Mathematical Analysis of Response Rates

Model a user as a response-generating process with rate r(t) that depends on the schedule.

**FR-n steady-state rate:**
```
r_FR = (1 / (n * tau_action + tau_pause)) * n = n / (n * tau_action + tau_pause)
```
where tau_action is the time per action and tau_pause is the post-reinforcement pause. As n increases, the effective rate approaches 1/tau_action (no pause) but tau_pause also increases, creating a tradeoff.

**VR-n steady-state rate:**
```
r_VR = 1 / tau_action  (no systematic pause)
```
VR eliminates the post-reinforcement pause because the next reward could come on the very next action. The response rate is bounded only by the physical action speed.

**FI-t steady-state rate:**
```
r_FI(tau) = r_max * (tau / t)^2  for tau in [0, t]
```
The quadratic acceleration model matches empirical data. Average rate: r_max/3 (much lower than FR or VR).

**VI-t steady-state rate:**
```
r_VI = c / t  (approximately constant)
```
where c is a proportionality constant. The rate is inversely proportional to the mean interval.

**Ranking by response rate:** VR > FR > VI > FI

**Ranking by persistence after extinction (reward removal):** VR > VI > FR > FI

The persistence ranking is critical for gamification: VR schedules create the most persistent behavior, meaning users continue engaging even after rewards become sparse. This is both the most effective schedule and the most ethically concerning.

### Reward Shaping (Ng et al. 1999)

Ng, Harada, and Russell (1999) proved a fundamental theorem about reward shaping in reinforcement learning: you can add a shaping reward F to the base reward R without changing the optimal policy, *if and only if* F is a potential-based shaping function:

```
F(s, a, s') = gamma * Phi(s') - Phi(s)
```

where Phi: S -> R is a potential function over states and gamma is the discount factor.

**Relevance to gamification:** When designing intermediate rewards (XP for partial progress, badges for milestones), we are reward shaping. If our shaping rewards are not potential-based, they can distort the intended behavior:

- **Potential-based shaping example:** Give XP proportional to (progress_after - progress_before). This is potential-based with Phi = XP_earned. It accelerates learning without changing what behavior is optimal.

- **Non-potential-based shaping example:** Give a flat 50 XP bonus for any scan, regardless of whether it provides new information. This changes the optimal behavior from "scan useful things" to "scan anything repeatedly."

The theorem gives gamification designers a formal test: does your reward structure change what users *should* do, or does it just make them do it faster?

### The Hook Model as a Markov Chain

Nir Eyal's Hook Model (2014) describes habitual product engagement as a four-phase cycle: Trigger -> Action -> Variable Reward -> Investment. We can model this as a Markov chain.

**States:** S = {Idle, Triggered, Acting, Rewarded, Invested, Churned}

**Transition matrix:**

```
         Idle  Trig  Act   Rew   Inv   Churn
Idle    [ 0    p_t   0     0     0     1-p_t ]
Trig    [ 0    0     p_a   0     0     1-p_a ]
Act     [ 0    0     0     p_r   0     1-p_r ]
Rew     [ 0    0     0     0     p_i   1-p_i ]
Inv     [ 0    p_t'  0     0     0     1-p_t']
Churn   [ 0    0     0     0     0     1     ]
```

where:
- p_t = P(trigger noticed | idle) — affected by notification design
- p_a = P(action taken | triggered) — affected by friction, motivation
- p_r = P(reward received | acted) — the reinforcement schedule determines this
- p_i = P(investment made | rewarded) — affected by reward quality
- p_t' = P(re-triggered | invested) — affected by habit strength

The probability of completing one full cycle:

```
P(full cycle) = p_t * p_a * p_r * p_i
```

The expected number of cycles before churning:

```
E[cycles] = 1 / (1 - P(full cycle) * p_t')
```

This is a geometric distribution. For the hook to create a habit, we need P(full cycle) * p_t' close to 1.

**Variable reward in the Markov model:** The VR schedule makes p_r stochastic. On each action, the user may or may not receive a reward. The key insight: variable rewards *increase* p_a on subsequent cycles (because the unpredictability maintains interest), even though they decrease p_r on any given cycle. The net effect on P(full cycle) can be positive if the VR schedule increases p_a enough to compensate.

## Formal Models

### Model 1: Expected Reward Rate by Schedule

Define the expected reward rate (rewards per unit time) for each schedule:

```
RR_FR(n) = r_FR / n = 1 / (n * tau_action + tau_pause(n))
RR_VR(n) = r_VR / n = 1 / (n * tau_action)
RR_FI(t) = 1 / t
RR_VI(t) = 1 / t
```

For fixed reward magnitude m, the expected reward per unit time:

```
E[reward/time]_FR = m / (n * tau_action + tau_pause(n))
E[reward/time]_VR = m / (n * tau_action)
```

VR always dominates FR in reward rate because it eliminates the pause. But from the *designer's* perspective, the cost is also higher (more rewards delivered per time), so the cost-effectiveness comparison depends on the cost structure.

### Model 2: Extinction Curves

After reward removal (extinction), response rate decays. Model the decay:

**FR extinction:**
```
r(t) = r_0 * exp(-t / tau_FR)
```
Fast exponential decay. Users quickly realize the fixed pattern has stopped.

**VR extinction:**
```
r(t) = r_0 * (1 + t/tau_VR)^(-1)
```
Power-law (hyperbolic) decay. Users take much longer to conclude that rewards have stopped, because the variable nature means any gap could be "normal."

The ratio of half-lives: tau_VR / tau_FR is typically 3-10x, meaning VR-trained behavior persists 3-10 times longer after reward removal.

### Model 3: Optimal Schedule Selection as a Bandit Problem

The gamification designer faces a schedule selection problem: which of the four schedules maximizes long-term engagement? This is a multi-armed bandit problem where each arm is a schedule.

```
Arms: {FR-n, VR-n, FI-t, VI-t}  (each with parameter n or t)
Reward: engagement(schedule, day)  (stochastic)
Objective: maximize cumulative engagement over T days
```

Using UCB1:

```
schedule* = argmax_s [mu_hat(s) + sqrt(2 * ln(T) / n_s)]
```

where mu_hat(s) is the estimated mean engagement for schedule s and n_s is the number of days schedule s has been used.

The complication: switching schedules mid-experiment can cause contrast effects (a user accustomed to VR may find FR disappointing). The bandit formulation assumes independent arms, but in reality, the arms interact through user state.

### Model 4: Potential-Based Shaping in Gamification

Define the gamification state space S and a potential function Phi(s):

```
Phi(s) = XP(s) / XP_needed_for_next_level(s)
```

This potential function measures progress toward the next level. The potential-based shaping reward:

```
F(s, a, s') = gamma * Phi(s') - Phi(s) = gamma * XP(s')/L(level+1) - XP(s)/L(level+1)
```

This simplifies to a reward proportional to XP gained, scaled by how close the user is to the next level. Importantly, it gives *larger* rewards when the user is close to leveling up (because Phi changes more rapidly near level boundaries). This matches the empirical observation that users are most motivated just before a level-up — the shaping reward formalizes this intuition.

Non-potential shaping (e.g., fixed bonus for first scan of the day) violates the theorem and can create suboptimal behaviors: users scan once per day to collect the bonus, then stop. The "optimal" behavior under this shaping is different from the intended behavior.

## Worked Examples

### Example 1: Comparing Schedules — 100-User Simulation

Simulate 100 users over 30 days under four schedules, all delivering the same total expected reward (30 rewards per user over 30 days).

**Parameters:**
- FR-1 (every action rewarded, but each reward = 1 XP, 30 expected actions over 30 days)
- VR-1 (each action has P=1/1 of reward — equivalent to FR-1, so use VR-3: P=1/3, reward=3)
- FI-1day (daily reward of 30 XP for first action each day)
- VI-1day (random daily reward, mean interval 1 day, reward = 30 XP)

**Model each user's daily action probability:**
```
P(active|FR) = 0.7 (moderate, with post-reinforcement pauses)
P(active|VR) = 0.85 (high, driven by variable reinforcement)
P(active|FI) = 0.6 (low on average, spikes near reward time)
P(active|VI) = 0.65 (moderate, steady but lower than ratio schedules)
```

**30-day engagement (average active days per user):**
- FR: 0.7 * 30 = 21 days
- VR: 0.85 * 30 = 25.5 days
- FI: 0.6 * 30 = 18 days
- VI: 0.65 * 30 = 19.5 days

**Variance (coefficient of variation):**
- FR: CV = 0.25 (predictable)
- VR: CV = 0.35 (some users get lucky/unlucky)
- FI: CV = 0.30 (timing variability)
- VI: CV = 0.40 (highest variance)

**VR wins on mean engagement but has higher variance.** Some users experience long drought periods (no reward for many actions) and disengage. The designer must decide: is 25.5 days with CV=0.35 better than 21 days with CV=0.25?

### Example 2: Reward Shaping — Badge Progression

Design a badge system for a 5-level badge track. Users must complete 10 actions per level. Compare two shaping approaches:

**Approach A (Non-potential):** Flat 50 XP bonus at each badge level (levels 1-5).
```
R_A(a) = 10 * I[action] + 50 * I[badge_earned]
XP sequence: 10, 10, ..., 10, 60, 10, ..., 10, 60, ...  (every 10th action gets +50)
```

This is effectively an FR-10 schedule for the bonus. It creates a predictable rhythm and post-reinforcement pauses after each badge.

**Approach B (Potential-based):** Shaping reward proportional to progress:
```
Phi(s) = (actions_toward_badge / 10) * 50
F(s, a, s') = gamma * Phi(s') - Phi(s) = gamma * 5 - 5  (approximately 0 for gamma near 1)
```

Wait — for gamma close to 1, potential-based shaping gives nearly zero extra reward. This is correct: potential-based shaping *should* be small (it preserves the original optimal policy). The non-potential approach fundamentally changes behavior by creating strong FR-10 incentives.

**Practical compromise:** Use small potential-based progress rewards (1 XP per action toward badge = visible progress) plus a larger badge completion bonus. The progress rewards keep users engaged between badges without dramatically distorting behavior.

### Example 3: Hook Model Probability Analysis

A facility feedback app has the following Hook cycle probabilities:
- p_t = 0.8 (push notification noticed)
- p_a = 0.5 (user acts on notification)
- p_r = 0.7 (reward received — VR schedule, 70% of actions rewarded)
- p_i = 0.6 (user makes "investment" — adds a comment, uploads photo)
- p_t' = 0.9 (invested user is re-triggered next cycle)

```
P(full cycle) = 0.8 * 0.5 * 0.7 * 0.6 = 0.168
E[cycles before churn] = 1 / (1 - 0.168 * 0.9) = 1 / (1 - 0.151) = 1 / 0.849 = 1.18
```

This is poor — users churn after about 1.2 cycles on average. The bottleneck is p_a = 0.5 (half the time, users ignore the trigger even when they see it).

Improving p_a to 0.8 (better trigger design, lower friction):
```
P(full cycle) = 0.8 * 0.8 * 0.7 * 0.6 = 0.269
E[cycles] = 1 / (1 - 0.269 * 0.9) = 1 / 0.758 = 1.32
```

Still not great. The multiplicative nature of the Hook chain means *every* probability must be high. To reach E[cycles] = 5:

```
1 / (1 - P_cycle * p_t') = 5  =>  P_cycle * p_t' = 0.8
```

If p_t' = 0.95 (strong habit), we need P_cycle = 0.842. With four stages: 0.842^(1/4) = 0.958 — each stage needs P > 95%.

This is why habit formation is hard. The Markov chain analysis reveals that even small friction at any stage compounds multiplicatively.

## Arena Connection

Reinforcement schedules connect to Arena in two ways:

**Direct parameter mapping:** Arena's reward structure is primarily FR-1 (every scan/feedback earns XP). The streakBonus adds an FI component (daily check-in reward). An agent could implement VR by varying the reward magnitude randomly across ticks, effectively creating variable rewards within the fixed-ratio structure.

**Schedule as agent strategy:** An agent could treat the choice of reward timing as a strategic variable. Rather than maintaining constant XP values, the agent could:
- Tick 1-5: High rewards (establish baseline)
- Tick 6-10: Gradually reduce (test extinction resistance)
- Tick 11-15: Reintroduce rewards (re-engagement)

This temporal pattern implements a form of partial reinforcement within the Arena's tick structure.

**Workshop connection:** Assignment 3 asks students to simulate the four schedules and compare outcomes. The Arena provides the platform for this simulation. An agent that understands reinforcement schedules can design more sophisticated reward strategies than one that simply optimizes static parameters.

**Reward shaping and Arena metrics:** If the agent adds progress-based rewards (potential-based shaping), it should not distort the underlying behavior the Arena measures. If shaping rewards cause users to game the system (scan without providing feedback), the feedback rate metric will drop — revealing that the shaping was non-potential-based and behavior-distorting.

## Discussion Questions

1. **Compute:** A VR-5 schedule rewards each action with probability 0.2 (mean 5 actions between rewards). Each reward is 25 XP. An FR-5 schedule rewards every 5th action with 25 XP. Both deliver the same expected XP per action (5 XP/action). If VR users have a response rate 30% higher than FR users, compute the daily XP expenditure for a population of 200 users under each schedule. Which schedule is more expensive for the designer?

2. **Design:** Duolingo uses a "streak freeze" mechanic combined with a daily goal (FI schedule) and XP rewards for lessons (FR schedule). Map Duolingo's complete reward structure to the four reinforcement schedules. Which schedule dominates? Is there a VR component?

3. **Ethical:** VR schedules are the most effective at creating persistent behavior and also the most closely associated with addictive products (slot machines, social media infinite scroll). Should gamification systems for workplace use be restricted to FR and FI schedules to avoid creating compulsive behavior? Where is the line between "effective engagement" and "behavioral exploitation"?

4. **Technical:** Ng et al.'s reward shaping theorem assumes a stationary MDP. In gamification, user preferences and skill levels change over time (non-stationary). Does the theorem still hold approximately? What could go wrong with potential-based shaping in a non-stationary environment?

## Further Reading

- Ferster, C.B. & Skinner, B.F. (1957). *Schedules of Reinforcement*. The original comprehensive study of reinforcement schedules — 700+ pages of data and analysis. Dense but foundational.
- Eyal, N. (2014). *Hooked: How to Build Habit-Forming Products*. The practitioner's guide to the Hook Model. Read critically through the Markov chain lens developed in this lecture.
- Devlin, S. & Kudenko, D. (2012). "Dynamic Potential-Based Reward Shaping." *AAMAS*. Extends Ng et al.'s static shaping theorem to dynamic environments — directly relevant to non-stationary gamification.
