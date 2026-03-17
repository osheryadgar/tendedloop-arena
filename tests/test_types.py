"""Tests for type deserialization."""

from tendedloop_agent import ConfigResult, ConfigUpdate, ScoreboardEntry, Signals, VariantInfo


class TestSignals:
    def test_from_dict_empty(self):
        signals = Signals.from_dict({})
        assert signals.enrolled == 0
        assert signals.active_today == 0
        assert signals.metrics == {}

    def test_from_dict_full(self):
        data = {
            "enrolled": 150,
            "activeToday": 42,
            "active7d": 98,
            "totalScans": 1847,
            "experimentDays": 12,
            "metrics": {
                "SCAN_FREQUENCY": {
                    "value": 3.2,
                    "stdDev": 1.4,
                    "sampleSize": 42,
                    "confidence": "high",
                },
                "RETENTION_RATE": {
                    "value": 0.72,
                    "sampleSize": 150,
                    "confidence": "high",
                },
            },
        }
        signals = Signals.from_dict(data)
        assert signals.enrolled == 150
        assert signals.active_today == 42
        assert signals.active_7d == 98
        assert signals.total_scans == 1847
        assert signals.experiment_days == 12
        assert len(signals.metrics) == 2
        assert signals.metrics["SCAN_FREQUENCY"].value == 3.2
        assert signals.metrics["SCAN_FREQUENCY"].std_dev == 1.4
        assert signals.metrics["SCAN_FREQUENCY"].sample_size == 42
        assert signals.metrics["SCAN_FREQUENCY"].confidence == "high"
        assert signals.metrics["RETENTION_RATE"].std_dev is None

    def test_from_dict_missing_metric_fields(self):
        data = {"metrics": {"XP_VELOCITY": {"value": 5.0}}}
        signals = Signals.from_dict(data)
        metric = signals.metrics["XP_VELOCITY"]
        assert metric.value == 5.0
        assert metric.std_dev is None
        assert metric.sample_size == 0
        assert metric.confidence == "low"


class TestConfigUpdate:
    def test_creation(self):
        update = ConfigUpdate(
            economy_overrides={"scanXp": 20, "feedbackXp": 18},
            reasoning="Boost engagement",
        )
        assert update.economy_overrides == {"scanXp": 20, "feedbackXp": 18}
        assert update.reasoning == "Boost engagement"
        assert update.signals is None

    def test_with_signals(self):
        update = ConfigUpdate(
            economy_overrides={"scanXp": 15},
            reasoning="test",
            signals={"scan_frequency": 2.1},
        )
        assert update.signals == {"scan_frequency": 2.1}


class TestConfigResult:
    def test_from_dict_accepted(self):
        data = {
            "accepted": True,
            "appliedConfig": {"scanXp": 15},
            "clampedDeltas": {"scanXp": {"requested": 20, "applied": 15, "clamped": True}},
            "decisionLogId": "dec_123",
            "nextAllowedUpdate": "2025-01-15T10:30:00Z",
        }
        result = ConfigResult.from_dict(data)
        assert result.accepted is True
        assert result.applied_config == {"scanXp": 15}
        assert result.clamped_deltas["scanXp"]["clamped"] is True
        assert result.decision_log_id == "dec_123"
        assert result.rejection_reason is None

    def test_from_dict_rejected(self):
        data = {
            "accepted": False,
            "rejectionReason": "RATE_LIMITED",
            "nextAllowedUpdate": "2025-01-15T11:00:00Z",
        }
        result = ConfigResult.from_dict(data)
        assert result.accepted is False
        assert result.rejection_reason == "RATE_LIMITED"
        assert result.applied_config is None


class TestVariantInfo:
    def test_from_dict(self):
        data = {
            "variantId": "v1",
            "variantName": "Treatment-A",
            "experimentId": "exp1",
            "experimentName": "XP Boost Test",
            "experimentStatus": "RUNNING",
            "mode": "AGENT",
            "isControl": False,
            "currentConfig": {"scanXp": 12},
            "updateIntervalMin": 30,
            "deltaLimitPct": 25,
        }
        info = VariantInfo.from_dict(data)
        assert info.variant_id == "v1"
        assert info.variant_name == "Treatment-A"
        assert info.experiment_status == "RUNNING"
        assert info.is_control is False
        assert info.current_config == {"scanXp": 12}
        assert info.update_interval_min == 30
        assert info.delta_limit_pct == 25

    def test_from_dict_defaults(self):
        info = VariantInfo.from_dict({})
        assert info.variant_id == ""
        assert info.update_interval_min == 60
        assert info.delta_limit_pct == 50
        assert info.is_control is False


class TestScoreboardEntry:
    def test_from_dict(self):
        data = {
            "variantId": "v1",
            "variantName": "Control",
            "isControl": True,
            "enrolledCount": 75,
            "activeCount": 30,
            "totalDecisions": 0,
        }
        entry = ScoreboardEntry.from_dict(data)
        assert entry.variant_name == "Control"
        assert entry.is_control is True
        assert entry.enrolled_count == 75
        assert entry.total_decisions == 0
