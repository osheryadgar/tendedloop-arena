# Strategic AI: Multi-Agent Systems & Optimization

**Department**: Computer Science / Artificial Intelligence
**Level**: Advanced undergraduate or graduate
**Prerequisites**: Algorithms, Probability & Statistics, Linear Algebra, Python programming; [Behavioral AI](behavioral-ai.md) complements this course with behavioral science foundations
**Credits**: 3-4

> Inspired by MIT 6.S890 (Farina & Daskalakis), Stanford CS 224M (Shoham & Leyton-Brown), and CMU's Cooperative AI program. See [survey of related courses](#related-courses) at the bottom.

## Course Description

This course covers the theory and algorithms of multi-agent systems — autonomous entities that perceive, reason, and act in shared environments. Students study how agents make decisions under uncertainty, compete and cooperate, and how system-level behavior emerges from individual strategies.

The course progresses from foundational game theory through modern multi-agent reinforcement learning to frontier topics like LLM agents and AI safety. Each module is motivated by real AI breakthroughs (AlphaGo, Pluribus, Cicero) and grounded in rigorous theory.

The accompanying [workshop](../workshop/README.md) provides a hands-on lab where students implement these algorithms as autonomous agents competing on the TendedLoop Arena platform.

> **Tip:** Students can practice with the SDK immediately using the local sandbox: `python -m tendedloop_agent demo` — no account or experiment required.

## Learning Outcomes

By the end of this course, students will be able to:
1. Formalize strategic interactions as games and compute equilibrium solutions
2. Derive and analyze bandit algorithms (regret bounds, optimality)
3. Design and evaluate multi-agent RL algorithms
4. Apply mechanism design principles to incentive systems
5. Reason about safety, alignment, and guardrails for autonomous agents
6. Critically evaluate current research in multi-agent AI

## Weekly Schedule

> **Lecture notes:** Complete lecture notes for each week are available in [lectures/strategic-ai/](lectures/strategic-ai/).

### Module 1: Foundations (Weeks 1-3)

#### [Week 1: Agents, Environments, and Decision Theory](lectures/strategic-ai/week-01.md)
- What is an agent? The agent-environment interaction loop
- PEAS framework (Performance, Environment, Actuators, Sensors)
- Sequential decision-making under uncertainty
- Markov Decision Processes (MDPs): formal definition
- Expected utility theory and rational choice

**Readings**: Russell & Norvig, Ch. 2, 16.1-16.3
**Workshop**: [Session 1](../workshop/README.md) — Setup and orientation

#### [Week 2: Normal-Form Games and Nash Equilibrium](lectures/strategic-ai/week-02.md)
- Strategic form games: players, strategies, payoffs
- Dominant strategies, iterated dominance
- Nash Equilibrium: existence (Nash's theorem), computation
- Mixed strategy Nash Equilibrium
- Canonical games: Prisoner's Dilemma, Stag Hunt, Battle of the Sexes, Chicken

**Readings**: Shoham & Leyton-Brown, Ch. 3-4
**Assignment 1**: Compute Nash Equilibria for 5 games (by hand + code verification)

#### [Week 3: Extensive-Form Games and Sequential Reasoning](lectures/strategic-ai/week-03.md)
- Game trees, information sets, subgame perfection
- Backward induction
- Imperfect information games: poker as a canonical example
- Behavioral strategies vs. mixed strategies
- Connection to real-world multi-agent competition

**Readings**: Shoham & Leyton-Brown, Ch. 5; MIT 6.S890 L15-L16 slides
**Case study**: How Pluribus beat human poker professionals

### Module 2: Bandit Algorithms (Weeks 4-6)

#### [Week 4: The Multi-Armed Bandit Problem](lectures/strategic-ai/week-04.md)
- Formalization: arms, rewards, regret
- The explore-exploit tradeoff
- Lower bounds: Lai-Robbins theorem (logarithmic regret is optimal)
- Epsilon-greedy: simplicity and its cost
- Explore-Then-Commit: analysis and limitations
- UCB1: derivation from Hoeffding's inequality, proof of O(√(KT log T)) regret

**Readings**: Lattimore & Szepesvari, Ch. 1-8
**Workshop**: [Session 4](../workshop/README.md) — The bandit problem
**Assignment 2**: Implement UCB1, epsilon-greedy, and ETC. Prove the UCB1 regret bound. Compare empirically on synthetic and Arena data.

#### [Week 5: Bayesian Bandits and Thompson Sampling](lectures/strategic-ai/week-05.md)
- Bayesian formulation: prior → posterior → decision
- Beta-Bernoulli Thompson Sampling
- Gaussian Thompson Sampling for continuous rewards
- Bayesian regret bounds and optimality
- Information-theoretic perspective: value of information

**Readings**: Russo et al. (2018) "A Tutorial on Thompson Sampling"
**Workshop**: [Session 5](../workshop/README.md) — Bayesian approaches

#### [Week 6: Contextual Bandits and Beyond](lectures/strategic-ai/week-06.md)
- From bandits to contextual bandits
- LinUCB: linear upper confidence bound with features (Li et al. 2010)
- Contextual Thompson Sampling
- Neural contextual bandits
- Offline evaluation: importance-weighted estimators
- Connection to personalization and recommendation

**Readings**: Li et al. (2010) "LinUCB"; Agarwal et al. (2014)
**Workshop**: [Session 5](../workshop/README.md) — Contextual approaches

### Module 3: Multi-Agent Learning (Weeks 7-10)

#### [Week 7: Single-Agent RL Review](lectures/strategic-ai/week-07.md)
- MDPs revisited: value functions, Bellman equations
- Tabular methods: Q-learning, SARSA
- Policy gradient: REINFORCE, Actor-Critic
- Deep RL: DQN, PPO, SAC
- Function approximation and stability

**Readings**: Sutton & Barto, Ch. 1-6, 13; Albrecht et al. (2024) Ch. 1-3
**Workshop**: [Session 6](../workshop/README.md) — RL with Arena

#### [Week 8: Multi-Agent Reinforcement Learning](lectures/strategic-ai/week-08.md)
- Stochastic games (Markov games): formal definition
- The non-stationarity problem: each agent's environment changes as others learn
- Independent learners: treat other agents as part of the environment
- Centralized training, decentralized execution (CTDE)
- Value decomposition: VDN, QMIX

**Readings**: Albrecht et al. (2024) Ch. 4-7; Zhang et al. (2021)
**Assignment 3**: Implement independent Q-learners in a matrix game. Analyze convergence (or failure to converge).

#### [Week 9: Competitive Multi-Agent Systems](lectures/strategic-ai/week-09.md)
- Zero-sum games and minimax
- Self-play: training against yourself
- Fictitious play and convergence
- Counterfactual Regret Minimization (CFR) for imperfect-information games
- From rock-paper-scissors to superhuman poker (Libratus, Pluribus)

**Readings**: Zinkevich et al. (2008) "Regret Minimization in Games"; Brown & Sandholm (2019)
**Case study**: How CFR solved No-Limit Texas Hold'em

#### [Week 10: Cooperative Multi-Agent Systems](lectures/strategic-ai/week-10.md)
- Team games and common-payoff games
- Communication: cheap talk, signaling, emergent communication
- Negotiation protocols and contract nets
- Cooperative game theory: Shapley value, core
- Real-world applications: traffic, energy grids, supply chains

**Readings**: Albrecht et al. (2024) Ch. 8-9; Wooldridge, Ch. 7
**Midterm exam**: Weeks 1-10

### Module 4: Mechanism Design and Optimization (Weeks 11-12)

#### [Week 11: Mechanism Design](lectures/strategic-ai/week-11.md)
- Mechanism design as "reverse game theory"
- Social choice functions and Arrow's theorem
- Incentive compatibility and the revelation principle
- VCG mechanisms: Vickrey auctions, Clarke taxes
- Applications: auctions, matching markets, resource allocation
- Connection to gamification: designing incentive structures

**Readings**: Shoham & Leyton-Brown, Ch. 10-11
**Assignment 4**: Design an auction mechanism for allocating server resources. Prove incentive compatibility.

#### [Week 12: Bayesian Optimization and Black-Box Methods](lectures/strategic-ai/week-12.md)
- Gaussian processes as surrogate models
- Acquisition functions: Expected Improvement, UCB, Knowledge Gradient
- Multi-point acquisition and parallel BO
- Comparison: when BO beats RL (sample efficiency) and when it doesn't (dimensionality)
- Hyperparameter optimization as a case study

**Readings**: Shahriari et al. (2016) "Taking the Human Out of the Loop"
**Workshop**: [Session 6](../workshop/README.md) — Bayesian Optimization with Arena

### Module 5: Frontier Topics (Weeks 13-14)

#### [Week 13: LLM Agents, Safety, and Alignment](lectures/strategic-ai/week-13.md)
- Language models as decision-making agents
- ReAct, Chain-of-Thought, Tool Use
- Generative agents: simulating human behavior (Park et al. 2023)
- Multi-agent LLM systems: debate, society of mind
- Safety: reward hacking, specification gaming, Goodhart's Law
- Guardrail design: rate limiting, clamping, circuit breakers, human oversight
- The alignment problem in multi-agent settings

**Readings**: Yao et al. (2023) "ReAct"; Park et al. (2023) "Generative Agents"; Amodei et al. (2016)
**Workshop**: [Sessions 7-8](../workshop/README.md) — LLM agents, ensembles, safety
**Assignment 5**: Analyze failure modes of an unconstrained LLM agent in Arena. Propose and implement guardrails.

#### [Week 14: Open Problems and Student Presentations](lectures/strategic-ai/week-14.md)
- Non-stationarity in multi-agent learning
- Scalability: from 2 agents to millions
- Fairness and equity in multi-agent optimization
- Transfer and generalization across environments
- Student project presentations

## Assessment

| Component | Weight | Description |
|-----------|--------|-------------|
| Assignments (5) | 40% | Theory proofs + implementation |
| Midterm exam | 20% | Weeks 1-10 (game theory, bandits, MARL) |
| Final exam or project | 25% | Comprehensive exam or research project |
| Workshop participation | 15% | Arena agent performance + writeup |

## Required and Recommended Textbooks

### Required
1. **Shoham & Leyton-Brown** — *Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations* (2009). Free at [masfoundations.org](https://www.masfoundations.org/)
2. **Albrecht, Christianos, Schafer** — *Multi-Agent Reinforcement Learning: Foundations and Modern Approaches* (MIT Press, 2024). Free at [marl-book.com](https://marl-book.com/)

### Recommended
3. **Lattimore & Szepesvari** — *Bandit Algorithms* (Cambridge, 2020). Free at [banditalgs.com](https://banditalgs.com/)
4. **Sutton & Barto** — *Reinforcement Learning: An Introduction* (2nd ed, 2018). Free at [incompleteideas.net](http://incompleteideas.net/book/the-book.html)
5. **Russell & Norvig** — *Artificial Intelligence: A Modern Approach* (4th ed, 2021)

## Related Courses

| Course | University | Focus |
|--------|-----------|-------|
| [CS 224M](https://web.stanford.edu/class/cs224m/) | Stanford | MAS foundations (Shoham) |
| [6.S890](https://www.mit.edu/~gfarina/6S890/) | MIT | Multi-agent learning (Farina, Daskalakis) |
| [CS 222](https://joonspk-research.github.io/cs222-fall24/) | Stanford | AI agents and social simulation (Park) |
| [CS 329A](https://cs329a.stanford.edu/) | Stanford | Self-improving AI agents |
| [CS 294](https://rdi.berkeley.edu/agentic-ai/f25) | Berkeley | Agentic AI (Dawn Song) |
| [15-784](https://www.cs.cmu.edu/~softagents/multi.html) | CMU | Cooperative AI (Sandholm) |
