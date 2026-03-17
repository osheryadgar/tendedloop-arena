"""Type definitions for TendedLoop Arena Agent SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricSignal:
    """A single metric's current value and statistical context."""

    value: float
    std_dev: float | None = None
    sample_size: int = 0
    confidence: str = "low"  # low | medium | high


@dataclass
class Signals:
    """Observation from the Arena environment."""

    enrolled: int = 0
    active_today: int = 0
    active_7d: int = 0
    total_scans: int = 0
    experiment_days: int = 0
    metrics: dict[str, MetricSignal] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Signals:
        metrics = {}
        for key, val in data.get("metrics", {}).items():
            metrics[key] = MetricSignal(
                value=val.get("value", 0),
                std_dev=val.get("stdDev"),
                sample_size=val.get("sampleSize", 0),
                confidence=val.get("confidence", "low"),
            )
        return cls(
            enrolled=data.get("enrolled", 0),
            active_today=data.get("activeToday", 0),
            active_7d=data.get("active7d", 0),
            total_scans=data.get("totalScans", 0),
            experiment_days=data.get("experimentDays", 0),
            metrics=metrics,
        )


@dataclass
class ConfigUpdate:
    """A proposed config change."""

    economy_overrides: dict[str, float]
    reasoning: str = ""
    signals: dict[str, Any] | None = None


@dataclass
class ConfigResult:
    """Result of a config update attempt."""

    accepted: bool
    applied_config: dict[str, float] | None = None
    clamped_deltas: dict[str, dict[str, Any]] | None = None
    rejection_reason: str | None = None
    next_allowed_update: str | None = None
    decision_log_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConfigResult:
        return cls(
            accepted=data.get("accepted", False),
            applied_config=data.get("appliedConfig"),
            clamped_deltas=data.get("clampedDeltas"),
            rejection_reason=data.get("rejectionReason"),
            next_allowed_update=data.get("nextAllowedUpdate"),
            decision_log_id=data.get("decisionLogId", ""),
        )


@dataclass
class VariantInfo:
    """Information about the agent's variant."""

    variant_id: str = ""
    variant_name: str = ""
    experiment_id: str = ""
    experiment_name: str = ""
    experiment_status: str = ""
    mode: str = ""
    is_control: bool = False
    current_config: dict[str, Any] | None = None
    last_config_update: str | None = None
    update_interval_min: int = 60
    delta_limit_pct: float = 50

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VariantInfo:
        return cls(
            variant_id=data.get("variantId", ""),
            variant_name=data.get("variantName", ""),
            experiment_id=data.get("experimentId", ""),
            experiment_name=data.get("experimentName", ""),
            experiment_status=data.get("experimentStatus", ""),
            mode=data.get("mode", ""),
            is_control=data.get("isControl", False),
            current_config=data.get("currentConfig"),
            last_config_update=data.get("lastConfigUpdate"),
            update_interval_min=data.get("updateIntervalMin", 60),
            delta_limit_pct=data.get("deltaLimitPct", 50),
        )


@dataclass
class ScoreboardEntry:
    """A variant's entry on the scoreboard."""

    variant_id: str = ""
    variant_name: str = ""
    is_control: bool = False
    current_config: dict[str, float] | None = None
    last_config_update: str | None = None
    last_heartbeat: str | None = None
    metrics: dict[str, Any] | None = None
    enrolled_count: int = 0
    active_count: int = 0
    total_decisions: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScoreboardEntry:
        return cls(
            variant_id=data.get("variantId", ""),
            variant_name=data.get("variantName", ""),
            is_control=data.get("isControl", False),
            current_config=data.get("currentConfig"),
            last_config_update=data.get("lastConfigUpdate"),
            last_heartbeat=data.get("lastHeartbeat"),
            metrics=data.get("metrics"),
            enrolled_count=data.get("enrolledCount", 0),
            active_count=data.get("activeCount", 0),
            total_decisions=data.get("totalDecisions", 0),
        )
