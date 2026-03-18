# Week 9: Competitive Multi-Agent Systems

> Strategic AI: Multi-Agent Systems & Optimization

## Overview

This week studies adversarial multi-agent interactions --- settings where one agent's gain is another's loss. We formalize zero-sum games, prove the minimax theorem, and develop algorithms for finding optimal strategies: fictitious play for normal-form games and Counterfactual Regret Minimization (CFR) for extensive-form games with imperfect information. The lecture culminates in a case study of how these ideas produced superhuman poker AI.

## Key Concepts

### Zero-Sum Games and the Minimax Theorem

A two-player **zero-sum game** satisfies $R_1(s, a_1, a_2) + R_2(s, a_1, a_2) = 0$ for all states and actions. We can represent the game by a single payoff matrix $A$ where entry $a_{ij}$ is the row player's payoff (column player receives $-a_{ij}$).

**The Minimax Theorem (von Neumann, 1928).** In any finite two-player zero-sum game:

$$\max_{\mathbf{x} \in \Delta_m} \min_{\mathbf{y} \in \Delta_n} \mathbf{x}^\top A \mathbf{y} = \min_{\mathbf{y} \in \Delta_n} \max_{\mathbf{x} \in \Delta_m} \mathbf{x}^\top A \mathbf{y} = v^*$$

where $\Delta_k$ is the $(k-1)$-simplex (the set of mixed strategies), and $v^*$ is the **value of the game**.

The theorem says the order of play does not matter when both players play optimally: the max-min value equals the min-max value. This is profound --- it means a rational player can guarantee at least $v^*$ regardless of the opponent's strategy, and no strategy can do better against a rational opponent.

**Proof sketch (via LP duality).** The maximin problem can be written as a linear program. Its dual is the minimax problem. By strong LP duality, optimal values coincide. $\square$

**Implication for Nash equilibria:** In zero-sum games, all Nash equilibria yield the same payoff $v^*$. Nash equilibrium strategies are precisely the maximin/minimax strategies. This makes zero-sum games uniquely tractable --- computing a Nash equilibrium is a polynomial-time LP.

### Self-Play

**Self-play** is a training paradigm where an agent improves by playing against copies of itself (or past versions). The key insight: in zero-sum games, a strategy that exploits weaknesses in the opponent is exactly what the opponent needs to fix.

**Naive self-play** trains against the latest version. Problem: the agent may "forget" how to beat earlier strategies, cycling through a sequence of specialist strategies. This is the **strategy forgetting** problem.

**Population-based self-play** maintains a population of past strategies and samples opponents from this population (e.g., AlphaGo, OpenAI Five). This regularizes training toward robustness rather than specialization.

**Fictitious Self-Play (FSP):** Combines fictitious play (below) with RL. Each agent maintains an average policy (the "average strategy" from fictitious play) and a best-response policy (trained via RL against the opponent's average policy). Heinrich et al. (2015) showed FSP converges to Nash equilibrium in two-player zero-sum games.

### Fictitious Play

**Fictitious play** (Brown, 1951) is one of the oldest learning algorithms for games. Each player maintains empirical frequencies of the opponent's past actions and best-responds to this historical distribution.

**Algorithm:**
1. Initialize counts $n_j(a_j) = 0$ for each opponent action.
2. At round $t$:
   - Compute opponent's empirical strategy: $\hat{\sigma}_j^t(a_j) = n_j(a_j) / t$.
   - Play best response: $a_i^t = \arg\max_{a_i} \sum_{a_j} R_i(a_i, a_j) \hat{\sigma}_j^t(a_j)$.
   - Update counts: $n_j(a_j^t) \leftarrow n_j(a_j^t) + 1$.

**Convergence:** In two-player zero-sum games, the **average strategies** of fictitious play converge to a Nash equilibrium (Robinson, 1951). The iterates themselves may cycle, but the time-averaged behavior converges.

**Rate:** Convergence is $O(1/\sqrt{T})$ in exploitability --- slow but guaranteed. For $n$-player general-sum games, fictitious play does not always converge (Shapley, 1964, gave a counterexample in a 3x3 game).

### Counterfactual Regret Minimization (CFR)

CFR (Zinkevich et al., 2008) is the foundational algorithm behind modern poker AI. It operates on **extensive-form games** --- games represented as trees with sequential actions, chance nodes, and information sets.

**Information set $I$:** A set of game states that are indistinguishable to the acting player (same action history from that player's perspective, but different hidden information).

**Counterfactual value:** For player $i$, strategy profile $\sigma$, and information set $I$:

$$v_i(\sigma, I) = \sum_{h \in I} \pi_{-i}^{\sigma}(h) \sum_{z \in Z_h} \pi^{\sigma}(h, z) u_i(z)$$

where $\pi_{-i}^{\sigma}(h)$ is the probability of reaching history $h$ given everyone **except** player $i$ plays according to $\sigma$, and $u_i(z)$ is $i$'s utility at terminal node $z$.

**Counterfactual regret** for not playing action $a$ at information set $I$:

$$r_i^t(I, a) = v_i(\sigma^t|_{I \to a}, I) - v_i(\sigma^t, I)$$

where $\sigma^t|_{I \to a}$ is the strategy that always plays $a$ at $I$ and follows $\sigma^t$ elsewhere.

**Cumulative regret:** $R_i^T(I, a) = \sum_{t=1}^{T} r_i^t(I, a)$

**Regret matching** produces the next strategy:

$$\sigma_i^{T+1}(I, a) = \begin{cases} \frac{R_i^{T,+}(I, a)}{\sum_{a'} R_i^{T,+}(I, a')} & \text{if } \sum_{a'} R_i^{T,+}(I, a') > 0 \\ \frac{1}{|\mathcal{A}(I)|} & \text{otherwise} \end{cases}$$

where $R_i^{T,+}(I, a) = \max(R_i^T(I, a), 0)$.

**Theorem (Zinkevich et al., 2008).** In a two-player zero-sum game, if both players use CFR, the average strategy profile $\bar{\sigma}^T$ converges to a Nash equilibrium, with exploitability bounded by $O(1/\sqrt{T})$.

### From CFR to Superhuman Poker

**Libratus** (Brown & Sandholm, 2017) beat top human professionals in heads-up no-limit Texas Hold'em using three modules:

1. **Blueprint strategy:** CFR+ (a variant with faster convergence) computed offline over an abstracted game (~$10^{12}$ information sets reduced to ~$10^9$).
2. **Nested subgame solving:** During actual play, Libratus refined its strategy in real-time for the specific subgame reached, using the blueprint as a starting point.
3. **Self-improvement:** After each day of play, Libratus identified actions where humans found exploits and added these to its action abstraction.

**Pluribus** (Brown & Sandholm, 2019) extended this to **6-player** no-limit Hold'em --- a fundamentally harder problem because 6-player games have no minimax theorem guarantee. Pluribus used:
- A modified CFR (Linear CFR) for the blueprint.
- **Depth-limited search** with learned value functions at leaves.
- The innovation: rather than modeling each opponent individually, Pluribus assumed all opponents play the blueprint strategy during search. This "multiplayer blueprint" approach proved sufficient.

Result: Pluribus achieved a win rate of ~5 bb/100 against elite professionals over 10,000 hands, with $p < 0.001$ --- a decisive, statistically significant victory.

## Formal Definitions

**Definition (Exploitability).** The exploitability of a strategy $\sigma_i$ in a two-player zero-sum game is:

$$\epsilon(\sigma_i) = v^* - \min_{\sigma_{-i}} u_i(\sigma_i, \sigma_{-i}) = v^* - \text{(value agent } i \text{ guarantees)}$$

A Nash equilibrium strategy has exploitability 0. Exploitability measures "how much value you leave on the table" against a worst-case opponent.

**Definition (Extensive-Form Game).** An extensive-form game is a tuple $\Gamma = \langle \mathcal{N}, H, Z, A, \tau, \rho, u, \mathcal{I} \rangle$ where $H$ is the set of non-terminal histories, $Z$ is terminal histories, $A$ maps histories to available actions, $\tau$ maps histories to acting player (including chance), $\rho$ is chance's strategy, $u$ is utility, and $\mathcal{I} = \{\mathcal{I}_i\}_{i \in \mathcal{N}}$ is the information partition.

**Theorem (Kuhn, 1953).** Every finite extensive-form game with perfect recall has a Nash equilibrium in behavioral strategies.

## Worked Examples

### Example 1: Minimax in a 2x3 Game

Row player's payoff matrix:

$$A = \begin{pmatrix} 3 & -1 & 2 \\ -2 & 4 & 1 \end{pmatrix}$$

**Row player (maximizer):** For mixed strategy $\mathbf{x} = (p, 1-p)$:
- vs. Column 1: $3p - 2(1-p) = 5p - 2$
- vs. Column 2: $-p + 4(1-p) = 4 - 5p$
- vs. Column 3: $2p + (1-p) = p + 1$

Maximin: maximize $\min(5p - 2, 4 - 5p, p + 1)$.

Setting $5p - 2 = 4 - 5p$: $10p = 6$, so $p = 0.6$. Value: $5(0.6) - 2 = 1$.
Check: $p + 1 = 1.6 > 1$. So the binding constraints are columns 1 and 2.

Game value: $v^* = 1$. Row plays $(0.6, 0.4)$. Column plays a mixture of columns 1 and 2 only (column 3 is dominated in this equilibrium support).

For column's strategy $\mathbf{y} = (q_1, q_2, 0)$ with $q_1 + q_2 = 1$:
- vs. Row 1: $3q_1 - q_2 = 3q_1 - (1 - q_1) = 4q_1 - 1 = 1 \Rightarrow q_1 = 0.5$

Nash equilibrium: Row plays $(0.6, 0.4)$, Column plays $(0.5, 0.5, 0)$, value $= 1$.

### Example 2: Fictitious Play in Rock-Paper-Scissors

Payoff matrix (row player):

$$A = \begin{pmatrix} 0 & -1 & 1 \\ 1 & 0 & -1 \\ -1 & 1 & 0 \end{pmatrix}$$

Nash equilibrium: $(1/3, 1/3, 1/3)$ for both players. Trace fictitious play:

**Round 1:** No history. Both play uniformly at random. Say P1 plays R, P2 plays S. P1 wins (+1).
- Counts: P1 sees P2 played S(1). P2 sees P1 played R(1).

**Round 2:** P1 best-responds to (0,0,1) = play R. P2 best-responds to (1,0,0) = play P.
- P1 plays R, P2 plays P. P2 wins. Counts: P2 played {S:1, P:1}. P1 played {R:2}.

**Round 3:** P1 best-responds to (0, 1/2, 1/2) = play R (ties with S, assume R). P2 best-responds to (1, 0, 0) = play P.
- P1 plays R, P2 plays P. Counts: P2 played {S:1, P:2}. P1 played {R:3}.

**Round 4:** P1 best-responds to (0, 2/3, 1/3) = play S. P2 best-responds to (1, 0, 0) = play P.
- P1 plays S, P2 plays P. P1 wins. Counts: P2 played {S:1, P:3}. P1 played {R:3, S:1}.

The iterates cycle, but the **average strategies** slowly converge to $(1/3, 1/3, 1/3)$. After $T$ rounds, exploitability $\leq O(1/\sqrt{T})$.

### Example 3: One Step of CFR

Simplified poker: 2 players, 2 cards (King, Queen). Player 1 receives a card, then chooses Bet or Check. If Bet, Player 2 chooses Call or Fold.

Player 1's information sets: $I_K = \{\text{holding King}\}$, $I_Q = \{\text{holding Queen}\}$.

Suppose at iteration $t$, cumulative regrets are:
- $R^t(I_K, \text{Bet}) = 5$, $R^t(I_K, \text{Check}) = -2$
- $R^t(I_Q, \text{Bet}) = -3$, $R^t(I_Q, \text{Check}) = 4$

Regret matching for $I_K$: positive regrets are Bet=5, Check=0. Strategy: $\sigma(I_K) = (\text{Bet}: 1.0, \text{Check}: 0.0)$.

Regret matching for $I_Q$: positive regrets are Bet=0, Check=4. Strategy: $\sigma(I_Q) = (\text{Bet}: 0.0, \text{Check}: 1.0)$.

This makes intuitive sense: bet with a King (value bet), check with a Queen (no bluff yet). As training continues and bluffing becomes profitable, regrets will shift.

## Arena Connection

Arena experiments create a competitive environment where student agents optimize gamification parameters against each other. The competitive dynamics mirror the theory:

- **Exploitability as a metric:** Just as poker AI measures strategy quality by exploitability, Arena agents can be evaluated by how much a best-response agent could outperform them. The platform's comparative metrics serve this purpose.
- **Self-play for agent development:** Students can train agents using self-play before deploying to Arena. The SDK's `agent.get_history()` provides the data needed to simulate self-play offline.
- **Regret minimization:** The bandit algorithms from Weeks 4-6 (UCB, Thompson Sampling) are online regret minimizers. CFR extends this idea to sequential games. In Arena, agents face sequential decisions (observe metrics, adjust config, observe new metrics) --- a natural extensive-form structure.

## Discussion Questions

1. The minimax theorem guarantees optimal play in two-player zero-sum games. Pluribus succeeded in 6-player poker despite no such guarantee. What structural properties of poker make this possible? Would the same approach work in a 6-player general-sum game?

2. CFR converges at rate $O(1/\sqrt{T})$. For a game with $10^{12}$ information sets, estimate the number of iterations needed to achieve exploitability below 1 milli-big-blind. What computational techniques make this feasible?

3. Self-play can lead to "strategy forgetting" where the agent loses ability to beat earlier versions. Propose a concrete mechanism to prevent this and analyze its computational cost.

4. In what sense is the Arena competition "zero-sum"? Are there scenarios where cooperation between student agents could yield higher payoffs for all? What game-theoretic concept describes this tension?

## Further Reading

1. **Brown, N. & Sandholm, T. (2019).** "Superhuman AI for Multiplayer Poker." *Science*, 365(6456). --- The Pluribus paper; demonstrates CFR-based AI beating 6 human professionals.

2. **Lanctot, M. et al. (2019).** "OpenSpiel: A Framework for Reinforcement Learning in Games." *arXiv:1908.09453*. --- DeepMind's open-source framework implementing CFR, fictitious play, and many MARL algorithms.

3. **Farina, G., Kroer, C., & Sandholm, T. (2019).** "Online Convex Optimization for Sequential Decision Processes and Extensive-Form Games." *AAAI*. --- Modern regret minimization techniques that achieve faster convergence than vanilla CFR.
