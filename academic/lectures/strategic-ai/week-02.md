# Week 2: Normal-Form Games and Nash Equilibrium

> Strategic AI: From Agents to Multi-Agent Systems

## Overview

This lecture introduces the mathematical framework for reasoning about strategic interactions between multiple decision-makers. We move from single-agent MDPs to multi-agent settings where the outcome depends on the *joint* actions of all agents. Normal-form (strategic-form) games provide the simplest model of such interactions, and Nash Equilibrium provides the central solution concept — the idea that rational agents will settle into strategy profiles from which no one wants to unilaterally deviate.

## Key Concepts

### Strategic Form Games

When multiple agents interact simultaneously (or without knowledge of each other's choices), we model the interaction as a normal-form game.

> **Definition (Normal-Form Game).** A finite normal-form game is a tuple **G = (N, {S_i}_{i in N}, {u_i}_{i in N})** where:
> - **N = {1, 2, ..., n}** is a finite set of players
> - **S_i** is a finite set of pure strategies (actions) available to player *i*
> - **u_i : S_1 x S_2 x ... x S_n -> R** is the utility (payoff) function for player *i*

A **strategy profile** is a tuple **s = (s_1, s_2, ..., s_n)** specifying one strategy per player. We write **s_{-i}** for the strategies of all players except *i*, so **s = (s_i, s_{-i})**.

For two-player games, we represent payoffs as a **bimatrix**. Player 1 (row) chooses a row, Player 2 (column) chooses a column. Each cell contains a pair (u_1, u_2).

### Dominant Strategies and Iterated Dominance

Before computing equilibria, we can sometimes simplify games by eliminating strategies that no rational player would ever use.

> **Definition (Strict Dominance).** Strategy s_i strictly dominates strategy s_i' if for all s_{-i} in S_{-i}: u_i(s_i, s_{-i}) > u_i(s_i', s_{-i}).

A rational player will never play a strictly dominated strategy. **Iterated elimination of strictly dominated strategies (IESDS)** repeatedly removes dominated strategies until no more can be eliminated. IESDS is order-independent (the same strategies survive regardless of elimination order) and preserves all Nash Equilibria.

> **Definition (Weak Dominance).** Strategy s_i weakly dominates s_i' if u_i(s_i, s_{-i}) >= u_i(s_i', s_{-i}) for all s_{-i}, with strict inequality for at least one s_{-i}.

Unlike strict dominance, iterated elimination of *weakly* dominated strategies is order-dependent and can eliminate Nash Equilibria. Use with caution.

### Nash Equilibrium

The central solution concept in non-cooperative game theory:

> **Definition (Nash Equilibrium).** A strategy profile **s* = (s_1*, ..., s_n*)** is a Nash Equilibrium if for every player *i* and every alternative strategy s_i in S_i:
>
> **u_i(s_i*, s_{-i}*) >= u_i(s_i, s_{-i}*)**
>
> No player can improve their payoff by unilaterally changing their strategy.

A NE is *strict* if the inequality is strict for all s_i != s_i*. Note: NE does not require that the outcome is "good" for anyone — only that it is stable.

### Mixed Strategies

Pure strategy NE need not exist (Rock-Paper-Scissors has none). We extend the framework:

> **Definition (Mixed Strategy).** A mixed strategy for player *i* is a probability distribution **sigma_i in Delta(S_i)** over pure strategies. The expected utility under mixed profile sigma = (sigma_1, ..., sigma_n) is:
>
> **u_i(sigma) = sum_{s in S} (prod_{j in N} sigma_j(s_j)) * u_i(s)**

A **mixed strategy Nash Equilibrium (MSNE)** is a profile of mixed strategies from which no player can improve expected utility by unilateral deviation.

### Nash's Existence Theorem

> **Theorem (Nash, 1950).** Every finite normal-form game has at least one Nash Equilibrium (possibly in mixed strategies).

**Proof sketch.** Define a continuous function f from the compact, convex set of mixed strategy profiles to itself, where f adjusts each player's mixing probabilities toward better responses. By Brouwer's Fixed Point Theorem, f has a fixed point. At a fixed point, no player has incentive to deviate — this is a Nash Equilibrium.

More precisely: let sigma be a mixed strategy profile. For each player *i* and pure strategy s_i, define the "regret" r_i(s_i, sigma) = max(0, u_i(s_i, sigma_{-i}) - u_i(sigma)). Then define:

f_i(s_i)(sigma) = (sigma_i(s_i) + r_i(s_i, sigma)) / (1 + sum_{s_i'} r_i(s_i', sigma))

This maps Delta(S_1) x ... x Delta(S_n) continuously into itself. By Brouwer, it has a fixed point. At a fixed point, all regrets are zero, which is exactly the NE condition.

### Computing Nash Equilibria: Support Enumeration

For two-player games, we can find all NE by **support enumeration**. The **support** of a mixed strategy sigma_i is the set of pure strategies played with positive probability: supp(sigma_i) = {s_i : sigma_i(s_i) > 0}.

**Key insight**: At a MSNE, every pure strategy in a player's support must yield the same expected utility. Otherwise, the player would shift probability toward the higher-payoff strategy.

**Algorithm (Support Enumeration for 2-player games):**
1. Enumerate all possible support pairs (T_1 subset S_1, T_2 subset S_2).
2. For each pair, solve the system of linear equations requiring:
   - Player 2's mixture makes Player 1 indifferent over T_1.
   - Player 1's mixture makes Player 2 indifferent over T_2.
   - Probabilities sum to 1 and are non-negative.
3. Verify: strategies outside the support must yield weakly lower expected utility.

This runs in exponential time in the worst case. Computing NE is PPAD-complete (Daskalakis, Goldberg, Papadimitriou, 2009) — unlikely to be polynomial-time solvable.

## Formal Definitions

> **Best Response.** Player *i*'s best response to s_{-i} is BR_i(s_{-i}) = argmax_{s_i in S_i} u_i(s_i, s_{-i}). A strategy profile is a NE iff every player is playing a best response.

> **Pareto Optimality.** Profile s Pareto dominates s' if u_i(s) >= u_i(s') for all i, with strict inequality for at least one. A profile is Pareto optimal if no profile Pareto dominates it.

> **Social Welfare.** The social welfare of profile s is sum_i u_i(s). The **Price of Anarchy** is the ratio of optimal social welfare to the worst NE social welfare.

## Worked Examples

### Example 1: Prisoner's Dilemma

|  | C | D |
|--|---|---|
| **C** | (3, 3) | (0, 5) |
| **D** | (5, 0) | (1, 1) |

D strictly dominates C for both players: regardless of the opponent's choice, D yields a higher payoff. The unique NE is (D, D) with payoffs (1, 1).

Yet (C, C) with payoffs (3, 3) Pareto dominates (D, D). This is the tragedy: individual rationality leads to a collectively suboptimal outcome. The Price of Anarchy is 6/2 = 3.

### Example 2: Battle of the Sexes

|  | Opera | Football |
|--|-------|----------|
| **Opera** | (3, 2) | (0, 0) |
| **Football** | (0, 0) | (2, 3) |

No dominated strategies. Two pure NE: (Opera, Opera) and (Football, Football).

For the mixed NE, let Player 1 play Opera with probability *p* and Player 2 play Opera with probability *q*.

Player 2 must be indifferent: u_2(Opera) = u_2(Football).
- u_2(Opera) = p * 2 + (1-p) * 0 = 2p
- u_2(Football) = p * 0 + (1-p) * 3 = 3(1-p)
- 2p = 3 - 3p => 5p = 3 => **p = 3/5**

Player 1 must be indifferent: u_1(Opera) = u_1(Football).
- u_1(Opera) = q * 3 + (1-q) * 0 = 3q
- u_1(Football) = q * 0 + (1-q) * 2 = 2(1-q)
- 3q = 2 - 2q => 5q = 2 => **q = 2/5**

Mixed NE: sigma_1 = (3/5, 2/5), sigma_2 = (2/5, 3/5). Expected payoffs: u_1 = 3 * (2/5) = 6/5, u_2 = 2 * (3/5) = 6/5. Both players get 6/5 in the mixed NE — worse than either pure NE. Mixing is costly.

### Example 3: Matching Pennies (Zero-Sum)

|  | H | T |
|--|---|---|
| **H** | (1, -1) | (-1, 1) |
| **T** | (-1, 1) | (1, -1) |

No pure NE. By symmetry, the unique MSNE is sigma_1 = sigma_2 = (1/2, 1/2). Expected payoff: 0 for both.

Verification: If Player 1 plays H with probability 1/2, Player 2's payoff from H is (1/2)(-1) + (1/2)(1) = 0, and from T is (1/2)(1) + (1/2)(-1) = 0. Player 2 is indifferent, confirming equilibrium.

## Arena Connection

Arena experiments can be modeled as games when multiple agents compete for the same arms. Consider two agents, each choosing between arm A and arm B. If both choose the same arm, they split the reward; if they choose different arms, each gets the full reward. This creates a coordination game with the structure of Battle of the Sexes.

In the Arena workshop (Sessions 2-3), students observe this dynamic: naive agents that ignore competitors converge to suboptimal outcomes. Understanding NE helps predict which arm allocations are stable and which will be disrupted by strategic behavior.

The Arena SDK's `experiment.get_competitors()` (if available in competitive mode) provides the observation needed to compute best responses. Students can implement fictitious play or regret matching to converge toward equilibrium allocations.

## Discussion Questions

1. The Prisoner's Dilemma shows that Nash Equilibrium can be Pareto dominated. Does this mean NE is a bad solution concept, or does it mean cooperation is genuinely hard? Under what conditions might cooperation emerge (hint: repeated games)?

2. Computing Nash Equilibria is PPAD-complete. What does this mean practically? If agents can't compute NE efficiently, should we expect real agents to play equilibrium strategies? What alternative behavioral models might be more realistic?

3. Battle of the Sexes has three NE (two pure, one mixed). Which would you predict real players to reach? How does the answer change with communication? With asymmetric information?

4. In a zero-sum game, the maximin strategy and the minimax strategy coincide at the NE (von Neumann's minimax theorem). Why does this result *not* extend to general-sum games?

## Further Reading

- **Nash (1950), "Equilibrium Points in N-Person Games"** — The 1-page paper that launched modern game theory. Remarkably concise; the proof uses Kakutani's fixed point theorem.
- **Daskalakis, Goldberg, Papadimitriou (2009), "The Complexity of Computing a Nash Equilibrium"** — Proves that finding NE is PPAD-complete, resolving a major open question. Explains why we should not expect efficient algorithms.
- **Nisan, Roughgarden, Tardos, Vazirani (2007), *Algorithmic Game Theory*, Ch. 1-3** — Bridges CS and economics perspectives on games; introduces Price of Anarchy with network routing examples.
