"""Tests for Agent client using httpx mock transport."""

import httpx
import pytest

from tendedloop_agent import Agent, ConfigUpdate

from .conftest import STANDARD_RESPONSES, make_agent


class TestAgentInit:
    def test_rejects_http_url(self):
        with pytest.raises(ValueError, match="Refusing to connect over plain HTTP"):
            Agent(api_url="http://api.example.com", strategy_token="strat_test")

    def test_allows_https_url(self):
        agent = Agent(api_url="https://api.example.com", strategy_token="strat_test")
        agent.close()

    def test_allows_localhost_http(self):
        agent = Agent(api_url="http://localhost:3001", strategy_token="strat_test")
        agent.close()

    def test_allows_127_0_0_1_http(self):
        agent = Agent(api_url="http://127.0.0.1:3001", strategy_token="strat_test")
        agent.close()


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

    def test_run_stops_on_403(self):
        """Run loop should stop gracefully when experiment ends (403)."""
        call_count = 0
        responses = dict(STANDARD_RESPONSES)
        responses["GET /api/arena/signals"] = (403, {"error": "Forbidden"})

        a = make_agent(responses)
        try:

            def decide(signals, config):
                nonlocal call_count
                call_count += 1
                return None

            a.run(decide, poll_interval=0, max_iterations=10)
            # Should have stopped before 10 iterations
            assert call_count == 0
        finally:
            a._client.close()

    def test_run_reraises_after_consecutive_errors(self):
        """Run loop should re-raise after too many consecutive errors."""
        a = make_agent()
        try:
            call_count = 0

            def bad_decide(signals, config):
                nonlocal call_count
                call_count += 1
                raise RuntimeError("Bug in decide function")

            with pytest.raises(RuntimeError, match="Bug in decide function"):
                a.run(bad_decide, poll_interval=0, max_iterations=100)

            assert call_count == 5  # _MAX_CONSECUTIVE_ERRORS
        finally:
            a._client.close()

    def test_run_resets_error_count_on_success(self, agent):
        """Consecutive error count should reset after a successful cycle."""
        call_count = 0
        success_count = 0

        def sometimes_fail(signals, config):
            nonlocal call_count, success_count
            call_count += 1
            # Fail on call 2-4, succeed on others
            if 2 <= call_count <= 4:
                raise RuntimeError("intermittent failure")
            success_count += 1
            return None

        # The 3 consecutive errors (calls 2-4) don't hit the threshold (5)
        # because call 1 succeeded and resets the counter.
        # Errors don't increment `iteration`, so max_iterations=5 means 5 successes.
        agent.run(sometimes_fail, poll_interval=0, max_iterations=5)
        assert success_count == 5

    def test_stop(self, agent):
        agent.stop()
        assert agent._stop_event.is_set()

    def test_is_running_property(self, agent):
        assert agent.is_running is True  # Event not set = running
        agent.stop()
        assert agent.is_running is False


class TestAgentRetry:
    def test_retries_on_connect_error(self):
        """Transient connect errors should be retried."""
        attempt_count = 0

        def flaky_handler(request):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise httpx.ConnectError("Connection refused")
            return httpx.Response(200, json={"success": True, "data": {"enrolled": 42}})

        responses = dict(STANDARD_RESPONSES)
        responses["GET /api/arena/signals"] = flaky_handler
        a = make_agent(responses)
        try:
            signals = a.observe()
            assert signals.enrolled == 42
            assert attempt_count == 3  # 2 failures + 1 success
        finally:
            a._client.close()

    def test_retries_on_500(self):
        """5xx server errors should be retried."""
        attempt_count = 0

        def flaky_handler(request):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                return httpx.Response(502, json={"error": "Bad gateway"})
            return httpx.Response(200, json={"success": True, "data": {"enrolled": 42}})

        responses = dict(STANDARD_RESPONSES)
        responses["GET /api/arena/signals"] = flaky_handler
        a = make_agent(responses)
        try:
            signals = a.observe()
            assert signals.enrolled == 42
            assert attempt_count == 3
        finally:
            a._client.close()

    def test_does_not_retry_on_400(self):
        """4xx client errors should not be retried."""
        responses = dict(STANDARD_RESPONSES)
        responses["GET /api/arena/signals"] = (400, {"error": "Bad request"})
        a = make_agent(responses)
        try:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                a.observe()
            assert exc_info.value.response.status_code == 400
        finally:
            a._client.close()


class TestAgentHeartbeat:
    def test_heartbeat_thread_starts_and_stops(self, agent):
        """Heartbeat thread should start and stop cleanly."""
        agent._start_heartbeat_thread()
        assert agent._heartbeat_thread is not None
        assert agent._heartbeat_thread.is_alive()

        agent.stop()
        agent._stop_heartbeat_thread()
        assert agent._heartbeat_thread is None
