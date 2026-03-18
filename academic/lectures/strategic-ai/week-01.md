# Week 1: Agents, Environments, and Decision Theory

> Strategic AI: From Agents to Multi-Agent Systems

## Overview

This lecture introduces the foundational abstractions that underpin all of multi-agent AI: what it means to be an agent, how agents interact with environments, and how rational decision-making is formalized mathematically. We build from informal intuition to the precise mathematical framework of Markov Decision Processes, which will serve as the backbone of the entire course.

## Key Concepts

### What Is an Agent?

An agent is an entity that perceives its environment through sensors and acts upon it through actuators. This definition is deceptively simple. The key insight is that an agent is defined not by what it *is* but by what it *does* — it maps percept histories to actions.

Formally, let **P** be the set of all possible percepts. A percept history at time *t* is a sequence *h_t = (p_1, p_2, ..., p_t)*. An agent is a function:

> **f : P* -> A**

where **P*** is the set of all possible percept sequences and **A** is the set of available actions.

This is the *agent function*. The *agent program* is its implementation. A lookup table could implement any agent function, but the table for most interesting environments would be astronomically large. The intellectual challenge of AI is finding compact, effective agent programs.

### The PEAS Framework

To specify an agent design problem, we use the PEAS framework:

- **Performance measure**: How do we evaluate the agent's behavior? This is external to the agent — it is the designer's specification of what "good" means. Getting this right is one of the deepest problems in AI (see Week 13 on alignment).
- **Environment**: The external world the agent operates in. Environments vary along critical dimensions: fully vs. partially observable, deterministic vs. stochastic, episodic vs. sequential, static vs. dynamic, discrete vs. continuous, single-agent vs. multi-agent.
- **Actuators**: The mechanisms through which the agent affects the environment.
- **Sensors**: The mechanisms through which the agent perceives the environment.

**Example — Arena Agent PEAS:**
- **Performance**: Cumulative reward from the Arena experiment (e.g., average feedback rating).
- **Environment**: The Arena platform — stochastic (noisy human feedback), sequential (decisions affect future state), dynamic (other agents may be operating), partially observable (agent sees only its own arm rewards).
- **Actuators**: API calls to select arms (`agent.pull(arm_id)`).
- **Sensors**: Reward observations returned after each pull.

### Environment Taxonomy

The distinctions between environment types drive algorithm design:

| Property | Simpler | Harder |
|----------|---------|--------|
| Observability | Fully observable | Partially observable |
| Determinism | Deterministic | Stochastic |
| Temporal structure | Episodic | Sequential |
| Dynamics | Static | Dynamic |
| Agents | Single | Multi-agent |
| State/action space | Discrete, finite | Continuous, infinite |

Multi-agent environments are the focus of this course. When another agent is part of your environment, the environment becomes non-stationary from your perspective — even if the underlying dynamics are stationary. This is the fundamental challenge of multi-agent systems.

### Sequential Decision-Making Under Uncertainty

Most interesting AI problems involve sequences of decisions where outcomes are uncertain. The agent must balance immediate rewards against information gain and future consequences. This is the *explore-exploit tradeoff*, which we will formalize precisely in Weeks 4-6.

The standard framework for sequential decision-making is the Markov Decision Process.

### Markov Decision Processes (MDPs)

An MDP is a tuple **(S, A, T, R, gamma)** where:

> **Definition (MDP).** A Markov Decision Process is a tuple **M = (S, A, T, R, gamma)** where:
> - **S** is a finite set of states
> - **A** is a finite set of actions (or **A(s)** for state-dependent action sets)
> - **T : S x A x S -> [0, 1]** is the transition function, where **T(s, a, s') = P(s_{t+1} = s' | s_t = s, a_t = a)**
> - **R : S x A -> R** is the reward function (or **R : S x A x S -> R** in some formulations)
> - **gamma in [0, 1)** is the discount factor

The Markov property is the crucial assumption: the future depends on the present state and action only, not on the history of how we arrived at that state:

> **P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, ..., s_0, a_0) = P(s_{t+1} | s_t, a_t)**

A **policy** pi : S -> A (deterministic) or pi : S x A -> [0,1] (stochastic) maps states to actions. The agent's goal is to find an optimal policy pi* that maximizes expected discounted return:

> **pi* = argmax_pi E_pi [ sum_{t=0}^{infinity} gamma^t R(s_t, a_t) ]**

The discount factor gamma serves three roles: (1) it ensures the infinite sum converges, (2) it models preference for sooner rewards, and (3) it controls the effective planning horizon (roughly 1/(1-gamma) steps).

### Expected Utility Theory

Why do we maximize *expected* reward? Expected utility theory (von Neumann & Morgenstern, 1944) provides the axiomatic foundation. If an agent's preferences over lotteries (probability distributions over outcomes) satisfy four axioms — completeness, transitivity, continuity, and independence — then there exists a utility function **u** such that the agent prefers lottery **L_1** to **L_2** if and only if:

> **E[u(L_1)] > E[u(L_2)]**

This is not a definition of rationality imposed from outside. It is a theorem: any agent whose preferences are internally consistent *must* behave as if maximizing expected utility. An agent that violates this can be exploited — it will accept sequences of trades that leave it strictly worse off (a "money pump").

### Rationality and Bounded Rationality

A *rational agent* selects the action that maximizes expected utility given its beliefs. But computing the optimal action is often intractable. Herbert Simon's concept of *bounded rationality* acknowledges that real agents have limited computation. They *satisfice* — seek solutions that are "good enough" — rather than optimize.

This tension between optimal and tractable is central to algorithm design throughout the course: UCB1 (Week 4) gives near-optimal regret guarantees with minimal computation; deep RL (Week 7) sacrifices provable guarantees for scalability.

## Formal Definitions

> **Definition (Agent Function).** An agent function **f : P* -> A** maps every possible percept sequence to an action.

> **Definition (MDP).** M = (S, A, T, R, gamma) as defined above. A solution to an MDP is an optimal policy pi* satisfying the Bellman optimality equation (Week 7).

> **Theorem (von Neumann-Morgenstern).** If a preference relation over lotteries satisfies completeness, transitivity, continuity, and independence, then there exists a utility function u : Outcomes -> R such that L_1 >= L_2 iff E[u(L_1)] >= E[u(L_2)]. This utility function is unique up to positive affine transformation.

## Worked Examples

### Example 1: Gridworld MDP

Consider a 3x3 grid. The agent starts at (0,0) and wants to reach (2,2). Actions: {up, down, left, right}. With probability 0.8 the agent moves in the intended direction; with probability 0.1 it moves in each perpendicular direction. The reward is -1 per step and +10 upon reaching (2,2).

**States**: S = {(i,j) : 0 <= i,j <= 2} plus a terminal state. |S| = 10.
**Actions**: A = {up, down, left, right}. |A| = 4.
**Transitions**: T((0,0), right, (1,0)) = 0.8, T((0,0), right, (0,1)) = 0.1, T((0,0), right, (0,0)) = 0.1 (bumps into wall from below). Walls cause the agent to stay in place.

This is a well-defined MDP that can be solved exactly via value iteration (Week 7).

### Example 2: Thermostat as an Agent

PEAS for a smart thermostat:
- **P**: Maximize occupant comfort while minimizing energy cost.
- **E**: Building interior — partially observable (sensors cover limited area), stochastic (outdoor weather, occupant behavior), sequential, dynamic, multi-agent (multiple occupants with different preferences).
- **A**: Adjust temperature setpoint, fan speed, HVAC mode.
- **S**: Temperature sensors, humidity sensors, occupancy sensors, time-of-day clock.

This is a continuous-state, continuous-action MDP. Exact solution requires function approximation (Week 7).

### Example 3: Why Discount?

Suppose gamma = 0.9, and an agent receives reward 1 every step forever. The discounted return is:

sum_{t=0}^{infinity} 0.9^t * 1 = 1 / (1 - 0.9) = 10

If gamma = 0.99, the return is 100. Higher gamma means the agent cares about rewards further into the future. With gamma = 0, the agent is purely myopic — it only cares about immediate reward. In the Arena, different discount factors lead to qualitatively different exploration strategies.

## Arena Connection

The Arena platform instantiates the agent-environment loop directly. Each Arena agent implements the observe-decide-act cycle:

1. **Observe**: The agent receives reward feedback from its last arm pull via the SDK's observation mechanism.
2. **Decide**: The agent's algorithm (e.g., UCB1, Thompson Sampling) selects the next arm.
3. **Act**: The agent calls the Arena API to pull the selected arm.

The Arena environment is:
- **Partially observable**: The agent only sees rewards for arms it pulls.
- **Stochastic**: Reward distributions have noise.
- **Sequential**: Each pull consumes budget and generates information.
- **Multi-agent** (in competitive experiments): Multiple agents share the same arm pool.

The SDK's `observe()` -> `decide()` -> `act()` structure mirrors the formal agent function. Workshop Session 1 walks through setting up this loop with `tendedloop-agent`.

## Discussion Questions

1. The PEAS framework requires specifying a performance measure. In a multi-agent system where agents have conflicting objectives, whose performance measure defines "rationality"? Is there a meaningful notion of system-level rationality?

2. The Markov property assumes the future is independent of the past given the present state. Give an example of a real-world decision problem where this assumption is clearly violated. How would you modify the MDP framework to handle it?

3. Expected utility theory assumes the agent has a consistent preference ordering. Empirically, humans violate the independence axiom (Allais paradox). Does this mean human decision-making is "irrational," or does it mean the axioms are wrong? What are the implications for designing AI agents that interact with humans?

4. Consider the discount factor gamma. An agent with gamma = 0 is myopic; an agent with gamma -> 1 considers the far future equally. What happens if we set gamma = 1 in an infinite-horizon MDP? Under what conditions is this still well-defined?

## Further Reading

- **Kaelbling, Littman, & Moore (1996), "Reinforcement Learning: A Survey"** — Excellent overview of the RL problem formulation including POMDPs; complements the MDP material with discussion of partial observability.
- **Simon (1955), "A Behavioral Model of Rational Choice"** — The original paper on bounded rationality; essential context for understanding why optimal solutions are often impractical.
- **Wooldridge & Jennings (1995), "Intelligent Agents: Theory and Practice"** — Foundational survey of agent architectures (reactive, deliberative, hybrid); gives a broader AI perspective on what "agent" means beyond the MDP formalism.
