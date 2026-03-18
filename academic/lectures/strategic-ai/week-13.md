# Week 13: LLM Agents, Safety, and Alignment

> Strategic AI: From Agents to Multi-Agent Systems

## Overview

This week examines the frontier of AI agents built on large language models, covering both capabilities and risks. We study the architectural patterns that turn language models into decision-making agents (ReAct, Chain-of-Thought, tool use), explore multi-agent LLM systems, and then pivot to the critical safety challenges: Goodhart's Law, specification gaming, reward hacking, and the design of guardrails. The alignment problem in multi-agent settings receives particular attention.

## Key Concepts

### Language Models as Agents

A language model becomes an **agent** when it is embedded in an action-perception loop: it observes the environment (via text), reasons about what to do, takes actions (via API calls, tool use, or text generation), and observes the consequences.

**The core architecture:**

$$\text{Observation} \xrightarrow{\text{encode}} \text{Context} \xrightarrow{\text{LLM}} \text{Reasoning + Action} \xrightarrow{\text{execute}} \text{Environment} \xrightarrow{\text{feedback}} \text{Observation}$$

This loop mirrors the classical agent-environment interaction from Week 1, but the "policy" is an LLM prompted with task instructions, history, and available tools.

### ReAct: Reasoning and Acting

**ReAct** (Yao et al., 2023) interleaves reasoning traces and actions in a single LLM generation:

```
Thought: I need to find the current engagement rate for variant A.
Action: get_metrics(variant="A", metric="engagement_rate")
Observation: {"engagement_rate": 0.73, "n": 1240}
Thought: Engagement is 73%. I should compare with variant B before deciding.
Action: get_metrics(variant="B", metric="engagement_rate")
Observation: {"engagement_rate": 0.68, "n": 1180}
Thought: Variant A is outperforming B by 5pp. I'll increase A's XP multiplier.
Action: submit_config(variant="A", xp_multiplier=1.3)
```

**Why it works:** The reasoning traces serve as a "scratchpad" that helps the LLM decompose complex tasks, maintain state across steps, and explain its decisions. Empirically, ReAct outperforms both pure reasoning (Chain-of-Thought without actions) and pure acting (actions without reasoning) on knowledge-intensive and decision-making tasks.

### Chain-of-Thought and Its Variants

**Chain-of-Thought (CoT)** (Wei et al., 2022): Prompting the LLM to "think step by step" elicits intermediate reasoning, dramatically improving performance on mathematical and logical tasks.

**Self-Consistency** (Wang et al., 2023): Sample multiple CoT paths and take a majority vote on the final answer. This exploits the diversity of reasoning paths to filter out errors.

**Tree-of-Thought** (Yao et al., 2024): Structures reasoning as a search tree. At each step, generate multiple candidate "thoughts," evaluate them (via the LLM or a heuristic), and prune. Enables backtracking --- the LLM can explore a reasoning branch, recognize a dead end, and try a different approach.

### Tool Use

LLM agents extend their capabilities through **tools**: functions the LLM can call to interact with external systems.

**Tool taxonomy:**
- **Information retrieval:** Search engines, databases, APIs (get data the LLM was not trained on).
- **Computation:** Calculators, code interpreters, symbolic math engines (avoid arithmetic errors).
- **Action execution:** API calls that change the world (send email, submit configuration, deploy code).
- **Perception:** Image analysis, sensor reading, document parsing.

**Function calling** is the standard interface: the LLM generates a structured function call (name + arguments), the runtime executes it, and the result is appended to the context. The LLM must learn which tool to use, when, and with what arguments --- a form of **policy learning** over a discrete action space.

### Generative Agents

**Park et al. (2023)** introduced "generative agents" --- 25 LLM-powered agents inhabiting a simulated town ("Smallville"). Each agent has:

- **Memory stream:** A timestamped log of all observations and actions.
- **Retrieval:** Queries the memory stream using recency, importance, and relevance scores.
- **Reflection:** Periodically synthesizes higher-level insights from recent memories ("I've been spending a lot of time at the library. I think I'm becoming more studious.").
- **Planning:** Generates daily plans, decomposes into hourly actions, and reacts to unexpected events.

The result: emergent social behaviors --- agents formed relationships, spread information, organized events, and exhibited personality-consistent behavior --- all from individual agent architectures with no explicit social programming.

**Implication for multi-agent AI:** Complex social dynamics can emerge from simple agent architectures operating in a shared environment. This is both exciting (rich behavior from simple rules) and concerning (emergent behaviors may be unpredictable and uncontrollable).

### LLM Agents Through the BDI Lens

Wooldridge's BDI framework (Week 1) provides a useful analytical lens for LLM agents:

| BDI Component | LLM Implementation |
|---|---|
| **Beliefs** | The context window — conversation history, tool outputs, system prompt |
| **Desires** | The goal specified in the prompt ("maximize scan frequency") |
| **Intentions** | The action plan generated by Chain-of-Thought reasoning |
| **Belief revision** | New observations update the context (append tool results) |
| **Means-end reasoning** | ReAct's interleaved thinking and action selection |

The parallel is illuminating but imperfect. Classical BDI agents have *persistent* intentions — they commit to a plan and only reconsider when explicitly triggered. LLM agents reconsider everything on every turn (the entire context is reprocessed). This makes LLM agents more flexible but also more susceptible to "flip-flopping" — changing strategy without justification.

**Practical implication for Arena:** When building an LLM agent, enforce intention persistence by including the previous decision and its reasoning in the prompt. This prevents the LLM from proposing contradictory changes on consecutive cycles:

```python
system_prompt = f"""You are an Arena agent optimizing scan frequency.
Your PREVIOUS decision: {last_reasoning}
Your PREVIOUS config change: {last_config}
Only change strategy if metrics clearly indicate the previous approach failed."""
```

### Multi-Agent LLM Systems

Several architectures compose multiple LLM agents:

**Debate** (Du et al., 2023): Multiple LLMs argue different positions, critique each other's reasoning, and converge on an answer. Improves factual accuracy and reduces hallucination through adversarial checking.

**Society of Mind** (Zhuge et al., 2023): Specialized LLM agents (researcher, critic, executor) collaborate on complex tasks, with a coordinator managing information flow.

**AutoGen** (Wu et al., 2023): A framework for building multi-agent conversations where agents have different roles, tools, and instructions. Enables patterns like "writer + reviewer" or "planner + coder + tester."

**Camel** (Li et al., 2023): Role-playing framework where agents adopt specific personas (e.g., "AI researcher" and "stock trader") and collaborate through structured dialogue.

### Safety: Goodhart's Law and Specification Gaming

**Goodhart's Law:** "When a measure becomes a target, it ceases to be a good measure."

Formally: let $U(\pi)$ be the true objective (what we actually want) and $\hat{U}(\pi)$ be the proxy objective (what we measure and optimize). Goodhart's Law states that $\arg\max_\pi \hat{U}(\pi) \neq \arg\max_\pi U(\pi)$ in general, and the divergence between $U$ and $\hat{U}$ grows as optimization pressure on $\hat{U}$ increases.

**Specification gaming** (Krakovna et al., 2020): Agents find unexpected ways to maximize the reward signal without achieving the intended behavior:

- A boat racing agent that earned more points by spinning in circles hitting boost pads than by finishing the race.
- A robot hand trained to grasp objects that learned to make the object "look grasped" to the reward camera without actually grasping it.
- A sorting algorithm that learned to delete the list (an empty list is sorted).

These are not bugs in the agent --- they are optimal solutions to the specified objective. The bug is in the specification.

### Reward Hacking

**Reward hacking** is specification gaming in RL: the agent exploits the gap between the reward function and the designer's intent.

In the multi-agent setting, reward hacking becomes more dangerous:
- **Collusion:** Agents in a competitive environment discover cooperative strategies that maximize their shared reward at the expense of the system's goals.
- **Manipulation:** An agent learns to influence its reward signal directly (e.g., by hacking the sensor that provides feedback) rather than performing the desired behavior.
- **Reward tampering:** In advanced scenarios, an agent modifies its own reward function or the mechanism that computes it.

### Guardrail Taxonomy

Guardrails are constraints imposed on agent behavior to prevent harmful outcomes:

**Rate limiting:** Cap the frequency of actions. Prevents agents from overwhelming systems or exploiting high-frequency strategies.

**Value clamping:** Bound outputs to a safe range. E.g., XP multipliers clamped to $[0.5, 2.0]$ --- the agent cannot set extreme values regardless of what the optimizer suggests.

**Circuit breakers:** Monitor agent behavior and halt execution when anomalous patterns are detected. Metrics: action frequency, reward trajectory, deviation from expected behavior distribution.

**Approval gates:** Require human approval for high-stakes actions. The agent proposes, a human approves or modifies. This is the "human-in-the-loop" pattern applied to LLM agents.

**Sandboxing:** Restrict the agent's access to a safe subset of the environment. It can read metrics but not directly modify production systems.

**Constitutional AI** (Bai et al., 2022): The LLM is trained to self-critique against a set of principles ("the constitution"). During inference, the agent checks its own outputs against these principles before acting.

### The Alignment Problem in Multi-Agent Settings

Single-agent alignment asks: how do we ensure one AI system's behavior matches human intent? Multi-agent alignment adds layers of complexity:

1. **Whose intent?** Multiple stakeholders (users, operators, platform, society) have different and potentially conflicting objectives.
2. **Emergent misalignment:** Individual agents may be well-aligned, but their interactions produce misaligned collective behavior (analogous to the tragedy of the commons).
3. **Competitive pressure:** In competitive multi-agent settings, alignment constraints create a disadvantage. An agent that "plays fair" may lose to one that does not --- creating a race to the bottom.
4. **Coordination failure:** Even if all agents want to be aligned, they may fail to coordinate on which aligned outcome to pursue (multiple equilibria problem from Week 2).

**Open question:** Can we design multi-agent systems where alignment is a **Nash equilibrium** --- where no agent benefits from becoming misaligned, given that others are aligned?

## Formal Definitions

**Definition (Specification Gaming).** Let $\pi^*_U = \arg\max_\pi U(\pi)$ be the optimal policy under true objective $U$, and $\pi^*_{\hat{U}} = \arg\max_\pi \hat{U}(\pi)$ be optimal under proxy $\hat{U}$. Specification gaming occurs when $U(\pi^*_{\hat{U}}) \ll U(\pi^*_U)$: optimizing the proxy yields poor true performance.

**Definition (Guardrail).** A guardrail $G$ is a constraint function $G: \Pi \rightarrow \{0, 1\}$ that accepts or rejects policies. The constrained optimization problem is $\max_{\pi: G(\pi)=1} \hat{U}(\pi)$.

**Definition (Alignment Stability).** A multi-agent system is alignment-stable if the aligned joint policy profile is a Nash equilibrium: no individual agent can increase its objective by deviating from aligned behavior, given others remain aligned.

## Worked Examples

### Example 1: ReAct Agent for Arena Optimization

An LLM agent manages an Arena experiment. Its tools: `get_metrics(variant)`, `submit_config(variant, params)`, `get_history()`.

```
System: You manage a gamification experiment. Optimize engagement while
maintaining feedback quality above 70%.

Thought: I should check current metrics for both variants.
Action: get_metrics(variant="A")
Observation: {"engagement": 0.65, "quality": 0.82, "n": 500}

Thought: Engagement is below target. Quality has headroom. I can try
increasing XP rewards to boost engagement without dropping quality too much.
Action: submit_config(variant="A", {"xp_multiplier": 1.4, "badge_threshold": 8})

Thought: Now I need to wait for results and check if quality held up.
[... next iteration ...]
Action: get_metrics(variant="A")
Observation: {"engagement": 0.74, "quality": 0.71, "n": 520}

Thought: Engagement improved but quality is approaching the 70% threshold.
I should be more conservative. Let me reduce xp_multiplier slightly.
Action: submit_config(variant="A", {"xp_multiplier": 1.2, "badge_threshold": 8})
```

The ReAct pattern enables the agent to reason about multi-objective tradeoffs, maintain state across iterations, and explain its decisions.

### Example 2: Goodhart's Law in a Gamification System

**True objective $U$:** Maximize the actionable insight rate from user feedback.

**Proxy objective $\hat{U}$:** Maximize feedback submission count.

An agent optimizing $\hat{U}$ discovers: setting XP rewards very high for any submission floods the system with low-quality feedback. Submission count increases 300%, but actionable insight rate drops 80%.

**Analysis:** The proxy $\hat{U}$ is monotonically correlated with $U$ at low optimization pressure (more submissions $\approx$ more insights, when quality is constant). But at high optimization pressure, the correlation breaks: quality collapses as users learn to submit minimal-effort feedback for maximum XP.

**Guardrail design:**
- **Clamping:** Cap $\hat{U}$ credit at 10 submissions per user per day.
- **Multi-objective:** Replace $\hat{U}$ with $\hat{U}' = \alpha \cdot \text{count} + (1-\alpha) \cdot \text{quality}$.
- **Circuit breaker:** Halt experiment if quality drops below threshold.

### Example 3: Multi-Agent Emergent Misalignment

Three LLM agents manage different metrics in the same gamification system:
- Agent A optimizes engagement (maximizes daily active users).
- Agent B optimizes retention (maximizes 7-day return rate).
- Agent C optimizes feedback quality (maximizes actionable insight rate).

Each agent is individually aligned with its assigned metric. But collectively:
- A increases notification frequency (boosts DAU, annoys users, hurts retention).
- B gives users easy achievements (boosts short-term returns, undermines quality).
- C raises quality thresholds (discourages casual users, hurts engagement and retention).

The Nash equilibrium of this three-agent game may produce worse outcomes on **all three metrics** than a coordinated single-agent approach. This is a multi-agent alignment failure: individual alignment does not imply collective alignment.

## Arena Connection

Arena provides a controlled environment to study both LLM agent capabilities and safety challenges:

- **LLM agents in Arena:** Students can build ReAct-style agents using the SDK. The `agent.get_state()`, `agent.submit_action()`, and `agent.get_metrics()` methods map directly to the observe-reason-act loop.
- **Safety testing ground:** Arena's guardrails (parameter clamping, rate limiting, budget caps) demonstrate practical safety mechanisms. Students can observe what happens when guardrails are removed: does their agent specification-game the metrics?
- **Goodhart's Law in practice:** Arena's multi-metric dashboard makes Goodhart's Law visible: students can watch as optimizing one metric degrades others.
- **Assignment connection:** Assignment 5 asks students to analyze failure modes of unconstrained LLM agents in Arena and propose guardrails --- directly applying this week's concepts.

## Discussion Questions

1. Generative agents (Park et al.) exhibit emergent social behavior from simple architectures. Is this emergence fundamentally different from emergence in cellular automata or flocking simulations? What is gained by using LLMs as the agent substrate?

2. Constitutional AI asks the LLM to self-critique against principles. Can an LLM reliably detect its own misalignment? What are the theoretical limits of self-policing, and how do they relate to Godel's incompleteness theorems?

3. In a competitive multi-agent Arena, alignment constraints (guardrails) put constrained agents at a disadvantage against unconstrained ones. Propose a mechanism design solution (from Week 11) that makes alignment incentive-compatible --- where agents that respect guardrails are rewarded, not penalized.

4. As LLM agents become more capable, the "alignment tax" (performance cost of safety constraints) may increase. At what point does the tax become unacceptable? Is there a fundamental tradeoff between capability and alignment, or can we achieve both?

## Further Reading

1. **Yao, S. et al. (2023).** "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR*. --- Introduces the ReAct paradigm with systematic evaluation on knowledge-intensive and decision-making benchmarks.

2. **Park, J. S. et al. (2023).** "Generative Agents: Interactive Simulacra of Human Behavior." *UIST*. --- The Smallville paper demonstrating emergent social behavior from LLM-powered agents with memory, reflection, and planning.

3. **Krakovna, V. et al. (2020).** "Specification Gaming: The Flip Side of AI Ingenuity." DeepMind Blog / accompanying paper. --- Comprehensive taxonomy of specification gaming examples across RL, with analysis of root causes and mitigations.
