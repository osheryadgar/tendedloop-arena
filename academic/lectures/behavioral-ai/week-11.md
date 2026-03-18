# Week 11: Reward Hacking, Alignment, and Ethics

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture confronts the failure modes of gamification systems through the lens of AI safety. We formalize Goodhart's Law as a divergence between the proxy metric and the true objective, analyze reward hacking as rational behavior under misspecified incentives, and develop formal guardrails (rate limits, clamping, circuit breakers) as optimization constraints. The alignment problem in gamification — optimizing engagement vs. wellbeing — mirrors the alignment problem in AI, and the solutions share structural similarities.

## Key Concepts

### Goodhart's Law Formalized

Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure." We formalize this. Let $\theta$ be the true objective (e.g., service quality) and $m$ be the measurable proxy (e.g., feedback submission count). In normal operation, $\text{Corr}(\theta, m) > 0$. But when we optimize for $m$ — setting rewards $r = f(m)$ — users shift behavior to maximize $m$, potentially breaking the correlation.

Define the Goodhart gap:

$$G = E_{\pi^*_m}[\theta] - E_{\pi^*_\theta}[\theta]$$

where $\pi^*_m = \arg\max_\pi E_\pi[m]$ (policy optimizing the proxy) and $\pi^*_\theta = \arg\max_\pi E_\pi[\theta]$ (policy optimizing the true objective). When $G < 0$, the proxy-optimal policy is worse than the true-optimal policy — optimization pressure on $m$ has reduced $\theta$.

**Four types of Goodhart failure** (Manheim & Garrabrant, 2019):

1. **Regressional.** The proxy $m$ is a noisy estimate of $\theta$. Optimizing $m$ exploits the noise. Example: XP as a proxy for engagement — users who maximize XP may be compulsively grinding, not genuinely engaged.

2. **Extremal.** The relationship $m \approx \theta$ holds in the training distribution but breaks down at extreme values. Example: streak length correlates with retention for streaks of 1-30 days, but at 365+ days, users may continue solely from sunk-cost anxiety, not genuine engagement.

3. **Causal.** Intervening on $m$ disrupts the causal mechanism linking $m$ to $\theta$. Example: feedback count correlates with user satisfaction because satisfied users give feedback. Rewarding feedback count causes submission of meaningless feedback, breaking the causal link.

4. **Adversarial.** Users strategically manipulate $m$. Example: clicking "submit" with empty feedback forms to earn XP. This is reward hacking in the narrow sense.

### Reward Hacking in Gamification

Reward hacking is rational behavior under misspecified incentives. The user solves:

$$\max_{a \in \mathcal{A}} r(a) - c(a)$$

where $r(a)$ is the reward from action $a$ and $c(a)$ is the cost. If the reward function does not properly capture the intended behavior, users find low-cost actions that yield high reward.

**Concrete examples in gamification:**

1. **XP farming.** A system awards 10 XP per feedback submission with no quality filter. Users submit empty or random feedback. Cost: seconds per submission. Reward: 10 XP. The system optimizes submission count but degrades data quality.

2. **Streak manipulation.** A streak system awards bonus XP for consecutive days of activity. Users open the app, perform the minimum action (a single tap), and close it. The streak counter increments, but no meaningful engagement occurs.

3. **Leaderboard Sybil attacks.** A user creates multiple accounts to boost their ranking or farm referral bonuses. The cost of creating an account is low; the reward (leaderboard position, referral XP) is high.

4. **Badge hunting.** Users perform specific actions solely to unlock badges, then abandon the behavior. The badge was supposed to reinforce a habit, but instead it creates a one-time spike followed by reversion.

Each example has the same structure: the reward function $r(a)$ is positively correlated with the intended behavior in normal use, but admits cheap alternatives that break the correlation.

### The Alignment Problem in Gamification

Define two objectives:
- **Engagement:** $E = f(\text{DAU}, \text{session time}, \text{actions per session}, \ldots)$ — maximized by the gamification system.
- **Wellbeing:** $W = g(\text{satisfaction}, \text{autonomy}, \text{skill development}, \ldots)$ — the user's actual welfare.

The alignment problem: we optimize $E$ because it is measurable, but we care about $W$. When is $\max E \neq \max W$?

**Case 1: Aligned.** Gamification increases both. User enjoys the feedback process, develops a habit, service quality improves. $\nabla_\theta E \cdot \nabla_\theta W > 0$.

**Case 2: Misaligned.** Dark patterns increase $E$ at the expense of $W$. Guilt-based streak notifications cause anxiety; loss-framed leaderboards cause status anxiety; variable-ratio rewards create compulsive checking. $\nabla_\theta E \cdot \nabla_\theta W < 0$.

**Case 3: Partially aligned.** Initial engagement boost improves $W$ (useful feedback habit), but over-optimization degrades $W$ (compulsive behavior). $E$ and $W$ are positively correlated up to a threshold, then diverge. This is the most common and most insidious case.

Formally, we want to solve the constrained problem:

$$\max_\theta E(\theta) \quad \text{subject to} \quad W(\theta) \geq W_{\min}$$

The challenge: $W$ is hard to measure. We need proxy constraints.

### Dark Patterns as Mechanism Design Failures

A dark pattern is a design choice where the designer's incentive is misaligned with the user's welfare. Through the mechanism design lens (from Strategic AI, Week 4), dark patterns violate individual rationality: if users fully understood the mechanism, they would not participate.

**Taxonomy relevant to gamification:**

- **Artificial scarcity.** "Only 2 hours left to claim your daily bonus!" Creates urgency without real constraint. The user acts under false time pressure.
- **Sunk cost exploitation.** "You'll lose your 47-day streak!" The streak has no intrinsic value, but loss aversion (Week 4) makes it feel costly to break.
- **Social pressure.** "Your team is counting on you!" Exploits cooperation norms for engagement metrics.
- **Hidden costs.** The true cost of engagement (time, attention, cognitive load) is obscured by salient rewards (XP, badges).

A mechanism is **autonomy-preserving** if: (1) users can opt out without penalty, (2) the true costs and benefits are transparent, and (3) the mechanism would still be chosen under full information.

### Formal Guardrails as Optimization Constraints

Guardrails prevent the most harmful outcomes of gamification optimization. We formalize them as constraints on the parameter space $\Theta$.

**Rate limiting.** Cap the number of rewarded actions per time window:

$$\sum_{t' \in [t-\Delta, t]} \mathbb{1}[a_{t'} = a] \leq R_a \quad \forall a, t$$

This prevents XP farming by making the marginal reward of additional actions zero after $R_a$ actions. In TendedLoop: the `dailyXpCap` parameter. The agent can tune the cap level but cannot remove it.

**Delta clamping.** Bound parameter changes between optimization steps:

$$|\theta_{t+1} - \theta_t| \leq \delta_{\max} \quad \forall t$$

This prevents sudden reward structure changes that confuse or frustrate users. A system that halves XP overnight will cause backlash; clamping ensures gradual transitions.

**Circuit breakers.** Halt optimization when a safety metric crosses a threshold:

$$\text{If } m_{\text{safety}}(t) < m_{\min}, \quad \text{then } \theta_{t+1} = \theta_{\text{safe}}$$

Example: if Day-7 retention drops below 30%, revert to the default configuration. This is analogous to a stop-loss in financial trading. Arena implements this through experiment-level guardrails that researchers can configure.

**Budget constraints.** Total XP awarded per period is bounded:

$$\sum_i \text{XP}_i(t) \leq B(t)$$

This prevents inflationary spirals where the optimizer increases all rewards to boost engagement, devaluing the currency.

## Formal Models

### Specification Gaming as a Principal-Agent Problem

Model the gamification system as a principal-agent game. The principal (system designer) wants action $a^*$ (genuine, thoughtful feedback). The agent (user) wants to maximize reward minus effort. The principal observes only a signal $s(a)$, not the action $a$ directly.

If $s(a^*) = s(a')$ for some cheap action $a'$ (e.g., empty submission looks the same in the signal as genuine feedback), the agent chooses $a'$. The principal must either:
1. **Enrich the signal** — add quality indicators (photo required, minimum text length, sentiment analysis).
2. **Align the costs** — make $c(a') \geq c(a^*)$ by adding verification.
3. **Randomize audits** — with probability $p$, manually review submissions, penalizing low quality. The expected penalty $p \cdot \text{penalty}$ must exceed the reward from gaming.

### Reward Robustness via Regularization

To make a reward function robust to gaming, add a regularization term that penalizes deviation from expected behavior distributions:

$$r_{\text{robust}}(a) = r(a) - \lambda \cdot D_{\text{KL}}(P(a) \| P_{\text{expected}})$$

where $P(a)$ is the empirical action distribution and $P_{\text{expected}}$ is the expected distribution under genuine engagement. Users who deviate significantly (e.g., submitting at a much higher rate than typical) receive penalized rewards. The hyperparameter $\lambda$ controls the strength of regularization.

## Worked Examples

### Example 1: XP Farming Detection

A gamification system awards 10 XP per feedback submission. Normal users submit 1-3 feedbacks/day ($\mu = 2, \sigma = 1$). A farmer submits 20/day. Define the anomaly score:

$$z_i = \frac{x_i - \mu}{\sigma} = \frac{20 - 2}{1} = 18$$

At $z > 3$ (probability $< 0.001$ under normal behavior), flag for review. But this is reactive. A proactive guardrail: diminishing returns. Set $r(k) = 10 \cdot \min(k, 5) + 2 \cdot \max(0, k - 5)$ — full XP for the first 5 submissions, 80% reduction after. The farmer's effective rate drops from 200 XP/day to $50 + 30 = 80$ XP/day, reducing the incentive to farm while still rewarding genuine high-activity users.

### Example 2: Streak Anxiety Quantification

Model the disutility of losing a streak of length $k$. Using prospect theory's loss aversion (from Week 4):

$$\text{Loss}(k) = -\lambda \cdot v(k) = -\lambda \cdot k^\alpha$$

with $\lambda = 2.25$ (Tversky-Kahneman loss aversion coefficient) and $\alpha = 0.88$. For a 30-day streak:

$$\text{Loss}(30) = -2.25 \cdot 30^{0.88} = -2.25 \cdot 22.4 = -50.4 \text{ utility units}$$

Compare to the gain from continuing the streak one more day: $v(31) - v(30) = 31^{0.88} - 30^{0.88} = 22.99 - 22.38 = 0.61$ utility units. The asymmetry is stark: the fear of loss ($-50.4$) dwarfs the joy of continuation ($+0.61$). At high streak values, users are motivated by anxiety, not reward. An ethical streak design would cap the streak bonus (diminishing the loss term) or provide "streak freeze" mechanics that reduce loss aversion.

### Example 3: Circuit Breaker in Action

An autonomous agent on Arena optimizes XP parameters. Over 5 days, it gradually increases `scanXp` from 10 to 25 to boost scan rate. Scan rate increases from 2.1 to 3.8, but Day-3 feedback quality (measured by comment length) drops from 45 chars to 12 chars — users are scanning without providing meaningful feedback.

Circuit breaker rule: if mean comment length drops below 20 chars, revert `scanXp` to baseline. The breaker fires on Day 4, resetting `scanXp = 10`. The agent must now find a parameter configuration that improves scan rate without degrading quality — a multi-objective problem that the constraint forces it to solve properly.

## Arena Connection

Arena embeds safety considerations into its experiment platform:

- **Parameter bounds.** Arena enforces minimum and maximum values for each tunable parameter. Agents cannot set `dailyXpCap = 0` (which would disable rewards) or `scanXp = 10000` (which would cause hyperinflation). These bounds are hard constraints on the optimization space.
- **Delta clamping.** Arena limits how much an agent can change parameters between update cycles. This prevents whiplash experiences for users and ensures stability.
- **The 6 metrics as proxy checks.** While no single metric captures "wellbeing," monitoring all 6 simultaneously reduces Goodhart risk — gaming one metric (e.g., scan rate) at the expense of another (e.g., feedback quality) is visible in the multi-metric dashboard.
- **Experiment duration limits.** Arena experiments have fixed durations, preventing indefinite optimization that might slowly degrade user experience through a sequence of individually small changes.
- **Ethical experimentation.** Arena experiments involve real users in enterprise contexts (employees providing feedback). Students must consider that their agents affect real people's experience — a concrete instance of the alignment problem.

## Discussion Questions

1. **Goodhart in your life.** Identify a real-world gamification system you use (fitness app, learning platform, productivity tool) that exhibits Goodhart's Law. Which of the four Goodhart types (regressional, extremal, causal, adversarial) best describes the failure? Propose a formal fix.

2. **The guardrail tradeoff.** Every constraint reduces the optimization space, potentially preventing the agent from finding the best solution. How do you formally characterize the "cost of safety" — the gap between the constrained and unconstrained optima? When is this cost worth paying?

3. **Autonomy-preserving gamification.** Design a gamification system that satisfies: (a) users can opt out of any mechanic without losing access to core functionality, (b) all reward mechanisms are transparent (users know how XP is calculated), and (c) no mechanic exploits cognitive biases (loss aversion, sunk cost, social pressure). Is such a system viable? Would it be competitive with systems that exploit these biases?

4. **Responsibility allocation.** An AI agent on Arena optimizes engagement and causes a user to develop compulsive checking behavior (opening the app 30+ times/day). Who is responsible? The agent developer? The platform? The enterprise that deployed it? Formalize using a responsibility framework (e.g., Matthias's "responsibility gap" in autonomous systems).

## Further Reading

- **Amodei, D. et al. (2016).** "Concrete Problems in AI Safety." *arXiv:1606.06565.* The foundational paper on AI safety problems, many of which (reward hacking, safe exploration, distributional shift) apply directly to gamification.
- **Manheim, D. & Garrabrant, S. (2019).** "Categorizing Variants of Goodhart's Law." *arXiv:1803.04585.* The four-type taxonomy used in this lecture.
- **Gray, C. M. et al. (2018).** "The Dark (Patterns) Side of UX Design." *CHI 2018.* Empirical study of dark patterns with a design-oriented taxonomy that complements our formal analysis.
