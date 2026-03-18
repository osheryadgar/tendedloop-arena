# Week 14: Research Frontiers and Open Problems

> Behavioral AI: Computational Gamification & Engagement

## Overview

This final lecture surveys the open research frontier at the intersection of AI and gamification. We examine five active research directions: autonomous reward optimization at scale, multi-agent gamification dynamics, sim-to-real transfer, generative gamification via LLMs, and fundamental open problems (non-stationarity, fairness, long-term effects). Each direction is framed as a precisely stated research problem with known partial results and concrete open questions.

## Key Concepts

### AI-Driven Gamification at Scale

The central premise of this course is that gamification can be treated as a computational optimization problem. At scale, this means autonomous agents managing reward structures for millions of users — adjusting parameters continuously based on observed behavior. The state of the art and open problems:

**What works now.** Static A/B testing with automated analysis (Arena's current paradigm). Bayesian optimization over parameter spaces with human-specified objectives. Contextual bandits for personalization within a fixed set of configurations (Week 12). These methods assume the objective is known and the environment is stationary.

**What remains hard.**

1. **Objective specification.** The designer must specify the optimization objective — but as we saw in Week 11, the "right" objective is difficult to formalize. Engagement proxies are gameable. Wellbeing is unmeasurable at scale. Composite metrics are arbitrary in their weighting. How do we construct objectives that remain aligned under optimization pressure?

2. **Non-stationarity.** Users adapt to reward structures. A parameter configuration that optimizes engagement in week 1 may be suboptimal by week 4, because users have habituated to the reward level (hedonic adaptation) or learned to exploit the reward function (reward hacking). Formally, the engagement function $E(\boldsymbol{\theta}, t)$ depends on $t$ not just through user state evolution but through users' learned strategies $\pi_t(\boldsymbol{\theta})$:

$$E(\boldsymbol{\theta}, t) = \int U(a, \boldsymbol{\theta}) \, d\pi_t(a | \boldsymbol{\theta})$$

The distribution $\pi_t$ shifts in response to $\boldsymbol{\theta}$, creating a non-stationary optimization landscape. Standard convergence guarantees for bandits and gradient methods do not apply.

3. **Scale effects.** As the user population grows, the parameter space must accommodate more heterogeneous preferences. A single configuration that works for 100 users is unlikely to work for 100,000. The personalization dimension (Week 12) interacts with the optimization dimension — we need algorithms that scale both in population size and configuration complexity.

### Multi-Agent Gamification

When multiple agents optimize reward structures for user subpopulations that interact, the system becomes a multi-agent game.

**Formal setup.** $K$ agents, each controlling parameters $\boldsymbol{\theta}_k$ for user population $P_k$. Users in different populations interact through shared features (leaderboards, referrals, network effects). Agent $k$'s objective:

$$\max_{\boldsymbol{\theta}_k} E_k(\boldsymbol{\theta}_k, \boldsymbol{\theta}_{-k}) = \int_{P_k} U_i(\boldsymbol{\theta}_k, \boldsymbol{\theta}_{-k}) \, dP_k(i)$$

where $\boldsymbol{\theta}_{-k}$ denotes the other agents' parameters. The dependence on $\boldsymbol{\theta}_{-k}$ arises because:
- Shared leaderboards: User $i$'s rank depends on other users' performance, which is influenced by their reward structure.
- Network effects: User $i$'s engagement depends on the engagement of connected users across populations.
- Resource competition: If there is a shared budget or platform capacity, one agent's generosity constrains another's.

**Nash equilibrium.** The agents converge to $(\boldsymbol{\theta}_1^*, \ldots, \boldsymbol{\theta}_K^*)$ where no agent can unilaterally improve their objective. But the Nash equilibrium may be Pareto-suboptimal — all agents could do better if they cooperated. This is the Prisoner's Dilemma of gamification: competitive optimization harms the collective.

**Open questions:**
- Under what conditions does the multi-agent game have a unique equilibrium?
- Do iterative best-response dynamics converge, and to what?
- Can mechanism design (from Strategic AI) align agent incentives with platform-level welfare?
- What happens when agents have different optimization algorithms — does algorithm diversity stabilize or destabilize the system?

### Sim-to-Real Transfer

Training gamification agents in simulation before deploying on real users offers safety and sample efficiency. But the sim-to-real gap is substantial.

**The simulation model.** A population of simulated users with behavioral models:

$$a_{i,t} \sim \pi(a | s_{i,t}, \boldsymbol{\theta}_t)$$

where $s_{i,t}$ is the user state (XP, streak, level, type) and $\pi$ is the behavioral policy. The simulator advances user states, computes engagement metrics, and provides reward signals to the agent.

**Sources of sim-to-real gap:**

1. **Model misspecification.** The simulated user model $\pi$ does not capture the full complexity of human behavior. Users exhibit irrational behavior, social influence, emotional states, and context-dependent preferences that no tractable model fully represents.

2. **Distribution shift.** The population characteristics (type distribution, activity patterns, network structure) in simulation may not match the real deployment. A policy optimized for simulated "average users" may fail on the actual skewed distribution.

3. **Adaptive opponents.** Real users learn and adapt to the reward structure in ways the simulation may not capture. The simulation's $\pi$ is typically fixed or follows simple adaptation rules, while real users can be strategic.

**Domain randomization.** A technique from robotics: train the agent across many randomized simulation settings (varying user model parameters, population compositions, noise levels). The agent must perform well under this distribution, producing a robust policy. Formally:

$$\boldsymbol{\theta}^* = \arg\max_\theta E_{\phi \sim \Phi}[E(\boldsymbol{\theta}, \phi)]$$

where $\phi$ are the simulator parameters and $\Phi$ is the randomization distribution. If $\Phi$ is broad enough to include reality, the policy will transfer.

**Open questions:**
- How to calibrate $\Phi$ from limited real-world data?
- Can we use real-world A/B test data to fine-tune simulation-trained agents (few-shot adaptation)?
- What is the minimum real-world sample needed to close the sim-to-real gap?

### Generative Gamification: LLMs Designing Challenges

Large language models open a new frontier: dynamically generating gamification content rather than selecting from a fixed set.

**Current gamification:** missions, challenges, and badges are predefined by designers. The parameter space is the configuration of these fixed elements. An agent selects from a menu.

**Generative gamification:** an LLM creates novel challenges, narratives, and reward descriptions personalized to individual users and contexts.

**Formal framework.** Extend the bandit formulation with a generative arm:

$$a_t = \text{LLM}(\text{context}_t, \text{user}_t, \text{history}_t)$$

The action space becomes the space of natural language instructions — effectively infinite. The reward model must evaluate arbitrary generated content, requiring a learned reward predictor $\hat{r}(a)$ rather than a lookup table.

**Examples:**
- "Submit feedback about the 3rd floor restroom before noon — a maintenance check was requested yesterday." (Contextual, time-bound, narratively motivated.)
- "You've scanned 5 amenities this week but none in Building B. Explore a new building for double XP." (Behavioral, personalized, exploration-incentivizing.)
- "Team Challenge: Your floor has the most diverse feedback this month. Keep it up for a collective badge." (Social, cooperative, progress-referenced.)

**Risks:**
- Hallucinated challenges (referencing non-existent amenities).
- Manipulation through emotional language (dark pattern generation).
- Unpredictable user response to novel stimuli (invalidating historical data).
- Evaluation: how do you A/B test when every user gets a unique treatment?

**Open questions:**
- How do we evaluate generative gamification? Traditional A/B testing assumes a fixed number of treatments; generative systems have infinite treatments.
- Can RLHF (reinforcement learning from human feedback) align an LLM gamification agent with user wellbeing, not just engagement?
- What is the right level of human oversight? Fully autonomous generation vs. human-approved templates with LLM personalization?

### Fundamental Open Problems

**Non-stationarity and habituation.** Users habituate to reward levels (hedonic treadmill). A reward that excites on Day 1 becomes expected by Day 30. Formally, the user's utility function shifts:

$$U_t(r) = U_0(r - r_{\text{ref}}(t)), \quad r_{\text{ref}}(t) = \gamma \cdot r_{\text{ref}}(t-1) + (1-\gamma) \cdot r_{t-1}$$

where $r_{\text{ref}}(t)$ is the reference point, adapting to recent rewards with rate $\gamma$. This creates an arms race: to maintain the same utility, rewards must escalate. Sustainable gamification must either (a) find non-habituating reward types (intrinsic motivation, social recognition, mastery), or (b) periodically reset reference points (seasonal resets, new challenge formats).

Open question: can we characterize the class of reward functions that are habituation-resistant? Is there a formal analogue to "reward functions with bounded reference-point growth"?

**Fairness across user groups.** Gamification systems optimized for the average user may systematically disadvantage subgroups. Define group fairness:

$$|E_k(\boldsymbol{\theta}) - E_\ell(\boldsymbol{\theta})| \leq \epsilon \quad \forall k, \ell \in \text{groups}$$

where $E_k$ is the engagement of group $k$. Achieving this constraint while maximizing total engagement is a constrained optimization problem that may require group-specific adaptations (personalization, Week 12) — but group-specific treatment raises its own ethical concerns (differential treatment, stereotyping).

Open question: when groups have different psychological profiles (Hexad types, cultural norms around competition), is equal engagement the right fairness criterion? Or should we aim for equal opportunity to engage? Equal satisfaction? These map to different mathematical constraints with different feasibility properties.

**Long-term effects.** Most gamification studies measure effects over weeks or months. The long-term effects (years) are unknown:
- Does gamification create lasting behavioral change, or do behaviors revert when rewards are removed (extinction)?
- Does prolonged exposure to extrinsic rewards permanently alter intrinsic motivation (crowding-out, Week 2)?
- Do gamification-induced habits transfer to non-gamified contexts?

Formally, define the persistence function: $P(\tau) = E[Y_t | \text{treatment removed at } t - \tau]$, the expected behavior $\tau$ days after treatment removal. If $P(\tau) \to Y_0$ (pre-treatment level), the effect is transient. If $P(\tau) \to Y^* > Y_0$, the gamification created lasting change. Characterizing $P(\tau)$ requires longitudinal studies rarely conducted in practice.

## Formal Models

### Non-Stationary Bandit Regret

In a non-stationary environment with $V_T$ total variation in the reward function over $T$ rounds, the minimax regret for any algorithm is:

$$R_T^* = \Theta(V_T^{1/3} T^{2/3})$$

This is achieved by algorithms like Sliding Window UCB or Discounted UCB that forget old data. The key insight: the regret depends on the rate of change $V_T/T$. Slowly changing environments (low $V_T/T$) allow near-stationary performance. Rapidly changing environments (high $V_T/T$) make optimization fundamentally harder.

For gamification: the rate of user adaptation determines the fundamental limit on optimization performance. If users adapt quickly ($V_T \propto T$), regret grows as $T^{1/3} \cdot T^{2/3} = T$ — linear regret, meaning the agent cannot learn faster than the environment changes. Sustainable gamification requires slowing user adaptation (through novelty, variety, and intrinsic motivation) to keep $V_T$ sublinear.

### Multi-Agent Convergence Conditions

For the multi-agent gamification game to have stable dynamics, the interaction must satisfy a contraction condition. If each agent's best response $\boldsymbol{\theta}_k^*(\boldsymbol{\theta}_{-k})$ is a contraction mapping with factor $\rho < 1$:

$$\|\boldsymbol{\theta}_k^*(\boldsymbol{\theta}_{-k}) - \boldsymbol{\theta}_k^*(\boldsymbol{\theta}_{-k}')\| \leq \rho \|\boldsymbol{\theta}_{-k} - \boldsymbol{\theta}_{-k}'\|$$

then iterated best response converges to the unique Nash equilibrium at rate $O(\rho^t)$. The contraction factor $\rho$ depends on the strength of inter-agent coupling: weak interaction (users in different populations rarely interact) gives small $\rho$ and fast convergence; strong interaction (shared leaderboard, dense referral network) gives large $\rho$ and potential divergence.

## Worked Examples

### Example 1: Sim-to-Real Gap Estimation

A gamification agent is trained in simulation for 10,000 episodes. In simulation, it achieves engagement score $E_{\text{sim}} = 7.2$. Deployed on real users for 30 days, it achieves $E_{\text{real}} = 5.1$. The sim-to-real gap is $\Delta = 7.2 - 5.1 = 2.1$ (29% degradation).

Diagnosis: the simulated user model assumed $\sigma_{\text{noise}} = 0.3$ for behavioral variability, but real users exhibit $\sigma_{\text{real}} = 0.8$. With domain randomization over $\sigma \in [0.1, 1.0]$, the retrained agent achieves $E_{\text{sim,DR}} = 6.0$ in simulation (lower due to robustness) but $E_{\text{real,DR}} = 5.8$ in deployment — the gap shrinks from 29% to 3%.

### Example 2: Multi-Agent Equilibrium

Two agents optimize for populations A and B, sharing a leaderboard. Agent A increases `scanXp` to boost A's scan rate, pushing A's users up the leaderboard. This demotivates B's users (social comparison, Week 8), reducing B's retention. Agent B responds by increasing `feedbackXp`, boosting B's XP but inflating the leaderboard. The escalation continues:

| Round | Agent A scanXp | Agent B feedbackXp | A scan rate | B retention |
|-------|---------------|-------------------|-------------|-------------|
| 0 | 10 | 15 | 2.0 | 65% |
| 1 | 18 | 15 | 2.8 | 58% |
| 2 | 18 | 28 | 2.6 | 63% |
| 3 | 22 | 28 | 2.9 | 55% |
| 4 | 22 | 35 | 2.7 | 61% |

The dynamics oscillate. Without a mechanism to coordinate (or a platform constraint on total XP), the agents engage in an inflationary arms race analogous to the Prisoner's Dilemma. A platform-level cap on total XP awarded across all variants would function as a coordination mechanism.

### Example 3: LLM-Generated Challenge Evaluation

An LLM generates 5 challenges for a user with profile (Achiever=0.8, Socializer=0.2, streak=12, level=5):

1. "Reach Level 6 by Friday — you're 80 XP away!" (Achiever-targeted, progress-referenced)
2. "Scan the newly renovated kitchen on Floor 3" (Contextual, exploration)
3. "Your 12-day streak is legendary — go for 14!" (Streak-extension, mild loss framing)
4. "Team Challenge: help your building hit 50 scans today" (Social, cooperative)
5. "Submit feedback with a photo for 3x XP today" (Quality incentive, temporary boost)

Evaluation criteria: (a) Relevance to user type (1, 3, 5 score high for Achiever; 4 scores low), (b) Novelty vs. history (if user got challenge 3 yesterday, it is not novel), (c) Safety (does it exploit cognitive biases without user benefit? Challenge 3's loss framing is borderline), (d) Feasibility (challenge 2 assumes the kitchen exists and is relevant — hallucination risk).

A reward model $\hat{r}: \text{challenge} \times \text{context} \to [0, 1]$ can score generated challenges on these criteria, filtering before presentation. This is analogous to RLHF's reward model in LLM alignment.

## Arena Connection

Arena is positioned at the frontier of several research directions:

- **Multi-agent experiments.** Arena natively supports multiple agents competing on the same experiment. This is the multi-agent gamification scenario described above — student agents interact through shared user populations, creating the emergent dynamics that characterize frontier research.
- **Sim-to-real pipeline.** The Arena SDK includes a local sandbox (`python -m tendedloop_agent demo`) for simulation-based development. The gap between sandbox and live experiments is a concrete instance of sim-to-real transfer. Agents that perform well in simulation but poorly in live experiments provide natural case studies.
- **Safety as research.** Arena's guardrails (parameter bounds, delta clamping, circuit breakers) are themselves research instruments. By varying the guardrail strictness, researchers can empirically measure the "cost of safety" — the engagement gap between constrained and unconstrained optimization.
- **Longitudinal data.** As Arena accumulates experimental data over semesters and years, it will enable the long-term effect studies that are currently absent from the literature. This is a unique contribution of an academic platform.

## Discussion Questions

1. **Research proposal.** Choose one open problem from this lecture and write a 1-paragraph research proposal. State the problem precisely, identify what makes it hard, and propose a methodology (formal analysis, simulation, empirical study, or hybrid).

2. **Generative gamification governance.** If an LLM generates gamification challenges, who should review them before deployment? Design a governance framework that balances personalization benefits against manipulation risks. How does this relate to content moderation in social media?

3. **Multi-agent stability.** In Arena's multi-agent setting, what happens if one agent is much more sophisticated than the others (e.g., uses deep RL while others use simple heuristics)? Does the sophisticated agent always win? Can a "dumb" agent exploit a "smart" one? Provide a game-theoretic analysis.

4. **The end of gamification?** If AI agents can optimize engagement arbitrarily well, does gamification become indistinguishable from manipulation? Is there a principled line between "helpful engagement design" and "exploitative behavior modification"? Where does it lie, and can it be formalized?

## Further Reading

- **Perdomo, J. et al. (2020).** "Performative Prediction." *ICML.* Formalizes the problem of predictions that influence the outcome they predict — directly applicable to non-stationary gamification.
- **Bai, Y. et al. (2022).** "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback." *arXiv.* RLHF methodology applicable to aligning generative gamification with user wellbeing.
- **Lanctot, M. et al. (2017).** "A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning." *NeurIPS.* Multi-agent learning algorithms relevant to the multi-agent gamification setting.
