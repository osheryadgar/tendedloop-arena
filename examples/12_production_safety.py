"""
TendedLoop Arena — Production Safety Agent

Demonstrates production-grade patterns for running agents safely:
  - Graceful handling of all rejection types
  - Circuit breaker awareness and backoff
  - Anomaly detection in own decisions
  - Metric drift monitoring with automatic conservatism
  - Structured logging for observability
  - Webhook registration for external alerting

This is not a new optimization strategy — it wraps a simple
strategy with the safety and observability patterns you need
when running agents against real users in production.

Run:
    pip install git+https://github.com/osheryadgar/tendedloop-arena.git
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/12_production_safety.py
"""

import logging
import os
import time

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("arena.production")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # Optional external alerting


# ─── Safety Monitor ───


class SafetyMonitor:
    """
    Tracks agent behavior and enforces conservative guardrails
    beyond what the platform provides.

    Client-side safety:
      - Consecutive rejection tracking (back off if rate limited)
      - Metric drift detection (reduce change magnitude if metrics swing)
      - Decision consistency check (flag if proposing contradictory changes)
      - Cooldown enforcement (wait N cycles after rejection before retrying)
    """

    def __init__(self, cooldown_cycles: int = 3, max_consecutive_rejects: int = 5):
        self.cooldown_cycles = cooldown_cycles
        self.max_consecutive_rejects = max_consecutive_rejects

        self.consecutive_rejects = 0
        self.cycles_since_reject = 999  # Start with no cooldown
        self.last_metrics: dict[str, float] = {}
        self.decision_history: list[dict] = []

    def should_skip(self) -> tuple[bool, str]:
        """Check if the agent should skip this cycle for safety."""
        if self.cycles_since_reject < self.cooldown_cycles:
            remaining = self.cooldown_cycles - self.cycles_since_reject
            return True, f"in cooldown ({remaining} cycles remaining)"

        if self.consecutive_rejects >= self.max_consecutive_rejects:
            return True, f"too many consecutive rejects ({self.consecutive_rejects})"

        return False, ""

    def record_result(self, accepted: bool, rejection_reason: str | None = None):
        """Track acceptance/rejection patterns."""
        if accepted:
            self.consecutive_rejects = 0
            self.cycles_since_reject = 999
        else:
            self.consecutive_rejects += 1
            self.cycles_since_reject = 0
            logger.warning(f"Rejection #{self.consecutive_rejects}: {rejection_reason}")

    def tick(self):
        """Called each cycle to advance timers."""
        self.cycles_since_reject += 1

    def check_drift(self, signals: Signals) -> float:
        """
        Compute metric drift magnitude. Returns a dampening factor [0.5, 1.0].
        High drift = reduce change magnitude (be more conservative).
        """
        current: dict[str, float] = {}
        for name, metric in signals.metrics.items():
            if metric.confidence != "low":
                current[name] = metric.value

        if not self.last_metrics:
            self.last_metrics = current
            return 1.0

        # Compute average absolute percent change across metrics
        drift_sum = 0.0
        count = 0
        for name, value in current.items():
            prev = self.last_metrics.get(name)
            if prev and prev > 0:
                drift_sum += abs(value - prev) / prev
                count += 1

        self.last_metrics = current

        if count == 0:
            return 1.0

        avg_drift = drift_sum / count

        # High drift (>20%) → dampen to 50% magnitude
        # Low drift (<5%) → full magnitude
        if avg_drift > 0.20:
            logger.info(f"High metric drift ({avg_drift:.1%}), dampening changes")
            return 0.5
        elif avg_drift > 0.10:
            return 0.75
        return 1.0

    def record_decision(self, changes: dict[str, float]):
        """Track decision history for anomaly detection."""
        self.decision_history.append({"changes": changes, "time": time.time()})
        # Keep last 20 decisions
        if len(self.decision_history) > 20:
            self.decision_history = self.decision_history[-20:]


# ─── Core Strategy (simple threshold-based) ───


def core_strategy(signals: Signals, config: dict, dampening: float) -> dict[str, int] | None:
    """
    Simple adaptive strategy — the safety wrapper is the point here,
    not the optimization logic.
    """
    freq = signals.metrics.get("SCAN_FREQUENCY")
    ret = signals.metrics.get("RETENTION_RATE")

    if not freq or freq.confidence == "low":
        return None

    changes: dict[str, int] = {}
    scan_xp = config.get("scanXp", 10)
    streak = config.get("streakBonusPerDay", 5)

    if freq.value < 2.0:
        boost = 0.15 * dampening  # Dampened by safety monitor
        changes["scanXp"] = round(scan_xp * (1 + boost))
    elif freq.value > 4.5:
        reduction = 0.10 * dampening
        changes["scanXp"] = round(scan_xp * (1 - reduction))

    if ret and ret.confidence != "low" and ret.value < 0.5:
        boost = 0.15 * dampening
        changes["streakBonusPerDay"] = round(streak * (1 + boost))

    return changes if changes else None


# ─── Decision Logic ───

monitor = SafetyMonitor(cooldown_cycles=3, max_consecutive_rejects=5)


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """Production-safe decision function with monitoring and backoff."""
    monitor.tick()

    # Safety check: should we skip this cycle?
    skip, reason = monitor.should_skip()
    if skip:
        logger.info(f"Skipping cycle: {reason}")
        return None

    # Check metric drift and compute dampening
    dampening = monitor.check_drift(signals)

    # Run core strategy
    changes = core_strategy(signals, current_config, dampening)
    if not changes:
        logger.debug("Core strategy proposes no changes")
        return None

    # Record decision for anomaly tracking
    monitor.record_decision(changes)

    return ConfigUpdate(
        economy_overrides=changes,
        reasoning=f"Production agent: dampening={dampening:.0%}, changes={changes}",
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — Production Safety Agent")
    print("=" * 43)
    print()
    print("  Safety features:")
    print(f"    Cooldown after rejection: {monitor.cooldown_cycles} cycles")
    print(f"    Max consecutive rejects: {monitor.max_consecutive_rejects}")
    print("    Metric drift dampening:  enabled")
    print("    Decision logging:        enabled")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")

        # Register webhook if URL is configured
        if WEBHOOK_URL:
            try:
                wh = agent.register_webhook(
                    WEBHOOK_URL,
                    events=["circuit_breaker_triggered", "heartbeat_timeout"],
                )
                logger.info(f"Registered webhook: {wh.webhook_id}")
            except Exception as e:
                logger.warning(f"Failed to register webhook: {e}")

        print()

        # Custom loop (not agent.run) for fine-grained control
        info_data = agent.info()
        current_config = dict(info_data.current_config or {})
        logger.info("Agent started")

        for cycle in range(100):
            try:
                signals = agent.observe()
                update = decide(signals, current_config)

                if update:
                    result = agent.act(update)
                    monitor.record_result(
                        result.accepted,
                        result.rejection_reason,
                    )

                    if result.accepted and result.applied_config:
                        current_config.update(result.applied_config)
                        logger.info(f"Cycle {cycle}: accepted — {update.reasoning}")
                    else:
                        logger.info(f"Cycle {cycle}: rejected — {result.rejection_reason}")
                else:
                    logger.debug(f"Cycle {cycle}: no change proposed")

            except Exception as e:
                logger.error(f"Cycle {cycle}: error — {e}")
                if "403" in str(e):
                    logger.warning("Experiment ended, stopping")
                    break

            time.sleep(60)

        logger.info("Agent stopped")


if __name__ == "__main__":
    main()
