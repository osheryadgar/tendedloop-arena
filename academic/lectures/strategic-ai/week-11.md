# Week 11: Mechanism Design

> Strategic AI: From Agents to Multi-Agent Systems

## Overview

Mechanism design inverts the game theory question: instead of analyzing how rational agents behave in a given game, we ask how to **design** the game so that self-interested agents' behavior produces a desired outcome. This "reverse game theory" framework underlies auctions, voting systems, matching markets, and --- critically for this course --- the design of incentive structures in gamification and AI systems.

## Key Concepts

### Mechanism Design as Reverse Game Theory

In standard game theory, the game is given and we predict behavior. In mechanism design, the desired outcome is given and we engineer the game.

**The designer's problem:** A social planner wants to implement a **social choice function** $f: \Theta \rightarrow X$ mapping agent types (private preferences) $\theta = (\theta_1, \dots, \theta_n) \in \Theta$ to outcomes $x \in X$. The challenge: the planner does not know agents' types. Agents will strategically misreport if it benefits them.

A **mechanism** $\mathcal{M} = (\mathcal{S}, g)$ specifies:
- A strategy space $\mathcal{S}_i$ for each agent (what they can report),
- An outcome function $g: \mathcal{S}_1 \times \cdots \times \mathcal{S}_n \rightarrow X$ mapping reports to outcomes.

The mechanism **implements** $f$ if, in equilibrium, the outcome matches $f(\theta)$ for all type profiles $\theta$.

### Arrow's Impossibility Theorem

Before designing mechanisms, we must understand what is achievable.

**Arrow's Impossibility Theorem (1951).** For $|X| \geq 3$ alternatives and $n \geq 2$ voters, there is no social welfare function $F$ (a rule that maps individual preference orderings to a social preference ordering) satisfying all of:

1. **Unrestricted domain:** $F$ works for all possible preference profiles.
2. **Pareto efficiency:** If all agents prefer $x$ to $y$, so does the social ordering.
3. **Independence of irrelevant alternatives (IIA):** The social ranking of $x$ vs. $y$ depends only on individual rankings of $x$ vs. $y$.
4. **Non-dictatorship:** No single agent's preferences always determine the social ordering.

**Implication:** There is no "perfect" voting system. Every non-dictatorial aggregation rule with $\geq 3$ alternatives must violate Pareto efficiency or IIA. This is not a mere technicality --- it fundamentally constrains what mechanism designers can achieve.

**Escape routes:** Arrow's theorem applies to ordinal aggregation. If we allow cardinal utilities (willingness to pay), monetary transfers, or restrict the domain, we can circumvent it. VCG mechanisms take exactly this route.

### Incentive Compatibility and the Revelation Principle

**Definition (Dominant Strategy Incentive Compatible, DSIC).** A mechanism is DSIC if truth-telling is a dominant strategy for every agent:

$$u_i(g(\theta_i, s_{-i}), \theta_i) \geq u_i(g(s_i, s_{-i}), \theta_i) \quad \forall s_i \in \mathcal{S}_i, \, \forall s_{-i} \in \mathcal{S}_{-i}, \, \forall \theta_i \in \Theta_i$$

No matter what other agents do, agent $i$ is best off reporting their true type $\theta_i$.

**The Revelation Principle (Myerson, 1981).** For any mechanism $\mathcal{M}$ that implements social choice function $f$ in some equilibrium, there exists a **direct revelation mechanism** where $\mathcal{S}_i = \Theta_i$ (agents simply report their type) and truth-telling is an equilibrium, implementing the same $f$.

**Significance:** The revelation principle is enormously simplifying. Instead of searching over all possible mechanism formats (auctions, voting rules, bargaining protocols, etc.), we need only consider direct mechanisms where agents report types truthfully. If no direct truthful mechanism implements $f$, then no mechanism of any form can implement $f$ in that equilibrium concept.

### The VCG Mechanism

The **Vickrey-Clarke-Groves (VCG) mechanism** is the most important constructive result in mechanism design. It works for settings with **quasi-linear utilities**: agent $i$'s utility is $u_i = v_i(x, \theta_i) - p_i$ where $v_i$ is the valuation and $p_i$ is a monetary payment.

**VCG mechanism:**
1. **Allocation rule:** Choose the outcome that maximizes social welfare:
$$x^*(\hat{\theta}) = \arg\max_{x \in X} \sum_{i=1}^{n} v_i(x, \hat{\theta}_i)$$

2. **Payment rule:** Each agent $i$ pays:
$$p_i(\hat{\theta}) = \max_{x \in X} \sum_{j \neq i} v_j(x, \hat{\theta}_j) - \sum_{j \neq i} v_j(x^*(\hat{\theta}), \hat{\theta}_j)$$

**Interpretation of payment:** Agent $i$ pays the **externality** they impose on others. The first term is the maximum welfare achievable by others without $i$; the second is others' welfare in the chosen outcome. The difference is the "damage" $i$'s presence causes to others.

**Theorem.** The VCG mechanism is:
1. **DSIC:** Truth-telling is a dominant strategy.
2. **Allocatively efficient:** It maximizes total welfare.
3. **Individually rational** (under Clarke pivot rule): No agent pays more than their value.

**Proof of DSIC:** If agent $i$ reports $\hat{\theta}_i$ instead of $\theta_i$, their utility is:

$$u_i = v_i(x^*(\hat{\theta}_i, \hat{\theta}_{-i}), \theta_i) - p_i = v_i(x^*, \theta_i) + \sum_{j \neq i} v_j(x^*, \hat{\theta}_j) - \underbrace{\max_x \sum_{j \neq i} v_j(x, \hat{\theta}_j)}_{\text{constant w.r.t. } \hat{\theta}_i}$$

Since the last term is independent of $i$'s report, $i$ maximizes utility by choosing $\hat{\theta}_i$ that maximizes $v_i(x^*, \theta_i) + \sum_{j \neq i} v_j(x^*, \hat{\theta}_j)$. But this is exactly what the allocation rule does when $\hat{\theta}_i = \theta_i$. $\square$

### The Vickrey Auction (VCG Special Case)

The **second-price sealed-bid auction** (Vickrey, 1961) is VCG applied to selling a single item.

- $n$ bidders, each with private value $\theta_i$ for the item.
- Allocation: item goes to highest bidder $i^* = \arg\max_i \hat{\theta}_i$.
- Payment: winner pays $p_{i^*} = \max_{j \neq i^*} \hat{\theta}_j$ (second-highest bid).
- Losers pay nothing.

**DSIC:** Bidding your true value is dominant. If you bid higher, you risk winning at a price above your value. If you bid lower, you risk losing when you would have profited. The second-price payment eliminates the incentive to shade your bid.

### Connection to Gamification and Incentive Design

Mechanism design provides the theoretical foundation for designing incentive structures:

**XP reward systems as mechanisms.** A gamification system assigns XP (the "payment" or reward) based on user actions (the "reports" of effort/engagement). The designer wants to elicit genuine engagement (the "social choice"), not gaming behavior.

**Design principles from mechanism design:**
- **Incentive compatibility:** The XP structure should make genuine engagement the dominant strategy. If users can earn more XP through low-quality rapid submissions than through thoughtful feedback, the mechanism is not incentive-compatible.
- **Individual rationality:** Users must be better off participating than not (positive expected utility from engagement).
- **Budget balance:** Total XP distributed should be sustainable (analogous to revenue in auctions).

**Goodhart's Law as mechanism failure:** "When a measure becomes a target, it ceases to be a good measure." This is precisely what happens when a gamification mechanism is not incentive-compatible: agents optimize the metric rather than the underlying desired behavior.

## Formal Definitions

**Definition (Social Choice Function).** A social choice function $f: \Theta_1 \times \cdots \times \Theta_n \rightarrow X$ maps type profiles to outcomes.

**Definition (Implementation).** Mechanism $\mathcal{M}$ implements $f$ in dominant strategies if for every type profile $\theta$, the dominant strategy equilibrium outcome is $f(\theta)$.

**Definition (Quasi-Linear Environment).** Agent $i$'s utility is $u_i(x, p_i, \theta_i) = v_i(x, \theta_i) - p_i$, separable in outcome valuation and payment.

**Theorem (Green-Laffont, 1977).** In a quasi-linear environment with unrestricted valuation domain, the only DSIC mechanisms that are allocatively efficient are the VCG family (Groves mechanisms).

**Theorem (Gibbard-Satterthwaite, 1973).** For $|X| \geq 3$ and unrestricted preferences, the only DSIC social choice functions are dictatorships. (This is the mechanism design analog of Arrow's theorem --- monetary transfers provide the escape route.)

## Worked Examples

### Example 1: VCG for a Multi-Item Allocation

Two items (A, B), three bidders with valuations:

| Bidder | $v(\{A\})$ | $v(\{B\})$ | $v(\{A,B\})$ |
|--------|-----------|-----------|-------------|
| 1 | 10 | 5 | 12 |
| 2 | 8 | 7 | 14 |
| 3 | 3 | 9 | 11 |

**Step 1: Efficient allocation.** Enumerate feasible allocations (each item to one bidder):

| Allocation | Welfare |
|------------|---------|
| A$\to$1, B$\to$2 | 10 + 7 = 17 |
| A$\to$1, B$\to$3 | 10 + 9 = 19 |
| A$\to$2, B$\to$1 | 8 + 5 = 13 |
| A$\to$2, B$\to$3 | 8 + 9 = 17 |
| A$\to$3, B$\to$1 | 3 + 5 = 8 |
| A$\to$3, B$\to$2 | 3 + 7 = 10 |
| $\{A,B\}\to$1 | 12 |
| $\{A,B\}\to$2 | 14 |
| $\{A,B\}\to$3 | 11 |

Optimal: A$\to$1, B$\to$3 with welfare 19.

**Step 2: VCG payments.**

*Bidder 1 (gets A):*
- Others' welfare with 1 present: $v_3(B) = 9$.
- Others' max welfare without 1: best allocation of A,B to {2,3}: A$\to$2, B$\to$3 gives $8 + 9 = 17$.
- Payment: $p_1 = 17 - 9 = 8$.
- Utility: $10 - 8 = 2 > 0$. Individually rational.

*Bidder 3 (gets B):*
- Others' welfare with 3 present: $v_1(A) = 10$.
- Others' max welfare without 3: A$\to$1, B$\to$2 gives $10 + 7 = 17$, or $\{A,B\}\to$2 gives 14. Max = 17.
- Payment: $p_3 = 17 - 10 = 7$.
- Utility: $9 - 7 = 2 > 0$.

*Bidder 2 (gets nothing):* $p_2 = 0$. Revenue: $8 + 7 = 15$.

### Example 2: Vickrey Auction

Four bidders, values: $\theta_1 = 100, \theta_2 = 80, \theta_3 = 60, \theta_4 = 45$.

Under truthful bidding (which is dominant):
- Winner: Bidder 1 (highest bid = 100).
- Payment: Second-highest bid = 80.
- Bidder 1's surplus: $100 - 80 = 20$.

**Why not lie?** If bidder 1 bids 70 (underbid), they lose to bidder 2. Surplus drops from 20 to 0. If bidder 2 bids 90 (overbid) and wins, they pay 80 but value it at 80, getting surplus 0 --- no better than losing. If bidder 2 bids 105 (overbid past bidder 1), they pay 100 but value it at 80: negative surplus of $-20$. Overbidding is strictly dominated.

### Example 3: Designing an XP Mechanism

A gamification platform wants to incentivize high-quality feedback. User types: $\theta \in \{\text{low-effort}, \text{high-effort}\}$. The designer observes a quality signal $q \in \{0, 1\}$ correlated with effort.

**Naive mechanism:** Award $\text{XP} = 10$ per submission, regardless of quality. Problem: low-effort users submit many low-quality responses. Not incentive-compatible for the "genuine engagement" social choice.

**VCG-inspired mechanism:** Award XP based on the marginal value of the submission to the system:
- If submission quality $q = 1$: $\text{XP} = c_H + \Delta$, where $c_H$ is the cost of high effort and $\Delta > 0$.
- If $q = 0$: $\text{XP} = c_L$ (just covers low-effort cost).

For incentive compatibility, high-effort users must prefer the honest strategy:
$$c_H + \Delta - c_H \geq p(q=1|\text{low}) \cdot (c_H + \Delta) + p(q=0|\text{low}) \cdot c_L - c_L$$

This gives $\Delta \geq \frac{p(q=1|\text{low}) \cdot (c_H + \Delta - c_L)}{1 - p(q=1|\text{low})}$, constraining the XP premium needed to separate types.

## Arena Connection

Arena is itself a mechanism design problem. The platform designer (instructor) chooses:
- How agents' configurations map to user experience (the allocation rule).
- How agents are scored/ranked (the payment/reward rule).
- What information agents receive (the information structure).

**Incentive alignment in Arena:**
- The scoring function should make "genuinely optimizing user experience" the dominant strategy, not "gaming the metric."
- VCG-style thinking: an agent's score should reflect its **marginal contribution** to overall experiment quality, not just its raw performance.
- **Budget balance:** The total "reward" (grades, recognition) is fixed; mechanism design ensures fair distribution based on true contribution.

**Student agents as mechanism designers:** Each agent designs an XP economy for its user cohort. The agent is simultaneously a player in the Arena game AND a mechanism designer for its users. This nested structure --- a game where each player designs a game --- is called a **meta-mechanism** and is an active research area.

## Discussion Questions

1. The Gibbard-Satterthwaite theorem says all non-dictatorial DSIC mechanisms with $\geq 3$ alternatives must use monetary transfers. How does gamification XP function as a "monetary transfer" in this framework? What breaks if XP is non-transferable?

2. VCG mechanisms are DSIC but not budget-balanced in general (the mechanism may run a deficit or surplus). Design a modification that achieves approximate budget balance while maintaining approximate incentive compatibility. What is the tradeoff?

3. Consider Arena's scoring function as a mechanism. If agents are scored on raw engagement metrics (clicks, submissions), what Goodhart's Law failure modes could emerge? Propose a scoring mechanism that is robust to gaming.

4. Arrow's theorem shows no perfect voting rule exists for ordinal preferences. Yet we routinely use voting (elections, committee decisions). Does Arrow's theorem matter in practice? Why or why not?

## Further Reading

1. **Nisan, N. et al. (Eds.) (2007).** *Algorithmic Game Theory.* Cambridge University Press, Ch. 9-12. --- Comprehensive treatment of mechanism design, VCG, combinatorial auctions, and computational aspects.

2. **Myerson, R. B. (1981).** "Optimal Auction Design." *Mathematics of Operations Research*, 6(1). --- The foundational paper on revenue-maximizing auctions; introduces the revelation principle in its general form.

3. **Conitzer, V. & Sandholm, T. (2002).** "Complexity of Mechanism Design." *UAI*. --- Shows that designing optimal mechanisms is computationally hard in general, connecting mechanism design to computational complexity.
