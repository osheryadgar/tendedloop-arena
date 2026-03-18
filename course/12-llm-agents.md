# Lesson 12: LLM Agents

> **Time:** ~35 minutes | **Complexity:** Advanced
>
> **Learning objectives** — by the end of this lesson you will be able to:
> 1. Compose effective system prompts that encode domain constraints for LLM-based decision-making
> 2. Integrate client-side validation and structured output parsing to make LLM agents production-safe
> 3. Adapt LLM reasoning with bandit execution in a hybrid architecture

> **Example**: [`examples/04_llm_agent.py`](../examples/04_llm_agent.py)

## A Different Paradigm

Every approach so far uses math — formulas, distributions, gradients. LLM agents use **reasoning**.

Instead of computing UCB values, the agent says: "Scan frequency is 1.8/day which is below the healthy range. Retention is 0.72 which is acceptable. I should boost scan rewards moderately without disturbing the retention pattern."

## How It Works

1. Format the current signals into a structured prompt
2. Send to Claude (or GPT) with a system prompt explaining the domain
3. Parse the JSON response into a ConfigUpdate
4. Submit to Arena

```python
SYSTEM_PROMPT = """You are an Arena agent optimizing a gamification economy.
Your goal: maximize user engagement while managing XP inflation.

You control these economy parameters:
- scanXp (default 10): XP per QR code scan
- feedbackXp (default 15): XP per feedback submission
...

PRINCIPLES:
- Don't change too many parameters at once
- Wait for statistical confidence before acting
- Prefer small, incremental changes

Respond with JSON: {"changes": {...}, "reasoning": "..."}"""
```

## Why LLMs Are Compelling

1. **Zero-shot**: Works without any training data or tuning
2. **Explainable**: The reasoning is in natural language, not opaque math
3. **Domain-aware**: Can reason about concepts like "XP inflation" that are hard to encode in a formula
4. **Flexible**: Can handle novel situations that rule-based agents can't anticipate

## Why LLMs Are Risky

1. **Non-deterministic**: Same signals → different actions each time
2. **Hallucination**: May propose parameter names that don't exist
3. **Cost**: Each decision is an API call ($0.003-0.015 per call)
4. **Latency**: 1-3 seconds per decision (not an issue for Arena's slow loop)
5. **No learning curve**: Doesn't get better over time (unless you add memory)

## Making LLM Agents Production-Ready

### Structured Output

Don't hope the LLM returns valid JSON — enforce it:

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",  # Use the latest Claude model
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": prompt}],
)
# Parse and validate
decision = json.loads(response.content[0].text)
if "changes" not in decision:
    return None  # Skip if malformed
```

### Guardrails on Top of Guardrails

The platform has 5 guardrails, but add your own:

```python
# Client-side validation before submitting
VALID_PARAMS = {"scanXp", "feedbackXp", "streakBonusPerDay", "firstScanOfDayXp", ...}

changes = decision.get("changes") or {}
validated = {
    param: max(1, int(value))  # No negative or zero XP
    for param, value in changes.items()
    if param in VALID_PARAMS
}
decision["changes"] = validated
```

### Cost Management

The LLM example uses `poll_interval=300` (5 minutes) — slower than the default 60 seconds, because each call costs money. At 5-minute intervals, that's ~288 LLM calls/day. At ~$0.01/call, that's $2.88/day. For tighter budgets, use 10-minute intervals (~$1.44/day) or skip the LLM call when metrics are stable.

## LLM + Bandit Hybrid

The most powerful pattern: use an LLM for **strategy selection** and a bandit for **execution**:

```python
# LLM chooses the strategy
strategy = llm_decide(signals)  # "Focus on retention this week"

# Bandit selects the best arm within that strategy
arm = ucb.select_arm(retention_focused_arms)
```

This combines the LLM's reasoning about what matters with the bandit's statistical rigor about what works.

## Exercises

1. **Add memory**: Pass the last 5 decisions and their outcomes to the LLM. Does it learn from its mistakes?
2. **Multi-model**: Use Claude for important decisions (confidence is low, metrics are changing) and skip the LLM when metrics are stable.
3. **LLM + PID**: Use the LLM to set the PID setpoint ("what should the target frequency be?") and PID to maintain it.

## Next

In [Lesson 13](13-ensemble-methods.md), we'll learn how to combine multiple strategies into an ensemble that adapts over time.
