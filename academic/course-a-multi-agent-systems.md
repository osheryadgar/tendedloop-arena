# Course A: Multi-Agent Systems

**Department**: Computer Science / Artificial Intelligence
**Level**: Advanced undergraduate or graduate
**Prerequisites**: Algorithms, Probability & Statistics, Linear Algebra, Python programming
**Credits**: 3-4

## Course Description

This course covers the theory and algorithms of multi-agent systems — autonomous entities that perceive, reason, and act in shared environments. Students study how agents make decisions under uncertainty, compete and cooperate, and how system-level behavior emerges from individual strategies. The course bridges classical game theory, modern bandit algorithms, and multi-agent reinforcement learning.

The accompanying [workshop](../course/README.md) offers a hands-on lab where students implement these algorithms as real autonomous agents competing on the TendedLoop Arena platform.

## Learning Outcomes

By the end of this course, students will be able to:
1. Design agent architectures for sequential decision-making under uncertainty
2. Analyze strategic interactions using game-theoretic frameworks
3. Implement and evaluate bandit algorithms (UCB, Thompson Sampling, contextual)
4. Apply reinforcement learning in multi-agent settings
5. Reason about safety, alignment, and mechanism design for autonomous systems
6. Evaluate agent performance using statistical methods

## Weekly Schedule

### Module 1: Foundations (Weeks 1-4)

#### Week 1: Agents and Environments
- What is an agent? Percepts, actions, goals, environments
- PEAS framework (Performance, Environment, Actuators, Sensors)
- Agent architectures: reflex, model-based, goal-based, utility-based
- Formal model: Markov Decision Processes (MDPs)

**Readings**: Russell & Norvig, Ch. 2; Wooldridge, Ch. 1-2
**Workshop link**: [Lesson 1 — What is Arena](../course/01-what-is-arena.md), [Lesson 2 — The Environment](../course/02-the-arena-environment.md)

#### Week 2: Decision Theory and Rational Choice
- Expected utility theory
- Decision trees and influence diagrams
- Risk preferences and utility functions
- Bounded rationality and satisficing

**Readings**: Russell & Norvig, Ch. 16.1-16.3
**Assignment 1**: Implement a simple utility-maximizing agent for a grid world

#### Week 3: Game Theory Fundamentals
- Normal form games and Nash Equilibrium
- Dominant strategies and iterated dominance
- Mixed strategies and minimax
- Prisoner's Dilemma, Stag Hunt, Chicken — canonical games

**Readings**: Shoham & Leyton-Brown, Ch. 3-4
**Workshop link**: Understanding variant competition in Arena

#### Week 4: Mechanism Design
- Mechanism design as "reverse game theory"
- Incentive compatibility and truthfulness
- VCG mechanisms
- Applications: auctions, voting, resource allocation
- Connection to gamification: designing incentive structures

**Readings**: Shoham & Leyton-Brown, Ch. 11
**Assignment 2**: Design and analyze an auction mechanism (sealed-bid, Vickrey)

### Module 2: Bandit Algorithms (Weeks 5-7)

#### Week 5: Multi-Armed Bandits
- The explore-exploit dilemma
- Regret: definition, lower bounds (Lai-Robbins)
- Explore-Then-Commit: analysis and limitations
- UCB1: derivation from Hoeffding's inequality
- Proof of O(sqrt(KT log T)) regret bound

**Readings**: Lattimore & Szepesvari, Ch. 1-7; Auer et al. (2002)
**Workshop link**: [Lesson 6 — Explore-Exploit](../course/06-explore-exploit.md), [Lesson 7 — UCB1](../course/07-ucb1.md)
**Assignment 3**: Implement UCB1, prove its regret bound, compare empirically with epsilon-greedy

#### Week 6: Bayesian Bandits and Thompson Sampling
- Bayesian formulation of the bandit problem
- Beta-Bernoulli Thompson Sampling
- Gaussian Thompson Sampling
- Theoretical results: Bayesian regret bounds
- Empirical comparison with UCB1

**Readings**: Russo et al. (2018) "A Tutorial on Thompson Sampling"
**Workshop link**: [Lesson 8 — Thompson Sampling](../course/08-thompson-sampling.md)

#### Week 7: Contextual Bandits
- From bandits to contextual bandits
- LinUCB: linear upper confidence bound with features
- Contextual Thompson Sampling
- Policy learning and offline evaluation
- Connections to personalization and recommendation

**Readings**: Li et al. (2010) "A Contextual-Bandit Approach to Personalized News Article Recommendation"
**Workshop link**: [Lesson 9 — Contextual Bandits](../course/09-contextual-bandits.md)
**Assignment 4**: Implement LinUCB on a news recommendation dataset, evaluate offline

### Module 3: Multi-Agent Learning (Weeks 8-10)

#### Week 8: Single-Agent Reinforcement Learning (Review)
- MDPs, value functions, Bellman equations
- Q-learning and SARSA
- Policy gradient methods (REINFORCE, Actor-Critic)
- Function approximation and deep RL basics

**Readings**: Sutton & Barto, Ch. 1-6, 13
**Workshop link**: [Lesson 11 — Reinforcement Learning](../course/11-reinforcement-learning.md)

#### Week 9: Multi-Agent Reinforcement Learning
- Stochastic games (Markov games)
- Independent learners vs. joint-action learners
- Cooperative MARL: QMIX, MAPPO
- Competitive MARL: minimax-Q, Nash Q-learning
- Non-stationarity problem: the environment changes as other agents learn

**Readings**: Zhang et al. (2021) "Multi-Agent Reinforcement Learning: A Selective Overview of Theories and Algorithms"
**Assignment 5**: Train competing RL agents in a simple matrix game, analyze convergence

#### Week 10: Bayesian Optimization and Black-Box Methods
- Gaussian processes as surrogate models
- Acquisition functions: EI, UCB, PI
- Multi-point acquisition and batch BO
- Relation to bandits in continuous spaces
- When BO beats RL (sample efficiency vs. expressiveness)

**Readings**: Shahriari et al. (2016) "Taking the Human Out of the Loop"
**Workshop link**: [Lesson 10 — Bayesian Optimization](../course/10-bayesian-optimization.md)

### Module 4: Advanced Topics (Weeks 11-14)

#### Week 11: Communication, Coordination, and Emergent Behavior
- Agent communication languages
- Coordination mechanisms: contracts, protocols, norms
- Emergent behavior in multi-agent systems
- Ensemble methods: boosting, bagging, mixture of experts
- The Hedge algorithm and online learning

**Readings**: Wooldridge, Ch. 7; Arora et al. (2012) "The Multiplicative Weights Update Method"
**Workshop link**: [Lesson 13 — Ensemble Methods](../course/13-ensemble-methods.md)

#### Week 12: LLM Agents and Foundation Models
- Language models as decision-making agents
- Reasoning, planning, and tool use
- ReAct, Chain-of-Thought, Tree-of-Thought
- Multi-agent LLM systems: debate, collaboration, society
- Limitations: hallucination, cost, non-determinism

**Readings**: Yao et al. (2023) "ReAct"; Park et al. (2023) "Generative Agents"
**Workshop link**: [Lesson 12 — LLM Agents](../course/12-llm-agents.md)

#### Week 13: Safety, Alignment, and Guardrails
- AI safety in multi-agent contexts
- Reward hacking and specification gaming
- Guardrail design: rate limiting, clamping, circuit breakers
- Human-in-the-loop oversight
- Responsible deployment of autonomous agents

**Readings**: Amodei et al. (2016) "Concrete Problems in AI Safety"
**Workshop link**: [Lesson 14 — Production Safety](../course/14-production-safety.md)
**Assignment 6**: Analyze failure modes of an unconstrained agent, propose guardrail designs

#### Week 14: Current Research and Open Problems
- Guest lectures / paper presentations
- Open problems: scalability, non-stationarity, transfer, fairness
- Student project presentations (if applicable)

## Assessment

| Component | Weight | Description |
|-----------|--------|-------------|
| Assignments (6) | 40% | Implementation + analysis |
| Midterm exam | 20% | Weeks 1-7 (game theory, bandits) |
| Final exam or project | 25% | Comprehensive or research project |
| Workshop participation | 15% | Arena agent performance + writeup (if paired with workshop) |

## Recommended Textbooks

1. **Shoham & Leyton-Brown** — *Multi-Agent Systems: Algorithmic, Game-Theoretic, and Logical Foundations* (primary)
2. **Lattimore & Szepesvari** — *Bandit Algorithms* (bandits module)
3. **Sutton & Barto** — *Reinforcement Learning: An Introduction* (RL module)
4. **Russell & Norvig** — *Artificial Intelligence: A Modern Approach* (foundations)
5. **Wooldridge** — *An Introduction to MultiAgent Systems* (reference)
