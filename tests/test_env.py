"""Tests for ArenaEnv (Gymnasium-style environment wrapper)."""

import httpx
import pytest

from tendedloop_agent import ArenaEnv


def mock_transport(responses: dict):
    """Create a mock transport that returns predefined responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method

        key = f"{method} {path}"
        if key in responses:
            resp_data = responses[key]
            if isinstance(resp_data, tuple):
                return httpx.Response(resp_data[0], json=resp_data[1])
            return httpx.Response(200, json=resp_data)

        for route_key, response_data in responses.items():
            route_method, route_path = route_key.split(" ", 1)
            if route_method == method and path.startswith(route_path):
                if isinstance(response_data, tuple):
                    return httpx.Response(response_data[0], json=response_data[1])
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
            "experimentName": "Test",
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
            "enrolled": 50,
            "activeToday": 20,
            "active7d": 35,
            "totalScans": 200,
            "experimentDays": 3,
            "metrics": {
                "SCAN_FREQUENCY": {
                    "value": 3.0,
                    "stdDev": 1.2,
                    "sampleSize": 20,
                    "confidence": "medium",
                },
                "RETENTION_RATE": {"value": 0.7, "sampleSize": 50, "confidence": "high"},
            },
        },
    },
    "PUT /api/arena/variant/config": {
        "success": True,
        "data": {
            "accepted": True,
            "appliedConfig": {"scanXp": 12},
            "decisionLogId": "dec_001",
        },
    },
}


@pytest.fixture
def env():
    """Create an ArenaEnv with mock transport."""
    e = ArenaEnv(
        api_url="https://api.test.com",
        strategy_token="strat_test",
        primary_metric="SCAN_FREQUENCY",
    )
    original_client = e._agent._client
    e._agent._client = httpx.Client(
        base_url="https://api.test.com",
        headers=original_client.headers,
        transport=mock_transport(MOCK_RESPONSES),
    )
    original_client.close()
    yield e
    e.close()


class TestReset:
    def test_reset_returns_observation(self, env):
        obs = env.reset()
        assert obs["enrolled"] == 50
        assert obs["active_today"] == 20
        assert obs["active_7d"] == 35
        assert obs["total_scans"] == 200
        assert obs["experiment_days"] == 3
        assert obs["config"] == {"scanXp": 10, "feedbackXp": 15}

    def test_reset_includes_metric_values(self, env):
        obs = env.reset()
        assert obs["metric_scan_frequency"] == 3.0
        assert obs["metric_scan_frequency_std"] == 1.2
        assert obs["metric_scan_frequency_n"] == 20
        assert obs["metric_retention_rate"] == 0.7

    def test_reset_resets_step_count(self, env):
        env.reset()
        assert env._step_count == 0
        assert env._last_reward == 0.0


class TestStep:
    def test_step_returns_five_tuple(self, env):
        env.reset()
        result = env.step({"scanXp": 12}, reasoning="test")
        assert len(result) == 5
        obs, reward, terminated, truncated, info = result
        assert isinstance(obs, dict)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)

    def test_step_accepted(self, env):
        env.reset()
        obs, reward, terminated, truncated, info = env.step({"scanXp": 12})
        assert info["accepted"] is True
        assert info["decision_log_id"] == "dec_001"
        assert terminated is False
        assert truncated is False

    def test_step_increments_counter(self, env):
        env.reset()
        env.step({"scanXp": 12})
        assert env._step_count == 1
        env.step({"scanXp": 14})
        assert env._step_count == 2

    def test_step_computes_reward_as_delta(self, env):
        env.reset()
        # Both observe() calls return same mock data, so delta = 0
        _, reward, _, _, _ = env.step({"scanXp": 12})
        assert reward == 0.0  # Same signals, no change


class TestStepRejection:
    def test_step_rejected_returns_truncated(self):
        """When act() returns rejected, truncated=True."""
        rejected_responses = dict(MOCK_RESPONSES)
        rejected_responses["PUT /api/arena/variant/config"] = {
            "success": True,
            "data": {
                "accepted": False,
                "rejectionReason": "RATE_LIMITED",
                "nextAllowedUpdate": "2025-01-15T11:00:00Z",
            },
        }

        e = ArenaEnv(api_url="https://api.test.com", strategy_token="strat_test")
        e._agent._client = httpx.Client(
            base_url="https://api.test.com",
            headers=e._agent._client.headers,
            transport=mock_transport(rejected_responses),
        )
        try:
            e.reset()
            _, _, terminated, truncated, info = e.step({"scanXp": 100})
            assert truncated is True
            assert terminated is False
            assert info["rejection_reason"] == "RATE_LIMITED"
        finally:
            e.close()


class TestStepTermination:
    def test_403_terminates(self):
        """When the API returns 403, terminated=True."""
        forbidden_responses = dict(MOCK_RESPONSES)
        forbidden_responses["PUT /api/arena/variant/config"] = (
            403,
            {"success": False, "error": "Forbidden"},
        )

        e = ArenaEnv(api_url="https://api.test.com", strategy_token="strat_test")
        e._agent._client = httpx.Client(
            base_url="https://api.test.com",
            headers=e._agent._client.headers,
            transport=mock_transport(forbidden_responses),
        )
        try:
            e.reset()
            _, _, terminated, truncated, info = e.step({"scanXp": 20})
            assert terminated is True
            assert truncated is False
            assert "error" in info
        finally:
            e.close()


class TestRender:
    def test_render_before_reset(self, env):
        assert "not initialized" in env.render()

    def test_render_after_reset(self, env):
        env.reset()
        output = env.render()
        assert "Step: 0" in output
        assert "Enrolled: 50" in output
        assert "SCAN_FREQUENCY" in output
        assert "RETENTION_RATE" in output

    def test_render_after_step(self, env):
        env.reset()
        env.step({"scanXp": 12})
        output = env.render()
        assert "Step: 1" in output


class TestContextManager:
    def test_context_manager(self):
        with ArenaEnv(api_url="https://api.test.com", strategy_token="strat_test") as env:
            assert env._agent is not None
        # After exit, agent should be stopped
