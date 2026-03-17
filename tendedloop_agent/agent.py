"""TendedLoop Arena Agent — main client class."""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable

import httpx

from .types import ConfigResult, ConfigUpdate, ScoreboardEntry, Signals, VariantInfo

logger = logging.getLogger("tendedloop_agent")


class Agent:
    """
    Client for the TendedLoop Arena Strategy API.

    Usage::

        agent = Agent(
            api_url="https://api.tendedloop.com",
            strategy_token="strat_...",
        )

        # Observe
        signals = agent.observe()

        # Act
        result = agent.act(ConfigUpdate(
            economy_overrides={"scanXp": 25},
            reasoning="Increase scan rewards to boost frequency",
        ))

        # Check scoreboard
        entries = agent.scoreboard()

        # Run automated loop
        agent.run(my_decide_fn, poll_interval=60)
    """

    def __init__(
        self,
        api_url: str,
        strategy_token: str,
        timeout: float = 15.0,
        heartbeat_interval: int = 30,
    ):
        self.api_url = api_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {strategy_token}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        self._heartbeat_interval = heartbeat_interval
        self._heartbeat_thread: threading.Thread | None = None
        self._running = False
        self._info: VariantInfo | None = None

    # ─── Core API Methods ───

    def info(self) -> VariantInfo:
        """Get variant info, current config, and constraints."""
        data = self._get("/api/arena/variant")
        self._info = VariantInfo.from_dict(data)
        return self._info

    def observe(self) -> Signals:
        """Get current signals (cached 5 min server-side)."""
        data = self._get("/api/arena/signals")
        return Signals.from_dict(data)

    def act(self, update: ConfigUpdate) -> ConfigResult:
        """Submit a config update. Subject to 5 guardrail checks."""
        payload: dict[str, Any] = {
            "economyOverrides": update.economy_overrides,
            "reasoning": update.reasoning,
        }
        if update.signals:
            payload["signals"] = update.signals

        data = self._put("/api/arena/variant/config", payload)
        return ConfigResult.from_dict(data)

    def heartbeat(self, metadata: dict[str, Any] | None = None) -> None:
        """Send a heartbeat signal to indicate agent liveness."""
        payload: dict[str, Any] = {}
        if metadata:
            payload["metadata"] = metadata
        payload["requestedPollInterval"] = self._heartbeat_interval
        self._post("/api/arena/heartbeat", payload)

    def scoreboard(self) -> list[ScoreboardEntry]:
        """Get the experiment-wide variant scoreboard."""
        data = self._get("/api/arena/scoreboard")
        return [ScoreboardEntry.from_dict(v) for v in data.get("variants", [])]

    def decisions(self, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Get paginated decision audit log."""
        return self._get(f"/api/arena/decisions?page={page}&pageSize={page_size}")

    # ─── Automated Loop ───

    def run(
        self,
        decide_fn: Callable[[Signals, dict[str, Any]], ConfigUpdate | None],
        poll_interval: int = 60,
        max_iterations: int | None = None,
    ) -> None:
        """
        Run the observe -> decide -> act loop.

        Args:
            decide_fn: Function that receives (signals, current_config) and returns
                       a ConfigUpdate or None to skip.
            poll_interval: Seconds between cycles.
            max_iterations: Stop after N iterations (None = run forever).
        """
        self._running = True
        self._start_heartbeat_thread()
        iteration = 0

        try:
            info = self.info()
            logger.info(f"Agent started for variant '{info.variant_name}' in '{info.experiment_name}'")

            while self._running:
                if max_iterations is not None and iteration >= max_iterations:
                    logger.info(f"Reached max iterations ({max_iterations}), stopping")
                    break

                try:
                    signals = self.observe()
                    current_config = self.info().current_config or {}

                    update = decide_fn(signals, current_config)

                    if update:
                        result = self.act(update)
                        if result.accepted:
                            logger.info(f"Config accepted: {update.reasoning}")
                        else:
                            logger.info(f"Config rejected: {result.rejection_reason}")
                    else:
                        logger.debug("No config change proposed this cycle")

                    iteration += 1

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403:
                        logger.warning("Experiment paused or ended, stopping agent")
                        break
                    logger.error(f"API error: {e}")
                except Exception as e:
                    logger.error(f"Error in agent loop: {e}")

                time.sleep(poll_interval)

        finally:
            self._running = False
            self._stop_heartbeat_thread()
            logger.info("Agent stopped")

    def stop(self) -> None:
        """Stop the agent loop."""
        self._running = False

    # ─── Heartbeat Thread ───

    def _start_heartbeat_thread(self) -> None:
        def _heartbeat_loop() -> None:
            while self._running:
                try:
                    self.heartbeat()
                except Exception as e:
                    logger.debug(f"Heartbeat failed: {e}")
                time.sleep(self._heartbeat_interval)

        self._heartbeat_thread = threading.Thread(target=_heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def _stop_heartbeat_thread(self) -> None:
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=5)
        self._heartbeat_thread = None

    # ─── HTTP Helpers ───

    def _get(self, path: str) -> dict[str, Any]:
        resp = self._client.get(path)
        resp.raise_for_status()
        body = resp.json()
        return body.get("data", body)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.post(path, json=payload)
        resp.raise_for_status()
        body = resp.json()
        return body.get("data", body)

    def _put(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.put(path, json=payload)
        resp.raise_for_status()
        body = resp.json()
        return body.get("data", body)

    def __enter__(self) -> Agent:
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop()
        self._client.close()
