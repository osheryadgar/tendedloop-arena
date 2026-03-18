# What Happens When You Let GPT-4 Run Your Experiment

I'd been writing agents for a few weeks at this point. Rule-based agents, PID controllers, bandits. Each one required me to think carefully about thresholds, formulas, and control theory. And each one worked, in its own narrow way.

Then I had a thought that was either brilliant or deeply irresponsible: what if I just... described what I wanted in English and let an LLM figure it out?

No formulas. No tuning. No carefully chosen constants. Just a system prompt that says "here's the game, here are the metrics, here are the knobs you can turn" and a language model that reasons about what to do next.

I gave Claude the keys to my experiment. Here's what happened.

## The LLM Agent Concept

Every agent we've built so far follows the same loop: observe signals, run some math, output a config change. An LLM agent follows the same loop, but replaces the math with reasoning.

The core idea is simple. You take the current metrics, format them into a readable prompt, send that prompt to an LLM with a system message explaining the domain, and parse the JSON response into a `ConfigUpdate`. That's it. The entire decision engine lives in a system prompt.

Here's the heart of the agent -- about 20 lines of actual logic:

```python
SYSTEM_PROMPT = """You are an Arena agent optimizing a gamification economy.
Your goal: maximize engagement while managing XP inflation.

You control these parameters:
- scanXp (default 10): XP per QR code scan
- feedbackXp (default 15): XP per feedback submission
- streakBonusPerDay (default 5): XP per consecutive day
- scanDailyCap (default 20): max scans counted per day

PRINCIPLES:
- Don't change too many parameters at once
- Wait for statistical confidence before acting
- Prefer small incremental changes

Respond with JSON only:
{"changes": {"paramName": value}, "reasoning": "explanation"}"""

def decide(signals, current_config):
    prompt = f"Config: {json.dumps(current_config)}\nMetrics:\n{format_signals(signals)}"
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    decision = json.loads(response.content[0].text)
    if decision.get("changes"):
        return ConfigUpdate(
            economy_overrides=decision["changes"],
            reasoning=f"[LLM] {decision['reasoning']}",
        )
    return None
```

That's a complete decision engine. No imports from scipy, no gradient calculations, no state machines. Just a prompt and a JSON parser.

## I Ran It. Here's What Happened.

I pointed the LLM agent at a sandbox experiment and watched the logs. Three cycles tell the story.

**Cycle 1** -- The cautious start:

```
Metrics:
  SCAN_FREQUENCY: 1.400 (n=12, confidence=low)
  RETENTION_RATE: 0.680 (n=18, confidence=medium)

Claude says: "Scan frequency is below 2.0 which suggests users aren't finding
enough incentive to scan regularly. However, confidence is LOW with only 12
samples. I'll wait for more data before making changes. The retention rate at
0.68 is acceptable but not great -- worth watching."

Decision: no changes
```

I did a double-take. A rule-based agent would have blindly boosted XP the moment it saw 1.4 scans/day. The LLM actually noticed the low confidence and decided to wait. That's the kind of judgment that takes humans 20 lines of if-statements to encode.

**Cycle 2** -- The measured intervention:

```
Metrics:
  SCAN_FREQUENCY: 1.650 (n=45, confidence=medium)
  RETENTION_RATE: 0.710 (n=42, confidence=medium)

Claude says: "With medium confidence now, scan frequency at 1.65 is still
below the healthy range of 2-4. Retention improved slightly to 0.71. I'll
make a small increase to scanXp to encourage more scanning without
disrupting the positive retention trend."

Decision: {"scanXp": 12}
```

A 20% increase. Modest, well-reasoned, and it explained why. If a stakeholder asked "why did your agent change the XP?", you could literally show them this paragraph.

**Cycle 3** -- The course correction:

```
Metrics:
  SCAN_FREQUENCY: 2.100 (n=58, confidence=medium)
  RETENTION_RATE: 0.690 (n=55, confidence=medium)

Claude says: "Scan frequency improved to 2.1, now in the healthy range.
But retention dipped slightly from 0.71 to 0.69. The scanXp increase may
be drawing low-quality scans. I'll hold scanXp steady and boost
streakBonusPerDay slightly to reward consistency over volume."

Decision: {"streakBonusPerDay": 6}
```

This blew me away. The model noticed a subtle interaction between two metrics -- scan frequency going up while retention dipped -- and inferred that the quality of scans might be dropping. No rule-based agent I've written would catch that. It would need explicit logic for "if frequency increases AND retention decreases, consider quality degradation."

## The Surprising Strengths

After running the LLM agent for about 20 cycles, three things stood out.

First, **every decision comes with an explanation**. This matters more than you think. When you're running an experiment with real users, being able to audit the reasoning behind each change is not just nice -- it's often required. The LLM writes its own audit trail.

Second, **it catches interactions between metrics that are hard to encode in rules**. The scan frequency / retention tradeoff from Cycle 3 is a perfect example. A PID controller optimizes one metric at a time. A multi-metric controller needs explicit coupling rules. The LLM just... notices.

Third, **it adapts its reasoning over time**. Not in a learning sense (it has no memory between calls unless you add one), but in the sense that it responds to the shape of the data. When metrics are stable, it recommends doing nothing. When something shifts, it reasons about why. That's remarkably human-like behavior.

## The Terrifying Weaknesses

Now for the part that kept me up at night.

**Hallucinated parameter names.** On cycle 7, Claude recommended setting `dailyLoginBonus` to 20. That parameter does not exist. If I hadn't validated the output against a whitelist, the API would have silently ignored it and my agent would have thought it made a change when it didn't. In one run, about 15% of proposed parameters were fabricated.

**Inconsistent strategy.** On cycle 11, Claude boosted `scanXp` because "frequency is too low." On cycle 12, with nearly identical metrics, it reduced `scanXp` because "we should focus on quality over quantity." Same data, opposite conclusions. LLMs are non-deterministic, and that non-determinism can look like flip-flopping to your users.

**JSON parsing failures.** Despite the system prompt saying "Respond with JSON only," about 1 in 10 responses came back wrapped in markdown code fences, or with a preamble like "Based on my analysis..." before the JSON, or occasionally as plain English with no JSON at all. You need robust parsing with fallbacks.

**Cost.** Each decision is an API call. At roughly $0.01-0.05 per call depending on the model and token count, running a decision every 5 minutes costs about $3-15 per day. That adds up over a multi-week experiment. And if you accidentally set `poll_interval=10` instead of `poll_interval=300`, you'll burn through your API budget 30 times faster than intended.

## The Hybrid That Actually Works

After a week of pure LLM experiments, I landed on a pattern that I think is the real insight here: use the LLM for reasoning but something else for execution.

The idea is straightforward. The LLM analyzes the metrics and decides on a strategy -- "focus on retention this week" or "we're in a good place, reduce rewards slightly to test price sensitivity." Then a bandit algorithm picks the specific parameter values within that strategy.

```python
# LLM picks the strategy
strategy = llm_decide(signals)  # "boost retention"

# Bandit picks the best config within that strategy
arm = ucb.select_arm(retention_arms)
```

This gets you the LLM's ability to reason about complex situations without its tendency to flip-flop on specific numbers. The bandit handles the numeric optimization with statistical rigor. The LLM handles the "what should we optimize right now?" question with contextual reasoning.

## Making It Production-Safe

If you do use an LLM agent -- hybrid or pure -- you need client-side guardrails on top of the platform's guardrails. Three lines of code save you from the most common disasters:

```python
VALID_PARAMS = {"scanXp", "feedbackXp", "streakBonusPerDay", "scanDailyCap"}

validated = {
    param: max(1, int(value))
    for param, value in changes.items()
    if param in VALID_PARAMS  # Kill hallucinated params
}
```

That whitelist filter catches hallucinated parameter names. The `max(1, ...)` prevents zero or negative values. And `int(value)` catches the occasional float that the LLM spits out. These three operations saved my agent from itself more times than I want to admit.

You should also add a fallback for when the LLM call fails entirely -- network errors, rate limits, malformed responses. My fallback is simple: return `None` (no changes this cycle) and try again next time. The experiment survives a skipped cycle. It might not survive a hallucinated config.

## The Philosophical Question

There's a deeper question lurking here that I keep coming back to. When the LLM explains its reasoning -- "retention dipped because scan quality decreased" -- is it actually reasoning? Or is it pattern-matching on training data about gamification and producing plausible-sounding explanations?

I genuinely don't know. And for the purposes of running experiments, it might not matter. The explanations are useful regardless of whether they reflect genuine understanding. They help humans audit the system, they catch issues that pure math misses, and they make the agent's behavior legible to non-technical stakeholders.

But it does matter if you're relying on those explanations to be causal. "Retention dipped because of scan quality" is a hypothesis, not a fact. The LLM doesn't have access to causal inference machinery. It's making the same kind of plausible-but-potentially-wrong inferences that humans make when they eyeball a dashboard.

Use the explanations. Read them carefully. But don't treat them as ground truth.

## Where This Leaves Us

LLM agents are powerful but fragile. They reason about complex situations better than any rule-based system. They explain themselves better than any bandit algorithm. And they break in ways that are uniquely hard to predict -- because the failure mode isn't a crash or an exception. It's a confidently wrong decision wrapped in a persuasive explanation.

The sweet spot, at least for now, is the hybrid: LLM reasoning with algorithmic execution, client-side validation, and a healthy dose of skepticism about those eloquent explanations.

But here's the thing. Whether you use an LLM agent, a bandit, or a PID controller, they all share the same failure modes in production. Your agent works perfectly in the sandbox. You deploy it. And at 3 AM, it does something catastrophic.

Next up: the five ways any agent -- LLM or not -- can break production, and how to prevent each one.

---

*This is part 7 of the [TendedLoop Arena](https://github.com/osheryadgar/tendedloop-arena) blog series. Arena is an open-source platform for multi-agent gamification research. Star the repo if this was useful.*
