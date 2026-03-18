# Week 8: Multi-Agent Reinforcement Learning

> Strategic AI: Multi-Agent Systems & Optimization

## Overview

This week extends single-agent reinforcement learning to the multi-agent setting, where multiple learners simultaneously adapt their policies in a shared environment. We formalize the problem as stochastic (Markov) games, examine why standard RL convergence guarantees break down when the environment includes other learning agents, and survey modern paradigms --- independent learners, centralized training with decentralized execution (CTDE), and value decomposition methods --- that address these challenges.

## Key Concepts

### Stochastic Games (Markov Games)

A **stochastic game** (Shapley, 1953) generalizes a Markov Decision Process to $n$ players. Formally:

$$\mathcal{G} = \langle \mathcal{N}, \mathcal{S}, \{\mathcal{A}_i\}_{i \in \mathcal{N}}, T, \{R_i\}_{i \in \mathcal{N}}, \gamma \rangle$$

where:

- $\mathcal{N} = \{1, \dots, n\}$ is the set of agents,
- $\mathcal{S}$ is the state space,
- $\mathcal{A}_i$ is the action space for agent $i$; the joint action space is $\mathcal{A} = \mathcal{A}_1 \times \cdots \times \mathcal{A}_n$,
- $T: \mathcal{S} \times \mathcal{A} \rightarrow \Delta(\mathcal{S})$ is the transition function,
- $R_i: \mathcal{S} \times \mathcal{A} \rightarrow \mathbb{R}$ is the reward function for agent $i$,
- $\gamma \in [0,1)$ is the discount factor.

Special cases:
- **$n = 1$**: reduces to a standard MDP.
- **$n = 2$, $R_1 = -R_2$**: zero-sum Markov game (covered in Week 9).
- **$R_1 = R_2 = \cdots = R_n$**: common-payoff (team) game (covered in Week 10).

Each agent $i$ seeks a policy $\pi_i : \mathcal{S} \rightarrow \Delta(\mathcal{A}_i)$ that maximizes its expected discounted return $\mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t R_i(s_t, \mathbf{a}_t)\right]$ given the joint policy $\boldsymbol{\pi} = (\pi_1, \dots, \pi_n)$.

### The Non-Stationarity Problem

In single-agent RL, convergence proofs (e.g., for Q-learning) rely on the environment being a stationary MDP: the transition and reward distributions do not change over time. In multi-agent settings, this assumption is violated.

From agent $i$'s perspective, the effective transition kernel is:

$$T_i^{\pi_{-i}}(s' | s, a_i) = \sum_{\mathbf{a}_{-i}} T(s' | s, a_i, \mathbf{a}_{-i}) \prod_{j \neq i} \pi_j(a_j | s)$$

As other agents update their policies $\pi_{-i}$, agent $i$'s induced MDP changes. The environment is a **moving target**: convergence guarantees of tabular Q-learning no longer apply because the data distribution shifts under the learner.

This creates several pathologies: **cyclic policy oscillations** (agents chase each other through strategy space), **relative overgeneralization** (agents converge to suboptimal joint policies because individually risky actions get penalized during training), and **shadowed equilibria** (Nash equilibria that are unreachable by gradient-based methods from certain initializations).

### Independent Learners

The simplest multi-agent approach: each agent runs its own single-agent RL algorithm, treating all other agents as part of the environment.

**Independent Q-Learning (IQL):** Each agent $i$ maintains $Q_i(s, a_i)$ and updates:

$$Q_i(s, a_i) \leftarrow Q_i(s, a_i) + \alpha \left[ r_i + \gamma \max_{a'_i} Q_i(s', a'_i) - Q_i(s, a_i) \right]$$

**Advantages:** Simple, scalable, no communication required.

**Disadvantages:** No convergence guarantees (non-stationary MDP), cannot represent joint-action values, prone to miscoordination.

Despite the lack of theory, IQL works surprisingly well in practice for many problems, especially when agents have loosely coupled reward structures. This pragmatic success has made it a common baseline.

### Centralized Training, Decentralized Execution (CTDE)

CTDE is the dominant paradigm in modern MARL. The key insight: during training, we have access to global information (all agents' observations, actions, rewards); at deployment, each agent acts based only on its local observation.

**Architecture:** A centralized critic $Q^{tot}(s, \mathbf{a})$ is trained using global state and joint actions. Each agent's actor $\pi_i(a_i | o_i)$ conditions only on local observation $o_i$ and is trained using the centralized critic's gradient signal.

**MADDPG** (Lowe et al., 2017): Multi-Agent Deep Deterministic Policy Gradient. Each agent $i$ has:
- Actor $\mu_i(o_i)$: maps local observation to action.
- Centralized critic $Q_i(s, a_1, \dots, a_n)$: conditions on global state and all actions.

The critic resolves non-stationarity because it explicitly models other agents' actions, while the actor remains decentralized.

### Value Decomposition: VDN and QMIX

For cooperative settings, value decomposition methods learn a joint value function $Q^{tot}$ that decomposes into per-agent utilities, enabling decentralized execution.

**VDN** (Sunehag et al., 2018): Value Decomposition Networks assume an additive decomposition:

$$Q^{tot}(s, \mathbf{a}) = \sum_{i=1}^{n} Q_i(s, a_i)$$

Each agent greedily selects $\arg\max_{a_i} Q_i(s, a_i)$, which jointly maximizes $Q^{tot}$.

**QMIX** (Rashid et al., 2018): Relaxes VDN's additivity to a monotonic mixing:

$$Q^{tot}(s, \mathbf{a}) = f_{\text{mix}}\left(Q_1(s, a_1), \dots, Q_n(s, a_n); s\right)$$

where $f_{\text{mix}}$ is a mixing network with **non-negative weights** (enforced via absolute value or hypernetwork), guaranteeing:

$$\frac{\partial Q^{tot}}{\partial Q_i} \geq 0 \quad \forall i$$

This monotonicity ensures the argmax of the joint action is consistent with individual argmaxes --- the Individual-Global-Max (IGM) principle.

## Formal Definitions

**Definition (Nash Equilibrium in Stochastic Games).** A joint policy $\boldsymbol{\pi}^* = (\pi_1^*, \dots, \pi_n^*)$ is a Nash equilibrium if for all agents $i$ and all alternative policies $\pi_i'$:

$$V_i^{\pi_i^*, \pi_{-i}^*}(s) \geq V_i^{\pi_i', \pi_{-i}^*}(s) \quad \forall s \in \mathcal{S}$$

where $V_i^{\boldsymbol{\pi}}(s) = \mathbb{E}_{\boldsymbol{\pi}}\left[\sum_{t=0}^{\infty} \gamma^t R_i(s_t, \mathbf{a}_t) \mid s_0 = s\right]$.

**Theorem (Existence, Fink 1964).** Every finite discounted stochastic game has at least one Nash equilibrium in stationary (Markov) strategies.

**Definition (IGM Principle).** A value decomposition satisfies IGM if:

$$\arg\max_{\mathbf{a}} Q^{tot}(s, \mathbf{a}) = \left(\arg\max_{a_1} Q_1(s, a_1), \dots, \arg\max_{a_n} Q_n(s, a_n)\right)$$

**Proposition.** VDN satisfies IGM trivially (additive decomposition). QMIX satisfies IGM when the mixing network has non-negative weights.

## Worked Examples

### Example 1: Independent Q-Learning in a 2-Player Matrix Game

Consider the coordination game:

|         | Left  | Right |
|---------|-------|-------|
| **Up**  | (2,2) | (0,0) |
| **Down**| (0,0) | (1,1) |

Two pure-strategy Nash equilibria: (Up, Left) with payoff (2,2) and (Down, Right) with payoff (1,1).

**Setup:** Both agents use IQL with $\epsilon$-greedy exploration ($\epsilon = 0.1$), learning rate $\alpha = 0.1$, discount $\gamma = 0$ (single-stage game). Initialize $Q_i(a) = 0$ for all actions.

**Iteration 1:** Both explore randomly. Suppose agent 1 plays Up, agent 2 plays Right. Rewards: $(0, 0)$.
- $Q_1(\text{Up}) \leftarrow 0 + 0.1(0 - 0) = 0$
- $Q_2(\text{Right}) \leftarrow 0 + 0.1(0 - 0) = 0$

**Iteration 2:** Suppose both play Down and Left respectively. Rewards: $(0, 0)$. No update.

**Iteration 3:** Suppose agent 1 plays Up, agent 2 plays Left. Rewards: $(2, 2)$.
- $Q_1(\text{Up}) \leftarrow 0 + 0.1(2 - 0) = 0.2$
- $Q_2(\text{Left}) \leftarrow 0 + 0.1(2 - 0) = 0.2$

Now both agents prefer their successful actions. Under $\epsilon$-greedy, they will mostly play (Up, Left), reinforcing the high-payoff equilibrium.

**Key observation:** IQL can converge to either equilibrium depending on early exploration. There is no guarantee it finds the Pareto-optimal equilibrium (Up, Left). Run multiple seeds and you will observe convergence to (Down, Right) in a non-trivial fraction.

### Example 2: QMIX Decomposition

Three agents in a cooperative task. Suppose $Q_1 = 3, Q_2 = 5, Q_3 = 2$ for the selected actions.

**VDN:** $Q^{tot} = 3 + 5 + 2 = 10$.

**QMIX:** The mixing network computes weights $w_1 = 0.4, w_2 = 0.8, w_3 = 0.3$ (all non-negative) and bias $b = 1.5$:
$$Q^{tot} = 0.4 \cdot 3 + 0.8 \cdot 5 + 0.3 \cdot 2 + 1.5 = 1.2 + 4.0 + 0.6 + 1.5 = 7.3$$

Since all weights are non-negative, increasing any $Q_i$ increases $Q^{tot}$, so each agent's greedy action selection is consistent with the joint optimum (IGM holds).

### Example 3: Non-Stationarity Demonstration

Matching Pennies (zero-sum):

|         | Heads | Tails |
|---------|-------|-------|
| **Heads** | (+1,-1) | (-1,+1) |
| **Tails** | (-1,+1) | (+1,-1) |

Unique Nash equilibrium: both play 50/50. With IQL, observe what happens:

- Agent 1 learns to play Heads more (because agent 2 initially plays Heads more often).
- Agent 2 adapts, shifting to Tails.
- Agent 1 observes Tails now yields higher reward, shifts to Tails.
- Cycle repeats. Q-values oscillate; no convergence.

This is the non-stationarity problem in its purest form: each agent's best response depends on the other's current policy, which is also changing.

## Arena Connection

The TendedLoop Arena platform instantiates a multi-agent stochastic game. Each student's agent interacts with the gamification economy (setting XP multipliers, badge thresholds, mission parameters) while competing against other agents doing the same.

- **Non-stationarity in Arena:** When one agent discovers a high-performing XP configuration, user behavior shifts, affecting all agents' reward signals. Your agent's reward function is implicitly conditioned on competitor policies.
- **CTDE relevance:** In Arena experiments, agents are trained with access to aggregate metrics (centralized information) but must submit configuration decisions based only on their own state (decentralized execution).
- **SDK connection:** The `agent.get_state()` method returns your agent's local observation; `agent.submit_action()` commits a configuration. The Arena backend computes the joint transition.

Students should consider: does independent learning suffice in Arena (where agent coupling is weak through shared user populations), or do you need to model other agents explicitly?

## Discussion Questions

1. Under what conditions does Independent Q-Learning converge in multi-agent settings? Can you construct a game where IQL provably fails to converge? (Hint: consider games with no pure-strategy Nash equilibrium.)

2. QMIX enforces monotonicity ($\partial Q^{tot} / \partial Q_i \geq 0$) to satisfy IGM. Give an example of a cooperative game where the optimal $Q^{tot}$ is non-monotonic in individual agent values, and explain why QMIX would fail there.

3. The CTDE paradigm assumes centralized information is available during training. In Arena, what constitutes "centralized" information? How would you design a CTDE agent that leverages experiment-wide metrics during training but executes with only local state?

4. Compare the non-stationarity problem in MARL with concept drift in supervised learning. Are the same mitigation strategies (e.g., sliding windows, experience replay with prioritization) applicable?

## Further Reading

1. **Hernandez-Leal, P., Kartal, B., & Taylor, M. E. (2019).** "A Survey and Critique of Multiagent Deep Reinforcement Learning." *Autonomous Agents and Multi-Agent Systems*, 33(6). --- Comprehensive survey of MARL algorithms with empirical comparisons.

2. **Papoudakis, G., Christianos, F., Schafer, L., & Albrecht, S. V. (2021).** "Benchmarking Multi-Agent Deep Reinforcement Learning Algorithms in Cooperative Tasks." *NeurIPS Datasets & Benchmarks*. --- Rigorous empirical comparison of IQL, VDN, QMIX, MADDPG, and others.

3. **Gronauer, S. & Diepold, K. (2022).** "Multi-Agent Deep Reinforcement Learning: A Survey." *Artificial Intelligence Review*, 55. --- Recent survey covering theoretical foundations and scalability challenges.
