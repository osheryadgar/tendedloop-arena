"""Tests for ArenaEnv (Gymnasium-style environment wrapper)."""

from tendedloop_agent import ArenaEnv

from .conftest import STANDARD_RESPONSES, make_env


class TestReset:
    def test_reset_returns_observation(self, env):
        obs = env.reset()
        assert obs["enrolled"] == 100
        assert obs["active_today"] == 30
        assert obs["active_7d"] == 70
        assert obs["total_scans"] == 500
        assert obs["experiment_days"] == 5
        assert obs["config"] == {"scanXp": 10, "feedbackXp": 15}

    def test_reset_includes_metric_values(self, env):
        obs = env.reset()
        assert obs["metric_scan_frequency"] == 2.5
        assert obs["metric_scan_frequency_std"] == 1.1
        assert obs["metric_scan_frequency_n"] == 30

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

    def test_step_before_reset_still_works(self):
        """Calling step() before reset() should still function (no crash)."""
        e = make_env()
        try:
            obs, reward, terminated, truncated, info = e.step({"scanXp": 12})
            assert isinstance(obs, dict)
            assert info["accepted"] is True
        finally:
            e.close()


class TestStepRejection:
    def test_step_rejected_returns_truncated(self):
        """When act() returns rejected, truncated=True."""
        rejected_responses = dict(STANDARD_RESPONSES)
        rejected_responses["PUT /api/arena/variant/config"] = {
            "success": True,
            "data": {
                "accepted": False,
                "rejectionReason": "RATE_LIMITED",
                "nextAllowedUpdate": "2025-01-15T11:00:00Z",
            },
        }

        e = make_env(rejected_responses)
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
        forbidden_responses = dict(STANDARD_RESPONSES)
        forbidden_responses["PUT /api/arena/variant/config"] = (
            403,
            {"success": False, "error": "Forbidden"},
        )

        e = make_env(forbidden_responses)
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
        assert "Enrolled: 100" in output
        assert "SCAN_FREQUENCY" in output

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
