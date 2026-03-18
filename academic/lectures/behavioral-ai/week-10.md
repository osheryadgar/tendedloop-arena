# Week 10: A/B Testing and Statistical Methods

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture provides the statistical machinery for rigorous gamification experiments. We derive the two core tests used in Arena (Welch's t-test for continuous metrics, Fisher's exact test for proportions), develop power analysis to determine required sample sizes, and address the critical pitfalls that invalidate experiments: peeking, multiple testing, and novelty effects. The overarching message: statistical rigor is not optional — it is the difference between evidence and anecdote.

## Key Concepts

### Experimental Design Fundamentals

An A/B test has four components:

1. **Hypothesis.** $H_0$: no difference between variants ($\mu_T = \mu_C$ or $p_T = p_C$). $H_1$: a difference exists. The hypothesis must be specified before data collection — post-hoc hypotheses inflate false positive rates.

2. **Randomization unit.** In gamification, this is typically the user. Each user is randomly assigned to exactly one variant with probability $\pi_k$ for variant $k$, where $\sum \pi_k = 1$. Equal allocation ($\pi_k = 1/K$) maximizes statistical power for pairwise comparisons.

3. **Treatment.** The gamification configuration that differs between variants. In Arena: the 10 economy parameters (scanXp, feedbackXp, streakBonus, dailyXpCap, etc.). A well-designed experiment changes one parameter (or a coherent bundle) at a time.

4. **Outcome metrics.** The measured response variables. Arena tracks 6 metrics; typically one is designated primary (for power analysis) and the rest are secondary (exploratory).

### Welch's t-test: Continuous Metrics

For comparing means of two groups with potentially unequal variances. Given samples $\{X_1, \ldots, X_{n_1}\}$ from treatment and $\{Y_1, \ldots, Y_{n_2}\}$ from control:

$$t = \frac{\bar{X} - \bar{Y}}{\sqrt{\frac{s_X^2}{n_1} + \frac{s_Y^2}{n_2}}}$$

The degrees of freedom are approximated by Welch-Satterthwaite:

$$\nu = \frac{\left(\frac{s_X^2}{n_1} + \frac{s_Y^2}{n_2}\right)^2}{\frac{(s_X^2/n_1)^2}{n_1-1} + \frac{(s_Y^2/n_2)^2}{n_2-1}}$$

**When to use.** Welch's t-test is appropriate for continuous outcomes: XP per day, scan rate, session duration. It does not assume equal variances (unlike Student's t-test), making it robust for gamification data where different reward configurations may change not just the mean but the variance of user behavior.

**Assumptions.** (1) Independent observations — violated if users interact (network effects). (2) Approximately normal sampling distribution of $\bar{X} - \bar{Y}$ — guaranteed by CLT for $n \geq 30$, but check with heavily skewed metrics. For skewed XP distributions, consider testing on $\log(X)$ or using a Mann-Whitney U test as a nonparametric alternative.

### Fisher's Exact Test: Proportions

For binary outcomes (converted vs. not, retained vs. churned). Given a $2 \times 2$ contingency table:

|  | Success | Failure | Total |
|--|---------|---------|-------|
| Treatment | $a$ | $b$ | $a+b$ |
| Control | $c$ | $d$ | $c+d$ |
| Total | $a+c$ | $b+d$ | $N$ |

Under $H_0$ (equal proportions), the probability of observing exactly $a$ successes in the treatment group follows the hypergeometric distribution:

$$P(a) = \frac{\binom{a+b}{a}\binom{c+d}{c}}{\binom{N}{a+c}}$$

The p-value sums probabilities over all tables at least as extreme as observed.

**When to use.** Fisher's exact test is appropriate for: feedback completion rate, badge earning rate, Day-7 retention (binary: active or not). It is exact (no large-sample approximation needed), making it ideal for small samples. For large $N$, it agrees with the chi-squared test but remains valid when cell counts are small.

**Arena's implementation.** Arena uses Fisher's exact test for conversion-type metrics and Welch's t-test for continuous metrics. The platform automatically selects the appropriate test based on metric type.

### Effect Size: Cohen's d

Statistical significance alone is insufficient — a p-value of 0.001 with $n = 1{,}000{,}000$ might reflect a trivially small effect. Cohen's $d$ quantifies the practical magnitude:

$$d = \frac{\bar{X} - \bar{Y}}{s_p}, \quad s_p = \sqrt{\frac{(n_1-1)s_X^2 + (n_2-1)s_Y^2}{n_1 + n_2 - 2}}$$

**Interpretation (Cohen's conventions):** $|d| = 0.2$ (small), $0.5$ (medium), $0.8$ (large). In gamification, effects of $d = 0.1 - 0.3$ are typical — meaningful at scale but requiring large samples to detect.

**For proportions**, the odds ratio provides an analogous effect size: $OR = \frac{a \cdot d}{b \cdot c}$. An OR of 1.5 means the treatment group has 50% higher odds of the outcome.

### Power Analysis

Statistical power = $P(\text{reject } H_0 | H_1 \text{ true}) = 1 - \beta$. Convention: $\beta = 0.20$, so power $= 0.80$.

For a two-sample t-test, the required sample size per group:

$$n = \frac{2(z_{\alpha/2} + z_\beta)^2}{d^2}$$

where $d$ is the target Cohen's $d$. Substituting standard values ($\alpha = 0.05$, power $= 0.80$):

$$n = \frac{2(1.96 + 0.84)^2}{d^2} = \frac{15.68}{d^2}$$

| Target $d$ | $n$ per group | Total $N$ |
|------------|--------------|-----------|
| 0.8 (large) | 25 | 50 |
| 0.5 (medium) | 63 | 126 |
| 0.2 (small) | 393 | 786 |
| 0.1 (tiny) | 1,568 | 3,136 |

**Implication for gamification.** If you expect a small effect ($d = 0.2$), you need ~400 users per variant. With 3 variants, that is 1,200 users. Enterprise gamification systems with 50-200 users per building cannot detect small effects with statistical confidence — they must either pool across buildings, run longer experiments, or accept that only large effects ($d \geq 0.5$) are detectable.

### Multiple Testing Correction

When testing $m$ hypotheses simultaneously (e.g., 6 Arena metrics $\times$ 3 pairwise comparisons = 18 tests), the family-wise error rate (FWER) inflates:

$$P(\text{at least one false positive}) = 1 - (1 - \alpha)^m \approx m\alpha \quad \text{for small } \alpha$$

With $m = 18$ and $\alpha = 0.05$: FWER $\approx 0.60$. More likely than not to get at least one spurious significant result.

**Bonferroni correction.** Test each hypothesis at $\alpha/m$. For $m = 18$: $\alpha_{\text{adj}} = 0.0028$. Simple but conservative — may miss real effects.

**Benjamini-Hochberg (FDR control).** Order p-values $p_{(1)} \leq \ldots \leq p_{(m)}$. Reject $H_{(i)}$ if $p_{(i)} \leq \frac{i}{m}\alpha$. This controls the expected false discovery rate at $\alpha$. Less conservative than Bonferroni while maintaining rigor. Preferred for exploratory analysis of multiple metrics.

### Sequential Testing and the Peeking Problem

**The peeking problem.** If you check results daily and stop when $p < 0.05$, you inflate the false positive rate dramatically. With daily checks over 30 days, the actual Type I error rate can exceed 25%.

**Why it happens.** Under $H_0$, the test statistic follows a random walk. A random walk will cross any threshold with probability 1 given enough time. Early stopping on significance is equivalent to setting a threshold and waiting.

**Group sequential designs.** Pre-specify $K$ interim analyses at times $t_1, \ldots, t_K$. Use adjusted significance levels $\alpha_k$ such that $P(\text{reject at any } k | H_0) = \alpha$. Methods:

- **O'Brien-Fleming:** $\alpha_k$ very small early, larger late ($\alpha_k = 2 - 2\Phi(z_{\alpha/2}/\sqrt{k/K})$). Conservative early, approximately unchanged at the final analysis.
- **Pocock:** Constant $\alpha_k$ at each look, adjusted so total FWER = $\alpha$. Equal spending at each look.

**Always Valid Inference (AVI).** Modern approaches use confidence sequences or mixture sequential probability ratio tests that allow continuous monitoring without inflating error rates. These are increasingly adopted in tech industry A/B testing platforms.

## Formal Models

### Multi-Armed Bandit Framing

Instead of a fixed experiment, consider each variant as an arm of a bandit. The Thompson Sampling approach maintains a posterior $p_k \sim \text{Beta}(\alpha_k, \beta_k)$ for each variant's success rate and samples from the posterior to choose which variant to assign the next user to. This naturally balances exploration (uncertain variants get more users) and exploitation (promising variants get allocated more traffic).

The regret of Thompson Sampling scales as $O(\sqrt{KT \log T})$ where $K$ is the number of variants and $T$ is the time horizon — much better than pure exploration (fixed-design A/B testing), which has regret $O(T)$ during the exploratory phase.

**Tradeoff.** Bandit methods minimize regret during the experiment but provide weaker statistical guarantees than fixed-horizon tests. For scientific rigor (publication, policy decisions), fixed-horizon A/B testing remains preferred. For operational optimization (deploying the best variant faster), bandits dominate.

## Worked Examples

### Example 1: Full Hypothesis Test

**Setup.** Arena experiment with 2 variants, 200 users each. Metric: daily XP.

| Variant | $n$ | $\bar{X}$ | $s$ |
|---------|-----|-----------|-----|
| Control | 200 | 45.2 | 18.3 |
| Treatment | 200 | 51.8 | 22.1 |

**Step 1.** $t = \frac{51.8 - 45.2}{\sqrt{18.3^2/200 + 22.1^2/200}} = \frac{6.6}{\sqrt{1.675 + 2.442}} = \frac{6.6}{2.028} = 3.25$

**Step 2.** Welch-Satterthwaite df: $\nu = \frac{(1.675 + 2.442)^2}{1.675^2/199 + 2.442^2/199} = \frac{16.94}{0.0141 + 0.0300} = \frac{16.94}{0.0441} = 384$

**Step 3.** $p = 2 \cdot P(T_{384} > 3.25) \approx 0.0013$. Significant at $\alpha = 0.05$.

**Step 4.** Effect size: $d = 6.6 / \sqrt{(199 \cdot 18.3^2 + 199 \cdot 22.1^2)/398} = 6.6 / 20.3 = 0.325$. A small-to-medium effect.

**Conclusion.** The treatment variant increases daily XP by 6.6 points ($d = 0.33$, $p = 0.001$). This is both statistically significant and practically meaningful.

### Example 2: Power Analysis for Experiment Planning

An Arena researcher wants to detect a 15% increase in Day-7 retention (from 40% to 46%). Using the arcsine transformation for proportions:

$$h = 2\arcsin\sqrt{p_1} - 2\arcsin\sqrt{p_0} = 2\arcsin\sqrt{0.46} - 2\arcsin\sqrt{0.40}$$
$$= 2(0.7442) - 2(0.6847) = 1.4884 - 1.3694 = 0.119$$

Required sample size: $n = \frac{(z_{0.025} + z_{0.20})^2}{h^2} = \frac{(1.96+0.84)^2}{0.119^2} = \frac{7.84}{0.0142} = 552$ per group.

With 3 variants: $3 \times 552 = 1{,}656$ users needed. If the building has 300 users, the experiment needs at least 6 buildings pooled, or a longer observation window to convert the retention question into a repeated-measures design.

### Example 3: Multiple Testing in Practice

An Arena experiment tests 3 variants against control across 6 metrics. That is $3 \times 6 = 18$ hypothesis tests. Raw p-values for the 4 lowest:

| Test | Metric | Raw $p$ | Bonferroni $p_{\text{adj}}$ | BH rank | BH threshold |
|------|--------|---------|-----------------------|---------|---------------|
| 1 | XP velocity | 0.001 | 0.018 | 1 | 0.0028 |
| 2 | Scan rate | 0.008 | 0.144 | 2 | 0.0056 |
| 3 | Retention | 0.023 | 0.414 | 3 | 0.0083 |
| 4 | Session freq | 0.041 | 0.738 | 4 | 0.0111 |

Under Bonferroni: only test 1 survives ($0.018 < 0.05$). Under BH (FDR $= 0.05$): only test 1 survives ($0.001 < 0.0028$). Neither test 2 nor 3 survives correction. Conclusion: only XP velocity shows a robust treatment effect.

## Practical Framework

### Experiment Checklist

Before launching any gamification A/B test, verify:

1. **Pre-registration.** State the primary metric, expected effect direction, sample size, and analysis plan. This prevents HARKing (Hypothesizing After Results are Known).
2. **Randomization check.** After assignment, verify that treatment and control groups are balanced on key covariates (tenure, baseline activity, building). Run a chi-squared test on categorical variables and t-tests on continuous ones. Any $p < 0.05$ suggests a randomization failure.
3. **Minimum duration.** Run the experiment for at least 2 full weekly cycles (14 days) to capture weekday/weekend patterns. For retention metrics, run for at least 30 days.
4. **Interference check.** If users can communicate across variants (same building, shared Slack channels), SUTVA may be violated. Consider cluster randomization (randomize by building, not by user) if interference is likely.
5. **Pre-commit to analysis.** Decide in advance: will you use one-sided or two-sided tests? What multiple testing correction? When will you analyze (fixed horizon or group sequential)? Changing these after seeing data invalidates the statistical guarantees.

### Variance Reduction: CUPED

CUPED (Controlled-experiment Using Pre-Experiment Data) reduces metric variance by adjusting for pre-experiment behavior. For each user $i$ in the experiment, let $Y_i$ be the post-experiment metric and $X_i$ be the corresponding pre-experiment metric. The adjusted metric:

$$\hat{Y}_i^{\text{adj}} = Y_i - \hat{\theta}(X_i - \bar{X})$$

where $\hat{\theta} = \text{Cov}(Y, X) / \text{Var}(X)$. This removes the component of post-experiment variance explained by pre-experiment behavior, reducing the required sample size by a factor of $(1 - \rho^2)$ where $\rho = \text{Corr}(X, Y)$.

In gamification: if pre-experiment scan rate correlates $\rho = 0.6$ with post-experiment scan rate, CUPED reduces required $n$ by $(1 - 0.36) = 64\%$, i.e., you need only 36% as many users. This is critical for enterprise settings with small populations.

## Arena Connection

Arena implements A/B testing as its core experimental paradigm:

- **Randomized variant assignment.** Arena randomly assigns users to variants at experiment creation, ensuring $(Y(0), Y(1)) \perp W$ by construction. The platform handles the randomization unit (user-level), eliminating a common source of experimental error.
- **Welch's t-test and Fisher's exact test.** Arena's statistical engine applies Welch's t-test to continuous metrics (XP velocity, scan rate, session frequency) and Fisher's exact test to binary metrics (retention, conversion). Students can verify the platform's computed p-values against their own calculations.
- **Effect sizes.** Arena reports Cohen's d for continuous comparisons. This allows students to assess practical significance alongside statistical significance.
- **The peeking temptation.** Arena allows real-time metric monitoring. This is pedagogically useful — students can observe how p-values fluctuate before convergence and why early stopping is dangerous. The platform does not currently implement sequential testing boundaries, making it the student's responsibility to commit to a fixed analysis time.
- **Multi-metric analysis.** With 6 metrics and potentially 3+ variants, students must apply multiple testing corrections to Arena results. The platform provides raw p-values; correction is an exercise left to the analyst.

## Discussion Questions

1. **Minimum detectable effect.** Your enterprise client has 150 users across 3 buildings. What is the minimum effect size (Cohen's $d$) you can reliably detect with 3 variants at $\alpha = 0.05$, power $= 0.80$? What does this mean for the types of gamification changes worth testing?

2. **Novelty effects.** Users in the treatment group might engage more simply because the gamification system looks different, not because the new parameters are better. How would you design an experiment to separate the novelty effect from the true treatment effect? How long should you wait before measuring?

3. **Network interference.** If users in the treatment group discuss their experience with control group users (e.g., "I earned 100 XP today, how about you?"), the stable unit treatment value assumption (SUTVA) is violated. How does this bias the estimated treatment effect? Upward or downward?

4. **Ethical stopping.** Suppose you are running an Arena experiment and one variant appears to drastically reduce engagement (users are churning). Is it ethical to continue the experiment for statistical power? How would you formalize an "ethical stopping rule"?

## Further Reading

- **Kohavi, R., Tang, D., & Xu, Y. (2020).** *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing.* Cambridge University Press. The definitive industry reference.
- **Johari, R., Koomen, P., Pekelis, L., & Walsh, D. (2017).** "Peeking at A/B Tests: Why It Matters and What to Do About It." *KDD.* Formal analysis of the peeking problem with practical solutions.
- **Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013).** "Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data." *WSDM.* CUPED variance reduction for faster experiments.
