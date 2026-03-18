# Week 9: Engagement Metrics and Causal Inference

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture bridges measurement theory and causal reasoning for gamification systems. We define engagement operationally through behavioral proxies, treat metrics as random variables with distributional properties, and introduce survival analysis for retention modeling. The second half introduces the Rubin causal model, which provides the formal machinery to answer: "Did the gamification intervention cause the observed engagement change, or would it have happened anyway?"

## Key Concepts

### Operational Definitions of Engagement

"Engagement" is not directly observable. We construct it from behavioral proxies — measurable actions that serve as indicators. Each proxy captures a different facet.

**DAU/MAU ratio (stickiness).** Let $A_d$ be the set of users active on day $d$ and $A_m$ be the set active during the 28-day window ending on $d$. Then:

$$\text{Stickiness}(d) = \frac{|A_d|}{|A_m|}$$

This ratio ranges from $1/28 \approx 0.036$ (every user active exactly once per month) to $1.0$ (every monthly user is a daily user). Typical consumer apps: 0.10-0.25. Enterprise: 0.30-0.60 (weekday-driven).

**Retention curve.** For a cohort $C_0$ that joined on day 0, define:

$$R(t) = \frac{|C_0 \cap A_t|}{|C_0|}$$

This is Day-$t$ retention. The curve $R(t)$ is monotonically non-increasing with $R(0) = 1$. Key metrics extracted: Day-1 retention (activation quality), Day-7 (habit formation), Day-30 (long-term stickiness). The shape of the curve — convex (rapid early drop, slow tail) vs. concave (gradual decline) — reveals the engagement dynamic.

**Session depth and frequency.** Let $S_{i,d}$ be the number of sessions user $i$ has on day $d$, and let $L_{i,s}$ be the duration of session $s$. Session frequency $\bar{S}_i = \frac{1}{T}\sum_d S_{i,d}$ and mean session depth $\bar{L}_i = \frac{1}{|\mathcal{S}_i|}\sum_s L_{i,s}$ capture intensity. Heavy engagement can mean many short sessions (habit-driven) or few long sessions (flow-state) — the same average time, very different dynamics.

### Metrics as Random Variables

Each metric for user $i$ is a random variable. For a population, we characterize the distribution.

**XP per active day.** Let $X_i$ be user $i$'s daily XP conditional on being active. Across users, $X_1, \ldots, X_N$ are i.i.d. draws from some distribution $F_X$. Gamification systems typically produce right-skewed distributions (many low-XP users, few power users), well-modeled by a log-normal or gamma:

$$X_i \sim \text{LogNormal}(\mu, \sigma^2)$$

The mean is $e^{\mu + \sigma^2/2}$ and the median is $e^\mu$. The gap between mean and median quantifies the power-user skew. A gamification system where mean $\gg$ median is dominated by a small fraction of heavy users — dangerous for population-level conclusions.

**Conversion rates as Bernoulli variables.** Whether user $i$ completes a target action (e.g., submits feedback with a photo) is $Y_i \sim \text{Bernoulli}(p)$. The sample proportion $\hat{p} = \frac{1}{N}\sum Y_i$ has standard error $\sqrt{\hat{p}(1-\hat{p})/N}$. This directly determines confidence interval width and required sample sizes.

### Survival Analysis for Retention

Retention is naturally modeled as time-to-event (event = churn). The survival function:

$$S(t) = P(\text{active at time } t) = 1 - F(t)$$

where $F(t)$ is the CDF of churn time $T$. The hazard function gives instantaneous churn risk:

$$h(t) = \frac{f(t)}{S(t)} = -\frac{d}{dt}\ln S(t)$$

**Constant hazard (exponential).** If $h(t) = \lambda$, then $S(t) = e^{-\lambda t}$ — a fixed daily churn probability. This is the null model: no engagement dynamics, users leave at random.

**Decreasing hazard (Weibull).** If $h(t) = \frac{k}{\lambda}(t/\lambda)^{k-1}$ with $k < 1$, hazard decreases over time — users who survive early are increasingly likely to stay. This is the "habit formation" pattern we want gamification to produce. The shape parameter $k$ measures how strongly early survival predicts long-term retention.

**Cohort comparison.** Given two cohorts (treatment and control), the log-rank test compares their survival curves:

$$\chi^2 = \frac{\left(\sum_t (O_{1t} - E_{1t})\right)^2}{\sum_t V_t}$$

where $O_{1t}$ and $E_{1t}$ are observed and expected events in group 1 at time $t$, and $V_t$ is the variance term. This tests whether the two groups have different churn dynamics.

### Causal Inference: The Potential Outcomes Framework

The fundamental problem of causal inference: for user $i$, we observe either the outcome under treatment $Y_i(1)$ or under control $Y_i(0)$, never both. The individual treatment effect $\tau_i = Y_i(1) - Y_i(0)$ is unobservable.

**Average Treatment Effect (ATE):**

$$\tau = E[Y(1) - Y(0)] = E[Y(1)] - E[Y(0)]$$

**Identification under randomization.** If treatment assignment $W_i$ is independent of potential outcomes ($(Y_i(0), Y_i(1)) \perp W_i$), then:

$$\tau = E[Y | W=1] - E[Y | W=0]$$

This is why randomization is powerful: it allows us to estimate causal effects from observable group means.

**Without randomization (observational data).** Selection bias arises:

$$E[Y | W=1] - E[Y | W=0] = \underbrace{\tau}_{\text{causal}} + \underbrace{E[Y(0)|W=1] - E[Y(0)|W=0]}_{\text{selection bias}}$$

The second term is nonzero when the treatment group differs systematically from control. In gamification: if you launch a new leaderboard and engaged users opt in disproportionately, the observed engagement increase is confounded by selection.

**Conditional ignorability.** If $(Y(0), Y(1)) \perp W | \mathbf{X}$ for covariates $\mathbf{X}$ (e.g., tenure, baseline activity), we can estimate:

$$\tau = E_{\mathbf{X}}[E[Y|W=1, \mathbf{X}] - E[Y|W=0, \mathbf{X}]]$$

Methods: matching, inverse propensity weighting, doubly-robust estimation.

## Formal Models

### Composite Engagement Score

Given $K$ metrics $m_1, \ldots, m_K$, define a composite engagement score:

$$E_i = \sum_{k=1}^{K} w_k \cdot \frac{m_{ik} - \bar{m}_k}{s_k}$$

where each metric is z-scored and $\sum w_k = 1$. The weights $w_k$ can be set by domain expertise or learned (e.g., by regressing on a downstream outcome like 90-day retention).

**Arena's 6 metrics** map to this framework:
1. Scan rate (daily scans per active user)
2. Feedback rate (submissions with comments/photos)
3. Retention (Day-7, Day-30)
4. Session frequency
5. XP velocity (XP earned per active day)
6. Feature adoption (fraction using streaks, missions, etc.)

Each is a random variable with its own distribution. The Arena experiment engine computes variant-level means and performs pairwise statistical tests.

### Propensity Score for Observational Gamification Data

When A/B testing is infeasible, we can use propensity scores. Define $e(\mathbf{x}_i) = P(W_i = 1 | \mathbf{X}_i = \mathbf{x}_i)$, typically estimated via logistic regression. Then the inverse propensity weighted (IPW) estimator:

$$\hat{\tau}_{IPW} = \frac{1}{N}\sum_{i=1}^{N}\left(\frac{W_i Y_i}{\hat{e}(\mathbf{x}_i)} - \frac{(1-W_i)Y_i}{1-\hat{e}(\mathbf{x}_i)}\right)$$

This reweights observations to simulate randomization. Crucial assumption: overlap ($0 < e(\mathbf{x}) < 1$ for all $\mathbf{x}$) — every user type must have nonzero probability of being in either group.

## Worked Examples

### Example 1: Interpreting a Retention Curve

A gamification experiment yields two retention curves:
- **Control:** $R_C(t) = 0.8 \cdot e^{-0.05t}$ (exponential, constant 5% daily hazard)
- **Treatment:** $R_T(t) = 0.85 \cdot (1 + t/10)^{-2}$ (power-law decay)

At Day 1: $R_C(1) = 0.76$, $R_T(1) = 0.70$. Treatment looks worse. But at Day 30: $R_C(30) = 0.18$, $R_T(30) = 0.85 \cdot (4)^{-2} = 0.053$... wait, let's recalculate. $R_T(30) = 0.85/(1+3)^2 = 0.85/16 = 0.053$. Hmm, that's worse too. Better specification: $R_T(t) = e^{-(t/20)^{0.5}}$ (Weibull with $k=0.5$). At Day 1: $R_T(1) = e^{-0.224} = 0.80$. At Day 30: $R_T(30) = e^{-1.22} = 0.30$. Now treatment wins long-term (0.30 vs. 0.18) despite similar Day-1 numbers. The Weibull shape $k=0.5 < 1$ means hazard decreases: the gamification mechanic creates a "habit barrier" — users who survive early periods churn less.

### Example 2: Selection Bias in Feature Rollout

A company adds badges to its feedback platform. They compare engagement before and after. Post-launch engagement is 40% higher. But during the same period, three new buildings onboarded (more users = more activity), and a holiday period ended (seasonal effect). The naive pre/post comparison conflates the badge effect with confounders. A difference-in-differences approach — comparing buildings that got badges vs. those that did not, before and after — isolates the causal effect. If the parallel trends assumption holds ($E[Y(0)_{\text{post}} - Y(0)_{\text{pre}} | \text{treated}] = E[Y(0)_{\text{post}} - Y(0)_{\text{pre}} | \text{control}]$), the DiD estimator is unbiased.

### Example 3: Sample Size for Detecting Engagement Change

We want to detect a 10% increase in daily scan rate ($\mu_0 = 2.0$ scans/day, target $\mu_1 = 2.2$). Historical data shows $\sigma = 1.5$. For a two-sample t-test at $\alpha = 0.05$, power $= 0.80$:

$$n = \frac{2(z_{\alpha/2} + z_\beta)^2 \sigma^2}{(\mu_1 - \mu_0)^2} = \frac{2(1.96 + 0.84)^2 \cdot 2.25}{0.04} = \frac{2 \cdot 7.84 \cdot 2.25}{0.04} = \frac{35.28}{0.04} = 882$$

We need ~882 users per group, or ~1764 total. If only 500 users are available, we either need a longer observation window (reducing variance through repeated measures) or can only detect larger effects ($\Delta \geq 0.17$, approximately 8.5% of $\sigma$).

## Practical Framework

### Building a Metric Dashboard

For any gamification system, the analyst should construct a metric hierarchy:

**Level 1 — Raw counts.** Total scans, total feedbacks, total active users. These are counters, not metrics — they grow with population size and time, making cross-period comparison meaningless without normalization.

**Level 2 — Normalized metrics.** Scans per active user per day, feedback rate (feedbacks/scans), DAU/MAU ratio. These control for population size and enable meaningful comparison.

**Level 3 — Distributional metrics.** Median session length, 90th percentile XP, interquartile range of daily activity. These capture the shape of user behavior, not just the center. A system where the median user does nothing but the mean is high (driven by power users) looks very different from one where activity is uniform.

**Level 4 — Causal metrics.** Estimated treatment effects from controlled experiments. These are the only metrics that support "X caused Y" claims. All Level 1-3 metrics are descriptive.

### Hazard Rate Estimation in Practice

Given a cohort of $N_0$ users who joined on day 0, define:
- $d_t$: number who churned on day $t$
- $n_t$: number at risk at the start of day $t$ (still active)

The Kaplan-Meier estimator of the survival function:

$$\hat{S}(t) = \prod_{t_j \leq t} \left(1 - \frac{d_{t_j}}{n_{t_j}}\right)$$

The 95% confidence band uses Greenwood's formula for variance:

$$\hat{\text{Var}}[\hat{S}(t)] = \hat{S}(t)^2 \sum_{t_j \leq t} \frac{d_{t_j}}{n_{t_j}(n_{t_j} - d_{t_j})}$$

This allows construction of confidence intervals around the retention curve — essential for determining whether two variants' retention curves are meaningfully different or just noisy.

## Arena Connection

Arena's measurement system directly implements these concepts:

- **The 6 metrics.** Arena tracks scan rate, feedback rate, retention, session frequency, XP velocity, and feature adoption. Each is computed as a variant-level statistic, enabling the composite engagement score framework described above. Student agents receive these as observation signals.
- **Cohort-based measurement.** Arena assigns users to variants at experiment start, creating clean cohorts. This eliminates selection bias by construction — the randomization is handled by the platform.
- **Time-series tracking.** Arena records metric values over the experiment duration, enabling survival analysis (retention curves per variant) and trend detection (is the treatment effect growing or decaying?).
- **Causal identification.** Because Arena randomizes variant assignment, the simple difference-in-means estimator is unbiased for the ATE. No propensity scoring needed — but students should understand why (and when observational methods would be necessary, e.g., if users could self-select into variants).

## Discussion Questions

1. **Metric selection.** If you could only measure one engagement metric to evaluate a gamification system, which would you choose and why? Formalize your argument in terms of information content (which metric has highest mutual information with "long-term engagement"?).

2. **Goodhart's Law preview.** DAU/MAU can be inflated by sending aggressive push notifications that cause brief app opens without meaningful engagement. How would you design a metric that is robust to this gaming? What properties should a "Goodhart-resistant" metric have?

3. **Ethical data collection.** Retention modeling requires tracking individual user behavior over time. In an enterprise gamification system (employee feedback), what are the privacy implications? How does anonymization interact with the ability to compute individual-level metrics like $X_i$ and $S_i$?

4. **Causal claims in practice.** A gamification vendor claims "our platform increased employee engagement by 35%." What questions would you ask to evaluate whether this is a causal claim? What confounders would you look for?

## Further Reading

- **Imbens, G. & Rubin, D. (2015).** *Causal Inference for Statistics, Social, and Biomedical Sciences.* Cambridge University Press. The definitive reference on the potential outcomes framework.
- **Chen, N. & Pu, P. (2014).** "HealthyTogether: Exploring Social Incentives for Mobile Fitness Applications." *ACM CSCW.* Empirical study connecting social gamification to engagement metrics.
- **Angrist, J. & Pischke, J. (2009).** *Mostly Harmless Econometrics.* Princeton University Press. Accessible treatment of DiD, IV, and RDD for causal inference.
