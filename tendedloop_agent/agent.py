"""TendedLoop Arena Agent — main client class."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Any

import httpx

from .types import ConfigResult, ConfigUpdate, ScoreboardEntry, Signals, VariantInfo, WebhookInfo

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
        max_retries: int = 2,
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
        self._poll_interval = heartbeat_interval  # Updated by run()
        self._max_retries = max_retries
        self._stop_event = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None
        self._info: VariantInfo | None = None

    # ─── Properties ───

    @property
    def is_running(self) -> bool:
        """Whether the agent loop is currently running."""
        return not self._stop_event.is_set()

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
        result = ConfigResult.from_dict(data)

        # Update cached config after successful act
        if result.accepted and result.applied_config and self._info:
            merged = dict(self._info.current_config or {})
            merged.update(result.applied_config)
            self._info.current_config = merged

        return result

    def heartbeat(self, metadata: dict[str, Any] | None = None) -> None:
        """Send a heartbeat signal to indicate agent liveness."""
        payload: dict[str, Any] = {}
        if metadata:
            payload["metadata"] = metadata
        payload["requestedPollInterval"] = self._poll_interval
        self._post("/api/arena/heartbeat", payload)

    def scoreboard(self) -> list[ScoreboardEntry]:
        """Get the experiment-wide variant scoreboard."""
        data = self._get("/api/arena/scoreboard")
        return [ScoreboardEntry.from_dict(v) for v in data.get("variants", [])]

    def decisions(self, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Get paginated decision audit log."""
        return self._get(f"/api/arena/decisions?page={page}&pageSize={page_size}")

    # ─── Webhook Management ───

    def register_webhook(self, url: str, events: list[str] | None = None) -> WebhookInfo:
        """
        Register a webhook to receive agent events.

        Args:
            url: The URL to receive webhook POST requests.
            events: Optional list of event types to subscribe to.
                    Defaults to all events: config_updated, heartbeat_timeout,
                    circuit_breaker_triggered, anomaly_detected.

        Returns:
            WebhookInfo with the registered webhook's ID and details.
        """
        payload: dict[str, Any] = {"url": url}
        if events:
            payload["events"] = events
        data = self._post("/api/arena/webhooks", payload)
        return WebhookInfo.from_dict(data)

    def delete_webhook(self, webhook_id: str) -> None:
        """Delete a registered webhook."""
        self._delete(f"/api/arena/webhooks/{webhook_id}")

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
        self._stop_event.clear()
        self._poll_interval = poll_interval
        self._start_heartbeat_thread()
        iteration = 0

        try:
            info = self.info()
            current_config = dict(info.current_config or {})
            logger.info(
                f"Agent started for variant '{info.variant_name}' in '{info.experiment_name}'"
            )

            while not self._stop_event.is_set():
                if max_iterations is not None and iteration >= max_iterations:
                    logger.info(f"Reached max iterations ({max_iterations}), stopping")
                    break

                try:
                    signals = self.observe()
                    update = decide_fn(signals, current_config)

                    if update:
                        result = self.act(update)
                        if result.accepted:
                            logger.info(f"Config accepted: {update.reasoning}")
                            # Update local config cache from applied result
                            if result.applied_config:
                                current_config.update(result.applied_config)
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

                self._stop_event.wait(timeout=poll_interval)

        finally:
            self._stop_event.set()
            self._stop_heartbeat_thread()
            logger.info("Agent stopped")

    def stop(self) -> None:
        """Stop the agent loop."""
        self._stop_event.set()

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self.stop()
        self._client.close()

    # ─── Heartbeat Thread ───

    def _start_heartbeat_thread(self) -> None:
        def _heartbeat_loop() -> None:
            while not self._stop_event.is_set():
                try:
                    self.heartbeat()
                except Exception as e:
                    logger.debug(f"Heartbeat failed: {e}")
                self._stop_event.wait(timeout=self._heartbeat_interval)

        self._heartbeat_thread = threading.Thread(target=_heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def _stop_heartbeat_thread(self) -> None:
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=5)
        self._heartbeat_thread = None

    # ─── HTTP Helpers ───

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make an HTTP request with retry for transient errors."""
        last_error: Exception | None = None
        for attempt in range(1 + self._max_retries):
            try:
                resp = self._client.request(method, path, **kwargs)
                resp.raise_for_status()
                if resp.status_code == 204 or not resp.content:
                    return {}
                body = resp.json()
                return body.get("data", body)
            except httpx.HTTPStatusError:
                raise  # Don't retry client errors (4xx)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout) as e:
                last_error = e
                if attempt < self._max_retries:
                    wait = 2**attempt  # Exponential backoff: 1s, 2s
                    logger.debug(f"Transient error, retrying in {wait}s: {e}")
                    time.sleep(wait)
        raise last_error  # type: ignore[misc]

    def _get(self, path: str) -> dict[str, Any]:
        return self._request("GET", path)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", path, json=payload)

    def _put(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("PUT", path, json=payload)

    def _delete(self, path: str) -> dict[str, Any]:
        return self._request("DELETE", path)

    def __enter__(self) -> Agent:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
