# Week 3: Extensive-Form Games and Sequential Reasoning

> Strategic AI: Multi-Agent Systems & Optimization

## Overview

Normal-form games model simultaneous decisions, but many strategic interactions unfold over time: chess, poker, negotiations, auctions with multiple rounds. Extensive-form games capture sequential structure, information asymmetry, and the ability to condition actions on observed history. This lecture introduces game trees, information sets, backward induction, and subgame perfect equilibrium — the tools needed to analyze sequential strategic reasoning.

## Key Concepts

### From Simultaneous to Sequential

In a normal-form game, all players choose simultaneously. In reality, players often move in sequence, observing (some of) their opponents' prior actions. This sequential structure changes the analysis fundamentally: a player who moves second can condition their strategy on what they observed.

The extensive form captures three things normal form cannot:
1. **Temporal ordering** of moves
2. **Information structure** — what each player knows when they act
3. **Chance events** — random moves by "nature"

### Game Trees

> **Definition (Extensive-Form Game).** An extensive-form game is a tuple **Gamma = (N, H, Z, A, chi, rho, sigma_c, u, I)** where:
> - **N** = set of players (plus nature, player 0)
> - **H** = set of non-terminal histories (decision nodes)
> - **Z** = set of terminal histories (leaves)
> - **A** = set of actions
> - **chi : H -> 2^A** assigns available actions at each node
> - **rho : H -> N union {0}** assigns which player moves at each node
> - **sigma_c** = nature's (fixed, known) strategy at chance nodes
> - **u = (u_1, ..., u_n)** where **u_i : Z -> R** are payoffs at terminal nodes
> - **I = (I_1, ..., I_n)** where **I_i** is a partition of player *i*'s decision nodes into information sets

A game tree is a rooted tree where each non-leaf node is a decision point for some player (or nature), edges represent actions, and leaves carry payoff vectors.

### Information Sets

The information set is the key concept that distinguishes perfect from imperfect information games.

> **Definition (Information Set).** An information set **I** for player *i* is a set of decision nodes such that:
> 1. Player *i* moves at every node in **I** (rho(h) = i for all h in I)
> 2. The same actions are available at every node in **I** (chi(h) = chi(h') for all h, h' in I)
> 3. Player *i* cannot distinguish between nodes in the same information set

If every information set is a singleton (contains exactly one node), the game has **perfect information** — every player observes all prior actions (chess, Go). If some information sets contain multiple nodes, the game has **imperfect information** (poker, Battleship).

### Strategies in Extensive-Form Games

A **pure strategy** for player *i* specifies an action at every information set, even those that might not be reached:

> **s_i : I_i -> A**, where **s_i(I) in chi(h)** for any **h in I**

This completeness requirement is important: strategies must specify behavior even off the equilibrium path, which matters for credibility of threats.

A **behavioral strategy** assigns a probability distribution over actions at each information set:

> **beta_i : I_i -> Delta(A)**

**Kuhn's Theorem (1953):** In games with perfect recall (a player never forgets their own prior actions or information), every mixed strategy is outcome-equivalent to a behavioral strategy. This means we can work with behavioral strategies without loss of generality — a major simplification.

### Backward Induction

For perfect information games, we can solve by reasoning backward from the terminal nodes.

**Algorithm (Backward Induction):**
1. Start at the terminal nodes.
2. At each decision node where all successors are terminal (or already solved), the acting player chooses the action maximizing their payoff.
3. Replace the subtree with the resulting payoff vector.
4. Repeat until the root is reached.

This yields a strategy profile that is a Nash Equilibrium and, more importantly, a *subgame perfect* equilibrium.

### Subgame Perfect Equilibrium

Not all Nash Equilibria of an extensive-form game are equally convincing. Some rely on **non-credible threats** — promises to take actions that would be irrational if the relevant decision point were actually reached.

> **Definition (Subgame).** A subgame of Gamma rooted at node *h* consists of all nodes and edges in the subtree below *h*, provided *h* is a singleton information set (the acting player knows they are at *h*) and the subtree does not break any information set.

> **Definition (Subgame Perfect Equilibrium).** A strategy profile is a subgame perfect equilibrium (SPE) if it induces a Nash Equilibrium in every subgame of the game.

SPE eliminates non-credible threats. In the entry deterrence game (see worked examples), the monopolist's threat to fight entry is not credible because, if entry actually occurs, accommodation yields higher profits.

**Relationship to NE:** Every SPE is a NE, but not every NE is subgame perfect. SPE is a *refinement* of NE.

### Imperfect Information: Poker as a Canonical Example

Poker is the canonical imperfect information game. Each player has private cards (their "hand"), creating information sets with multiple nodes — you know your cards but not your opponent's.

Key features that make poker hard:
- **Hidden information**: You don't observe opponent's cards.
- **Bluffing**: Betting strongly with a weak hand is a rational strategy (in equilibrium, bluffs must occur at the right frequency).
- **Information sets are large**: In No-Limit Texas Hold'em, the game tree has approximately 10^161 nodes.

The optimal strategy in a poker subgame involves randomization — mixing between value bets and bluffs at precise frequencies that make the opponent indifferent between calling and folding.

### From Theory to Superhuman Play: Pluribus

Pluribus (Brown & Sandholm, 2019) defeated elite human professionals in six-player no-limit Texas Hold'em. Key ideas:

1. **Blueprint strategy**: Computed offline using Monte Carlo CFR (see Week 9) on an abstracted game.
2. **Real-time search**: During play, Pluribus searches deeper in the current subgame, refining the blueprint. Unlike chess engines, it cannot assume opponent rationality — it must consider multiple opponent strategies.
3. **No neural networks**: Pluribus uses tabular CFR, not deep learning. The algorithm's structure, not raw computation, drives performance.

The significance: this is a 6-player, imperfect-information game with enormous state spaces. Classical game-theoretic algorithms, carefully engineered, suffice for superhuman play.

## Formal Definitions

> **Theorem (Zermelo, 1913).** Every finite perfect-information game has a pure strategy Nash Equilibrium, computable by backward induction.

> **Theorem (Kuhn, 1953).** In any extensive-form game with perfect recall, every mixed strategy is equivalent to a behavioral strategy (and vice versa).

> **Definition (Sequential Rationality).** Player *i* is sequentially rational if, at every information set reached with positive probability, their strategy maximizes expected utility conditional on reaching that information set.

## Worked Examples

### Example 1: Entry Deterrence Game

An entrant (E) decides whether to enter a market or stay out. If E enters, the monopolist (M) decides whether to fight (price war) or accommodate.

```
          E
         / \
      Enter  Stay Out
       /        \
      M       (0, 2)
     / \
  Fight  Accommodate
   /        \
(-1, -1)   (1, 1)
```

Payoffs: (E, M).

**Backward induction:** At M's node, Accommodate (payoff 1) > Fight (payoff -1). So M accommodates. E anticipates this: Enter gives payoff 1, Stay Out gives 0. E enters.

**SPE:** (Enter, Accommodate) with payoffs (1, 1).

**Non-credible NE:** (Stay Out, Fight) is also a NE — if E stays out, M's strategy is irrelevant. But M's threat to fight is not credible: if E entered, M would prefer to accommodate. SPE rules out this equilibrium.

### Example 2: Centipede Game

Two players alternate. At each turn, the current player can Stop (taking a larger share) or Continue (passing to the other player, growing the total pie).

```
P1      P2      P1      P2
|       |       |       |
S  C -- S  C -- S  C -- S  C --> (5, 5)
|       |       |       |
(1,0)  (0,2)  (3,1)  (2,4)
```

**Backward induction:** At the last node, P2 prefers Stop (4 > 5? No: 4 vs continuing to 5,5. Let me use standard payoffs.) Using standard payoffs where stopping always gives slightly more to the stopper:

At every node, backward induction says Stop. The SPE outcome is that P1 stops immediately, getting (1, 0).

Yet this is paradoxical: both players could achieve (5, 5) by always continuing. Experimental evidence shows real humans often do continue, especially in early rounds. This highlights the gap between game-theoretic prediction and human behavior — a topic we revisit with cooperative AI in Week 10.

### Example 3: Simple Poker (Kuhn Poker)

Kuhn Poker: 3 cards (J, Q, K), 2 players. Each antes 1 chip. Each receives one card. Player 1 acts first: Check or Bet (1 chip). If P1 checks, P2 can Check (showdown) or Bet. If P2 bets, P1 can Call or Fold. If P1 bets, P2 can Call or Fold.

This game has non-trivial information sets. Player 1's strategy must specify an action for each possible private card: {J, Q, K} x {Check, Bet}. But P1 doesn't know P2's card.

The Nash Equilibrium involves P1 betting with K (value bet), checking with Q, and betting with J at a specific frequency alpha in [0, 1/3] (bluff). P2's equilibrium response involves calling with K always, folding with J always, and calling with Q at a frequency that makes P1's bluff break even.

This tiny game illustrates the core of poker strategy: value betting, bluffing at balanced frequencies, and optimal calling frequencies.

## Arena Connection

Extensive-form reasoning appears in Arena when agents face sequential decision points within an experiment. Consider a multi-round Arena experiment where:

1. **Phase 1**: Agents explore arms and gather data (rounds 1-50).
2. **Phase 2**: Agents exploit their best arm (rounds 51-100).

An agent's strategy must specify behavior at every decision point — including what to do if early observations are surprising. This is analogous to specifying actions at off-path information sets.

In competitive Arena experiments, agents may observe competitors' cumulative performance (imperfect information about their strategies). The optimal response depends on the information structure: if you see your competitor pulling arm B heavily, is that because B is genuinely good, or are they bluffing (sacrificing short-term reward to mislead you)?

Workshop Session 3 introduces sequential game modeling within Arena experiments, connecting backward induction to the agent's planning horizon.

## Discussion Questions

1. Backward induction in the Centipede Game predicts immediate defection, but humans typically cooperate for several rounds. Does this mean backward induction is "wrong," or that the model (common knowledge of rationality) is wrong? How would you test the difference?

2. In Kuhn Poker, P1's optimal bluffing frequency is between 0 and 1/3 with J. Why must bluffs exist in equilibrium? What would happen if P1 never bluffed?

3. Subgame perfection requires Nash Equilibrium in every subgame, but in imperfect information games, subgames may not exist at many nodes (information sets span multiple nodes). What refinements beyond SPE address this? (Hint: sequential equilibrium, perfect Bayesian equilibrium.)

4. Pluribus uses no neural networks and defeated humans at 6-player poker. DeepMind's AlphaGo uses deep neural networks and defeated humans at Go. Why the difference in approach? What properties of each game drive the algorithmic choice?

## Further Reading

- **Brown & Sandholm (2019), "Superhuman AI for multiplayer poker"** — The Pluribus paper. Describes blueprint computation via MCCFR and real-time depth-limited search. Accessible and well-written.
- **Kuhn (1950), "A simplified two-person poker"** — The original Kuhn Poker paper. Short, elegant, and solvable by hand. An excellent exercise in applying extensive-form analysis.
- **Osborne & Rubinstein (1994), *A Course in Game Theory*, Ch. 6-7** — Rigorous treatment of extensive-form games, subgame perfection, and sequential equilibrium with careful proofs.
