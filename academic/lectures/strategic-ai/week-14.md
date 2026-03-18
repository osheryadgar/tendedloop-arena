# Week 14: Open Problems and Student Presentations

> Strategic AI: From Agents to Multi-Agent Systems

## Overview

This final lecture surveys the open problems at the frontier of multi-agent AI research. Rather than presenting solved theory, we map the landscape of what remains unknown and hard. Each section frames a challenge, reviews the state of the art, and poses research directions. The goal is to equip students with the vocabulary and context to identify viable research contributions.

## Key Concepts

### Non-Stationarity in Multi-Agent Learning

The non-stationarity problem (introduced in Week 8) remains the central theoretical challenge in MARL. Despite decades of work, we lack general convergence guarantees for multi-agent learning in the settings that matter most.

**What we know:**
- Two-player zero-sum games: Many algorithms converge to Nash equilibrium (fictitious play, CFR, optimistic gradient descent/ascent). The minimax structure provides a variational inequality framework.
- Potential games: Games where a single potential function captures all agents' incentive gradients. Gradient-based methods converge.
- Specific game classes: Monotone games, variationally stable games --- convergence is known for no-regret dynamics.

**What we do not know:**
- General-sum games with $n > 2$ players: No polynomial-time algorithm is known to find Nash equilibria (PPAD-complete even for 2 players in general). Worse, Nash equilibria may not be the right solution concept --- they can be Pareto-dominated, and there may be exponentially many.
- Which solution concept to converge to: Nash equilibrium, correlated equilibrium, coarse correlated equilibrium, Stackelberg equilibrium? Each has different computational and strategic properties. The field lacks consensus.
- Non-stationary non-stationarity: In most MARL research, the non-stationarity arises from other agents learning. But in real deployments (e.g., Arena), the environment itself changes (user behavior drifts, external events occur). This compounds the problem.

**Research directions:**
- **Mean-field games:** Model infinitely many agents as a continuous distribution. Individual agents interact with the mean field rather than specific opponents. Reduces multi-agent problems to a fixed-point equation. Promising for scalability but sacrifices individual agent modeling.
- **Opponent modeling:** Explicitly model and predict other agents' learning dynamics. Bayesian approaches (maintaining beliefs over opponent types) and learning-to-learn (meta-learning) are active areas. The challenge: recursive modeling ("I think that you think that I think...") leads to infinite regress.
- **Safe policies under non-stationarity:** Instead of converging to equilibrium, guarantee that the agent's performance is above a safety threshold regardless of how others behave. Connects to robust optimization and worst-case analysis.

### Scalability: From Two Agents to Millions

Most MARL theory and algorithms are designed for $n \leq 10$ agents. Real-world multi-agent systems involve thousands to millions of participants.

**The curse of agents:** Joint action spaces grow exponentially: $|\mathcal{A}|^n$ for $n$ agents with $|\mathcal{A}|$ actions each. Joint state spaces, value functions, and communication requirements face similar explosions.

**Current approaches and their limits:**

*Mean-field approximation:* Replace interactions with $n-1$ specific agents by interaction with the population average. Works when agents are approximately exchangeable (anonymous games). Breaks when individual identities matter or when the population is heterogeneous.

*Factored value functions:* Decompose the global value function into local components depending on small subsets of agents. VDN and QMIX (Week 8) are examples for cooperative games. Challenge: determining the right factorization automatically.

*Hierarchical decomposition:* Organize agents into groups, each managed by a higher-level agent. The hierarchy reduces effective dimensionality but introduces questions of how to structure the hierarchy and how to handle cross-group interactions.

*Graph neural networks:* Model inter-agent interactions as edges in a graph. Each agent aggregates information from its neighbors via message passing. Scalable, but the graph structure must be chosen or learned, and long-range dependencies are expensive.

**What we do not know:**
- Is there a general-purpose scalable MARL algorithm? All existing methods exploit structure (exchangeability, locality, hierarchy). Is structure-agnostic scalability fundamentally impossible?
- How does the sample complexity of MARL scale with $n$? Few theoretical results exist beyond toy settings.
- Can we provably learn in mean-field games from finite samples? The approximation error from the mean-field limit introduces bias that is not well-understood.

### Fairness and Equity in Multi-Agent Optimization

When multiple agents optimize in a shared environment, the outcomes may be efficient (high total welfare) but unfair (welfare concentrated in a few agents).

**Formal frameworks:**

*Envy-freeness:* Agent $i$ does not prefer agent $j$'s allocation to their own. In divisible resource settings, envy-free allocations always exist; with indivisible resources, they may not.

*Max-min fairness:* Maximize the minimum utility across all agents. This Rawlsian criterion protects the worst-off agent but may sacrifice total welfare.

*Proportional fairness:* An allocation $\mathbf{x}$ is proportionally fair if no feasible reallocation $\mathbf{x}'$ satisfies $\sum_i \frac{x'_i - x_i}{x_i} > 0$. Equivalent to maximizing $\sum_i \log(x_i)$ (Nash bargaining solution).

*$\alpha$-fairness:* A parametric family unifying utilitarian ($\alpha = 0$), proportional ($\alpha = 1$), and max-min ($\alpha \to \infty$) fairness:

$$\max_{\mathbf{x}} \sum_i \frac{x_i^{1-\alpha}}{1 - \alpha}$$

**Open challenges:**
- **Fairness under uncertainty:** Agents have private types. Fair allocations must be computed without full knowledge of agents' utilities. Mechanism design (Week 11) provides tools, but fairness constraints add complexity.
- **Dynamic fairness:** In repeated interactions, should fairness hold at each time step or only in expectation over time? Temporal fairness allows more flexibility but requires trust.
- **Fairness vs. incentive compatibility:** Implementing a fair allocation rule as a mechanism may require violating incentive compatibility (Gibbard-Satterthwaite style impossibilities). The tradeoff between fairness and truthfulness is not fully characterized.
- **Intersectional fairness in AI systems:** When agents represent demographic groups, multi-agent fairness connects to algorithmic fairness. Ensuring equity across protected attributes while maintaining system efficiency is an active area with deep societal implications.

### Transfer and Generalization Across Environments

A multi-agent policy trained in one environment typically fails in another. Transfer learning in MARL is far less developed than in single-agent settings.

**The challenge:** In single-agent RL, transfer involves adapting to new dynamics or reward structures. In MARL, transfer also involves adapting to new **opponents** --- agents with different strategies, capabilities, and communication patterns. The opponent is part of the environment, and it changes.

**Current approaches:**

*Zero-shot coordination (ZSC):* Train agents that can cooperate with unseen partners without prior interaction (Hu et al., 2020). The "Other-Play" algorithm symmetrizes the training objective to produce policies that are robust to partner conventions.

*Policy space diversity:* Train a diverse population of agents during training so that the learned policy is robust to a range of partner behaviors. Related to population-based training and quality-diversity algorithms.

*Sim-to-real transfer:* Train in simulation, deploy in the real world. In multi-agent settings, the sim-to-real gap includes not just physics but also human behavior modeling. Domain randomization over agent populations is one approach.

*Foundation models for MARL:* Can large pre-trained models (LLMs, vision-language models) provide a general-purpose substrate for multi-agent policies? The generative agents approach (Week 13) suggests yes for language-based coordination. Whether this transfers to non-linguistic domains remains open.

**What we do not know:**
- What constitutes a "generalizable" multi-agent skill? In single-agent RL, skills like "walk," "grasp," and "navigate" transfer across tasks. Multi-agent analogs ("negotiate," "coordinate," "compete") are less well-defined and harder to disentangle from the specific game structure.
- Can we define and measure "multi-agent generalization" rigorously? Single-agent generalization can be measured by performance on held-out MDPs. Multi-agent generalization depends on the distribution over opponent policies --- a much richer and harder-to-specify distribution.
- Is there a multi-agent analog of pre-training? Can agents be pre-trained on a diverse set of games and then fine-tuned for specific interactions, the way LLMs are pre-trained on text and fine-tuned for tasks?

### What We Don't Know

A curated list of fundamental open questions, ordered roughly by increasing ambition:

1. **Computational:** Is there a polynomial-time algorithm for computing Nash equilibria in general $n$-player games? (Likely no --- but proving hardness beyond PPAD is open.)

2. **Learning-theoretic:** What is the optimal sample complexity for learning an $\epsilon$-Nash equilibrium in a stochastic game with $|\mathcal{S}|$ states, $|\mathcal{A}|$ actions per player, and $n$ players? Current bounds have exponential dependence on $n$.

3. **Solution concepts:** Is there a solution concept that is (a) always exists, (b) unique, (c) efficiently computable, (d) strategically justified, and (e) learnable? Nash equilibrium satisfies (a) and (d) but not (b), (c), or (e). Correlated equilibrium satisfies (a), (c), (e) but not (b) or arguably (d).

4. **Emergent behavior:** Can we predict emergent phenomena in large multi-agent systems from properties of individual agents? Is there a "statistical mechanics of multi-agent systems" analogous to how thermodynamics emerges from particle physics?

5. **Alignment at scale:** As the number of AI agents in the world increases, can we ensure that the collective behavior of all AI systems is aligned with human values? This is not a single-agent alignment problem scaled up --- it is qualitatively different due to strategic interactions between AI systems.

6. **Value learning in multi-agent settings:** If we learn human values from behavior (inverse RL), and multiple agents are learning values from different human populations, will the learned values converge or diverge? What happens when AI systems with different learned values interact?

7. **Multi-agent consciousness and moral status:** As AI agents become more sophisticated (generative agents exhibiting personality, memory, social relationships), do philosophical questions of moral status arise? This is not a technical question, but it may become a practical one.

## Research Challenges

### Challenge 1: The Non-Stationary Bandit Arena

**Problem:** Design a multi-agent bandit algorithm that achieves sublinear regret when the reward distribution is non-stationary AND the non-stationarity is caused by other agents' actions (not just nature).

**Context:** Standard bandit algorithms assume stationary or adversarial rewards. In Arena, rewards are neither: they are shaped by the collective behavior of all agents. Can you design an algorithm with regret guarantees that explicitly account for the game-theoretic structure?

**Starting point:** Consider the EXP3 algorithm (adversarial bandits) combined with opponent modeling. Can you improve over worst-case adversarial bounds by exploiting the fact that opponents are learning (and therefore somewhat predictable)?

### Challenge 2: Scalable Cooperative MARL

**Problem:** Design a value decomposition method that (a) scales to 100+ agents, (b) handles heterogeneous agents (different observation/action spaces), and (c) has convergence guarantees in the cooperative setting.

**Context:** VDN and QMIX (Week 8) scale to ~10 agents in practice. Graph-based methods scale better but lose global coordination. Can you design an architecture that maintains global coordination guarantees while scaling?

**Starting point:** Consider a hierarchical value decomposition: agents are grouped into clusters, each cluster has a local $Q^{tot}$, and cluster-level values are aggregated into a global value. What structural assumptions make this correct?

### Challenge 3: Fair Multi-Agent Optimization

**Problem:** In an Arena-like setting with $n$ agents optimizing over a shared user population, design a scoring mechanism that is (a) incentive-compatible, (b) efficient, and (c) satisfies proportional fairness.

**Context:** This combines mechanism design (Week 11) with fairness theory. The challenge: fairness constraints interact with incentive compatibility constraints, and it is not clear that all three desiderata can be simultaneously satisfied.

**Starting point:** Consider a VCG-like mechanism where each agent's score is their marginal contribution to a fair social welfare function (e.g., Nash product instead of utilitarian sum). Is this mechanism incentive-compatible?

### Challenge 4: Transfer in Multi-Agent Systems

**Problem:** Train a multi-agent policy on Game A (e.g., a cooperative navigation task) and deploy it in Game B (a different cooperative task with the same agent count but different dynamics). Measure zero-shot performance and identify what transfers.

**Context:** This is the multi-agent analog of transfer learning. The hypothesis: agents learn "social skills" (communication conventions, coordination patterns, trust dynamics) that transfer across games, even when task-specific skills do not.

**Starting point:** Use a population-based training approach in Game A, then evaluate the best agent in Game B. Compare against (a) training from scratch in Game B and (b) fine-tuning the Game A agent in Game B. What fraction of the training budget is saved?

## Arena Connection

Arena serves as both a testbed and a motivating example for these open problems:

- **Non-stationarity:** Arena experiments with multiple concurrent agents exhibit all the non-stationarity challenges discussed. Student agents can observe and measure the non-stationarity in their reward signals.
- **Scalability:** Future Arena versions may support 50+ concurrent agents. The current 2-4 agent experiments already reveal coordination challenges; scaling will require the techniques discussed here.
- **Fairness:** Arena's ranking system implicitly defines a fairness criterion. Is it fair that early-moving agents can lock in advantage? Should the scoring mechanism compensate for ordering effects?
- **Transfer:** Students who build Arena agents for one experiment and deploy them (with minimal modification) in another are performing transfer learning. The SDK is designed to support this: the interface is experiment-agnostic, even as the underlying dynamics change.

## Discussion Questions

1. If Nash equilibrium is computationally hard and strategically questionable (multiple equilibria, dominated equilibria), what solution concept should MARL algorithms target? Argue for a specific alternative, addressing existence, uniqueness, computability, and strategic justification.

2. Mean-field games assume agents are exchangeable. In most real multi-agent systems, agents are heterogeneous. Propose a framework that captures the benefits of mean-field approximation while preserving agent heterogeneity. What is the approximation error?

3. The "alignment at scale" problem suggests that even if each AI agent is individually aligned, collective behavior may be misaligned. Is this analogous to any existing phenomenon in economics, ecology, or physics? What tools from those fields might apply?

4. If you could start a PhD in multi-agent AI tomorrow, which of the problems discussed today would you work on, and why? What would your first experiment be?

## Further Reading

1. **Zhang, K., Yang, Z., & Basar, T. (2021).** "Multi-Agent Reinforcement Learning: A Selective Overview of Theories and Algorithms." *Handbook of Reinforcement Learning and Control*, Springer. --- The most comprehensive theoretical survey of MARL, covering convergence results, complexity, and open problems.

2. **Hu, H. et al. (2020).** "Other-Play for Zero-Shot Coordination." *ICML*. --- Introduces the zero-shot coordination problem and the Other-Play algorithm for training agents that cooperate with unseen partners.

3. **Dafoe, A. et al. (2021).** "Cooperative AI: Machines Must Learn to Find Common Ground." *Nature*, 593. --- A vision paper from DeepMind on the challenges and importance of cooperative AI, bridging technical and societal perspectives.
