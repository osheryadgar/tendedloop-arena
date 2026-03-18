# Behavioral AI: Computational Gamification & Engagement

**Department**: Computer Science / Artificial Intelligence
**Level**: Advanced undergraduate or graduate
**Prerequisites**: Algorithms, Probability & Statistics, Python programming; [Strategic AI](strategic-ai.md) recommended but not required
**Credits**: 3

> **Note**: This course fills a gap in CS/AI curricula. Existing gamification courses (e.g., Werbach's Wharton/Coursera course, Chou's Octalysis) are design/business-oriented. No established university course treats gamification as a computational optimization problem with formal models, algorithms, and rigorous experimentation. This course is the first to do so. See [related courses](#related-courses-and-resources) at the bottom.

## Course Description

This course treats gamification as a **computational optimization problem**. Students study the behavioral science foundations (motivation theory, reward psychology, behavioral economics) but with a CS/AI lens: how do we model user engagement mathematically, optimize reward structures algorithmically, and measure outcomes with statistical rigor?

Where traditional gamification courses teach design principles, this course teaches the **engineering** of incentive systems — formalizing reward structures as parameterized functions, engagement as measurable signals, and optimization as the job of autonomous agents.

The accompanying [workshop](../workshop/README.md) lets students deploy autonomous agents that optimize these gamification systems in real-time on the TendedLoop Arena platform.

> **Tip:** Students can practice with the SDK immediately using the local sandbox: `python -m tendedloop_agent demo` — no account or experiment required.

## Learning Outcomes

By the end of this course, students will be able to:
1. Model user engagement as a computational optimization problem
2. Design reward functions grounded in behavioral science (SDT, operant conditioning, behavioral economics)
3. Formalize gamification mechanics as parameterized systems amenable to algorithmic tuning
4. Apply statistical methods (A/B testing, causal inference) to evaluate gamification interventions
5. Analyze the reward hacking and alignment problems in gamification systems
6. Design safe, ethical incentive structures with formal guardrails

## Weekly Schedule

> **Lecture notes:** Complete lecture notes for each week are available in [lectures/behavioral-ai/](lectures/behavioral-ai/).

### Module 1: Behavioral Foundations for AI (Weeks 1-4)

#### [Week 1: Gamification as an Optimization Problem](lectures/behavioral-ai/week-01.md)
- Gamification: applying game mechanics to non-game contexts
- The computational framing: users as agents in an incentive environment
- Parameterized reward systems: XP, streaks, levels, caps as tunable variables
- The optimization objective: maximize engagement subject to cost constraints
- Formal model: engagement = f(reward_params, user_state, time)

**Readings**: Deterding et al. (2011) "From Game Design Elements to Gamefulness"; Morschheuser et al. (2018)
**Workshop link**: [Session 1](../workshop/README.md) — [Lesson 1 — What is Arena](../workshop/01-what-is-arena.md), [Lesson 2 — The Environment](../workshop/02-the-arena-environment.md)

#### [Week 2: Motivation Theory for Reward Function Design](lectures/behavioral-ai/week-02.md)
- Self-Determination Theory (SDT): autonomy, competence, relatedness
- Intrinsic vs. extrinsic motivation — modeling the crowding-out effect
- Cognitive Evaluation Theory: when external rewards decrease internal drive
- Formal model: utility = w_intrinsic * U_intrinsic(task) + w_extrinsic * U_extrinsic(reward) - cost(effort)
- Implication for AI: reward functions must account for motivation dynamics, not just maximize XP output

**Readings**: Ryan & Deci (2000) "SDT and Intrinsic Motivation"; Gneezy et al. (2011) "When and Why Incentives (Don't) Work"
**Assignment 1**: Formally model the overjustification effect — at what reward level does extrinsic motivation crowd out intrinsic? Simulate with different utility functions.

#### [Week 3: Flow, Engagement, and Dynamic Difficulty](lectures/behavioral-ai/week-03.md)
- Csikszentmihalyi's Flow model as an optimization target
- The challenge-skill balance: a control systems perspective
- Modeling engagement as a function of difficulty and skill mismatch
- Dynamic Difficulty Adjustment (DDA) in games — a PID control analogy
- Engagement metrics as proxy reward signals for AI agents

**Readings**: Csikszentmihalyi (1990) *Flow*; Hunicke (2005) "The Case for Dynamic Difficulty Adjustment in Games"
**Workshop link**: [Session 3](../workshop/README.md) — [Lesson 4 — PID Control](../workshop/04-feedback-loops.md) (control theory for engagement targets)

#### [Week 4: Behavioral Economics and Computational Nudging](lectures/behavioral-ai/week-04.md)
- Prospect theory: modeling loss aversion mathematically (Kahneman-Tversky value function)
- Temporal discounting: hyperbolic vs. exponential models
- Anchoring and framing effects in reward presentation
- Computational nudge design: optimal default selection
- Connection to mechanism design (Strategic AI, Week 4)

**Readings**: Kahneman & Tversky (1979) "Prospect Theory" (required — sections 1-3). *Recommended:* Thaler & Sunstein (2008) *Nudge*, Ch. 1-3
**Assignment 2**: Implement a streak system with loss aversion — compare user retention curves for "streak freeze" (loss frame) vs. "bonus day" (gain frame) using simulation

### Module 2: Reward System Engineering (Weeks 5-8)

#### [Week 5: Parameterized Reward Systems](lectures/behavioral-ai/week-05.md)
- Points, badges, leaderboards as formal reward signals
- The PBL critique: necessary but not sufficient
- Parameterization: which variables are tunable? Which are fixed?
- State space: (scanXp, feedbackXp, streakBonus, caps, ...) = config vector
- Objective function: engagement(config, user_population, time) → R
- Constraint space: budget, fairness, inflation limits

**Readings**: Werbach & Hunter (2012) *For the Win*; Hamari (2017) "Do badges increase user activity?"
**Workshop link**: [Session 1](../workshop/README.md) — [Lesson 2 — The Arena Environment](../workshop/02-the-arena-environment.md) (the 10 tunable parameters)

#### [Week 6: Reinforcement Schedules and Reward Shaping](lectures/behavioral-ai/week-06.md)
- Operant conditioning as a formal reward model
- Fixed-ratio, variable-ratio, fixed-interval, variable-interval schedules
- Mathematical analysis: which schedule maximizes response rate? Persistence?
- Reward shaping in RL: potential-based shaping (Ng et al. 1999)
- The hook model as a Markov chain: Trigger → Action → Variable Reward → Investment
- Connection to bandit algorithms: each schedule is an "arm"

**Readings**: Skinner (1953); Ng et al. (1999) "Policy Invariance Under Reward Transformations"
**Assignment 3**: Model 4 reinforcement schedules as reward functions. Simulate a population of 100 agents. Which schedule produces highest long-term engagement? Which has highest variance?

#### [Week 7: Progression Systems and XP Economics](lectures/behavioral-ai/week-07.md)
- XP curves: linear O(n), polynomial O(n^k), exponential O(c^n)
- Level thresholds: why most games use O(n^2) or O(n^1.5)
- XP inflation: formal analysis (total XP awarded / total XP needed to level)
- Currency sinks: mechanisms to remove excess XP from the economy
- Streak mechanics formalized: P(retain | streak_day=k) as a function of streak bonus
- Diminishing returns and marginal utility

**Readings**: Schell (2019) *The Art of Game Design*; Adams (2014) *Fundamentals of Game Design*
**Workshop link**: [Session 3](../workshop/README.md) — [Lesson 5 — Multi-Objective](../workshop/05-multi-objective.md) (managing XP inflation as a constraint)

#### [Week 8: Social Dynamics and Network Effects](lectures/behavioral-ai/week-08.md)
- Social comparison: Festinger's theory formalized as utility functions
- Leaderboard design: full ranking vs. relative position vs. percentile
- Competition vs. cooperation: game-theoretic analysis (public goods game)
- Network effects in gamification: viral coefficient, referral modeling
- Agent-based simulation of social gamification dynamics

**Readings**: Festinger (1954); Morschheuser et al. (2017) "Cooperation and Competition in Gameful Design"
**Midterm exam**: Weeks 1-8

### Module 3: Measurement, Experimentation, and Safety (Weeks 9-11)

#### [Week 9: Engagement Metrics and Causal Inference](lectures/behavioral-ai/week-09.md)
- Defining engagement operationally: behavioral proxies
- Metrics as random variables: DAU/MAU ratio, retention curves, session distributions
- Cohort analysis: survival functions and hazard rates
- Causal inference: potential outcomes framework (Rubin causal model)
- Observational vs. experimental estimation of treatment effects
- The Arena's 6 metrics as measurement instruments

**Readings**: Kohavi et al. (2020) *Trustworthy Online Controlled Experiments*, Ch. 1-3; Imbens & Rubin (2015)
**Workshop link**: [Session 1](../workshop/README.md) — [Lesson 2 — Signals](../workshop/02-the-arena-environment.md) (the 6 metrics Arena measures)

#### [Week 10: A/B Testing and Statistical Methods](lectures/behavioral-ai/week-10.md)
- Experimental design: hypothesis, randomization, control
- Welch's t-test and Fisher's exact test (the Arena's statistical methods)
- Effect size: Cohen's d, odds ratio, confidence intervals
- Power analysis: sample size determination for gamification experiments
- Multiple testing: Bonferroni, FDR, and the multi-metric problem
- Sequential testing: when can you stop an experiment early?
- Common pitfalls: peeking, novelty effects, network interference

**Readings**: Kohavi et al. (2020) Ch. 4-8; Johari et al. (2017) "Peeking at A/B Tests"
**Workshop link**: [Session 3](../workshop/README.md) — [Lesson 5 — Multi-Objective](../workshop/05-multi-objective.md)
**Assignment 4**: Given a dataset of 1000 users across 3 variants, compute all statistical tests (t-test, Fisher's exact, Cohen's d, power) and determine which variant wins. Implement in Python.

#### [Week 11: Reward Hacking, Alignment, and Ethics](lectures/behavioral-ai/week-11.md)
- Reward hacking in gamification: users gaming the system (Goodhart's Law)
- Specification gaming: when the metric improves but behavior doesn't
- The alignment problem: optimizing engagement vs. optimizing wellbeing
- Formal guardrails: rate limiting, delta clamping, circuit breakers as constraints
- Dark patterns through the lens of mechanism design: misaligned incentives
- Ethical frameworks: autonomy-preserving design, informed consent, transparency
- When an AI agent optimizes engagement — who is responsible for outcomes?

**Readings**: Gray et al. (2018) "The Dark Side of UX Design"; Amodei et al. (2016) "Concrete Problems in AI Safety"
**Workshop link**: [Session 8](../workshop/README.md) — [Lesson 14 — Safety](../workshop/14-production-safety.md) (guardrails preventing harmful incentive structures)

### Module 4: Adaptive Systems and Research Frontiers (Weeks 12-14)

#### [Week 12: Personalization and Adaptive Gamification](lectures/behavioral-ai/week-12.md)
- User modeling: Bartle's taxonomy, Hexad model as feature spaces
- Collaborative filtering for reward personalization
- Contextual bandits for adaptive gamification (LinUCB with user features)
- Dynamic reward adjustment: the agent-per-user vs. agent-per-population tradeoff
- Privacy-preserving personalization: federated learning, differential privacy

**Readings**: Tondello et al. (2016) "The Gamification User Types Hexad Scale"; Li et al. (2010) "LinUCB"
**Workshop link**: [Session 5](../workshop/README.md) — [Lesson 9 — Contextual Bandits](../workshop/09-contextual-bandits.md)

#### [Week 13: Case Studies — Computational Analysis](lectures/behavioral-ai/week-13.md)
- **Duolingo**: Reverse-engineer the XP economy, model the streak mechanics, estimate the reward schedule
- **Enterprise gamification**: TendedLoop's facility feedback platform (the Arena domain)
- **Agent-optimized systems**: What happens when AI controls the reward structure?
- Computational case study methodology: data-driven analysis, not just description

**Readings**: Hamari et al. (2014) "Does Gamification Work?"; student-selected papers
**Assignment 5**: Reverse-engineer a gamification system. Extract the parameter space, model the reward function, simulate 1000 users, and identify the likely optimization objective.

#### [Week 14: Research Frontiers and Open Problems](lectures/behavioral-ai/week-14.md)
- AI-driven gamification: autonomous reward optimization at scale
- Multi-agent gamification: competing agents in shared user populations
- Sim-to-real transfer: training agents in simulation, deploying in production
- Generative gamification: LLMs designing personalized challenges
- Open problems: non-stationarity, fairness across user groups, long-term effects
- Student project presentations

**Readings**: Recent papers from CHI, CSCW, AAAI, NeurIPS (selected by instructor)

## Assessment

| Component | Weight | Description |
|-----------|--------|-------------|
| Assignments (5) | 40% | Implementation + mathematical analysis |
| Midterm exam | 20% | Weeks 1-8 (behavioral models + reward engineering) |
| Final project | 25% | Design and simulate a complete adaptive gamification system |
| Workshop participation | 15% | Arena agent performance + research writeup (if paired with workshop) |

## Required and Recommended References

### Required
1. **Kohavi, Tang, Xu** — *Trustworthy Online Controlled Experiments* (Cambridge, 2020). The definitive guide to A/B testing at scale.
2. **Werbach & Hunter** — *For the Win: The Power of Gamification* (2012). Foundational gamification framework.
3. **Kahneman** — *Thinking, Fast and Slow* (2011). Behavioral economics foundations.

### Recommended
4. **Schell** — *The Art of Game Design: A Book of Lenses* (3rd ed, 2019). Game mechanics and progression design.
5. **Sutton & Barto** — *Reinforcement Learning: An Introduction* (2nd ed, 2018). Reward shaping (Ch. 17).
6. **Chou** — *Actionable Gamification: Beyond Points, Badges, and Leaderboards* (2015). Octalysis framework (8 Core Drives).

### Key Papers
7. Ryan & Deci (2000) — "Self-Determination Theory and Intrinsic Motivation"
8. Gneezy, Meier, Rey-Biel (2011) — "When and Why Incentives (Don't) Work"
9. Ng, Harada, Russell (1999) — "Policy Invariance Under Reward Transformations"
10. Hamari, Koivisto, Sarsa (2014) — "Does Gamification Work? A Literature Review"
11. Gray et al. (2018) — "The Dark (Patterns) Side of UX Design"

## Related Courses and Resources

**No equivalent course exists** in CS/AI curricula. Existing gamification education is design-oriented:

| Course | Institution | Orientation | How This Course Differs |
|--------|-----------|------------|------------------------|
| [Gamification](https://www.coursera.org/learn/gamification) | Wharton (Coursera) | Business/Design | We formalize with algorithms and models |
| [Octalysis Framework](https://yukaichou.com/) | Yu-Kai Chou | Practitioner | We optimize computationally, not manually |
| [CS 222](https://joonspk-research.github.io/cs222-fall24/) | Stanford | Agent simulation | We focus on real-world incentive optimization |

This course fills the gap between behavioral science (which provides the domain knowledge) and multi-agent AI (which provides the optimization algorithms).

> **Note:** The courses above provide excellent foundational knowledge. Students with background in Wharton's gamification course or Chou's Octalysis framework bring valuable design intuition to this computational course.
