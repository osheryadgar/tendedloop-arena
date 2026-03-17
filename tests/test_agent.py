"""Tests for Agent client using httpx mock transport."""

import httpx
import pytest

from tendedloop_agent import Agent, ConfigUpdate


def mock_transport(responses: dict):
    """Create a mock transport that returns predefined responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method

        key = f"{method} {path}"
        if key in responses:
            return httpx.Response(200, json=responses[key])

        # Match partial paths (for query string endpoints)
        for route_key, response_data in responses.items():
            route_method, route_path = route_key.split(" ", 1)
            if route_method == method and path.startswith(route_path):
                return httpx.Response(200, json=response_data)

        return httpx.Response(404, json={"success": False, "error": "Not found"})

    return httpx.MockTransport(handler)


MOCK_RESPONSES = {
    "GET /api/arena/variant": {
        "success": True,
        "data": {
            "variantId": "v1",
            "variantName": "Treatment-A",
            "experimentId": "exp1",
            "experimentName": "Test Experiment",
            "experimentStatus": "RUNNING",
            "mode": "AGENT",
            "isControl": False,
            "currentConfig": {"scanXp": 10, "feedbackXp": 15},
            "updateIntervalMin": 60,
            "deltaLimitPct": 50,
        },
    },
    "GET /api/arena/signals": {
        "success": True,
        "data": {
            "enrolled": 100,
            "activeToday": 30,
            "active7d": 70,
            "totalScans": 500,
            "experimentDays": 5,
            "metrics": {
                "SCAN_FREQUENCY": {
                    "value": 2.5,
                    "stdDev": 1.1,
                    "sampleSize": 30,
                    "confidence": "high",
                },
            },
        },
    },
    "PUT /api/arena/variant/config": {
        "success": True,
        "data": {
            "accepted": True,
            "appliedConfig": {"scanXp": 12},
            "decisionLogId": "dec_001",
            "nextAllowedUpdate": "2025-01-15T11:00:00Z",
        },
    },
    "POST /api/arena/heartbeat": {"success": True, "data": {}},
    "POST /api/arena/webhooks": {
        "success": True,
        "data": {
            "webhookId": "wh_001",
            "url": "https://example.com/hook",
            "events": ["config_updated"],
        },
    },
    "DELETE /api/arena/webhooks": {"success": True, "data": {}},
    "GET /api/arena/scoreboard": {
        "success": True,
        "data": {
            "variants": [
                {
                    "variantId": "v0",
                    "variantName": "Control",
                    "isControl": True,
                    "enrolledCount": 50,
                },
                {
                    "variantId": "v1",
                    "variantName": "Treatment-A",
                    "isControl": False,
                    "enrolledCount": 50,
                },
            ],
        },
    },
    "GET /api/arena/decisions": {
        "success": True,
        "data": {"decisions": [], "total": 0, "page": 1, "pageSize": 20},
    },
}


@pytest.fixture
def agent():
    """Create an Agent with mock transport."""
    a = Agent(api_url="https://api.test.com", strategy_token="strat_test")
    a._client = httpx.Client(
        base_url="https://api.test.com",
        headers=a._client.headers,
        transport=mock_transport(MOCK_RESPONSES),
    )
    yield a
    a._client.close()


class TestAgentInfo:
    def test_info_returns_variant_info(self, agent):
        info = agent.info()
        assert info.variant_name == "Treatment-A"
        assert info.experiment_status == "RUNNING"
        assert info.current_config == {"scanXp": 10, "feedbackXp": 15}
        assert info.update_interval_min == 60

    def test_info_caches_internally(self, agent):
        info = agent.info()
        assert agent._info is not None
        assert agent._info.variant_id == info.variant_id


class TestAgentObserve:
    def test_observe_returns_signals(self, agent):
        signals = agent.observe()
        assert signals.enrolled == 100
        assert signals.active_today == 30
        assert len(signals.metrics) == 1
        assert signals.metrics["SCAN_FREQUENCY"].value == 2.5
        assert signals.metrics["SCAN_FREQUENCY"].confidence == "high"


class TestAgentAct:
    def test_act_accepted(self, agent):
        result = agent.act(
            ConfigUpdate(
                economy_overrides={"scanXp": 12},
                reasoning="Test boost",
            )
        )
        assert result.accepted is True
        assert result.applied_config == {"scanXp": 12}
        assert result.decision_log_id == "dec_001"

    def test_act_updates_cached_config(self, agent):
        agent.info()  # Populate cache
        agent.act(ConfigUpdate(economy_overrides={"scanXp": 12}, reasoning="test"))
        assert agent._info.current_config["scanXp"] == 12
        assert agent._info.current_config["feedbackXp"] == 15  # Unchanged

    def test_act_with_signals(self, agent):
        result = agent.act(
            ConfigUpdate(
                economy_overrides={"scanXp": 15},
                reasoning="Boost",
                signals={"scan_frequency": 2.5},
            )
        )
        assert result.accepted is True


class TestAgentScoreboard:
    def test_scoreboard_returns_entries(self, agent):
        entries = agent.scoreboard()
        assert len(entries) == 2
        assert entries[0].variant_name == "Control"
        assert entries[0].is_control is True
        assert entries[1].variant_name == "Treatment-A"


class TestAgentDecisions:
    def test_decisions_returns_paginated(self, agent):
        result = agent.decisions(page=1, page_size=20)
        assert result["total"] == 0
        assert result["decisions"] == []


class TestAgentWebhooks:
    def test_register_webhook(self, agent):
        webhook = agent.register_webhook("https://example.com/hook", events=["config_updated"])
        assert webhook.webhook_id == "wh_001"
        assert webhook.url == "https://example.com/hook"
        assert webhook.events == ["config_updated"]

    def test_delete_webhook(self, agent):
        agent.delete_webhook("wh_001")  # Should not raise


class TestAgentContextManager:
    def test_context_manager(self):
        with Agent(api_url="https://api.test.com", strategy_token="strat_test") as agent:
            assert not agent._stop_event.is_set()


class TestAgentRun:
    def test_run_with_max_iterations(self, agent):
        call_count = 0

        def decide(signals, config):
            nonlocal call_count
            call_count += 1
            return None  # No changes

        agent.run(decide, poll_interval=0, max_iterations=2)
        assert call_count == 2

    def test_run_with_decide_returning_update(self, agent):
        updates = []

        def decide(signals, config):
            if len(updates) == 0:
                update = ConfigUpdate(
                    economy_overrides={"scanXp": 12},
                    reasoning="First update",
                )
                updates.append(update)
                return update
            return None

        agent.run(decide, poll_interval=0, max_iterations=2)
        assert len(updates) == 1

    def test_run_updates_config_cache(self, agent):
        """Verify that run() updates local config after successful act()."""
        configs_seen = []

        def decide(signals, config):
            configs_seen.append(dict(config))
            if len(configs_seen) == 1:
                return ConfigUpdate(economy_overrides={"scanXp": 12}, reasoning="boost")
            return None

        agent.run(decide, poll_interval=0, max_iterations=2)
        # First call sees original config
        assert configs_seen[0]["scanXp"] == 10
        # Second call sees updated config (from act result)
        assert configs_seen[1]["scanXp"] == 12

    def test_stop(self, agent):
        agent.stop()
        assert agent._stop_event.is_set()

    def test_is_running_property(self, agent):
        assert agent.is_running is True  # Event not set = running
        agent.stop()
        assert agent.is_running is False
