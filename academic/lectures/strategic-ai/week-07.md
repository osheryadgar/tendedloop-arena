# Week 7: Single-Agent RL Review

> Strategic AI: From Agents to Multi-Agent Systems

## Overview

This lecture provides a concise but rigorous review of single-agent reinforcement learning, bridging the bandit algorithms of Weeks 4-6 to the multi-agent RL of Week 8. We revisit MDPs with full mathematical machinery: value functions, Bellman equations, and the key algorithms — Q-learning, REINFORCE, DQN, and PPO. The goal is not to teach RL from scratch (students have taken a prerequisite), but to establish precise notation and highlight the assumptions that break down in multi-agent settings.

## Key Concepts

### MDPs Revisited

Recall from Week 1: an MDP is **M = (S, A, T, R, gamma)** with states S, actions A, transition function T, reward function R, and discount factor gamma. Now we develop the solution machinery.

A policy **pi : S -> Delta(A)** maps states to action distributions. We seek the optimal policy pi* that maximizes expected discounted return from every state.

### Value Functions

> **Definition (State Value Function).** The value of state *s* under policy pi:
>
> **V^pi(s) = E_pi [ sum_{t=0}^{infinity} gamma^t R(s_t, a_t) | s_0 = s ]**

> **Definition (Action Value Function).** The value of taking action *a* in state *s* and following pi thereafter:
>
> **Q^pi(s, a) = E_pi [ sum_{t=0}^{infinity} gamma^t R(s_t, a_t) | s_0 = s, a_0 = a ]**

The relationship: **V^pi(s) = sum_a pi(a|s) Q^pi(s, a)** and **Q^pi(s, a) = R(s, a) + gamma sum_{s'} T(s, a, s') V^pi(s')**.

### Bellman Equations

The value functions satisfy recursive equations that are the foundation of all RL algorithms.

> **Bellman Expectation Equation:**
>
> **V^pi(s) = sum_a pi(a|s) [ R(s, a) + gamma sum_{s'} T(s, a, s') V^pi(s') ]**
>
> **Q^pi(s, a) = R(s, a) + gamma sum_{s'} T(s, a, s') sum_{a'} pi(a'|s') Q^pi(s', a')**

> **Bellman Optimality Equation:**
>
> **V*(s) = max_a [ R(s, a) + gamma sum_{s'} T(s, a, s') V*(s') ]**
>
> **Q*(s, a) = R(s, a) + gamma sum_{s'} T(s, a, s') max_{a'} Q*(s', a')**

The optimal policy is greedy with respect to Q*: **pi*(s) = argmax_a Q*(s, a)**.

**Dynamic Programming solutions** (when T is known):
- **Policy Evaluation**: Solve V^pi by iterating the Bellman expectation equation to convergence.
- **Policy Iteration**: Alternate between evaluation and improvement (set pi(s) = argmax_a Q^pi(s, a)).
- **Value Iteration**: Iterate the Bellman optimality equation directly: V_{k+1}(s) = max_a [R(s,a) + gamma sum_{s'} T(s,a,s') V_k(s')].

Both converge in polynomial time. But they require known T and R — the "planning" setting.

### From Planning to Learning: Model-Free RL

When T is unknown, the agent must learn from experience. The two fundamental approaches:

1. **Value-based**: Estimate Q* directly, derive the policy as argmax.
2. **Policy-based**: Parameterize the policy directly, optimize by gradient ascent on expected return.

### Q-Learning

> **Algorithm (Q-Learning, Watkins 1989).** Initialize Q(s, a) arbitrarily. At each step:
> 1. In state s_t, choose a_t (e.g., epsilon-greedy w.r.t. Q).
> 2. Observe reward r_t and next state s_{t+1}.
> 3. Update:
>
> **Q(s_t, a_t) <- Q(s_t, a_t) + alpha_t [ r_t + gamma max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t) ]**

The term in brackets is the **temporal difference (TD) error**: delta_t = r_t + gamma max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t).

> **Theorem (Convergence of Q-Learning).** Under the conditions: (1) all state-action pairs are visited infinitely often, (2) step sizes satisfy sum_t alpha_t = infinity and sum_t alpha_t^2 < infinity, Q-learning converges to Q* with probability 1.

The proof relies on the stochastic approximation theorem (Robbins-Monro) and the contraction property of the Bellman optimality operator.

**SARSA** is the on-policy counterpart: it updates toward Q(s_{t+1}, a_{t+1}) (the action actually taken) rather than max_{a'} Q(s_{t+1}, a'). SARSA converges to Q^pi (the value of the current policy), not Q*.

### Policy Gradient Methods

Value-based methods struggle with continuous actions and can be unstable with function approximation. Policy gradient methods directly parameterize the policy pi_theta and optimize:

> **J(theta) = E_{tau ~ pi_theta} [ sum_{t=0}^{T} gamma^t R(s_t, a_t) ] = E_{s_0} [ V^{pi_theta}(s_0) ]**

The key result:

> **Policy Gradient Theorem (Sutton et al., 1999).**
>
> **nabla_theta J(theta) = E_{pi_theta} [ sum_{t=0}^{T} nabla_theta ln pi_theta(a_t | s_t) * G_t ]**
>
> where **G_t = sum_{k=t}^{T} gamma^{k-t} r_k** is the return from time *t*.

### REINFORCE

The simplest policy gradient algorithm:

> **Algorithm (REINFORCE, Williams 1992).**
> 1. Sample a trajectory tau = (s_0, a_0, r_0, s_1, ...) under pi_theta.
> 2. For each time step *t*, compute return G_t.
> 3. Update: **theta <- theta + alpha sum_t nabla_theta ln pi_theta(a_t | s_t) * G_t**

REINFORCE is unbiased but has high variance. The **baseline** trick reduces variance without introducing bias:

**theta <- theta + alpha sum_t nabla_theta ln pi_theta(a_t | s_t) * (G_t - b(s_t))**

A common baseline is the value function b(s) = V(s), leading to the **advantage** A(s, a) = Q(s, a) - V(s). This gives us Actor-Critic methods: the "actor" (policy) is updated using advantages estimated by the "critic" (value function).

### Deep RL: DQN

For large state spaces (e.g., images), tabular methods are infeasible. Deep Q-Networks (DQN, Mnih et al. 2015) approximate Q* with a neural network Q(s, a; w).

**Key innovations that stabilize training:**

1. **Experience replay**: Store transitions (s, a, r, s') in a buffer. Sample mini-batches uniformly to break temporal correlations.
2. **Target network**: Use a slowly-updated copy w^- for the target: y = r + gamma max_{a'} Q(s', a'; w^-). This prevents the moving target problem.

The loss is the squared TD error:

> **L(w) = E_{(s,a,r,s') ~ D} [ (r + gamma max_{a'} Q(s', a'; w^-) - Q(s, a; w))^2 ]**

DQN achieved superhuman performance on 29/49 Atari games, demonstrating that deep RL can scale to high-dimensional observations.

**Limitations:** DQN overestimates Q-values (maximization bias). Double DQN (van Hasselt et al. 2016) addresses this by decoupling action selection from evaluation.

### Deep RL: PPO

Proximal Policy Optimization (Schulman et al. 2017) is the most widely used deep policy gradient algorithm. It improves upon vanilla REINFORCE and Actor-Critic with a clipped surrogate objective that prevents destructively large policy updates.

> **PPO Objective:**
>
> **L^{CLIP}(theta) = E_t [ min( r_t(theta) A_t, clip(r_t(theta), 1-epsilon, 1+epsilon) A_t ) ]**
>
> where **r_t(theta) = pi_theta(a_t | s_t) / pi_{theta_old}(a_t | s_t)** is the probability ratio.

The clipping (typically epsilon = 0.2) prevents the ratio from deviating too far from 1, ensuring stable updates. When the advantage A_t is positive (good action), the ratio is clipped from above; when negative, from below.

PPO is:
- Simpler to implement than TRPO (no second-order optimization).
- More stable than vanilla policy gradient.
- The default algorithm for many applications (robotics, game AI, RLHF for LLMs).

### Function Approximation: The Deadly Triad

Using function approximation (neural nets) with bootstrapping (TD learning) and off-policy data creates instability — the "deadly triad" (Sutton & Barto). Each ingredient is fine alone; together, they can diverge.

- **DQN** manages this via experience replay (partial off-policy) and target networks (stabilize bootstrapping).
- **PPO** avoids it by being on-policy (no replay buffer) and using Monte Carlo returns (no bootstrapping, or GAE which controls the bias-variance tradeoff).

Understanding the deadly triad is essential for Week 8: in multi-agent RL, non-stationarity adds a fourth source of instability on top of the triad.

## Formal Definitions

> **Bellman Optimality Operator.** (T*V)(s) = max_a [R(s,a) + gamma sum_{s'} T(s,a,s') V(s')]. T* is a gamma-contraction in the sup-norm: ||T*V - T*V'||_inf <= gamma ||V - V'||_inf. V* is the unique fixed point.

> **Policy Gradient Theorem.** nabla_theta J(theta) = E_{d^{pi_theta}, pi_theta} [ Q^{pi_theta}(s, a) nabla_theta ln pi_theta(a | s) ], where d^{pi_theta} is the discounted state visitation distribution.

> **Convergence of Q-Learning.** Q(s,a) -> Q*(s,a) w.p. 1 if: (1) sum alpha_t(s,a) = infinity and sum alpha_t(s,a)^2 < infinity for all (s,a), and (2) gamma < 1.

## Worked Examples

### Example 1: Bellman Equation for a 3-State MDP

States: {s_1, s_2, s_3}. Actions: {L, R}. Discount gamma = 0.9. Terminal state s_3.

Transitions and rewards:
- (s_1, L) -> s_1 with R = 1
- (s_1, R) -> s_2 with R = 0
- (s_2, L) -> s_1 with R = 0
- (s_2, R) -> s_3 with R = 10

Bellman optimality equations:
- V*(s_1) = max(1 + 0.9 * V*(s_1), 0 + 0.9 * V*(s_2))
- V*(s_2) = max(0 + 0.9 * V*(s_1), 10 + 0.9 * 0) = max(0.9 * V*(s_1), 10)
- V*(s_3) = 0

Try V*(s_2) = 10 (choosing R): then V*(s_1) = max(1 + 0.9 * V*(s_1), 9).
If V*(s_1) = 1 + 0.9 * V*(s_1), then 0.1 * V*(s_1) = 1, V*(s_1) = 10.
Check: max(1 + 9, 9) = max(10, 9) = 10. Consistent.
Check V*(s_2): max(0.9 * 10, 10) = max(9, 10) = 10. Consistent.

Optimal policy: pi*(s_1) = L (loop for reward 1 forever), pi*(s_2) = R (take the big reward).

Wait — V*(s_1) = 10 from looping, and going R gives 0 + 0.9 * 10 = 9 < 10. So yes, stay and collect 1 per step with discounted sum 10.

### Example 2: Q-Learning Update

State s, two actions {a, b}. Current Q-values: Q(s, a) = 3.0, Q(s, b) = 2.5. Learning rate alpha = 0.1, gamma = 0.9.

Agent takes action a, observes r = 1, transitions to s'. In s': Q(s', a) = 4.0, Q(s', b) = 3.5.

TD target: y = r + gamma * max_{a'} Q(s', a') = 1 + 0.9 * 4.0 = 4.6.
TD error: delta = 4.6 - 3.0 = 1.6.
Update: Q(s, a) <- 3.0 + 0.1 * 1.6 = 3.16.

The Q-value moved toward the TD target. After many such updates (with decreasing alpha and sufficient exploration), Q(s, a) will converge to Q*(s, a).

### Example 3: REINFORCE Gradient for a Softmax Policy

Policy: pi_theta(a | s) = exp(theta_a^T phi(s)) / sum_b exp(theta_b^T phi(s)).

For a single trajectory step with state s, action a taken, return G = 5.0, and feature phi(s) = (1, 0.5):

nabla_theta_a ln pi_theta(a | s) = phi(s) - sum_b pi_theta(b | s) phi(s) = phi(s) * (1 - pi_theta(a | s))

If pi_theta(a | s) = 0.6: nabla = (1, 0.5) * 0.4 = (0.4, 0.2).

Gradient step: theta_a <- theta_a + alpha * (0.4, 0.2) * 5.0 = theta_a + alpha * (2.0, 1.0).

The parameters for action a increase, making a more likely in state s. The magnitude is proportional to the return G — good actions in good trajectories get reinforced more.

## Arena Connection

Single-agent RL is the bridge from bandits to full multi-agent learning on the Arena platform. While standard Arena experiments present a bandit problem (no state transitions between pulls), the Arena also supports **sequential experiments** where:

1. The agent's current arm selection affects the distribution of future contexts (e.g., choosing a reward configuration today affects tomorrow's engagement patterns).
2. The experiment has a finite horizon with a known number of rounds.
3. The agent receives cumulative rewards that depend on the *sequence* of choices.

Workshop Session 6 introduces RL-based Arena agents:
- A **Q-learning agent** that discretizes the context space and learns Q-values for each context-arm pair.
- A **policy gradient agent** using REINFORCE with a linear policy that maps context features to arm selection probabilities.

The key lesson: when the bandit assumption (i.i.d. rewards, no state) holds, bandit algorithms from Weeks 4-5 are more sample-efficient. When state dynamics matter, RL algorithms from this week are necessary. Choosing the right abstraction level is an engineering judgment.

In Week 8, we add the multi-agent dimension: other agents' strategies become part of the environment, creating non-stationarity that violates the foundational MDP assumption.

## Discussion Questions

1. Q-learning is off-policy (learns Q* regardless of the behavior policy), while SARSA is on-policy (learns Q^pi). In what situations would you prefer SARSA? (Hint: consider the cliff-walking problem.)

2. The deadly triad (function approximation + bootstrapping + off-policy) causes instability. DQN addresses this with experience replay and target networks. Are these fixes principled, or are they hacks? What theoretical guarantees (if any) do they provide?

3. PPO clips the probability ratio to prevent large updates. What would happen without clipping? Why is this problem worse in RL than in supervised learning? Connect this to the non-stationarity of the RL objective.

4. We reviewed single-agent RL. In the multi-agent setting (Week 8), other agents are part of the environment, making it non-stationary. Which of the algorithms from this lecture — Q-learning, SARSA, REINFORCE, DQN, PPO — would you expect to be most robust to non-stationarity? Why?

## Further Reading

- **Sutton & Barto (2018), *Reinforcement Learning: An Introduction*, Ch. 6, 13** — The standard reference. Chapter 6 covers TD learning and Q-learning with exceptional clarity; Chapter 13 covers policy gradients with the actor-critic framework.
- **Mnih et al. (2015), "Human-level control through deep reinforcement learning"** — The DQN Nature paper. A landmark result demonstrating that deep RL can learn from raw pixels. Well worth reading for both the algorithm and the experimental methodology.
- **Schulman et al. (2017), "Proximal Policy Optimization Algorithms"** — The PPO paper is refreshingly short and practical. It includes ablation studies showing why clipping works better than the theoretically-motivated TRPO constraint.
