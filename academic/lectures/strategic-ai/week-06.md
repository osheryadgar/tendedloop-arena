# Week 6: Contextual Bandits and Beyond

> Strategic AI: Multi-Agent Systems & Optimization

## Overview

Standard bandits assume that all arms have the same reward distribution regardless of when or where they are pulled. In practice, context matters: a cleaning schedule that works well on weekdays may fail on weekends; a configuration optimal for one building may be suboptimal for another. Contextual bandits formalize this by allowing the agent to observe a feature vector (context) before each decision. This lecture derives LinUCB — the workhorse algorithm for contextual bandits — from ridge regression and explores how to engineer features, evaluate policies offline, and connect to modern recommendation systems.

## Key Concepts

### From Bandits to Contextual Bandits

> **Definition (Stochastic Contextual Bandit).** A contextual bandit consists of:
> - **K arms** (actions)
> - A context space **X** (typically X subset R^d)
> - At each round *t*: nature draws context **x_t ~ D_X**, the agent observes x_t, selects arm **a_t in {1, ..., K}**, and receives reward **r_t = f(x_t, a_t) + eta_t** where eta_t is zero-mean noise
> - The function **f : X x A -> R** is unknown and must be learned

The key difference from standard bandits: the optimal arm depends on the context. There is no single "best arm" — there is a best arm *for each context*.

> **Definition (Regret for Contextual Bandits).** The regret of a policy pi after T rounds is:
>
> **R_T = sum_{t=1}^{T} [ max_a f(x_t, a) - f(x_t, pi(x_t)) ]**
>
> where pi(x_t) is the arm chosen by the policy given context x_t.

### The Linear Reward Model

The most tractable assumption is that the expected reward is linear in a feature vector:

> **Assumption (Linear Rewards).** For each arm *a*, there exists an unknown parameter vector **theta_a* in R^d** such that:
>
> **E[r_t | x_t, a_t = a] = x_t^T theta_a***

The context vector x_t might include features like: day of week, time of day, building occupancy, weather, historical feedback scores. The parameter theta_a* captures how these features affect the reward of arm *a*.

Alternatively, we can use arm-specific features: **phi(x_t, a) in R^d** encodes both context and arm, with a single shared theta*:

**E[r_t | x_t, a_t = a] = phi(x_t, a)^T theta***

This is more flexible (different arms can have different feature representations) but requires careful feature engineering.

### Ridge Regression Review

Before deriving LinUCB, we review the estimation step. Given n observations {(x_i, r_i)}_{i=1}^n, the ridge regression estimator is:

> **theta_hat = (X^T X + lambda I)^{-1} X^T r = A^{-1} b**
>
> where **A = X^T X + lambda I** (the regularized design matrix) and **b = X^T r** (the moment vector).

The regularization parameter lambda > 0 prevents overfitting when data is scarce. The estimate can be updated incrementally:

**A_new = A_old + x_t x_t^T** and **b_new = b_old + r_t x_t**

This makes LinUCB computationally efficient: O(d^2) per update (matrix-vector outer product), O(d^2) for prediction (using Sherman-Morrison to maintain A^{-1} incrementally).

### Deriving LinUCB

LinUCB applies the optimism principle from UCB1 to the linear contextual setting. The idea: construct a confidence set for theta_a* and act as if the most optimistic parameter in that set is true.

**Step 1: Confidence Set.**

Under the linear model with sub-Gaussian noise, the ridge regression estimator concentrates around the true parameter:

> **P(||theta_hat_a - theta_a*||_{A_a} <= C_a(t, delta)) >= 1 - delta**

where ||v||_M = sqrt(v^T M v) is the M-weighted norm and:

**C_a(t, delta) = sqrt(lambda) * ||theta_a*|| + sigma * sqrt(d * ln((1 + n_a/lambda) / delta))**

This is an *ellipsoidal* confidence set — the shape is determined by the covariance structure of observed contexts.

**Step 2: Optimistic Prediction.**

For context x_t and arm a, the optimistic reward estimate is:

max_{theta in confidence set} x_t^T theta = x_t^T theta_hat_a + C_a * ||x_t||_{A_a^{-1}}

The maximum occurs at the boundary of the ellipsoid, in the direction of x_t.

**Step 3: The LinUCB Algorithm.**

> **Algorithm (LinUCB — Disjoint Model).**
> 1. Initialize: For each arm *a*, set A_a = lambda * I_d, b_a = 0_d.
> 2. At each round *t*:
>    a. Observe context x_t.
>    b. For each arm *a*:
>       - Compute theta_hat_a = A_a^{-1} b_a
>       - Compute UCB_a = x_t^T theta_hat_a + alpha * sqrt(x_t^T A_a^{-1} x_t)
>    c. Pull arm A_t = argmax_a UCB_a.
>    d. Observe reward r_t.
>    e. Update: A_{A_t} = A_{A_t} + x_t x_t^T, b_{A_t} = b_{A_t} + r_t x_t.

The parameter alpha controls the exploration-exploitation tradeoff (analogous to the confidence level in UCB1). Setting alpha = 1 + sqrt(ln(2/delta) / 2) gives theoretical guarantees.

### LinUCB Regret Bound

> **Theorem (Abbasi-Yadkori et al., 2011).** LinUCB with appropriate alpha achieves:
>
> **R_T = O(d * sqrt(T) * polylog(T, K, d))**

Key observations:
- Regret scales with **d** (feature dimension), not K (number of arms). If d << K, contextual bandits are much more efficient than treating each context-arm pair as a separate arm.
- Regret is **O(sqrt(T))** — sublinear. The agent improves over time.
- No dependence on the number of distinct contexts (which may be infinite).

### Feature Engineering

The power of contextual bandits lies in choosing the right features. In the Arena setting:

**Temporal features:**
- Day of week (one-hot encoded: 7 dimensions)
- Hour of day (cyclical encoding: sin(2*pi*h/24), cos(2*pi*h/24))
- Is holiday (binary)

**Environmental features:**
- Building occupancy level (continuous)
- Weather conditions (categorical, one-hot)
- Recent feedback trend (rolling average)

**Arm-specific features:**
- Historical performance of this arm (mean, variance)
- How long since this arm was last pulled
- Similarity to other arms (embedding distance)

The feature vector x_t is the concatenation of all relevant features. Feature engineering is where domain knowledge enters the algorithm.

### Contextual Thompson Sampling

The Bayesian analogue of LinUCB maintains a posterior distribution over theta_a:

> **Algorithm (Linear Thompson Sampling).**
> 1. Initialize: For each arm *a*, set A_a = lambda * I_d, b_a = 0_d.
> 2. At each round *t*:
>    a. Observe context x_t.
>    b. For each arm *a*:
>       - Compute theta_hat_a = A_a^{-1} b_a and B_a = sigma^2 A_a^{-1}
>       - Sample theta_tilde_a ~ N(theta_hat_a, v^2 * A_a^{-1})
>    c. Pull arm A_t = argmax_a x_t^T theta_tilde_a.
>    d. Observe reward r_t. Update A_{A_t} and b_{A_t}.

The parameter v^2 controls exploration (larger v^2 means wider sampling distribution). This achieves Bayesian regret O(d * sqrt(T * ln T)), matching LinUCB.

### Offline Policy Evaluation

In many applications, we cannot deploy a new policy and observe its performance directly. Instead, we must evaluate a new policy using historical data collected by a different policy (the "logging policy").

> **Definition (Offline Evaluation Problem).** Given logged data D = {(x_t, a_t, r_t)}_{t=1}^T collected by logging policy pi_0, estimate the value of a new target policy pi_1:
>
> **V(pi_1) = E_{x ~ D_X}[E[r | x, pi_1(x)]]**

**Inverse Propensity Scoring (IPS):**

> **V_hat_IPS(pi_1) = (1/T) sum_{t=1}^{T} r_t * I(pi_1(x_t) = a_t) / pi_0(a_t | x_t)**

This is unbiased but can have high variance when pi_1 differs greatly from pi_0 (the propensity weights explode). Doubly-robust estimators combine IPS with a reward model to reduce variance.

Offline evaluation is crucial for safe deployment: before switching from the current service configuration to a new one, estimate the new policy's expected performance using historical feedback data.

## Formal Definitions

> **Definition (Linear Contextual Bandit).** A linear contextual bandit satisfies E[r | x, a] = x^T theta_a* for unknown theta_a* in R^d, with sigma-sub-Gaussian noise.

> **Theorem (LinUCB Regret).** With probability at least 1 - delta, LinUCB achieves cumulative regret R_T = O(d * sqrt(T * ln(T * K / delta))).

> **Definition (IPS Estimator).** V_hat_IPS = (1/T) sum_t r_t * I(a_t = pi(x_t)) / mu(a_t | x_t), where mu is the known logging policy. Unbiased: E[V_hat_IPS] = V(pi).

## Worked Examples

### Example 1: LinUCB with 2D Features

Two arms, 2D context. Arm 1 has theta_1* = (1, 0), arm 2 has theta_2* = (0, 1).

Context x = (0.8, 0.3):
- True rewards: arm 1 gives 0.8, arm 2 gives 0.3.
- Arm 1 is optimal for this context.

Context x = (0.2, 0.9):
- True rewards: arm 1 gives 0.2, arm 2 gives 0.9.
- Arm 2 is optimal for this context.

After initialization (lambda = 1, A_a = I_2, b_a = 0):
- theta_hat_1 = theta_hat_2 = (0, 0). Both predicted rewards are 0.
- UCB_1 = 0 + alpha * sqrt(x^T I^{-1} x) = alpha * ||x||.
- UCB_2 = 0 + alpha * ||x||.
- Tie-break randomly. Say we pull arm 1 for context (0.8, 0.3) and observe r = 0.8 + noise.

Update A_1 = I + (0.8, 0.3)(0.8, 0.3)^T = [[1.64, 0.24], [0.24, 1.09]], b_1 = 0.8 * (0.8, 0.3) = (0.64, 0.24).
Now theta_hat_1 = A_1^{-1} b_1, which points roughly toward (1, 0). Future contexts with large first components will favor arm 1.

### Example 2: Feature Engineering for Arena

Arena experiment with 3 arms (cleaning schedules: morning, midday, evening). Context features:

x_t = [day_mon, day_tue, ..., day_sun, occupancy, temperature, prev_rating]

This gives d = 10 dimensions. A LinUCB agent learns that:
- theta_morning* has high weights on weekday indicators and morning occupancy.
- theta_evening* has high weights on weekend indicators.
- theta_midday* performs uniformly across contexts.

After 200 rounds, the agent has learned to select morning cleaning on busy weekdays and evening cleaning on weekends — a context-dependent policy that a standard bandit could never discover.

### Example 3: Offline Evaluation with IPS

Historical data: 1000 rounds with uniform random logging policy (pi_0 = 1/3 for each arm).
New policy pi_1 always picks arm 1 for weekday contexts and arm 3 for weekend contexts.

For each data point where the logged action matches pi_1's recommendation:

V_hat_IPS = (1/1000) sum_{matching} r_t / (1/3) = 3/1000 * sum_{matching} r_t

If 400 data points match (pi_1 agrees with the logged action) with average reward 0.72:

V_hat_IPS = 3 * 400 * 0.72 / 1000 = 0.864

The new policy's estimated value is 0.864, compared to the uniform policy's observed value of 0.60. The improvement is estimated at 44%.

Caution: variance is high. The 95% confidence interval might be (0.71, 1.01). More logged data or doubly-robust estimators would tighten this.

## Arena Connection

Contextual bandits are the natural next step for Arena agents. The Arena platform provides context through the experiment's metadata and environmental signals:

- **Time-of-day** and **day-of-week** are directly available from the SDK.
- **Building occupancy** and **recent feedback** can be queried as contextual features.
- **Arm metadata** (cleaning type, schedule parameters) serve as arm-specific features.

Workshop Session 5 (contextual approaches) has students:
1. Implement a `LinUCBAgent` that ingests context features from the Arena API.
2. Compare its performance against a context-free Thompson Sampling agent on the same experiment.
3. Demonstrate that contextual agents outperform context-free agents when the optimal arm genuinely varies with context (e.g., weekday vs. weekend patterns).

The SDK provides a `context` dictionary with each observation, which students map to feature vectors. The choice of features and their encoding is left to the student — mirroring real-world ML engineering.

For offline evaluation, students use the Arena's historical data export to estimate the value of their contextual policy before deploying it, practicing the IPS estimator derived in this lecture.

## Discussion Questions

1. LinUCB assumes a linear reward model. What happens when the true reward function is nonlinear? How would you detect model misspecification? What alternatives exist (hint: neural contextual bandits, kernelized bandits)?

2. In offline evaluation, the IPS estimator is unbiased but can have enormous variance when the target policy differs greatly from the logging policy. What is the practical consequence? How does the doubly-robust estimator address this?

3. Feature engineering is critical for contextual bandits. Propose a systematic approach to discovering relevant features for an Arena experiment. How would you handle feature selection — should you include all available features, or is regularization sufficient?

4. Consider a setting where the context is a user's demographic profile. A contextual bandit might learn to show different content to different demographic groups. When is this personalization beneficial, and when might it be harmful (discriminatory)? How should we think about fairness in contextual bandits?

## Further Reading

- **Li, Chu, Langford, & Schapire (2010), "A Contextual-Bandit Approach to Personalized News Article Recommendation"** — The LinUCB paper. Introduced LinUCB and demonstrated it on Yahoo! News personalization with real user data. Highly cited and practically influential.
- **Agarwal, Hsu, Kale, Langford, Li, & Schapire (2014), "Taming the Monster: A Fast and Simple Algorithm for Contextual Bandits"** — Introduces the epoch-greedy and oracle-efficient approaches. Important for understanding the computational challenges of contextual bandits beyond linear models.
- **Dudik, Erhan, Langford, & Li (2014), "Doubly Robust Policy Evaluation and Optimization"** — The key paper on offline policy evaluation. Introduces the doubly-robust estimator and shows its variance reduction properties. Essential reading for anyone deploying contextual bandits in production.
