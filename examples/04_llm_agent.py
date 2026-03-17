"""
TendedLoop Arena — LLM-Powered Agent (Claude / GPT)

Demonstrates using a large language model to reason about
engagement signals and propose economy changes. The LLM acts
as a strategy advisor that explains its reasoning.

This example uses Anthropic's Claude, but the pattern works
with any LLM that supports structured output.

Run:
    pip install "tendedloop-agent[llm] @ git+https://github.com/osheryadgar/tendedloop-arena.git"
    export STRATEGY_TOKEN=strat_your_token_here
    export ANTHROPIC_API_KEY=sk-ant-...
    python examples/04_llm_agent.py
"""

import json
import logging
import os

import anthropic

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")

# ─── LLM Setup ───

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an Arena agent optimizing a gamification economy for a facility feedback platform.

Your goal: maximize user engagement (scan frequency, retention, feedback quality) while managing XP inflation.

You control these economy parameters:
- scanXp (default 10): XP per QR code scan
- feedbackXp (default 15): XP per feedback submission
- issueReportXp (default 25): XP per issue report
- photoXp (default 10): XP per photo attachment
- firstScanOfDayXp (default 15): bonus for first daily scan
- streakBonusPerDay (default 5): XP per consecutive day
- streakBonusCap (default 50): max daily streak bonus
- scanDailyCap (default 20): max scans counted per day
- feedbackDailyCap (default 10): max feedback counted per day

CONSTRAINTS:
- Changes are clamped to ±50% of current value per update
- You can update at most once per hour
- The control variant is immutable — you're optimizing a treatment variant
- A circuit breaker will freeze all updates if user retention drops dangerously

PRINCIPLES:
- Don't change too many parameters at once — isolate variables
- Wait for statistical confidence before acting
- Prefer small, incremental changes over large swings
- If metrics are healthy, do nothing

Respond with JSON only:
{"changes": {"paramName": value, ...}, "reasoning": "explanation"}
or: {"changes": null, "reasoning": "why no change"}"""


# ─── Decision Logic ───


def format_signals(signals: Signals) -> str:
    """Format signals into a readable string for the LLM."""
    lines = [
        f"Enrolled: {signals.enrolled}",
        f"Active today: {signals.active_today}",
        f"Active (7d): {signals.active_7d}",
        f"Total scans: {signals.total_scans}",
        f"Experiment day: {signals.experiment_days}",
        "",
        "Metrics:",
    ]
    for name, m in signals.metrics.items():
        std = f" +/-{m.std_dev:.2f}" if m.std_dev else ""
        lines.append(f"  {name}: {m.value:.3f}{std} (n={m.sample_size}, confidence={m.confidence})")
    return "\n".join(lines)


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """Ask Claude to analyze signals and propose changes."""
    user_msg = f"""Current economy config: {json.dumps(current_config, indent=2)}

Live signals:
{format_signals(signals)}

Analyze the situation and decide whether to adjust the economy. Respond with JSON only."""

    print(f"\n  Asking Claude to analyze {len(signals.metrics)} metrics...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )

        # Parse LLM response
        text = response.content[0].text.strip()

        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        decision = json.loads(text)
        reasoning = decision.get("reasoning", "No reasoning provided")
        changes = decision.get("changes")

        print(f"  Claude says: {reasoning}")

        if not changes:
            return None

        return ConfigUpdate(
            economy_overrides=changes,
            reasoning=f"[LLM] {reasoning}",
        )

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"  Failed to parse LLM response: {e}")
        return None
    except anthropic.APIError as e:
        print(f"  Anthropic API error: {e}")
        return None


# ─── Main ───


def main():
    print("TendedLoop Arena — LLM Agent (Claude)")
    print("=" * 38)
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print("  Model:      claude-sonnet-4-20250514")
        print()

        # Run with longer poll interval (LLM calls are expensive)
        agent.run(decide, poll_interval=300, max_iterations=20)


if __name__ == "__main__":
    main()
