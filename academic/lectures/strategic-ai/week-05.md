# Week 5: Bayesian Bandits and Thompson Sampling

> Strategic AI: From Agents to Multi-Agent Systems

## Overview

Last week we derived UCB1, a frequentist algorithm that constructs confidence bounds from concentration inequalities. This week we take the Bayesian perspective: we maintain a full probability distribution (posterior) over each arm's mean and use it to make decisions. Thompson Sampling, the resulting algorithm, is beautifully simple — sample from the posterior, act as if the sample is truth — yet achieves optimal regret bounds. Understanding both frequentist and Bayesian approaches gives students two complementary lenses for the explore-exploit tradeoff.

## Key Concepts

### The Bayesian Framework for Bandits

In the Bayesian formulation, arm means are not fixed unknowns but random variables drawn from a prior distribution. The agent updates its beliefs after each observation using Bayes' rule.

> **Setup.** For each arm *i*, the true mean mu_i is drawn from a prior P(mu_i). After observing rewards x_1, ..., x_n from arm *i*, the posterior is:
>
> **P(mu_i | x_1, ..., x_n) = P(x_1, ..., x_n | mu_i) * P(mu_i) / P(x_1, ..., x_n)**

The key computational question: can we update the posterior efficiently? For certain prior-likelihood pairs (conjugate families), the answer is yes — the posterior stays in the same family as the prior.

### Beta-Bernoulli Model

The most natural model for binary outcomes (success/failure, thumbs up/down):

> **Model.** Each arm *i* has a success probability theta_i. The prior is **theta_i ~ Beta(alpha_i, beta_i)**. After observing s_i successes and f_i failures:
>
> **theta_i | data ~ Beta(alpha_i + s_i, beta_i + f_i)**

**Why this works.** The Beta distribution is conjugate to the Bernoulli likelihood. The posterior update simply adds observed successes to alpha and failures to beta. No matrix inversions, no iterative algorithms — just two counter increments.

The Beta(alpha, beta) distribution has:
- **Mean**: alpha / (alpha + beta)
- **Variance**: alpha * beta / ((alpha + beta)^2 * (alpha + beta + 1))
- **Mode** (for alpha, beta > 1): (alpha - 1) / (alpha + beta - 2)

As we collect more data, the variance shrinks and the posterior concentrates around the true mean. The prior Beta(1, 1) = Uniform(0, 1) is uninformative — it represents no prior knowledge about the arm's success probability.

### Thompson Sampling Algorithm

> **Algorithm (Thompson Sampling for Bernoulli Bandits).**
> 1. Initialize: For each arm *i*, set alpha_i = 1, beta_i = 1 (uniform prior).
> 2. At each round *t*:
>    a. For each arm *i*, sample theta_hat_i ~ Beta(alpha_i, beta_i).
>    b. Pull the arm with the highest sample: A_t = argmax_i theta_hat_i.
>    c. Observe reward X_t in {0, 1}.
>    d. Update: If X_t = 1, set alpha_{A_t} += 1. If X_t = 0, set beta_{A_t} += 1.

That's it. The entire algorithm fits in a few lines of code. The elegance is striking: by sampling from the posterior, the algorithm automatically balances exploration and exploitation.

**Intuition:** Arms about which we are uncertain have wide posteriors. Wide posteriors occasionally produce high samples, causing the arm to be explored. Arms about which we are certain and know to be bad have tight posteriors concentrated on low values — they rarely produce high samples and are rarely explored. The exploration rate is automatically calibrated by uncertainty.

### Why Thompson Sampling Works: Probability Matching

Thompson Sampling implements **probability matching** (also called the "posterior sampling" principle):

> **P(A_t = i) = P(mu_i = max_j mu_j | data)**

The probability of selecting arm *i* equals the posterior probability that arm *i* is optimal. This is a principled exploration strategy: we explore arms in proportion to how likely they are to be the best.

Formally, let theta be the vector of true arm means, and let theta_hat be the sampled vector. Then:

P(A_t = i) = P(theta_hat_i = max_j theta_hat_j) = integral P(theta_hat_i = max_j theta_hat_j | theta) * P(theta | data) d_theta

For well-behaved posteriors, this equals P(theta_i = max_j theta_j | data), the posterior probability of optimality.

### Bayesian Regret

The appropriate performance metric in the Bayesian setting is Bayesian regret — regret averaged over the prior.

> **Definition (Bayesian Regret).** The Bayesian regret is:
>
> **BR_T = E_theta E_pi [ sum_{t=1}^{T} (mu*(theta) - mu_{A_t}(theta)) ]**
>
> where the outer expectation is over the prior on arm means theta, and the inner expectation is over the algorithm's randomness.

> **Theorem (Russo & Van Roy, 2014).** Thompson Sampling with a Beta-Bernoulli model achieves Bayesian regret:
>
> **BR_T = O(sqrt(KT ln T))**

This matches the minimax lower bound (up to logarithmic factors). Thompson Sampling is Bayes-optimal in a strong sense.

For instance-dependent (gap-dependent) bounds:

> **BR_T = O(sum_{i : Delta_i > 0} (ln T) / Delta_i)**

This matches the Lai-Robbins lower bound asymptotically. Thompson Sampling is simultaneously near-optimal in both gap-dependent and gap-free senses.

### Gaussian Thompson Sampling

For continuous rewards (e.g., ratings on a 1-5 scale), we use a Gaussian model:

> **Model.** Assume rewards from arm *i* are X ~ N(mu_i, sigma^2) with known variance sigma^2. The conjugate prior for mu_i is Gaussian: **mu_i ~ N(mu_0, sigma_0^2)**.
>
> After observing n_i rewards with sample mean x_bar_i, the posterior is:
>
> **mu_i | data ~ N(mu_post, sigma_post^2)**
>
> where **sigma_post^2 = 1 / (1/sigma_0^2 + n_i/sigma^2)** and **mu_post = sigma_post^2 * (mu_0/sigma_0^2 + n_i * x_bar_i / sigma^2)**

Thompson Sampling proceeds identically: sample mu_hat_i from the posterior, pull argmax_i mu_hat_i.

### Frequentist vs. Bayesian Perspectives

| Aspect | Frequentist (UCB1) | Bayesian (Thompson) |
|--------|-------------------|---------------------|
| Parameters | Fixed, unknown constants | Random variables with priors |
| Uncertainty | Confidence intervals (Hoeffding) | Posterior distributions |
| Exploration mechanism | Optimism (inflate estimates) | Randomization (sample from posterior) |
| Regret metric | Worst-case (frequentist) regret | Bayesian regret (averaged over prior) |
| Hyperparameters | Confidence scaling constant | Prior parameters (alpha, beta) |
| Computation | Deterministic, cheap | Requires sampling, slightly more expensive |
| Empirical performance | Good | Often better (especially early) |

Both achieve O(sqrt(KT ln T)) gap-free regret. Thompson Sampling often outperforms UCB1 empirically, especially in the early rounds when the Bayesian prior provides useful regularization.

### The Value of Information

The Bayesian framework enables a clean formulation of the *value of information* — how much would it be worth to observe a particular arm's reward before making a decision?

> **Definition (Value of Perfect Information for arm i).** The expected gain from observing arm *i*'s true mean before acting:
>
> **VPI_i = E_theta_i [ max(mu*, theta_i) ] - mu***
>
> where the expectation is over the posterior of theta_i.

Arms with high VPI are worth exploring: the information might reveal that they are optimal. Thompson Sampling implicitly computes a quantity related to VPI — the posterior probability of optimality serves as a proxy.

The information ratio (Russo & Van Roy, 2016) formalizes this: it measures the ratio of squared expected regret to information gained, providing a unified analysis framework for Thompson Sampling.

## Formal Definitions

> **Definition (Conjugate Prior).** A prior P(theta) is conjugate to a likelihood P(x | theta) if the posterior P(theta | x) is in the same distributional family as the prior.

> **Theorem (Thompson Sampling Regret).** For K-armed Bernoulli bandits with Beta(1,1) priors, Thompson Sampling achieves: (1) Bayesian regret BR_T = O(sqrt(KT ln T)), and (2) Instance-dependent Bayesian regret BR_T = O(sum_i (ln T) / Delta_i). Both are order-optimal.

> **Definition (Information Ratio).** Gamma_t = (E[Delta_{A_t}])^2 / I_t(A_t; theta*), where I_t is the mutual information between the selected arm and the identity of the optimal arm. Thompson Sampling maintains Gamma_t <= K/2.

## Worked Examples

### Example 1: Beta-Bernoulli Posterior Evolution

Two arms, both initialized with Beta(1, 1). After 10 rounds:

Arm 1: pulled 6 times, 4 successes, 2 failures. Posterior: Beta(5, 3). Mean = 5/8 = 0.625.
Arm 2: pulled 4 times, 1 success, 3 failures. Posterior: Beta(2, 4). Mean = 2/6 = 0.333.

At round 11, we sample:
- theta_hat_1 ~ Beta(5, 3): This distribution has mean 0.625 and is concentrated. A typical sample might be 0.58.
- theta_hat_2 ~ Beta(2, 4): Mean 0.333 but wider. Samples range broadly, say 0.41.

Since 0.58 > 0.41, we pull arm 1 (exploit). But occasionally Beta(2, 4) will produce a sample above Beta(5, 3)'s sample — this is exploration, and it happens with probability proportional to how likely arm 2 is to actually be better.

### Example 2: Posterior Update Step by Step

Arm with prior Beta(1, 1). We pull it 5 times and observe: 1, 0, 1, 1, 0.

After observation 1 (success): Beta(2, 1). Mean = 2/3 = 0.667.
After observation 2 (failure): Beta(2, 2). Mean = 2/4 = 0.500.
After observation 3 (success): Beta(3, 2). Mean = 3/5 = 0.600.
After observation 4 (success): Beta(4, 2). Mean = 4/6 = 0.667.
After observation 5 (failure): Beta(4, 3). Mean = 4/7 = 0.571.

The posterior mean converges toward the MLE (s/n = 3/5 = 0.6), but the prior (pseudocounts of 1 each) provides regularization early on. Variance: 4*3 / (7^2 * 8) = 12/392 = 0.031, so standard deviation ~ 0.175. The 95% credible interval is approximately (0.24, 0.88) — still quite wide after only 5 observations.

### Example 3: Thompson Sampling vs. UCB1 on Easy vs. Hard Instances

**Easy instance:** Arms with means [0.9, 0.1]. Delta = 0.8.
- UCB1: After ~3 pulls of arm 2, its UCB drops below arm 1's mean. Near-zero regret.
- Thompson: After 1-2 pulls of arm 2, Beta posterior concentrates near 0.1, rarely sampled above 0.9. Near-zero regret.
- Both algorithms perform similarly on easy instances.

**Hard instance:** Arms with means [0.51, 0.49]. Delta = 0.02.
- UCB1: Needs O(ln(T) / 0.02) = O(50 ln T) pulls of each arm before gaps resolve. At T=10000, roughly 460 suboptimal pulls.
- Thompson: Empirically, Thompson makes fewer suboptimal pulls than UCB1 on hard instances because posterior sampling is smoother than the hard threshold of UCB.

The empirical advantage of Thompson Sampling is well-documented: Chapelle & Li (2011) showed it consistently outperforms UCB variants across a range of problems.

## Arena Connection

Thompson Sampling is the recommended starting algorithm for Arena agents. The SDK's agent template includes a `ThompsonAgent` class that maintains Beta posteriors for each arm:

```python
class ThompsonAgent:
    def __init__(self, arms):
        self.alpha = {arm: 1 for arm in arms}
        self.beta = {arm: 1 for arm in arms}

    def select_arm(self):
        samples = {arm: np.random.beta(self.alpha[arm], self.beta[arm]) for arm in self.alpha}
        return max(samples, key=samples.get)

    def update(self, arm, reward):
        if reward > 0.5:  # threshold for binary feedback
            self.alpha[arm] += 1
        else:
            self.beta[arm] += 1
```

Workshop Session 5 explores:
1. Visualizing how posteriors evolve as the agent collects Arena feedback.
2. Comparing Thompson Sampling against UCB1 on the same Arena experiment.
3. Experimenting with informative priors — encoding domain knowledge (e.g., "most service configurations yield ratings around 3.5/5") into the prior.

Arena's reward structure (typically continuous ratings) motivates Gaussian Thompson Sampling as an extension of the basic Beta-Bernoulli model.

## Discussion Questions

1. Thompson Sampling requires specifying a prior. What if the prior is badly misspecified (e.g., you use Beta(100, 1) when the true mean is 0.3)? How quickly does the algorithm recover? How does this compare to UCB1, which has no prior?

2. The Bayesian regret guarantee averages over the prior. A critic might argue: "The prior is wrong, so Bayesian regret is meaningless." Respond to this criticism. Under what conditions do Bayesian guarantees translate to frequentist guarantees?

3. Thompson Sampling is randomized (it samples from posteriors), while UCB1 is deterministic. In what settings might randomization be an advantage beyond just exploration? (Hint: adversarial opponents, game-theoretic settings.)

4. The information ratio bounds regret in terms of information gain. Intuitively, what does it mean for an algorithm to have a low information ratio? Can you think of an algorithm with a high information ratio?

## Further Reading

- **Russo, Van Roy, Kazerouni, Osband, & Wen (2018), "A Tutorial on Thompson Sampling"** — The definitive modern reference. Covers theory, extensions, and practical guidance. Remarkably readable for a paper with serious theorems.
- **Chapelle & Li (2011), "An Empirical Evaluation of Thompson Sampling"** — Influential empirical study showing Thompson Sampling's practical superiority over UCB and epsilon-greedy across diverse problem settings.
- **Russo & Van Roy (2016), "An Information-Theoretic Analysis of Thompson Sampling"** — Introduces the information ratio framework. Provides the cleanest available analysis of Thompson Sampling's regret, unifying many special cases.
