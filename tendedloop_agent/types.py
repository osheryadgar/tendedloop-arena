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

    def __repr__(self) -> str:
        std = f" +/-{self.std_dev:.2f}" if self.std_dev else ""
        return f"MetricSignal({self.value:.3f}{std}, n={self.sample_size}, {self.confidence})"


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

    def __repr__(self) -> str:
        metric_keys = ", ".join(self.metrics.keys()) if self.metrics else "none"
        return (
            f"Signals(enrolled={self.enrolled}, active_today={self.active_today}, "
            f"day={self.experiment_days}, metrics=[{metric_keys}])"
        )


@dataclass
class ConfigUpdate:
    """A proposed config change."""

    economy_overrides: dict[str, int | float]
    reasoning: str = ""
    signals: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.economy_overrides:
            raise ValueError("economy_overrides must not be empty")
        for key, value in self.economy_overrides.items():
            if not isinstance(value, (int, float)):
                vtype = type(value).__name__
                raise TypeError(f"economy_overrides['{key}'] must be int or float, got {vtype}")
            if value < 0:
                raise ValueError(f"economy_overrides['{key}'] must be >= 0, got {value}")

    def __repr__(self) -> str:
        overrides = ", ".join(f"{k}={v}" for k, v in self.economy_overrides.items())
        reason = f", reason='{self.reasoning[:50]}'" if self.reasoning else ""
        return f"ConfigUpdate({overrides}{reason})"


@dataclass
class ConfigResult:
    """Result of a config update attempt."""

    accepted: bool
    applied_config: dict[str, int | float] | None = None
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

    def __repr__(self) -> str:
        if self.accepted:
            return f"ConfigResult(accepted=True, log={self.decision_log_id})"
        return f"ConfigResult(rejected: {self.rejection_reason})"


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

    def __repr__(self) -> str:
        return (
            f"VariantInfo('{self.variant_name}' in '{self.experiment_name}', "
            f"status={self.experiment_status})"
        )


@dataclass
class ScoreboardEntry:
    """A variant's entry on the scoreboard."""

    variant_id: str = ""
    variant_name: str = ""
    is_control: bool = False
    current_config: dict[str, int | float] | None = None
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

    def __repr__(self) -> str:
        role = "control" if self.is_control else "treatment"
        return f"ScoreboardEntry('{self.variant_name}', {role}, enrolled={self.enrolled_count})"


@dataclass
class WebhookInfo:
    """A registered webhook."""

    webhook_id: str = ""
    url: str = ""
    events: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WebhookInfo:
        return cls(
            webhook_id=data.get("webhookId", data.get("id", "")),
            url=data.get("url", ""),
            events=data.get("events", []),
        )
