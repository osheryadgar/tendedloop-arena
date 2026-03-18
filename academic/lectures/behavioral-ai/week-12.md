# Week 12: Personalization and Adaptive Gamification

> Behavioral AI: The Science of Incentive Design

## Overview

This lecture shifts from population-level optimization to individual-level adaptation. We formalize user types as feature vectors, apply collaborative filtering to predict reward preferences, and introduce contextual bandits (LinUCB) as the core algorithm for adaptive gamification. The central design question — one agent per user vs. one agent per population — has deep implications for sample efficiency, privacy, and fairness. We close with privacy-preserving methods that enable personalization without exposing individual behavior.

## Key Concepts

### User Modeling: From Taxonomies to Feature Spaces

Traditional user typologies provide qualitative labels. We convert them into quantitative feature vectors for algorithmic use.

**Bartle's Player Types (1996).** Four types defined by two axes: acting vs. interacting, players vs. world. Killers (acting on players), Achievers (acting on world), Socializers (interacting with players), Explorers (interacting with world). We encode these as a 4-dimensional vector:

$$\mathbf{u}_i = (u_{\text{killer}}, u_{\text{achiever}}, u_{\text{socializer}}, u_{\text{explorer}})^T, \quad u_k \in [0, 1], \quad \sum_k u_k = 1$$

Each user is a mixture, not a discrete type. The vector is estimated from behavioral signals: an achiever checks leaderboards frequently; an explorer tries new features; a socializer interacts with team mechanics.

**Hexad Model (Tondello et al., 2016).** Six types: Philanthropist, Socialiser, Free Spirit, Achiever, Player, Disruptor. We extend to a 6-dimensional feature vector $\mathbf{u}_i \in \mathbb{R}^6$, derived from the validated 24-item Hexad questionnaire or inferred from behavioral data. The Hexad model maps to specific gamification elements:

| Type | Preferred Elements | Feature Signal |
|------|--------------------|----------------|
| Philanthropist | Purpose, meaning | High-quality feedback, team contributions |
| Socialiser | Teams, social features | Referral activity, leaderboard views |
| Free Spirit | Exploration, customization | Feature discovery, diverse actions |
| Achiever | Challenges, badges | Badge pursuit, level progression focus |
| Player | Points, rewards | XP-maximizing behavior, reward redemption |
| Disruptor | Innovation, change | Unusual behavior patterns, edge cases |

The key insight: different user types respond differently to the same gamification parameters. A one-size-fits-all configuration is suboptimal by definition.

### Collaborative Filtering for Reward Personalization

Given a user-reward interaction matrix $\mathbf{R} \in \mathbb{R}^{N \times M}$ where $R_{ij}$ is user $i$'s engagement response to gamification configuration $j$ (partially observed), we factor:

$$\mathbf{R} \approx \mathbf{U} \mathbf{V}^T$$

where $\mathbf{U} \in \mathbb{R}^{N \times d}$ (user latent factors) and $\mathbf{V} \in \mathbb{R}^{M \times d}$ (configuration latent factors), with $d \ll \min(N, M)$.

**Objective (regularized):**

$$\min_{\mathbf{U}, \mathbf{V}} \sum_{(i,j) \in \Omega} (R_{ij} - \mathbf{u}_i^T \mathbf{v}_j)^2 + \lambda(\|\mathbf{U}\|_F^2 + \|\mathbf{V}\|_F^2)$$

where $\Omega$ is the set of observed entries. Solved via alternating least squares (ALS) or stochastic gradient descent.

**Prediction.** For an unseen user-config pair $(i, j')$: $\hat{R}_{ij'} = \mathbf{u}_i^T \mathbf{v}_{j'}$. This allows predicting which gamification configuration a user will respond to best, without having tested it on them directly.

**Cold-start problem.** New users have no interaction history. Solutions: (1) use Hexad scores or demographic features as side information ($\mathbf{u}_i = f(\mathbf{x}_i)$ where $\mathbf{x}_i$ are observed features); (2) assign to the population-average configuration initially, then adapt.

### Contextual Bandits: LinUCB

The contextual bandit framework formalizes adaptive gamification. At each decision point $t$:

1. Observe context $\mathbf{x}_t$ (user features, current state, time).
2. Choose arm $a_t \in \{1, \ldots, K\}$ (gamification configuration).
3. Observe reward $r_t$ (engagement metric).

**LinUCB (Li et al., 2010).** Assume the expected reward of arm $a$ given context $\mathbf{x}$ is linear:

$$E[r | \mathbf{x}, a] = \mathbf{x}^T \boldsymbol{\theta}_a$$

For each arm $a$, maintain:
- Design matrix: $\mathbf{A}_a = \mathbf{I}_d + \sum_{t: a_t=a} \mathbf{x}_t \mathbf{x}_t^T$
- Response vector: $\mathbf{b}_a = \sum_{t: a_t=a} r_t \mathbf{x}_t$
- Parameter estimate: $\hat{\boldsymbol{\theta}}_a = \mathbf{A}_a^{-1} \mathbf{b}_a$

Select the arm with highest upper confidence bound:

$$a_t = \arg\max_a \left(\hat{\boldsymbol{\theta}}_a^T \mathbf{x}_t + \alpha \sqrt{\mathbf{x}_t^T \mathbf{A}_a^{-1} \mathbf{x}_t}\right)$$

The second term is the exploration bonus — proportional to the uncertainty of the reward prediction for this context-arm pair. The parameter $\alpha$ controls the exploration-exploitation tradeoff.

**Regret bound.** LinUCB achieves $O(d\sqrt{T \log T})$ regret, scaling with feature dimension $d$ and time horizon $T$. This is near-optimal for linear contextual bandits.

**For gamification.** The context $\mathbf{x}_t$ includes user type features (Hexad scores), behavioral history (streak length, total XP, days since signup), and temporal features (day of week, time of day). Arms are discretized gamification configurations (e.g., 5 preset "profiles"). The algorithm learns which profile works best for which user type.

### Agent-Per-User vs. Agent-Per-Population

**Agent-per-user.** Each user has a dedicated optimization process. Maximum personalization but minimum data — each "experiment" has $N = 1$. Statistical inference is impossible in the traditional sense; we rely on sequential decisions and bandit convergence.

Formally, for user $i$, the bandit observes a stream of rewards $r_{i,1}, r_{i,2}, \ldots$ The convergence rate of the estimated optimal arm depends on the number of observations per arm, which grows as $O(T/K)$ — slow when $K$ is large.

**Agent-per-population.** One agent optimizes for all users. Maximum data efficiency but ignores heterogeneity. The estimated optimal configuration $\theta^*$ minimizes average regret:

$$\theta^* = \arg\min_\theta \frac{1}{N}\sum_{i=1}^{N} \text{Regret}_i(\theta)$$

This is Jensen's inequality territory: the average-optimal policy can be far from any individual's optimal.

**Contextual bandits as the middle ground.** LinUCB is formally an agent-per-population that personalizes via context. All users contribute data, but the predicted reward depends on the user's context vector. This achieves personalization with population-level sample efficiency.

**The practical tradeoff:**

| Approach | Sample efficiency | Personalization | Privacy risk |
|----------|-------------------|-----------------|--------------|
| Per-population | High | None | Low |
| Contextual bandit | High | Moderate | Medium |
| Per-user | Very low | Full | High |

### Privacy-Preserving Personalization

Personalization requires user data. Two frameworks protect privacy while enabling adaptation.

**Federated Learning.** Instead of centralizing user data, each user's device maintains a local model. Updates are aggregated:

1. Server sends global model $\boldsymbol{\theta}$ to all users.
2. Each user $i$ computes local gradient $\nabla_i \mathcal{L}(\boldsymbol{\theta}; D_i)$ on their private data $D_i$.
3. Server aggregates: $\boldsymbol{\theta} \leftarrow \boldsymbol{\theta} - \eta \cdot \frac{1}{N}\sum_i \nabla_i \mathcal{L}$.

The server never sees individual data, only aggregated gradients. For gamification: the reward model improves from collective data without any single user's behavior being exposed.

**Differential Privacy.** Add calibrated noise to queries or model updates to ensure that any individual's data has bounded influence on the output.

$(\epsilon, \delta)$-differential privacy: for any dataset $D$ and $D'$ differing in one record, and any output set $S$:

$$P(\mathcal{M}(D) \in S) \leq e^\epsilon \cdot P(\mathcal{M}(D') \in S) + \delta$$

For gamification metrics, this means: "Whether or not user $i$ participates, the published aggregate metric changes by at most a bounded amount." Noise is added via the Gaussian mechanism:

$$\hat{m} = m + \mathcal{N}\left(0, \frac{2\ln(1.25/\delta) \cdot \Delta_2^2}{\epsilon^2}\right)$$

where $\Delta_2$ is the $L_2$ sensitivity of the query (how much one user can change the metric).

**Privacy-utility tradeoff.** Stronger privacy (smaller $\epsilon$) requires more noise, reducing the signal quality for personalization. With $N$ users, the noise-to-signal ratio scales as $O(1/(\epsilon\sqrt{N}))$ — larger populations enable stronger privacy guarantees with less utility loss.

## Formal Models

### Bayesian User Type Inference

Instead of asking users to complete a Hexad questionnaire, infer their type from behavior using Bayesian updating. Let $\mathbf{z}$ be the latent type distribution and $\mathbf{a}_{1:t}$ be observed actions:

$$P(\mathbf{z} | \mathbf{a}_{1:t}) \propto P(\mathbf{a}_{1:t} | \mathbf{z}) \cdot P(\mathbf{z})$$

With a Dirichlet prior $\mathbf{z} \sim \text{Dir}(\boldsymbol{\alpha}_0)$ and multinomial action likelihoods per type, the posterior is also Dirichlet:

$$\mathbf{z} | \mathbf{a}_{1:t} \sim \text{Dir}(\boldsymbol{\alpha}_0 + \mathbf{n}_t)$$

where $n_{t,k}$ counts actions associated with type $k$. After sufficient observations, the posterior concentrates on the user's true type mixture.

### Multi-Armed Bandit with User Segmentation

Segment users into $S$ groups via clustering on feature vectors. Within each segment, run an independent bandit. The effective sample size per arm per segment is $N_s / K$ where $N_s$ is the segment size. Optimal segmentation balances granularity (more segments = more personalization) against data (fewer users per segment = higher variance):

$$S^* = \arg\min_S \sum_{s=1}^{S} \text{Regret}_s(T, N_s, K)$$

This is a bias-variance tradeoff: too few segments (underfitting user heterogeneity) vs. too many (overfitting to noise within small segments).

## Worked Examples

### Example 1: LinUCB for Adaptive XP

Context features: $\mathbf{x} = (\text{tenure}_{\text{days}}, \text{streak}_{\text{length}}, \text{hexad}_{\text{achiever}}, \text{hexad}_{\text{socializer}}, 1)^T$ (5-dimensional with intercept). Arms: 3 configurations — Low XP / High Social, High XP / Low Social, Balanced. After 50 observations per arm:

$$\hat{\boldsymbol{\theta}}_1 = (0.02, 0.15, -0.3, 0.8, 1.2)^T$$

For a new user with $\mathbf{x} = (30, 5, 0.7, 0.2, 1)^T$:
- Arm 1 predicted reward: $\mathbf{x}^T\hat{\boldsymbol{\theta}}_1 = 0.6 + 0.75 - 0.21 + 0.16 + 1.2 = 2.50$
- UCB for arm 1: $2.50 + 1.0 \cdot \sqrt{\mathbf{x}^T \mathbf{A}_1^{-1} \mathbf{x}} = 2.50 + 0.35 = 2.85$

The algorithm selects the arm with highest UCB across all 3 arms. This high-achiever, low-socializer user is likely matched to the High XP / Low Social configuration.

### Example 2: Cold-Start Resolution

A new user joins with no behavioral history. The Hexad questionnaire yields $\mathbf{h} = (0.6, 0.1, 0.1, 0.1, 0.05, 0.05)$ — strong Philanthropist. The collaborative filtering model maps this to a latent factor: $\mathbf{u}_{\text{new}} = f(\mathbf{h}) = (0.8, -0.2, 0.3)$ in a 3-dimensional latent space. The nearest neighbor in the configuration latent space $\mathbf{V}$ suggests configuration $j = 7$ (purpose-driven rewards: bonus XP for high-quality feedback, team goal contributions weighted heavily). After 10 interactions, the user's behavioral data refines $\mathbf{u}_{\text{new}}$ via online matrix factorization.

### Example 3: Differential Privacy Budget

An enterprise wants to publish per-group engagement statistics while protecting individual users. Group has $N = 80$ users. Query: mean daily XP. Sensitivity $\Delta_1 = \text{maxXP}/N$. With `dailyXpCap = 200`: $\Delta_1 = 200/80 = 2.5$. For $\epsilon = 1.0$, $\delta = 10^{-5}$:

$$\text{Noise } \sigma = \frac{\sqrt{2\ln(1.25/10^{-5})} \cdot 2.5}{1.0} = \frac{\sqrt{23.5} \cdot 2.5}{1.0} = 4.85 \cdot 2.5 = 12.1$$

The published mean has $\pm 12.1$ noise. If the true mean is 45 XP, the published value is in $[33, 57]$ with high probability. This is a wide range — strong privacy but limited utility. With $N = 500$ users, $\Delta_1 = 0.4$ and noise drops to $1.94$, much more useful.

## Arena Connection

Arena's multi-variant architecture naturally supports personalization experiments:

- **Variant as arm.** Each Arena variant is a bandit arm with a fixed configuration. The experiment engine's randomized assignment implements an explore-then-commit strategy. A student agent could implement LinUCB on top, using user features to decide which variant to emphasize.
- **User features.** Arena exposes user-level behavioral data (tenure, activity history, streak patterns) that serve as the context vector $\mathbf{x}$ for contextual bandits. The challenge is featurizing this data into a compact, informative representation.
- **Segment-level optimization.** Arena experiments can be designed with segments in mind — e.g., one variant optimized for power users (high tenure, long streaks) and another for new users (short tenure, no streaks). The agent's challenge is discovering the right segmentation without prior knowledge.
- **Privacy in enterprise context.** Arena operates in enterprise environments where employee behavior data is sensitive. The differential privacy framework is directly applicable: aggregate metrics can be published (to building managers) while individual-level data remains protected. The `dailyXpCap` parameter indirectly bounds sensitivity, making privacy guarantees cheaper.

## Discussion Questions

1. **Feature engineering.** What behavioral signals would you use to infer a user's Hexad type without a questionnaire? Design a feature extraction pipeline that maps raw event logs (scans, feedbacks, leaderboard views, badge checks) to a 6-dimensional Hexad estimate.

2. **Fairness in personalization.** If LinUCB learns that a particular demographic group responds best to competitive leaderboards while another prefers cooperative mechanics, is it fair to show them different experiences? When does personalization become discrimination? Formalize a fairness constraint for the contextual bandit.

3. **Exploration cost.** In LinUCB, the exploration bonus $\alpha\sqrt{\mathbf{x}^T \mathbf{A}^{-1} \mathbf{x}}$ means some users receive suboptimal configurations while the algorithm explores. In an enterprise gamification system (real employees), is this exploration cost ethical? How would you minimize it?

4. **Privacy-personalization frontier.** Plot the theoretical tradeoff between differential privacy budget $\epsilon$ and personalization quality (measured by bandit regret). At what $\epsilon$ does personalization become useless? Does the answer depend on population size?

## Further Reading

- **Li, L., Chu, W., Langford, J., & Schapire, R. (2010).** "A Contextual-Bandit Approach to Personalized News Article Recommendation." *WWW.* The LinUCB paper — foundational for contextual personalization.
- **Tondello, G. F. et al. (2016).** "The Gamification User Types Hexad Scale." *CHI PLAY.* The validated psychometric instrument for user type assessment.
- **Kairouz, P. et al. (2021).** "Advances and Open Problems in Federated Learning." *Foundations and Trends in Machine Learning.* Comprehensive survey of federated learning with direct applications to privacy-preserving personalization.
