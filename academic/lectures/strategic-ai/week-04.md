# Week 4: The Multi-Armed Bandit Problem

> Strategic AI: Multi-Agent Systems & Optimization

## Overview

The multi-armed bandit problem distills the explore-exploit tradeoff to its purest form: an agent repeatedly chooses among K actions ("arms"), each with an unknown reward distribution, seeking to maximize cumulative reward. This lecture formalizes the problem, establishes that logarithmic regret is the best any algorithm can achieve (Lai-Robbins lower bound), and derives the UCB1 algorithm step-by-step from concentration inequalities. Understanding bandits is essential because they form the foundation of the Arena platform's optimization loop.

## Key Concepts

### The K-Armed Bandit Problem

> **Definition (Stochastic K-Armed Bandit).** A stochastic K-armed bandit problem consists of:
> - **K arms** (actions), indexed {1, 2, ..., K}
> - Each arm *i* has an unknown reward distribution **P_i** with mean **mu_i**
> - At each round **t = 1, 2, ..., T**, the agent selects an arm **A_t in {1, ..., K}**
> - The agent observes a reward **X_t ~ P_{A_t}**, drawn i.i.d. from the selected arm's distribution
> - The agent observes **only** the reward of the arm it pulled (bandit feedback)

Let **mu* = max_i mu_i** be the mean of the best arm, and **Delta_i = mu* - mu_i** be the **suboptimality gap** of arm *i*. Define **i* = argmax_i mu_i** as the optimal arm.

### Regret

The agent's performance is measured by how much reward it forfeits compared to always playing the optimal arm.

> **Definition (Regret).** The (pseudo-)regret of an algorithm after T rounds is:
>
> **R_T = T * mu* - sum_{t=1}^{T} mu_{A_t} = sum_{t=1}^{T} Delta_{A_t}**

Equivalently, if **N_i(T)** is the number of times arm *i* is pulled in *T* rounds:

> **R_T = sum_{i=1}^{K} Delta_i * E[N_i(T)]**

This decomposition is crucial: regret grows by Delta_i each time a suboptimal arm *i* is pulled. To minimize regret, we must quickly identify and avoid arms with large gaps, while still exploring enough to confirm which arm is best.

### The Explore-Exploit Tradeoff

- **Pure exploitation** (always play the arm with highest observed mean): Risks locking onto a suboptimal arm due to early bad luck. Can incur linear regret.
- **Pure exploration** (pull each arm equally): Learns well but wastes half the budget on suboptimal arms. Linear regret.
- **Smart algorithms** balance exploration and exploitation, achieving sublinear regret.

### The Lai-Robbins Lower Bound

Any "consistent" algorithm (one that achieves sublinear regret on every bandit instance) must incur at least logarithmic regret:

> **Theorem (Lai & Robbins, 1985).** For any consistent algorithm and any bandit instance with gaps Delta_i > 0:
>
> **lim inf_{T -> infinity} R_T / ln(T) >= sum_{i : Delta_i > 0} Delta_i / KL(P_i, P_{i*})**
>
> where **KL(P_i, P_{i*})** is the KL divergence from arm *i*'s distribution to the optimal arm's distribution.

For Bernoulli bandits with means mu_i and mu*, this becomes:

> **lim inf R_T / ln(T) >= sum_i Delta_i / kl(mu_i, mu*)**

where kl(p, q) = p ln(p/q) + (1-p) ln((1-p)/(1-q)).

**Intuition:** To distinguish arm *i* from arm *i**, you need roughly 1/KL(P_i, P_{i*}) samples of arm *i*. Each such sample incurs regret Delta_i. Across all suboptimal arms, you pay at least sum_i Delta_i / KL(...) per factor of ln(T). No algorithm can avoid this information-theoretic cost.

### Epsilon-Greedy

The simplest approach to balancing exploration and exploitation:

**Algorithm:** With probability epsilon, pull a uniformly random arm (explore). With probability 1 - epsilon, pull the arm with highest empirical mean (exploit).

With constant epsilon, this incurs **linear regret** O(epsilon * T * Delta) because it never stops exploring. With decaying epsilon_t = min(1, cK / (d^2 * t)) for appropriate constants c, d, the regret is O(K ln(T) / Delta), which is order-optimal. However, the constants depend on Delta, which is unknown.

### Explore-Then-Commit (ETC)

**Algorithm:** Pull each arm *m* times (exploration phase: K*m rounds total). Then commit to the arm with highest empirical mean for the remaining T - Km rounds.

> **Theorem.** With m = ceil((4/Delta^2) * ln(T * Delta^2 / 4)), ETC achieves regret O((K/Delta) * ln(T)).

**Limitation:** The optimal m depends on Delta, which is unknown. If m is too small, we commit to the wrong arm. If m is too large, we waste budget exploring. ETC illustrates why *adaptive* algorithms are preferable.

### UCB1: Derivation from Hoeffding's Inequality

UCB1 (Upper Confidence Bound) is the first algorithm we derive from first principles. It embodies **optimism in the face of uncertainty**: treat each arm as if it might be as good as its upper confidence bound.

**Step 1: Hoeffding's Inequality.**

> **Lemma (Hoeffding).** Let X_1, ..., X_n be i.i.d. random variables with X_i in [0, 1] and mean mu. Then:
>
> **P(|X_bar_n - mu| >= epsilon) <= 2 exp(-2n * epsilon^2)**

where X_bar_n = (1/n) sum X_i is the empirical mean.

**Step 2: Constructing the Confidence Bound.**

We want P(mu_i <= UCB_i) to be high. Setting the right tail:

P(X_bar_n - mu >= epsilon) <= exp(-2n * epsilon^2)

Choose epsilon = sqrt(ln(t) / (2 * N_i(t))) so that the failure probability is at most t^{-1} per arm per round (via union bound over time). This gives:

> **UCB_i(t) = X_bar_{N_i(t)} + sqrt(ln(t) / (2 * N_i(t)))**

**Step 3: The UCB1 Algorithm.**

> **Algorithm (UCB1).** Initialize by pulling each arm once. At round t, pull:
>
> **A_t = argmax_i [ X_bar_i(t-1) + sqrt(ln(t) / (2 * N_i(t-1))) ]**

**Step 4: Regret Bound.**

> **Theorem (Auer, Cesa-Bianchi, Fischer, 2002).** UCB1 achieves:
>
> **E[R_T] <= sum_{i : Delta_i > 0} (2 ln(T) / Delta_i) + (1 + pi^2/3) * sum_i Delta_i**
>
> This is **O((K ln T) / Delta_min)** — logarithmic in T, matching Lai-Robbins up to constants.

**Proof sketch.** Arm *i* is pulled at time *t* only if UCB_i(t) >= UCB_{i*}(t). This requires either:
1. The best arm's mean is underestimated (UCB_{i*} is too low), or
2. Arm *i*'s mean is overestimated (UCB_i is too high).

Event 1 happens with probability O(1/t^2) (by Hoeffding). Event 2 can only happen O(ln(T) / Delta_i^2) times before the confidence interval shrinks below Delta_i. Summing over time and arms gives the bound.

### Comparing the Three Algorithms

| Algorithm | Regret | Adaptive? | Gap-dependent? |
|-----------|--------|-----------|----------------|
| epsilon-greedy (constant) | O(epsilon * K * T) = linear | No | No |
| ETC | O((K/Delta) ln T) | No | Yes (needs Delta) |
| UCB1 | O((K/Delta) ln T) | Yes | No (automatic) |

UCB1 wins: it is fully adaptive, requires no knowledge of Delta, and achieves near-optimal regret.

## Formal Definitions

> **Definition (Consistency).** An algorithm is consistent if E[N_i(T)] = o(T^a) for every suboptimal arm *i*, every a > 0, and every bandit instance.

> **Theorem (Lai-Robbins Lower Bound).** See statement above. The key implication: O(ln T) regret is the best achievable; any algorithm with o(ln T) regret on some instance must have super-logarithmic regret on another.

> **Theorem (UCB1 Regret).** See statement above. The gap-free form is: E[R_T] = O(sqrt(KT ln T)).

## Worked Examples

### Example 1: Two-Armed Bernoulli Bandit

Arms: mu_1 = 0.6 (optimal), mu_2 = 0.4. Gap Delta_2 = 0.2.

**Round 1**: Pull arm 1. Observe X_1 = 1 (success). X_bar_1 = 1, N_1 = 1.
**Round 2**: Pull arm 2. Observe X_2 = 0 (failure). X_bar_2 = 0, N_2 = 1.
**Round 3**: UCB_1 = 1 + sqrt(ln(3)/2) = 1 + 0.741 = 1.741. UCB_2 = 0 + sqrt(ln(3)/2) = 0.741. Pull arm 1.
**Round 4**: Say X_3 = 0. X_bar_1 = 1/2. UCB_1 = 0.5 + sqrt(ln(4)/4) = 0.5 + 0.589 = 1.089. UCB_2 = 0 + sqrt(ln(4)/2) = 0.833. Pull arm 1.
**Round 5**: Say X_4 = 1. X_bar_1 = 2/3. UCB_1 = 0.667 + sqrt(ln(5)/6) = 0.667 + 0.519 = 1.186. UCB_2 = 0 + sqrt(ln(5)/2) = 0.898. Pull arm 1.

Arm 2 has been pulled only once. Eventually its UCB will exceed arm 1's (when N_1 grows enough to shrink its bonus), triggering another exploration of arm 2. But it won't be pulled often — the gap is clear.

### Example 2: Lai-Robbins Bound Calculation

Two Bernoulli arms: mu_1 = 0.7, mu_2 = 0.5. The KL divergence:

kl(0.5, 0.7) = 0.5 * ln(0.5/0.7) + 0.5 * ln(0.5/0.3)
             = 0.5 * ln(0.714) + 0.5 * ln(1.667)
             = 0.5 * (-0.336) + 0.5 * (0.511)
             = -0.168 + 0.256 = 0.088

Lower bound: R_T >= (Delta_2 / kl(mu_2, mu_1)) * ln(T) = (0.2 / 0.088) * ln(T) = 2.27 * ln(T).

For T = 10000: R_T >= 2.27 * 9.21 = 20.9. Even the best algorithm must incur at least ~21 units of regret. UCB1 will typically incur somewhat more due to constant factors.

### Example 3: When ETC Fails

Arms: mu_1 = 0.51, mu_2 = 0.49. Delta = 0.02. Optimal ETC exploration: m = (4/0.0004) * ln(T * 0.0004/4) which for T = 10000 gives m ~ 10000 * something negative. The gap is so small that ETC needs to explore almost the entire horizon before committing, leaving no rounds for exploitation. UCB1 handles this gracefully: it gradually shifts toward the better arm, accumulating regret proportional to ln(T) / 0.02.

## Arena Connection

The multi-armed bandit is the *direct* model of the Arena platform. Each Arena experiment presents K arms representing different service configurations (e.g., cleaning schedules, amenity layouts). The agent's job is to identify and exploit the best configuration while minimizing cumulative regret.

Workshop Session 4 has students implement three agents:
1. **EpsilonGreedyAgent**: Fixed epsilon = 0.1, observing linear regret.
2. **ETCAgent**: Fixed exploration budget, seeing the failure mode when Delta is small.
3. **UCBAgent**: Implementing the UCB1 formula and watching logarithmic regret emerge.

The SDK's `agent.pull(arm_id)` corresponds to selecting an arm, and the returned reward is the bandit feedback. Students can plot cumulative regret against the theoretical bounds derived in this lecture.

Key Arena-specific nuances:
- Reward distributions may be non-stationary (facility conditions change) — motivating sliding-window or discounted UCB variants.
- The budget T is finite and known, enabling Bayesian approaches (Week 5).
- In competitive experiments, other agents' pulls may affect your rewards, breaking the i.i.d. assumption.

## Discussion Questions

1. UCB1's confidence bonus is sqrt(ln(t) / (2n)). What happens if you increase the constant? You get more exploration (wider confidence intervals). When might you want this? When might it hurt?

2. The Lai-Robbins lower bound depends on KL divergence, not just the gap Delta. Give an intuitive explanation: why are some bandit instances harder than others, even with the same gap?

3. Epsilon-greedy with constant epsilon has linear regret, yet it remains popular in practice (A/B testing platforms, recommendation systems). Why? What practical considerations favor simplicity over optimal regret?

4. Consider a bandit where arm rewards are adversarially chosen (not stochastic). Does UCB1 still work? What regret guarantee can you hope for? (Hint: research EXP3.)

## Further Reading

- **Lattimore & Szepesvari (2020), *Bandit Algorithms*, Chapters 1-8** — The definitive modern textbook treatment. Chapter 7 on UCB is particularly clear, with a cleaner proof than the original paper.
- **Auer, Cesa-Bianchi, & Fischer (2002), "Finite-time Analysis of the Multiarmed Bandit Problem"** — The UCB1 paper. Introduced the finite-time analysis framework that replaced the asymptotic analyses of Lai-Robbins.
- **Bubeck & Cesa-Bianchi (2012), "Regret Analysis of Stochastic and Nonstochastic Multi-Armed Bandit Problems"** — Comprehensive survey covering both stochastic and adversarial settings; excellent for understanding the full landscape of bandit algorithms.
