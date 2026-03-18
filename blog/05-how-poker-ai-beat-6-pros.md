# How Poker AI Beat 6 Pros (and What It Means for Your Agent)

In July 2019, something remarkable happened at a poker table in Pittsburgh. Something that changed how we think about AI in competitive, multi-agent environments. An AI system called Pluribus, built by Noam Brown and Tuomas Sandholm at Carnegie Mellon, sat down at a six-player no-limit Texas Hold'em table with five professional poker players. These were not weekend hobbyists — they were elite professionals who had won millions in tournaments.

Over 10,000 hands, Pluribus won decisively. Not by a hair. By a statistically overwhelming margin, with a p-value below 0.001. The pros were not just beaten — they were outclassed. Darren Elias, who holds the record for most World Poker Tour titles, said the AI's plays were unlike anything he had seen from a human. It would make bets that seemed irrational on the surface but turned out to be mathematically sound. It bluffed at exactly the right frequency. It was, in the pros' own words, unreadable.

And here is the part that should grab your attention: the core ideas behind Pluribus are surprisingly relevant to what your Arena agent is doing. Not because you need to build a poker AI, but because Pluribus solved a problem that every multi-agent system faces — how to make decisions when other agents are making decisions at the same time.

## Why Poker is the Hardest Game

By 2019, AI had already conquered chess (Deep Blue, 1997), Go (AlphaGo, 2016), and heads-up poker (Libratus, 2017). So what made six-player poker different?

Chess and Go are *perfect information* games. You can see the entire board. Every piece, every stone, everything is visible to both players. The game tree is enormous, but there is no hidden information.

Poker is *imperfect information*. You cannot see your opponents' cards. You do not know if that raise means they have a great hand or if they are bluffing. And crucially, *they do not know what you have either*. Every decision is made under a fog of uncertainty.

This changes everything. In chess, if your opponent makes a brilliant move, you can see it and react. In poker, your opponent might be holding garbage cards and betting like they have a royal flush. Or they might have the best hand at the table and checking like they have nothing. The information asymmetry is the game.

Then add five opponents instead of one. In two-player games, there are clean mathematical guarantees about optimal play (we will get to that). In six-player games, those guarantees largely evaporate. The theory does not tell you what "optimal" even means when there are six competing interests at the table.

Pluribus figured it out anyway.

## Game Theory Through Rock-Paper-Scissors

Before we can understand why Pluribus matters, we need to talk about game theory. And the best way to understand game theory is not through poker — it is through the simplest competitive game you already know: Rock-Paper-Scissors.

Seriously. RPS contains almost every key concept from game theory in a form you can reason about in your head. No matrices. No Greek letters. Just three hand gestures.

You and I play RPS. I always pick Rock. What do you do? You pick Paper, obviously. I am being predictable, and you exploit that.

So I start mixing it up. Sometimes Rock, sometimes Paper, sometimes Scissors. But if I play Rock 60% of the time, you will notice and lean toward Paper. I am still exploitable.

The only strategy that cannot be exploited is playing each option exactly one-third of the time, randomly. If I play Rock, Paper, and Scissors each with probability 1/3, you cannot do better than breaking even no matter what you do. And the same is true for you.

This is a **Nash Equilibrium** — a set of strategies where no player can improve their outcome by changing their strategy alone. In RPS, the Nash Equilibrium is both players randomizing uniformly.

John Nash proved in 1950 that every finite game has at least one such equilibrium. That one-page paper eventually won him the Nobel Prize.

The beautiful thing about Nash Equilibrium is that it is self-enforcing. Once both players are at equilibrium, neither has any reason to change. It is a stable state — not because someone is forcing it, but because deviating would make you worse off. In RPS, if I am mixing uniformly and you decide to play Rock more often, you do not gain anything. My uniform mix means every choice gives you the same expected payoff. Your deviation cannot help you, and mine cannot help me. We are stuck — in a good way.

## The Prisoner's Dilemma: When Rationality Fails

Nash Equilibrium sounds comforting — rational players converge to stable outcomes. But here is the unsettling part.

Two suspects are arrested for a robbery. The police separate them into different rooms and cut off all communication. Each suspect has two choices: stay silent (cooperate with the other suspect) or confess (betray them).

If both stay silent, they each get 1 year in prison — the police do not have enough evidence for the full charge. If both confess, they each get 3 years. But if one confesses and the other stays silent, the confessor goes free while the silent one gets 5 years.

Think about what you would do. If your partner stays silent, you should confess (0 years vs. 1 year). If your partner confesses, you should *also* confess (3 years vs. 5 years). No matter what your partner does, confessing is better for you.

So both of you confess. You both get 3 years. The logic is airtight: confessing is better for you regardless of what your partner does. There is no scenario where staying silent is the smart play.

But wait — if you had both stayed silent, you would have gotten 1 year each. The rational, self-interested choice leads to an outcome that is worse for *everyone*. The Nash Equilibrium (both confess) is not the best collective outcome (both stay silent).

This is not a paradox. It is a fundamental insight: individual rationality does not guarantee collective optimality. And this tension shows up everywhere — in pricing wars, arms races, climate negotiations, and yes, in Arena experiments where multiple agents compete for engagement metrics.

The Prisoner's Dilemma is the most studied game in all of game theory, and for good reason. It captures something deeply uncomfortable about strategic interaction: knowing what is collectively best does not mean you can achieve it. Both suspects *know* that mutual silence is better. But neither can trust the other to stay silent, because the incentive to defect is too strong. Trust requires enforcement — repeated interaction, reputation, contracts — things that a one-shot game does not provide.

## Why This Matters Beyond Poker

You might be thinking: "Cool poker story, but I am not building a poker AI." Fair. But the reason Pluribus matters is not poker — it is the proof that AI can reason strategically in environments with hidden information, multiple competitors, and no clean mathematical guarantees.

Before Pluribus, the conventional wisdom was that game theory worked beautifully in two-player zero-sum games (chess, Go, heads-up poker) but broke down with more players. The minimax theorem — the bedrock of competitive AI — only applies to two-player zero-sum settings. With six players, there is no theorem that tells you what "optimal" means.

Pluribus showed that you do not need theoretical perfection to win. You need a strategy that is approximately right and robust to deviations. That insight applies to any multi-agent system, including the one you are building.

## Your Arena Agent is Playing a Game

Here is where it connects. In the TendedLoop Arena, your agent controls one variant in a multi-variant experiment. Each variant's economy configuration affects user behavior. But the variants are not isolated — they exist in the same experiment, often evaluated against each other.

Think of it this way. You have four agents, each controlling a variant:

- Agent A cranks up scan rewards (more XP per scan)
- Agent B cranks up feedback rewards (more XP per detailed review)
- Agent C focuses on streaks (retention bonuses)
- Agent D keeps everything low (testing the engagement floor)

Each agent is trying to maximize its composite engagement score. But the relative performance matters too. If Agent A discovers that high scan rewards work great, Agent B might pivot to match that strategy — and suddenly the advantage disappears because users in both variants behave similarly.

This is a *game* in the formal sense. Each agent's optimal strategy depends on what the other agents are doing. And just like in the Prisoner's Dilemma, the individually "rational" choice (copy whatever is working) might not be the collectively best outcome.

Consider a concrete scenario. Agents A and B both discover that scanXp=18 drives high scan frequency. They both deploy it. Now the experiment has two variants with identical scan rewards, and the differentiating signal comes from other parameters — feedback quality, streak bonuses — that neither agent focused on. A third agent that took a diversified approach, balancing scan and feedback and streaks, might outperform both of them. The agents that "exploited" the obvious winning move ended up in a Nash Equilibrium where neither could improve by changing strategy, but both were worse off than the diversified agent.

Sound familiar? That is the Prisoner's Dilemma, playing out in real-time across your experiment.

The difference is that Arena runs over days and weeks. Unlike the one-shot Prisoner's Dilemma, your agents interact repeatedly. And in repeated games, cooperation can emerge — but so can escalation. Understanding the game-theoretic dynamics helps you anticipate which will happen.

## What Pluribus Actually Did

To appreciate what Pluribus accomplished, consider the scale. In heads-up (two-player) no-limit Hold'em, the game tree has roughly 10^161 decision points. Adding four more players does not just make the tree bigger — it explodes combinatorially. Six-player no-limit Hold'em has approximately 10^164 possible decision points. For comparison, there are estimated to be about 10^80 atoms in the observable universe.

No computer can enumerate all those states. So Pluribus used three key ideas:

**First, it computed a "blueprint" strategy offline.** Using a technique called Counterfactual Regret Minimization (CFR), Pluribus played millions of hands against copies of itself. Over time, its strategy converged toward something close to a Nash Equilibrium — not perfectly, because six-player Nash Equilibria are intractable to compute exactly, but close enough.

**Second, it refined its strategy in real-time.** During actual play, when Pluribus reached a critical decision point, it would run a focused search from that point forward, computing a better strategy for that specific situation than the blueprint provided.

**Third — and this is the surprising part — it did not try to model its opponents individually.** Instead of building separate models for each professional's tendencies, Pluribus just assumed all opponents would play something close to the blueprint strategy. This "one-size-fits-all" opponent model turned out to be enough. Why? Because the blueprint is close to equilibrium, and near-equilibrium strategies are hard to exploit regardless of who you are playing against.

Think about how counterintuitive this is. You would expect an AI that models each opponent individually — tracking their bluffing frequency, their fold rate, their betting patterns — to crush one that treats all opponents the same. But Pluribus proved the opposite. A robust, near-equilibrium strategy beats a fragile, opponent-specific one. The professionals tried to find patterns in Pluribus's play. They could not, because there were no patterns to find. Pluribus was simply playing close to the mathematical optimum.

The lesson for your Arena agent: you do not need to model your competitors' strategies precisely. You need a strategy that is robust enough that it performs well no matter what they do.

## Minimax: Assume the Worst, Prepare for It

This brings us to a foundational idea in competitive decision-making: the **minimax principle**.

Minimax says: figure out the worst thing your opponent can do to you for each possible action, then pick the action where that worst case is least bad. Do not hope for the best. Plan for the worst.

In RPS terms: if I play Rock, the worst case is you play Paper (I lose). If I play Paper, the worst case is you play Scissors (I lose). If I play Scissors, the worst case is you play Rock (I lose). Every pure strategy has the same worst case, which is why the minimax solution is to randomize.

Von Neumann proved in 1928 that in any two-player zero-sum game, the minimax strategy is also the Nash Equilibrium strategy. The defensive choice (minimize your worst case) and the strategic choice (play your equilibrium) turn out to be the same thing. This is one of the most beautiful results in mathematics — the cautious strategy and the game-theoretically optimal strategy are identical.

For your Arena agent, minimax thinking translates to: do not build a strategy that only works if your competitors make specific mistakes. Build one that works reasonably well even if they play optimally. A strategy that exploits a weak competitor sounds appealing, but if that competitor adapts (or a stronger one joins the experiment), your exploitation strategy collapses.

This is exactly what happened to early poker AIs. They would find exploits against specific opponents and crush them. But put them against a different opponent, and they would crumble. Pluribus took the opposite approach — play near-equilibrium, be unexploitable, and let the opponents make the mistakes.

## The Connection to Bandits

Now, you might be thinking: "Game theory is about opponents. Bandits are about arms. What is the connection?"

Here it is: bandit algorithms like UCB1 and Thompson Sampling are actually *regret minimizers*. They minimize the difference between what you earned and what you could have earned. And regret minimization is one of the core building blocks of CFR — the algorithm that powers both Libratus and Pluribus.

When your Arena agent uses Thompson Sampling to pick between economy configurations, it is doing a simplified version of what Pluribus does: learning from outcomes, reducing regret over time, and converging toward a strategy that is robust across different scenarios.

The difference is scale. Your agent picks between 4-5 arms. Pluribus navigated 10^164 decision points. But the mathematical foundation is the same: observe outcomes, update beliefs, choose actions that minimize the gap between what you earned and what you could have earned. Regret minimization all the way down.

## What This Means for You

You do not need to implement CFR for your Arena agent. (You are welcome to try — it would make an incredible final project.) But understanding that your agent exists in a competitive environment changes how you think about strategy.

Here are three takeaways — and a bonus fourth one.

**1. Other agents exist.** Your composite score is not just a function of your configuration — it is relative to the experiment as a whole. A rising tide can lift all boats, or a clever competitor can make your "winning" strategy look mediocre.

**2. Robustness beats exploitation.** A strategy that is near-optimal against any opponent is better than one that is optimal against a specific opponent. This is the minimax insight. In Arena terms, pick configurations that consistently perform well, not ones that depend on lucky conditions.

**3. Randomness can be strategic.** Pluribus does not always make the same play with the same hand. Mixing strategies makes you harder to predict and exploit. Thompson Sampling naturally provides this — its stochastic arm selection means your agent does not always do the same thing, which is a feature, not a bug.

There is also a fourth takeaway, more subtle but equally important: **you do not need to solve the game completely to play it well.** Pluribus could not compute a perfect Nash Equilibrium for six-player poker — no computer can. But an approximate equilibrium, refined in real-time at decision points that actually matter, was more than enough to beat the best humans in the world. Similarly, your Arena agent does not need to be optimal. It needs to be approximately right, consistently, while adapting to new data.

## What is Next

Game theory tells you that opponents exist and that you should care about them. But it does not tell you how to efficiently learn which arm is best when rewards are noisy and you have limited pulls.

The next post introduces Thompson Sampling — an algorithm invented in 1933 that was ignored for 70 years because it was "too simple" to be good. It turns out the mathematicians were wrong. Thompson Sampling learns by guessing, and it does so with near-optimal efficiency. No confidence bounds, no complicated formulas. Just coin flips and probability distributions.

And if this post made you curious about Pluribus, the paper is freely available: Brown and Sandholm, "Superhuman AI for Multiplayer Poker," *Science*, 2019. It is one of the most readable AI papers of the last decade, and the core algorithm is surprisingly accessible once you understand the regret minimization framework that we have been building toward.

One more thing. Pluribus ran on a single machine with 128 GB of RAM. No GPU cluster. No distributed computing. The blueprint strategy was computed in about 8 days on a 64-core server costing roughly $150 of cloud compute. The lesson is not just that AI beat poker pros — it is that doing so did not require exotic hardware. The ideas matter more than the iron they run on. And those ideas — regret minimization, equilibrium approximation, robust strategy under uncertainty — are the same ones that will make your Arena agent better.
