# Week 12: Bayesian Optimization and Black-Box Methods

> Strategic AI: Multi-Agent Systems & Optimization

## Overview

This week studies Bayesian Optimization (BO), a principled framework for optimizing expensive black-box functions under a limited evaluation budget. We develop Gaussian Processes as surrogate models, derive the posterior predictive distribution, and define acquisition functions that balance exploration and exploitation. We compare BO with reinforcement learning and connect the framework directly to the Arena setting, where BO provides a natural approach to tuning gamification economy parameters.

## Key Concepts

### Gaussian Processes as Surrogate Models

A **Gaussian Process** (GP) is a distribution over functions, fully specified by a mean function and a covariance (kernel) function:

$$f(\mathbf{x}) \sim \mathcal{GP}(m(\mathbf{x}), k(\mathbf{x}, \mathbf{x}'))$$

where:
- $m(\mathbf{x}) = \mathbb{E}[f(\mathbf{x})]$ is the mean function (often set to 0 or a constant),
- $k(\mathbf{x}, \mathbf{x}') = \text{Cov}(f(\mathbf{x}), f(\mathbf{x}'))$ is the kernel function encoding assumptions about smoothness, periodicity, and lengthscale.

**Key property:** Any finite collection of function values $(f(\mathbf{x}_1), \dots, f(\mathbf{x}_n))$ follows a multivariate Gaussian distribution:

$$\begin{pmatrix} f(\mathbf{x}_1) \\ \vdots \\ f(\mathbf{x}_n) \end{pmatrix} \sim \mathcal{N}\left(\begin{pmatrix} m(\mathbf{x}_1) \\ \vdots \\ m(\mathbf{x}_n) \end{pmatrix}, \begin{pmatrix} k(\mathbf{x}_1, \mathbf{x}_1) & \cdots & k(\mathbf{x}_1, \mathbf{x}_n) \\ \vdots & \ddots & \vdots \\ k(\mathbf{x}_n, \mathbf{x}_1) & \cdots & k(\mathbf{x}_n, \mathbf{x}_n) \end{pmatrix}\right)$$

**Common kernels:**

*Squared Exponential (RBF):*
$$k_{\text{SE}}(\mathbf{x}, \mathbf{x}') = \sigma_f^2 \exp\left(-\frac{\|\mathbf{x} - \mathbf{x}'\|^2}{2\ell^2}\right)$$

where $\ell$ is the lengthscale (controls smoothness) and $\sigma_f^2$ is the signal variance. Produces infinitely differentiable functions --- very smooth.

*Matern kernel:*
$$k_{\nu}(\mathbf{x}, \mathbf{x}') = \sigma_f^2 \frac{2^{1-\nu}}{\Gamma(\nu)} \left(\frac{\sqrt{2\nu} \|\mathbf{x} - \mathbf{x}'\|}{\ell}\right)^\nu K_\nu\left(\frac{\sqrt{2\nu} \|\mathbf{x} - \mathbf{x}'\|}{\ell}\right)$$

The Matern-5/2 ($\nu = 5/2$) is widely used in practice: twice differentiable, more realistic than the infinitely smooth SE kernel.

### Deriving the GP Posterior

Given $n$ observations $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^{n}$ where $y_i = f(\mathbf{x}_i) + \epsilon_i$, $\epsilon_i \sim \mathcal{N}(0, \sigma_n^2)$, the posterior at a new point $\mathbf{x}_*$ is:

$$f(\mathbf{x}_*) | \mathcal{D} \sim \mathcal{N}(\mu_*,\, \sigma_*^2)$$

where:

$$\mu_* = \mathbf{k}_*^\top (K + \sigma_n^2 I)^{-1} \mathbf{y}$$

$$\sigma_*^2 = k(\mathbf{x}_*, \mathbf{x}_*) - \mathbf{k}_*^\top (K + \sigma_n^2 I)^{-1} \mathbf{k}_*$$

Here $K$ is the $n \times n$ kernel matrix with $K_{ij} = k(\mathbf{x}_i, \mathbf{x}_j)$, $\mathbf{k}_*$ is the $n \times 1$ vector with $k_{*i} = k(\mathbf{x}_*, \mathbf{x}_i)$, and $\mathbf{y} = (y_1, \dots, y_n)^\top$.

**Interpretation:**
- $\mu_*$ is a weighted average of observed values, with weights determined by kernel similarity.
- $\sigma_*^2$ is the posterior uncertainty: small near observed points, large far from data.
- The posterior **contracts** around observations and **reverts to the prior** in unexplored regions.

**Computational cost:** $(K + \sigma_n^2 I)^{-1}$ requires $O(n^3)$ time. This becomes prohibitive for $n > 10{,}000$, motivating sparse GP approximations (inducing points) and structured kernel methods.

### Acquisition Functions

The **acquisition function** $\alpha(\mathbf{x})$ determines where to evaluate next. It uses the GP posterior $(\mu(\mathbf{x}), \sigma(\mathbf{x}))$ to balance exploitation (querying where the predicted value is high) and exploration (querying where uncertainty is high).

**Expected Improvement (EI):**

$$\text{EI}(\mathbf{x}) = \mathbb{E}\left[\max(f(\mathbf{x}) - f^+, 0)\right]$$

where $f^+ = \max_{i} y_i$ is the current best observation. Under the GP posterior:

$$\text{EI}(\mathbf{x}) = (\mu(\mathbf{x}) - f^+) \Phi(Z) + \sigma(\mathbf{x}) \phi(Z), \quad Z = \frac{\mu(\mathbf{x}) - f^+}{\sigma(\mathbf{x})}$$

where $\Phi$ and $\phi$ are the standard normal CDF and PDF. EI is zero when $\sigma = 0$ (fully explored) and positive when either $\mu > f^+$ (exploit) or $\sigma$ is large (explore).

**GP Upper Confidence Bound (GP-UCB):**

$$\alpha_{\text{UCB}}(\mathbf{x}) = \mu(\mathbf{x}) + \beta_t \sigma(\mathbf{x})$$

where $\beta_t$ is an exploration parameter. Setting $\beta_t = \sqrt{2 \log(t^{d/2+2} \pi^2 / 3\delta)}$ yields a cumulative regret bound of $O(\sqrt{T \gamma_T \log T})$ where $\gamma_T$ is the maximum information gain (Srinivas et al., 2010).

**Knowledge Gradient (KG):**

$$\text{KG}(\mathbf{x}) = \mathbb{E}\left[\max_{\mathbf{x}'} \mu_{n+1}(\mathbf{x}') \mid \text{next observation at } \mathbf{x}\right] - \max_{\mathbf{x}'} \mu_n(\mathbf{x}')$$

KG measures the expected improvement in the **best predicted point** (not the best observation). It is one-step Bayes-optimal and performs well in noisy settings and when the goal is recommendation (not just evaluation).

### The Bayesian Optimization Loop

1. **Initialize:** Evaluate $f$ at a small set of points (Latin hypercube or random).
2. **Fit GP:** Condition the GP on all observations $\mathcal{D}_t$.
3. **Optimize acquisition:** $\mathbf{x}_{t+1} = \arg\max_{\mathbf{x}} \alpha(\mathbf{x} | \mathcal{D}_t)$.
4. **Evaluate:** $y_{t+1} = f(\mathbf{x}_{t+1}) + \epsilon_{t+1}$.
5. **Update:** $\mathcal{D}_{t+1} = \mathcal{D}_t \cup \{(\mathbf{x}_{t+1}, y_{t+1})\}$.
6. **Repeat** until budget exhausted.
7. **Recommend:** Return $\mathbf{x}^* = \arg\max_{\mathbf{x}_i \in \mathcal{D}} y_i$ or $\arg\max_{\mathbf{x}} \mu_T(\mathbf{x})$.

### BO vs. Reinforcement Learning

| Criterion | Bayesian Optimization | Reinforcement Learning |
|-----------|----------------------|----------------------|
| **Sample efficiency** | Excellent (designed for $<1000$ evaluations) | Poor (often needs millions) |
| **Dimensionality** | Low-medium ($d \leq 20$ typically) | Handles high-dimensional state/action spaces |
| **Sequential decisions** | Typically single-step (optimize parameters) | Multi-step (sequential policies) |
| **Model** | Explicit surrogate (GP) | Often model-free; model-based RL uses learned dynamics |
| **Exploration** | Principled (acquisition functions with guarantees) | Heuristic ($\epsilon$-greedy) or learned (curiosity) |
| **Best for** | Hyperparameter tuning, design optimization | Control, games, sequential interaction |

**When to use BO:** The objective is expensive to evaluate, the parameter space is low-dimensional, and you need a good solution in few evaluations. Classic examples: hyperparameter optimization, drug design, materials science, experimental design.

**When to use RL:** The problem is inherently sequential, the action space is large or continuous, and you can afford many interactions (simulation or real-time).

**Hybrid approaches:** Use BO to tune RL hyperparameters. Use RL for sequential decision-making within each BO evaluation. In Arena, BO tunes the economy configuration (low-dimensional parameter vector) while the economy's effect on users unfolds over time.

## Formal Definitions

**Definition (Gaussian Process).** A Gaussian process is a collection of random variables, any finite subset of which has a joint Gaussian distribution.

**Definition (Positive Definite Kernel).** A function $k: \mathcal{X} \times \mathcal{X} \rightarrow \mathbb{R}$ is a positive definite kernel if for all $n$, all $\{x_i\}_{i=1}^n \subset \mathcal{X}$, and all $\{c_i\}_{i=1}^n \subset \mathbb{R}$:

$$\sum_{i=1}^{n} \sum_{j=1}^{n} c_i c_j k(x_i, x_j) \geq 0$$

**Theorem (Bayesian Regret Bound, Srinivas et al. 2010).** For GP-UCB with appropriate $\beta_t$, the cumulative Bayesian regret satisfies:

$$R_T = \sum_{t=1}^{T} \left[f(\mathbf{x}^*) - f(\mathbf{x}_t)\right] \leq O\left(\sqrt{T \gamma_T \log T}\right)$$

where $\gamma_T = \max_{\{x_1,\dots,x_T\}} \frac{1}{2} \log \det(I + \sigma_n^{-2} K_T)$ is the maximum information gain. For the SE kernel, $\gamma_T = O((\log T)^{d+1})$; for Matern-$\nu$, $\gamma_T = O(T^{d(d+1)/(2\nu+d(d+1))} (\log T))$.

## Worked Examples

### Example 1: GP Posterior with Two Observations

Let $k(x, x') = \exp(-(x - x')^2 / 2)$ (SE kernel, $\ell = 1, \sigma_f = 1$), no noise ($\sigma_n = 0$), zero mean.

Observations: $(x_1, y_1) = (0, 1)$ and $(x_2, y_2) = (2, -1)$.

$$K = \begin{pmatrix} 1 & e^{-2} \\ e^{-2} & 1 \end{pmatrix}, \quad K^{-1} = \frac{1}{1 - e^{-4}} \begin{pmatrix} 1 & -e^{-2} \\ -e^{-2} & 1 \end{pmatrix}$$

Predict at $x_* = 1$:

$$\mathbf{k}_* = \begin{pmatrix} e^{-1/2} \\ e^{-1/2} \end{pmatrix}$$

$$\mu_* = \mathbf{k}_*^\top K^{-1} \mathbf{y} = \frac{e^{-1/2}}{1 - e^{-4}} \left[(1 - e^{-2}) \cdot 1 + (-e^{-2} + 1) \cdot (-1)\right]$$

$$= \frac{e^{-1/2}}{1 - e^{-4}} \left[(1 - e^{-2}) - (1 - e^{-2})\right] = 0$$

By symmetry: $x_* = 1$ is equidistant from both observations with equal-magnitude but opposite values. The posterior mean is 0.

$$\sigma_*^2 = 1 - \frac{2e^{-1}}{1 - e^{-4}}(1 - e^{-2}) = 1 - \frac{2e^{-1}(1 - e^{-2})}{1 - e^{-4}} = 1 - \frac{2e^{-1}}{1 + e^{-2}} \approx 1 - \frac{0.736}{1.135} \approx 0.351$$

So $f(1) | \mathcal{D} \sim \mathcal{N}(0, 0.351)$: moderate uncertainty at the midpoint.

### Example 2: Expected Improvement Calculation

Continuing from Example 1: best observation $f^+ = 1$ (at $x = 0$). Consider candidate $x_* = 3$.

$$\mathbf{k}_* = \begin{pmatrix} e^{-9/2} \\ e^{-1/2} \end{pmatrix} \approx \begin{pmatrix} 0.011 \\ 0.607 \end{pmatrix}$$

After computing: $\mu_* \approx -0.59$, $\sigma_* \approx 0.73$.

$$Z = \frac{-0.59 - 1}{0.73} = \frac{-1.59}{0.73} \approx -2.18$$

$$\text{EI}(x_* = 3) = (-1.59) \cdot \Phi(-2.18) + 0.73 \cdot \phi(-2.18)$$
$$\approx (-1.59)(0.015) + 0.73(0.037) \approx -0.024 + 0.027 = 0.003$$

Very small EI --- the model predicts low value with moderate certainty. The BO loop would prefer evaluating near $x = 0$ (exploit near the best) or far from all data (explore) over $x = 3$.

### Example 3: GP-UCB Decision

Same setup. Compare two candidates using $\text{UCB}(\mathbf{x}) = \mu(\mathbf{x}) + 2\sigma(\mathbf{x})$ ($\beta = 2$):

- $x = 1$: $\mu = 0, \sigma \approx 0.59$. UCB $= 0 + 2(0.59) = 1.18$.
- $x = -2$: far from data, $\mu \approx 0$ (prior), $\sigma \approx 0.97$. UCB $= 0 + 2(0.97) = 1.94$.
- $x = 0.2$: near best observation, $\mu \approx 0.9, \sigma \approx 0.19$. UCB $= 0.9 + 0.38 = 1.28$.

GP-UCB selects $x = -2$: maximum uncertainty dominates. This is exploratory. With smaller $\beta$, the exploitative $x = 0.2$ would be preferred.

## Arena Connection

Bayesian Optimization is the most natural optimization framework for Arena experiments:

- **Parameter space:** Arena economy parameters (XP multipliers, badge thresholds, mission difficulty) form a low-dimensional continuous space --- ideal for BO.
- **Expensive evaluations:** Each configuration must run for a time window to accumulate meaningful engagement metrics. Evaluations are expensive in wall-clock time, not computation.
- **Noisy observations:** User engagement metrics are inherently noisy. The GP's noise model $\sigma_n^2$ handles this naturally.
- **SDK integration:** The `agent.submit_action(config)` call corresponds to a BO evaluation; `agent.get_metrics()` returns the noisy observation. A BO agent loops: fit GP on history, optimize acquisition function, submit next configuration.
- **Multi-point BO:** If Arena allows parallel configurations (different user cohorts), batch acquisition methods (e.g., q-EI) enable evaluating multiple configurations simultaneously.

## Discussion Questions

1. The GP posterior contracts around observations and reverts to the prior far from data. What happens if the prior (mean function, kernel) is badly misspecified? How would you detect and correct for this in an Arena experiment?

2. Expected Improvement and GP-UCB represent different exploration-exploitation tradeoffs. Design an experiment (using Arena or otherwise) to empirically compare them. What metrics would you use, and how many evaluations would you need for statistical significance?

3. BO scales poorly beyond $\sim$20 dimensions due to the curse of dimensionality. Arena's economy might have 30+ tunable parameters. Propose a strategy to make BO work in this setting. (Consider: random embeddings, additive structure, active subspaces.)

4. How does the maximum information gain $\gamma_T$ relate to the effective dimensionality of the optimization problem? Why does the SE kernel give $\gamma_T = O((\log T)^{d+1})$ (near dimension-free) while Matern kernels give polynomial dependence?

## Further Reading

1. **Shahriari, B. et al. (2016).** "Taking the Human Out of the Loop: A Review of Bayesian Optimization." *Proceedings of the IEEE*, 104(1). --- The standard survey covering GP models, acquisition functions, and practical considerations.

2. **Srinivas, N., Krause, A., Kakade, S., & Seeger, M. (2010).** "Gaussian Process Optimization in the Bandit Setting: No Regret and Experimental Design." *ICML*. --- Derives the GP-UCB algorithm with rigorous regret bounds.

3. **Frazier, P. I. (2018).** "A Tutorial on Bayesian Optimization." *arXiv:1807.02811*. --- Accessible introduction covering EI, Knowledge Gradient, and practical implementation guidance. Excellent starting point for implementation.
