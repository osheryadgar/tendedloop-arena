# Week 10: Cooperative Multi-Agent Systems

> Strategic AI: Multi-Agent Systems & Optimization

## Overview

This week shifts from adversarial to cooperative settings, where agents share common goals or must negotiate mutually beneficial outcomes. We formalize team games and common-payoff games, study communication protocols that enable coordination, and develop the mathematical tools of cooperative game theory --- the Shapley value and the core --- for fairly distributing the gains from cooperation. Real-world applications in traffic routing, energy management, and supply chains ground the theory.

## Key Concepts

### Team Games and Common-Payoff Games

A **common-payoff game** (also called a team game or fully cooperative game) is a stochastic game where all agents share the same reward function:

$$R_1(s, \mathbf{a}) = R_2(s, \mathbf{a}) = \cdots = R_n(s, \mathbf{a}) = R(s, \mathbf{a})$$

Despite aligned incentives, coordination remains hard. The **decentralized coordination problem** arises because agents cannot observe each other's private information or chosen actions before committing.

**Example (Decentralized POMDP):** Two rescue robots must simultaneously choose which victim to save. If both go to the same victim, one is wasted. Optimal coordination requires either prior agreement (convention), communication, or shared knowledge of a focal point.

**Dec-POMDP** (Decentralized Partially Observable MDP) is the formal framework: a tuple $\langle \mathcal{N}, \mathcal{S}, \{\mathcal{A}_i\}, T, R, \{\Omega_i\}, O, \gamma \rangle$ where $\Omega_i$ is agent $i$'s observation space and $O$ is the observation function. Dec-POMDPs are NEXP-complete to solve optimally (Bernstein et al., 2002) --- dramatically harder than single-agent POMDPs (PSPACE-complete).

### Communication Protocols

Communication can dramatically reduce the coordination problem's complexity.

**Cheap talk:** Messages that are costless to send and non-binding. In cooperative settings, cheap talk is credible because agents have aligned incentives. A protocol: before acting, agents exchange messages about their private observations, then coordinate on a joint action.

**Signaling:** Actions that convey information through their cost or structure. Unlike cheap talk, signals are credible because they are costly to fake (Spence, 1973). Example: an agent that invests computational resources in exploring a region of the state space signals the value of that region to teammates.

**Emergent communication:** In deep MARL, agents can learn communication protocols end-to-end. The **CommNet** architecture (Sukhbaatar et al., 2016) uses a continuous communication channel; **DIAL** (Foerster et al., 2016) uses Differentiable Inter-Agent Learning, where gradients flow through discrete messages during training. Results show agents invent task-specific "languages" --- often uninterpretable to humans but effective for coordination.

**Communication complexity matters:** Adding a 1-bit communication channel to a Dec-POMDP can exponentially reduce the policy space that needs to be searched. However, the optimal communication policy is itself hard to compute.

### Negotiation and Contract Nets

In mixed-motive settings (partially aligned incentives), agents negotiate.

**Contract Net Protocol (Smith, 1980):** A classic multi-agent coordination mechanism:
1. **Manager** broadcasts a task announcement.
2. **Contractors** evaluate and submit bids.
3. Manager evaluates bids and awards contract.
4. Contractor executes task, reports results.

This protocol decentralizes task allocation without a central planner. It is widely used in manufacturing, logistics, and multi-robot systems.

**Automated negotiation** formalizes bargaining with alternating offers (Rubinstein, 1982). Two agents alternate proposals over a "pie" of size 1. With discount factors $\delta_1, \delta_2 < 1$ (patience), the unique subgame-perfect equilibrium gives agent 1:

$$x_1^* = \frac{1 - \delta_2}{1 - \delta_1 \delta_2}$$

More patient agents get larger shares --- patience is power in negotiation.

### Cooperative Game Theory: The Shapley Value

Cooperative game theory (CGT) studies **coalitional games** where the fundamental question is: how should the gains from cooperation be distributed?

A **coalitional game** (or TU game) is a pair $(N, v)$ where $N = \{1, \dots, n\}$ is the set of players and $v: 2^N \rightarrow \mathbb{R}$ is the **characteristic function** with $v(\emptyset) = 0$. The value $v(S)$ represents the total payoff coalition $S$ can achieve on its own.

The **Shapley value** (Shapley, 1953) assigns each player $i$ a unique payoff:

$$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|! \, (n - |S| - 1)!}{n!} \left[ v(S \cup \{i\}) - v(S) \right]$$

**Interpretation:** Consider all possible orderings in which players join the coalition. For each ordering, player $i$'s marginal contribution is $v(S \cup \{i\}) - v(S)$ where $S$ is the set of players before $i$. The Shapley value is the average marginal contribution over all orderings.

**Shapley's Axioms** (uniqueness characterization): The Shapley value is the **unique** allocation satisfying:
1. **Efficiency:** $\sum_{i \in N} \phi_i(v) = v(N)$ --- the entire value is distributed.
2. **Symmetry:** If $v(S \cup \{i\}) = v(S \cup \{j\})$ for all $S$, then $\phi_i = \phi_j$.
3. **Null player:** If $v(S \cup \{i\}) = v(S)$ for all $S$, then $\phi_i = 0$.
4. **Additivity:** $\phi_i(v + w) = \phi_i(v) + \phi_i(w)$.

### The Core

The **core** of a coalitional game is the set of payoff allocations $\mathbf{x} = (x_1, \dots, x_n)$ such that:

1. **Efficiency:** $\sum_{i \in N} x_i = v(N)$
2. **Coalitional rationality:** $\sum_{i \in S} x_i \geq v(S)$ for all $S \subseteq N$

The core represents allocations where no coalition has an incentive to "break away" and form on its own. It may be empty (not all games have stable allocations), and when non-empty, it may contain many allocations.

**Bondareva-Shapley Theorem:** The core is non-empty if and only if the game is **balanced** --- a condition involving balanced collections of coalitions.

The Shapley value may or may not lie in the core. When it does, it provides a focal allocation that is both fair (axiomatically) and stable (no coalition wants to deviate).

## Formal Definitions

**Definition (Superadditivity).** A coalitional game $(N, v)$ is superadditive if for all disjoint coalitions $S, T \subseteq N$:

$$v(S \cup T) \geq v(S) + v(T)$$

Superadditivity means cooperation never hurts --- the grand coalition $N$ is always weakly optimal.

**Definition (Convex Game).** A coalitional game is convex if for all $S \subseteq T \subseteq N \setminus \{i\}$:

$$v(S \cup \{i\}) - v(S) \leq v(T \cup \{i\}) - v(T)$$

Marginal contributions are increasing: larger coalitions benefit more from adding a player. In convex games, the core is always non-empty, and the Shapley value lies in the core.

**Theorem (Dec-POMDP Complexity, Bernstein et al. 2002).** Finding the optimal joint policy for a finite-horizon Dec-POMDP is NEXP-complete.

## Worked Examples

### Example 1: Computing the Shapley Value

Three companies ($N = \{1, 2, 3\}$) consider sharing delivery infrastructure. Characteristic function (in $1000s saved):

| Coalition | $v(S)$ |
|-----------|--------|
| $\{1\}$ | 0 |
| $\{2\}$ | 0 |
| $\{3\}$ | 0 |
| $\{1,2\}$ | 60 |
| $\{1,3\}$ | 48 |
| $\{2,3\}$ | 30 |
| $\{1,2,3\}$ | 90 |

Compute $\phi_1$. There are $3! = 6$ orderings:

| Ordering | $S$ before 1 | Marginal $v(S \cup \{1\}) - v(S)$ |
|----------|--------------|------|
| (1,2,3) | $\emptyset$ | $v(\{1\}) - v(\emptyset) = 0$ |
| (1,3,2) | $\emptyset$ | $0$ |
| (2,1,3) | $\{2\}$ | $v(\{1,2\}) - v(\{2\}) = 60$ |
| (3,1,2) | $\{3\}$ | $v(\{1,3\}) - v(\{3\}) = 48$ |
| (2,3,1) | $\{2,3\}$ | $v(\{1,2,3\}) - v(\{2,3\}) = 60$ |
| (3,2,1) | $\{2,3\}$ | $v(\{1,2,3\}) - v(\{2,3\}) = 60$ |

$$\phi_1 = \frac{0 + 0 + 60 + 48 + 60 + 60}{6} = \frac{228}{6} = 38$$

Similarly: $\phi_2 = (0 + 60 + 0 + 30 + 42 + 42)/6 = 174/6 = 29$

Check $\phi_2$ via formula for ordering (3,2,1): $S = \{3\}$ before 2, marginal = $v(\{2,3\}) - v(\{3\}) = 30$.
For ordering (1,3,2): $S = \{1,3\}$, marginal = $v(\{1,2,3\}) - v(\{1,3\}) = 90 - 48 = 42$.

$\phi_3 = 90 - 38 - 29 = 23$ (by efficiency).

**Verify:** $38 + 29 + 23 = 90 = v(N)$. Check coalitional rationality:
- $\phi_1 + \phi_2 = 67 \geq 60 = v(\{1,2\})$. Yes.
- $\phi_1 + \phi_3 = 61 \geq 48 = v(\{1,3\})$. Yes.
- $\phi_2 + \phi_3 = 52 \geq 30 = v(\{2,3\})$. Yes.

The Shapley value is in the core --- the allocation is stable.

### Example 2: Finding the Core

Using the same game, the core is the set of $(x_1, x_2, x_3)$ satisfying:

$$x_1 + x_2 + x_3 = 90, \quad x_1 + x_2 \geq 60, \quad x_1 + x_3 \geq 48, \quad x_2 + x_3 \geq 30, \quad x_i \geq 0$$

From $x_1 + x_2 + x_3 = 90$ and $x_2 + x_3 \geq 30$: $x_1 \leq 60$.
From $x_1 + x_3 \geq 48$ and $x_3 = 90 - x_1 - x_2$: $90 - x_2 \geq 48$, so $x_2 \leq 42$.
From $x_1 + x_2 \geq 60$: $x_3 \leq 30$.

The core is a polytope in $\mathbb{R}^3$. The Shapley value $(38, 29, 23)$ lies within it.

### Example 3: Emergent Communication in a Coordination Game

Two agents in a grid world must meet at the same location. Each observes a different landmark. Before moving, each sends a 1-bit message $\{0, 1\}$.

Without communication: random meeting probability $= 1/k^2$ for $k$ locations.

With 1-bit communication: agents can learn a protocol like "if you see landmark A, send 1; otherwise send 0." The receiver learns "if partner sends 1, go to location associated with A."

In deep MARL experiments (Foerster et al., 2016), agents trained end-to-end discover such protocols without being told what the messages should mean. The communication channel develops semantic content through gradient-based optimization of the shared reward.

## Arena Connection

Cooperative dynamics appear in Arena when students consider the broader ecosystem:

- **Shapley value for attribution:** When multiple configuration changes contribute to improved metrics, the Shapley value provides a principled way to attribute credit. Which parameter change mattered most? The SDK's `agent.get_metrics()` history enables such analysis.
- **Communication between agents:** In multi-agent Arena setups, agents could benefit from sharing information about which parameter regions are promising. This mirrors the cheap talk and emergent communication literature.
- **Coalition formation:** If Arena allows team-based competitions, cooperative game theory governs how teams should form and how to distribute rewards among team members.
- **Contract nets for task allocation:** The protocol maps naturally to how Arena agents might decompose the optimization problem: one sub-agent explores XP multipliers, another explores badge thresholds, coordinated via a contract-net-like protocol.

## Discussion Questions

1. Dec-POMDPs are NEXP-complete. Yet practical multi-robot systems solve Dec-POMDP-like problems daily. What structural assumptions (communication, loose coupling, hierarchical decomposition) make real-world problems tractable? Give specific examples.

2. The Shapley value requires evaluating $2^n$ coalitions. For a system with 100 agents, this is computationally infeasible. Describe and analyze an approximation algorithm for the Shapley value. (Hint: Monte Carlo sampling of orderings.)

3. Emergent communication in deep MARL often produces protocols that are effective but uninterpretable. Is interpretability important for cooperative AI systems? Argue both sides, considering safety implications.

4. In the Rubinstein bargaining model, the more patient agent gets a larger share. How does this principle manifest in Arena, where agents with longer time horizons (more exploration budget) might achieve better outcomes?

## Further Reading

1. **Oliehoek, F. A. & Amato, C. (2016).** *A Concise Introduction to Decentralized POMDPs.* Springer. --- The definitive reference on Dec-POMDPs, covering exact and approximate algorithms.

2. **Foerster, J. N. et al. (2016).** "Learning to Communicate with Deep Multi-Agent Reinforcement Learning." *NeurIPS*. --- Foundational paper on emergent communication via differentiable inter-agent learning (DIAL).

3. **Roth, A. E. (Ed.) (1988).** *The Shapley Value: Essays in Honor of Lloyd S. Shapley.* Cambridge University Press. --- Comprehensive treatment of the Shapley value with applications to economics, political science, and cost allocation.
