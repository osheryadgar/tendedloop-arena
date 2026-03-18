# Week 4: Behavioral Economics and Computational Nudging

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture brings behavioral economics into the computational gamification framework. We formalize three key phenomena — loss aversion (prospect theory), temporal discounting, and anchoring — as mathematical models, then show how each becomes a design lever in gamification systems. The central tool is the Kahneman-Tversky value function, which replaces the rational utility model with one that accounts for how people actually evaluate gains and losses. We then introduce computational nudge design: using optimization to select defaults, frames, and choice architectures.

## Key Concepts

### Prospect Theory: The Value Function

Expected utility theory assumes people evaluate outcomes by their absolute value. Kahneman and Tversky (1979) showed that people evaluate outcomes *relative to a reference point*, and that they are more sensitive to losses than to equivalent gains.

The value function v(x) maps an outcome x (relative to a reference point) to subjective value:

```
v(x) = x^alpha              if x >= 0  (gains)
v(x) = -lambda * (-x)^beta  if x < 0   (losses)
```

**Parameters:**
- alpha in (0, 1): diminishing sensitivity to gains (typical estimate: 0.88)
- beta in (0, 1): diminishing sensitivity to losses (typical estimate: 0.88)
- lambda > 1: loss aversion coefficient (typical estimate: 2.25)

**Key properties:**
1. **Reference dependence:** v(0) = 0. Outcomes are evaluated as gains or losses from a reference point, not in absolute terms.
2. **Loss aversion:** |v(-x)| > v(x) for all x > 0 when lambda > 1. Losing 10 XP feels worse than gaining 10 XP feels good.
3. **Diminishing sensitivity:** v is concave for gains and convex for losses. The difference between 100 and 200 XP feels larger than between 1000 and 1100 XP.

### The Probability Weighting Function

Prospect theory also includes a probability weighting function pi(p) that distorts objective probabilities:

```
pi(p) = p^gamma / (p^gamma + (1-p)^gamma)^(1/gamma)
```

with gamma approximately 0.65. This function overweights small probabilities and underweights large ones. In gamification:

- Rare badge drops feel more exciting than they "should" (pi(0.01) >> 0.01)
- Guaranteed daily rewards feel less valuable than they "should" (pi(0.99) < 0.99)
- Variable-ratio rewards exploit probability overweighting (covered in Week 6)

### Loss Aversion in Gamification Mechanics

Loss aversion is the most exploitable behavioral bias in gamification. Common implementations:

**Streaks:** A streak is a loss-framed mechanic. The user has accumulated a streak of k days. Breaking it means "losing" the streak — a loss that prospect theory says is weighted lambda times more heavily than the equivalent gain. This makes streaks powerful retention tools, but also potentially coercive (see ethics discussion).

Formally, the subjective value of maintaining a streak of length k:

```
V_maintain(k) = v(streakBonus(k)) = streakBonus(k)^alpha
```

The subjective value of breaking it:

```
V_break(k) = v(-streakValue(k)) = -lambda * streakValue(k)^beta
```

The net motivation to continue is:

```
M(k) = V_maintain(k) - V_break(k) = streakBonus(k)^alpha + lambda * streakValue(k)^beta
```

Loss aversion makes M(k) much larger than it would be under rational utility theory, where lambda = 1. This is why streaks work — users are disproportionately motivated to avoid losing what they have.

**Streak freezes:** Offering a "streak freeze" (pay gems to preserve streak) converts a pure loss into a choice. The user now evaluates: pay cost c to avoid loss L. They will pay whenever c < lambda * L^beta, which occurs for smaller c than rational theory would predict (since lambda > 1).

### Temporal Discounting Models

How do people value future rewards? Two competing models:

**Exponential discounting (rational model):**

```
V(x, t) = delta^t * v(x)
```

where delta in (0, 1) is the discount factor. This model is time-consistent: if you prefer 10 XP today over 15 XP tomorrow, you also prefer 10 XP on day 100 over 15 XP on day 101.

**Hyperbolic discounting (behavioral model):**

```
V(x, t) = v(x) / (1 + k*t)
```

where k > 0 is the discount rate. This model is time-*inconsistent*: you might prefer 15 XP tomorrow over 10 XP today (when both are in the future), but when "today" arrives, you switch to preferring the immediate 10 XP.

**Quasi-hyperbolic (beta-delta) discounting:**

```
V(x, 0) = v(x)                    (immediate)
V(x, t) = beta * delta^t * v(x)   (future, t >= 1)
```

where beta in (0, 1) captures the present bias and delta is the long-run discount factor. Typical estimates: beta = 0.7, delta = 0.99.

The beta-delta model explains why gamification works for behavior change: people know they *should* exercise/give feedback/study, but they discount future benefits hyperbolically. Gamification adds immediate rewards (XP now) for behaviors with delayed natural benefits, effectively overcoming the present bias.

### Anchoring and Framing in Reward Presentation

**Anchoring:** The first number a user sees becomes a reference point that biases subsequent evaluations. In gamification:

- Showing "You could earn up to 500 XP today" anchors expectations. Earning 200 XP then feels like a loss (200 - 500 = -300 relative to anchor).
- Showing the leaderboard leader's score anchors the user's evaluation of their own score.

**Framing:** The same outcome can be presented as a gain or a loss with different behavioral effects:

- Gain frame: "Complete 3 scans to earn 30 bonus XP"
- Loss frame: "You'll lose your 30 XP bonus if you don't complete 3 scans today"

Prospect theory predicts that the loss frame is more motivating (by factor lambda) but also more aversive. The optimal frame depends on the designer's objective: maximize short-term compliance (loss frame) or long-term satisfaction (gain frame).

### Computational Nudge Design

A **nudge** is a choice architecture intervention that predictably alters behavior without forbidding options or significantly changing economic incentives (Thaler & Sunstein, 2008).

Formalize nudge design as an optimization problem. Let D = {d_1, ..., d_m} be a set of possible default options. Each user u has a true preference ordering over outcomes, but exhibits behavioral biases (status quo bias, anchoring, etc.).

The nudge design problem:

```
maximize    sum_u W(outcome(u, d*))    (social welfare)
subject to  d* in D                     (feasible defaults)
            outcome(u, d) = argmax_a  v_u(a) + bias(a, d)  (behavioral choice model)
```

where bias(a, d) captures the status quo bias toward the default d. Users are more likely to choose the default, so the designer can steer behavior by selecting d*.

In gamification, defaults include:
- Default daily goal (Duolingo: 10 XP/day default, but offers 20/30/50)
- Default notification frequency
- Default leaderboard visibility (opt-in vs. opt-out)
- Default streak freeze purchase (auto-buy vs. manual)

## Formal Models

### Model 1: Prospect-Theoretic Streak Valuation

Let s_k be the streak bonus for maintaining a streak of length k. The cumulative streak value is:

```
S(k) = sum_{j=1}^{k} s_j
```

Under prospect theory, the subjective value of the streak depends on whether we frame it as accumulated gains or potential loss:

**Gains frame (building up):**
```
V_gains(k) = sum_{j=1}^{k} v(s_j) = sum_{j=1}^{k} s_j^alpha
```

Due to diminishing sensitivity (alpha < 1), the marginal subjective value of each additional day decreases. Integration yields diminishing motivation over time.

**Loss frame (maintaining):**
```
V_loss(k) = -v(-S(k)) = lambda * S(k)^beta
```

The entire accumulated streak is at risk, and its loss is amplified by lambda. This grows with k (longer streaks feel more valuable to protect), which explains why long streaks create strong lock-in.

**Design insight:** Streak value perception switches from gains frame (early days) to loss frame (after several days). The transition happens approximately when:

```
s_{k+1}^alpha < lambda * (S(k+1)^beta - S(k)^beta)
```

i.e., when the marginal loss from breaking exceeds the marginal gain from extending.

### Model 2: Optimal Reward Timing Under Hyperbolic Discounting

Consider a gamification system that can deliver a total reward budget B over T days. Under exponential discounting, timing doesn't matter (present value is the same). Under hyperbolic discounting, front-loading rewards is suboptimal because it reduces motivation for future actions.

The optimal allocation problem:

```
maximize    sum_{t=0}^{T} r(t) / (1 + k*t)
subject to  sum_t r(t) = B
            r(t) >= 0
```

Using Lagrange multipliers, the optimal allocation under hyperbolic discounting is:

```
r*(t) proportional to 1/(1 + k*t)^2
```

This means rewards should be *front-loaded* but with a long tail. Give larger rewards early (to overcome present bias) but maintain small rewards throughout (to sustain engagement). This is exactly what most successful gamification systems do: large early XP gains, then diminishing rewards per action.

### Model 3: Anchoring as Bayesian Updating with Biased Prior

Model anchoring as a Bayesian estimation problem where the anchor serves as an informative (but biased) prior:

```
E_anchored[x] = w * anchor + (1 - w) * E_true[x]
```

where w in (0, 1) is the anchoring weight. Empirically, w is approximately 0.4-0.6 even for clearly irrelevant anchors.

In gamification, this means the first XP value a user encounters sets their reference point:
- If the first action gives 50 XP and subsequent actions give 10 XP, users feel underrewarded (anchored at 50)
- If the first action gives 5 XP and subsequent actions give 10 XP, users feel pleasantly surprised (anchored at 5)

**Design rule:** Anchor low, deliver high. Start users with modest rewards and gradually increase. This creates a positive trajectory that aligns with prospect theory's reference-dependent evaluation.

## Worked Examples

### Example 1: Streak Freeze Pricing

A system offers streak freezes (preserving a streak when a user misses a day) at cost c gems. What is the maximum c a loss-averse user will pay?

**Setup:** User has a 14-day streak. Daily streak bonus = 5 XP. Total streak value S(14) = 70 XP (linear). Prospect theory parameters: alpha = 0.88, beta = 0.88, lambda = 2.25.

**Subjective loss from breaking streak:**
```
V_loss = lambda * S(14)^beta = 2.25 * 70^0.88 = 2.25 * 49.0 = 110.2
```

A rational user (lambda = 1) would value the loss at 70^0.88 = 49.0. The loss-averse user values it at 110.2 — more than double.

If gems have linear utility (1 gem = 1 utility unit), the user will pay up to c = 110.2 gems for a freeze. A system could price freezes at 80 gems and most loss-averse users would buy them, while a rational pricing model (based on expected XP loss) would set the price much lower.

**Ethical note:** This is a textbook example of exploiting loss aversion for monetization. Whether it's acceptable depends on whether the streak freeze genuinely benefits the user (reduces stress) or primarily extracts value.

### Example 2: Comparing Gain vs. Loss Frames

A company wants to increase engagement actions. They test two notification messages:

- **Gain frame:** "Submit feedback today and earn 25 XP!"
- **Loss frame:** "Don't miss your 25 XP — submit feedback before midnight!"

Model the expected response rate under prospect theory.

**Gain frame subjective value:** v(25) = 25^0.88 = 18.8
**Loss frame subjective value:** |v(-25)| = 2.25 * 25^0.88 = 42.3

If the probability of submission is proportional to subjective value (logistic model):

```
P(submit | gain) = sigmoid(18.8 - cost)
P(submit | loss) = sigmoid(42.3 - cost)
```

For cost = 20 (moderate effort):
- P(gain) = sigmoid(-1.2) = 0.23
- P(loss) = sigmoid(22.3) = 1.0 (essentially certain)

The loss frame is approximately 4.3x more effective in subjective value terms. Empirical studies typically find a 1.5-2.5x difference (the mathematical model overpredicts because real decisions involve more factors than prospect-theoretic value alone).

### Example 3: Optimal Onboarding XP Schedule

Design an onboarding sequence for a 7-day tutorial. Total XP budget: 500. User has beta-delta discounting with beta = 0.7, delta = 0.99.

**Flat schedule:** 500/7 = 71.4 XP/day

Present value to user:
```
PV_flat = 71.4 + 0.7*0.99*71.4 + 0.7*0.99^2*71.4 + ... + 0.7*0.99^6*71.4
        = 71.4 + 0.7*71.4*(0.99 + 0.99^2 + ... + 0.99^6)
        = 71.4 + 0.7*71.4*5.79
        = 71.4 + 289.3 = 360.7
```

**Front-loaded schedule:** [150, 100, 80, 60, 50, 35, 25]

Present value:
```
PV_front = 150 + 0.7*(0.99*100 + 0.99^2*80 + 0.99^3*60 + 0.99^4*50 + 0.99^5*35 + 0.99^6*25)
         = 150 + 0.7*(99 + 78.4 + 58.2 + 48.0 + 33.3 + 23.5)
         = 150 + 0.7*340.4
         = 150 + 238.3 = 388.3
```

**Back-loaded schedule:** [25, 35, 50, 60, 80, 100, 150]

Present value:
```
PV_back = 25 + 0.7*(0.99*35 + 0.99^2*50 + ... + 0.99^6*150)
        = 25 + 0.7*(34.6 + 49.0 + 58.2 + 57.6 + 47.5 + 44.1)  (heavily discounted)
        = 25 + 0.7*291.0
        = 25 + 203.7 = 228.7
```

The front-loaded schedule has the highest present value (388.3 vs. 360.7 vs. 228.7) under hyperbolic discounting. However, it risks the anchoring problem: if day 1 gives 150 XP, day 7's 25 XP feels disappointing. The optimal schedule balances discounting benefits with anchoring costs.

A compromise: moderate front-loading with a "surprise" bonus on the final day: [120, 80, 60, 50, 40, 50, 100]. The day-7 spike creates a peak-end effect (Kahneman's peak-end rule), leaving the user with a positive memory of onboarding.

## Arena Connection

Behavioral economics maps directly to Arena's parameter tuning:

**Loss aversion and streaks:** Arena's streakBonus parameter controls the incentive to maintain streaks. An agent exploiting loss aversion would set high streakBonus (making streak loss painful) combined with a streak freeze option. The optimal streakBonus depends on the population's loss aversion coefficient lambda, which the agent must estimate from behavioral data (willingness to pay for freezes, engagement drop after streak breaks).

**Temporal discounting and XP velocity:** Arena's XP velocity metric reflects how quickly users accumulate XP. Under hyperbolic discounting, users overvalue immediate XP. An agent can exploit this by front-loading rewards (high scanXp, low dailyXpCap) to create an engaging first impression, then gradually shifting the reward structure. However, this risks the anchoring trap if initial rewards are too generous.

**Framing effects and missions:** Mission descriptions in Arena can be framed as gains ("Complete 5 scans to earn 50 XP") or losses ("5-scan streak at risk — 50 XP on the line"). The agent's choice of framing doesn't change the parameters but changes user response — a reminder that optimization involves more than just numbers.

**Connection to mechanism design (Strategic AI Week 4):** Both courses study incentive design. Strategic AI asks "what mechanism makes rational agents truth-tell?" Behavioral AI asks "what mechanism accounts for bounded rationality?" The intersection is mechanism design for behavioral agents, an active research frontier.

## Discussion Questions

1. **Compute:** A user has a 21-day streak with linear bonus (streakBonus = 3 XP/day, so S(21) = 63). Using prospect theory (alpha = beta = 0.88, lambda = 2.25), compute the subjective value of (a) maintaining the streak for one more day and (b) losing the streak. At what streak length k does the loss value exceed 200 subjective utility units?

2. **Design:** Duolingo's streak freeze costs 10 gems (effectively free for active users). Analyze this pricing decision through the lens of prospect theory. Is the streak freeze designed to reduce user anxiety (pro-social) or to increase streak investment and therefore loss aversion on the day the user *doesn't* have a freeze (extractive)? Can it be both?

3. **Ethical:** Hyperbolic discounting means users systematically undervalue future consequences of present actions. A gamification system that exploits this (giving immediate XP for actions with delayed costs) is technically a "nudge" — but toward whose benefit? Formalize the distinction between a "nudge" and a "sludge" (a choice architecture that works against the user's long-term interest).

4. **Technical:** The anchoring model E_anchored = w * anchor + (1-w) * E_true suggests that XP values are evaluated relative to anchors. If Arena resets all XP values at the start of each experiment, users in the second experiment may be anchored to the first experiment's values. How should an Arena agent handle cross-experiment anchoring effects?

## Further Reading

- Tversky, A. & Kahneman, D. (1992). "Advances in Prospect Theory: Cumulative Representation of Uncertainty." *Journal of Risk and Uncertainty*. The refined version of prospect theory with the probability weighting function.
- Thaler, R.H. (1999). "Mental Accounting Matters." *Journal of Behavioral Decision Making*. How people categorize and evaluate financial outcomes — directly applicable to how users "account for" XP, gems, and streaks.
- Laibson, D. (1997). "Golden Eggs and Hyperbolic Discounting." *Quarterly Journal of Economics*. The foundational paper on quasi-hyperbolic discounting and commitment devices — relevant to understanding why streaks serve as self-imposed commitment mechanisms.
