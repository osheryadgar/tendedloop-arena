"""
Gymnasium-compatible environment wrapper for TendedLoop Arena.

Follows the Gymnasium API conventions (reset, step, render)
for compatibility with standard RL frameworks.
"""

from __future__ import annotations

from typing import Any

import httpx

from .agent import Agent
from .types import ConfigUpdate, Signals


class ArenaEnv:
    """
    Gymnasium-style environment for TendedLoop Arena.

    Usage::

        env = ArenaEnv(
            api_url="https://api.tendedloop.com",
            strategy_token="strat_...",
            primary_metric="SCAN_FREQUENCY",
        )

        obs = env.reset()
        for _ in range(100):
            action = {"scanXp": 25, "streakBonusXp": 15}
            obs, reward, terminated, truncated, info = env.step(action)
            if terminated:
                break
    """

    def __init__(
        self,
        api_url: str,
        strategy_token: str,
        primary_metric: str = "SCAN_FREQUENCY",
        **agent_kwargs: Any,
    ):
        self._agent = Agent(api_url=api_url, strategy_token=strategy_token, **agent_kwargs)
        self._primary_metric = primary_metric
        self._last_signals: Signals | None = None
        self._last_reward: float = 0.0
        self._step_count = 0

    def reset(self) -> dict[str, Any]:
        """Reset the environment. Returns initial observation."""
        info = self._agent.info()
        signals = self._agent.observe()
        self._last_signals = signals
        self._last_reward = 0.0
        self._step_count = 0

        return self._signals_to_obs(signals, info.current_config or {})

    def step(
        self,
        action: dict[str, float],
        reasoning: str = "",
    ) -> tuple[dict[str, Any], float, bool, bool, dict[str, Any]]:
        """
        Take an action (config update) and return (obs, reward, terminated, truncated, info).

        Args:
            action: Economy override values to set.
            reasoning: Optional reasoning string for the decision log.

        Returns:
            obs: Current observation after action.
            reward: Change in primary metric value.
            terminated: True if experiment has ended.
            truncated: True if action was rejected.
            info: Additional context (config result, decision log ID).
        """
        self._step_count += 1

        try:
            update = ConfigUpdate(
                economy_overrides=action, reasoning=reasoning or f"Step {self._step_count}"
            )
            result = self._agent.act(update)

            # Observe new state
            signals = self._agent.observe()

            # Compute reward as metric delta
            prev_value = (
                self._last_signals.metrics.get(self._primary_metric, None)
                if self._last_signals
                else None
            )
            curr_value = signals.metrics.get(self._primary_metric, None)

            prev_v = prev_value.value if prev_value else 0.0
            curr_v = curr_value.value if curr_value else 0.0
            reward = curr_v - prev_v

            self._last_signals = signals
            self._last_reward = reward

            info_dict: dict[str, Any] = {
                "accepted": result.accepted,
                "decision_log_id": result.decision_log_id,
                "clamped_deltas": result.clamped_deltas,
            }

            if not result.accepted:
                info_dict["rejection_reason"] = result.rejection_reason
                return self._signals_to_obs(signals, {}), 0.0, False, True, info_dict

            current_config = self._agent.info().current_config or {}
            return self._signals_to_obs(signals, current_config), reward, False, False, info_dict

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                obs = self._signals_to_obs(self._last_signals or Signals(), {})
                return obs, 0.0, True, False, {"error": str(e)}
            raise
        except Exception as e:
            err_msg = str(e)
            if "EXPERIMENT_PAUSED" in err_msg:
                obs = self._signals_to_obs(self._last_signals or Signals(), {})
                return obs, 0.0, True, False, {"error": err_msg}
            raise

    def render(self) -> str:
        """Return a human-readable summary of the current state."""
        if not self._last_signals:
            return "Environment not initialized. Call reset() first."

        s = self._last_signals
        lines = [
            f"Step: {self._step_count}",
            f"Enrolled: {s.enrolled}, Active today: {s.active_today}",
            f"Experiment days: {s.experiment_days}",
            f"Last reward: {self._last_reward:.4f}",
            "Metrics:",
        ]
        for key, metric in s.metrics.items():
            lines.append(
                f"  {key}: {metric.value:.4f} "
                f"(+/-{metric.std_dev or 0:.4f}, n={metric.sample_size}, conf={metric.confidence})"
            )

        return "\n".join(lines)

    def close(self) -> None:
        """Clean up resources."""
        self._agent.stop()
        self._agent._client.close()

    def _signals_to_obs(self, signals: Signals, config: dict[str, Any]) -> dict[str, Any]:
        """Convert signals to a flat observation dict."""
        obs: dict[str, Any] = {
            "enrolled": signals.enrolled,
            "active_today": signals.active_today,
            "active_7d": signals.active_7d,
            "total_scans": signals.total_scans,
            "experiment_days": signals.experiment_days,
            "config": config,
        }
        for key, metric in signals.metrics.items():
            obs[f"metric_{key.lower()}"] = metric.value
            obs[f"metric_{key.lower()}_std"] = metric.std_dev or 0
            obs[f"metric_{key.lower()}_n"] = metric.sample_size
        return obs

    def __enter__(self) -> ArenaEnv:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
