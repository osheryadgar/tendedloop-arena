"""
TendedLoop Arena — Local Mock Server.

A self-contained mock Arena API server using only Python stdlib.
Lets developers try the SDK without a TendedLoop account.

    python -m tendedloop_agent demo [port]

Then point your agent at http://localhost:7860 with token 'strat_demo_local'.
"""

from __future__ import annotations

import json
import math
import random
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

# ─── ANSI Colors ───

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"
_CYAN = "\033[36m"
_RED = "\033[31m"
_WHITE = "\033[97m"
_BG_GREEN = "\033[42m"
_BG_RED = "\033[41m"
_BG_YELLOW = "\033[43m"

# ─── Default Economy Config ───

DEFAULT_ECONOMY = {
    "scanXp": 10,
    "feedbackXp": 15,
    "issueReportXp": 25,
    "statusReportXp": 20,
    "photoXp": 10,
    "firstScanOfDayXp": 15,
    "streakBonusPerDay": 5,
    "streakBonusCap": 50,
    "scanDailyCap": 20,
    "feedbackDailyCap": 10,
}

# ─── Guardrail Constants ───

RATE_LIMIT_SECONDS = 60  # 1 minute for demo (prod is 60 min)
DELTA_LIMIT_PCT = 50
CIRCUIT_BREAKER_THRESHOLD = 3  # rejections in a row before circuit-break


class ArenaSimulation:
    """Stateful simulation of an Arena experiment."""

    def __init__(self) -> None:
        self.lock = threading.Lock()

        # Variant config
        self.economy = dict(DEFAULT_ECONOMY)
        self.baseline_economy = dict(DEFAULT_ECONOMY)

        # Experiment metadata
        self.experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
        self.experiment_name = "Demo Sandbox Experiment"
        self.variant_id = f"var_{uuid.uuid4().hex[:8]}"
        self.variant_name = "Agent-Treatment"
        self.control_variant_id = f"var_{uuid.uuid4().hex[:8]}"
        self.start_time = time.time()

        # Counters
        self.observe_count = 0
        self.decision_count = 0
        self.heartbeat_count = 0
        self.rejected_streak = 0

        # Population simulation
        self.enrolled = 80
        self.control_enrolled = 75

        # Metrics state — influenced by config
        self._scan_freq_base = 2.3
        self._retention_base = 0.68
        self._feedback_quality_base = 3.2
        self._issue_report_base = 1.1

        # Guardrails
        self.last_config_update: float | None = None
        self.circuit_breaker_open = False
        self.circuit_breaker_rejections = 0

        # Audit log
        self.decisions: list[dict[str, Any]] = []

        # Webhooks
        self.webhooks: dict[str, dict[str, Any]] = {}

        # Last heartbeat
        self.last_heartbeat: float | None = None

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def experiment_days(self) -> int:
        return max(1, int((time.time() - self.start_time) / 10) + 1)  # 10s = 1 "day" in demo

    def _metric_confidence(self) -> str:
        if self.observe_count < 3:
            return "low"
        elif self.observe_count < 8:
            return "medium"
        return "high"

    def _sample_size(self) -> int:
        base = min(self.enrolled, 30 + self.observe_count * 5)
        return base + random.randint(-3, 3)

    def _apply_config_effect(self) -> None:
        """Adjust metric baselines based on how config differs from defaults."""
        scan_ratio = self.economy["scanXp"] / max(DEFAULT_ECONOMY["scanXp"], 1)
        # Higher scanXp -> higher scan frequency (with diminishing returns)
        self._scan_freq_base = 2.3 * (0.5 + 0.5 * math.log1p(scan_ratio))

        streak_ratio = self.economy["streakBonusPerDay"] / max(
            DEFAULT_ECONOMY["streakBonusPerDay"], 1
        )
        # Higher streak bonus -> slightly better retention
        self._retention_base = min(0.85, 0.68 * (0.7 + 0.3 * math.log1p(streak_ratio)))

        feedback_ratio = self.economy["feedbackXp"] / max(DEFAULT_ECONOMY["feedbackXp"], 1)
        self._feedback_quality_base = 3.2 * (0.6 + 0.4 * math.log1p(feedback_ratio))

        issue_ratio = self.economy["issueReportXp"] / max(DEFAULT_ECONOMY["issueReportXp"], 1)
        self._issue_report_base = 1.1 * (0.5 + 0.5 * math.log1p(issue_ratio))

    def get_signals(self) -> dict[str, Any]:
        with self.lock:
            self.observe_count += 1

            # Slowly grow population
            if self.observe_count % 5 == 0:
                self.enrolled = min(500, self.enrolled + random.randint(1, 3))
                self.control_enrolled = min(500, self.control_enrolled + random.randint(0, 2))

            self._apply_config_effect()

            days = self.experiment_days()
            conf = self._metric_confidence()
            n = self._sample_size()
            noise = lambda: random.gauss(0, 0.08)  # noqa: E731

            active_today = max(5, int(self.enrolled * (0.3 + random.uniform(-0.05, 0.05))))
            active_7d = max(active_today, int(self.enrolled * (0.6 + random.uniform(-0.05, 0.05))))
            total_scans = int(self._scan_freq_base * self.enrolled * days * 0.4)

            return {
                "enrolled": self.enrolled,
                "activeToday": active_today,
                "active7d": active_7d,
                "totalScans": total_scans,
                "experimentDays": days,
                "metrics": {
                    "SCAN_FREQUENCY": {
                        "value": round(self._scan_freq_base + noise(), 3),
                        "stdDev": round(0.8 + random.uniform(0, 0.3), 3),
                        "sampleSize": n,
                        "confidence": conf,
                    },
                    "RETENTION_RATE": {
                        "value": round(self._retention_base + noise() * 0.5, 3),
                        "stdDev": round(0.12 + random.uniform(0, 0.05), 3),
                        "sampleSize": n,
                        "confidence": conf,
                    },
                    "FEEDBACK_QUALITY": {
                        "value": round(self._feedback_quality_base + noise(), 3),
                        "stdDev": round(0.5 + random.uniform(0, 0.2), 3),
                        "sampleSize": n,
                        "confidence": conf,
                    },
                    "ISSUE_REPORT_RATE": {
                        "value": round(self._issue_report_base + noise() * 0.3, 3),
                        "stdDev": round(0.3 + random.uniform(0, 0.1), 3),
                        "sampleSize": n,
                        "confidence": conf,
                    },
                },
            }

    def get_variant_info(self) -> dict[str, Any]:
        with self.lock:
            return {
                "variantId": self.variant_id,
                "variantName": self.variant_name,
                "experimentId": self.experiment_id,
                "experimentName": self.experiment_name,
                "experimentStatus": "RUNNING",
                "mode": "AGENT",
                "isControl": False,
                "currentConfig": dict(self.economy),
                "lastConfigUpdate": (
                    datetime.fromtimestamp(self.last_config_update, tz=timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                    if self.last_config_update
                    else None
                ),
                "updateIntervalMin": 1,  # 1 minute for demo
                "deltaLimitPct": DELTA_LIMIT_PCT,
            }

    def apply_config(self, economy_overrides: dict[str, Any], reasoning: str) -> dict[str, Any]:
        with self.lock:
            now = time.time()
            decision_id = f"dec_{uuid.uuid4().hex[:8]}"

            # ── Guardrail 1: Control lock (agent variant is never control) ──
            # Always passes in demo since we set isControl=False

            # ── Guardrail 2: Status gate ──
            # Experiment is always RUNNING in demo

            # ── Guardrail 3: Circuit breaker ──
            if self.circuit_breaker_open:
                self.circuit_breaker_open = False  # Reset after one rejection
                return self._reject(
                    decision_id,
                    "CIRCUIT_BREAKER_ACTIVE",
                    f"Circuit breaker tripped after {CIRCUIT_BREAKER_THRESHOLD} "
                    "consecutive rejections. Cooling off — try again.",
                    reasoning,
                    economy_overrides,
                )

            # ── Guardrail 4: Rate limiter ──
            if self.last_config_update is not None:
                elapsed = now - self.last_config_update
                if elapsed < RATE_LIMIT_SECONDS:
                    remaining = int(RATE_LIMIT_SECONDS - elapsed)
                    self.circuit_breaker_rejections += 1
                    if self.circuit_breaker_rejections >= CIRCUIT_BREAKER_THRESHOLD:
                        self.circuit_breaker_open = True
                        self.circuit_breaker_rejections = 0

                    next_allowed = datetime.fromtimestamp(
                        self.last_config_update + RATE_LIMIT_SECONDS, tz=timezone.utc
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")

                    return self._reject(
                        decision_id,
                        "RATE_LIMITED",
                        f"Rate limited. Next update allowed in {remaining}s.",
                        reasoning,
                        economy_overrides,
                        next_allowed=next_allowed,
                    )

            # ── Guardrail 5: Delta clamping ──
            applied = {}
            clamped_deltas = {}
            for key, new_val in economy_overrides.items():
                if key not in self.baseline_economy:
                    continue
                baseline = self.baseline_economy[key]
                if baseline == 0:
                    applied[key] = new_val
                    continue

                max_delta = baseline * (DELTA_LIMIT_PCT / 100.0)
                lower = max(0, baseline - max_delta)
                upper = baseline + max_delta
                clamped = max(lower, min(upper, new_val))

                if clamped != new_val:
                    clamped_deltas[key] = {
                        "requested": new_val,
                        "applied": clamped,
                        "baseline": baseline,
                        "maxDelta": max_delta,
                    }

                applied[key] = (
                    int(round(clamped)) if isinstance(baseline, int) else round(clamped, 2)
                )

            if not applied:
                self.circuit_breaker_rejections += 1
                if self.circuit_breaker_rejections >= CIRCUIT_BREAKER_THRESHOLD:
                    self.circuit_breaker_open = True
                    self.circuit_breaker_rejections = 0
                return self._reject(
                    decision_id,
                    "NO_VALID_KEYS",
                    "No valid economy keys provided.",
                    reasoning,
                    economy_overrides,
                )

            # Accept
            self.economy.update(applied)
            self.last_config_update = now
            self.decision_count += 1
            self.circuit_breaker_rejections = 0

            next_allowed = datetime.fromtimestamp(
                now + RATE_LIMIT_SECONDS, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")

            decision = {
                "id": decision_id,
                "timestamp": self.now_iso(),
                "accepted": True,
                "economyOverrides": economy_overrides,
                "appliedConfig": dict(applied),
                "clampedDeltas": clamped_deltas if clamped_deltas else None,
                "reasoning": reasoning,
            }
            self.decisions.append(decision)

            result: dict[str, Any] = {
                "accepted": True,
                "appliedConfig": applied,
                "decisionLogId": decision_id,
                "nextAllowedUpdate": next_allowed,
            }
            if clamped_deltas:
                result["clampedDeltas"] = clamped_deltas
            return result

    def _reject(
        self,
        decision_id: str,
        code: str,
        reason: str,
        reasoning: str,
        overrides: dict[str, Any],
        next_allowed: str | None = None,
    ) -> dict[str, Any]:
        decision = {
            "id": decision_id,
            "timestamp": self.now_iso(),
            "accepted": False,
            "economyOverrides": overrides,
            "rejectionReason": reason,
            "rejectionCode": code,
            "reasoning": reasoning,
        }
        self.decisions.append(decision)
        result: dict[str, Any] = {
            "accepted": False,
            "rejectionReason": code,
            "rejectionDetail": reason,
            "decisionLogId": decision_id,
        }
        if next_allowed:
            result["nextAllowedUpdate"] = next_allowed
        return result

    def get_scoreboard(self) -> dict[str, Any]:
        with self.lock:
            control_metrics = {
                "SCAN_FREQUENCY": {
                    "value": 2.3,
                    "stdDev": 0.9,
                    "sampleSize": 25,
                    "confidence": "high",
                },
                "RETENTION_RATE": {
                    "value": 0.68,
                    "stdDev": 0.14,
                    "sampleSize": 25,
                    "confidence": "high",
                },
                "FEEDBACK_QUALITY": {
                    "value": 3.2,
                    "stdDev": 0.6,
                    "sampleSize": 25,
                    "confidence": "high",
                },
                "ISSUE_REPORT_RATE": {
                    "value": 1.1,
                    "stdDev": 0.35,
                    "sampleSize": 25,
                    "confidence": "high",
                },
            }
            treatment_metrics = {}
            for key in control_metrics:
                base = getattr(self, f"_{_camel_to_snake(key)}_base", control_metrics[key]["value"])
                treatment_metrics[key] = {
                    "value": round(base + random.gauss(0, 0.05), 3),
                    "stdDev": control_metrics[key]["stdDev"],
                    "sampleSize": self._sample_size(),
                    "confidence": self._metric_confidence(),
                }

            return {
                "variants": [
                    {
                        "variantId": self.control_variant_id,
                        "variantName": "Control",
                        "isControl": True,
                        "currentConfig": dict(DEFAULT_ECONOMY),
                        "lastConfigUpdate": None,
                        "lastHeartbeat": None,
                        "metrics": control_metrics,
                        "enrolledCount": self.control_enrolled,
                        "activeCount": max(5, int(self.control_enrolled * 0.3)),
                        "totalDecisions": 0,
                    },
                    {
                        "variantId": self.variant_id,
                        "variantName": self.variant_name,
                        "isControl": False,
                        "currentConfig": dict(self.economy),
                        "lastConfigUpdate": (
                            datetime.fromtimestamp(
                                self.last_config_update, tz=timezone.utc
                            ).strftime("%Y-%m-%dT%H:%M:%SZ")
                            if self.last_config_update
                            else None
                        ),
                        "lastHeartbeat": (
                            datetime.fromtimestamp(self.last_heartbeat, tz=timezone.utc).strftime(
                                "%Y-%m-%dT%H:%M:%SZ"
                            )
                            if self.last_heartbeat
                            else None
                        ),
                        "metrics": treatment_metrics,
                        "enrolledCount": self.enrolled,
                        "activeCount": max(5, int(self.enrolled * 0.35)),
                        "totalDecisions": self.decision_count,
                    },
                ]
            }

    def get_decisions(self, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        with self.lock:
            total = len(self.decisions)
            start = (page - 1) * page_size
            end = start + page_size
            items = list(reversed(self.decisions))[start:end]
            return {
                "decisions": items,
                "total": total,
                "page": page,
                "pageSize": page_size,
            }

    def record_heartbeat(self, metadata: dict[str, Any] | None = None) -> None:
        with self.lock:
            self.heartbeat_count += 1
            self.last_heartbeat = time.time()

    def register_webhook(self, url: str, events: list[str] | None = None) -> dict[str, Any]:
        with self.lock:
            wh_id = f"wh_{uuid.uuid4().hex[:8]}"
            all_events = events or [
                "config_updated",
                "heartbeat_timeout",
                "circuit_breaker_triggered",
                "anomaly_detected",
            ]
            self.webhooks[wh_id] = {"webhookId": wh_id, "url": url, "events": all_events}
            return self.webhooks[wh_id]

    def delete_webhook(self, wh_id: str) -> bool:
        with self.lock:
            return self.webhooks.pop(wh_id, None) is not None


def _camel_to_snake(name: str) -> str:
    """Convert UPPER_SNAKE to lower_snake (for metric name -> attribute mapping)."""
    return name.lower()


# ─── HTTP Handler ───


class ArenaHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the mock Arena API."""

    sim: ArenaSimulation  # Set by the server factory

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress default logging — we do our own colorful output
        pass

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        body = json.dumps({"success": True, "data": data}).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, error: str) -> None:
        body = json.dumps({"success": False, "error": error}).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw)

    def _log(self, color: str, method: str, path: str, detail: str = "") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        detail_str = f"  {_DIM}{detail}{_RESET}" if detail else ""
        print(f"  {_DIM}{ts}{_RESET}  {color}{_BOLD}{method:6s}{_RESET} {path}{detail_str}")

    # ─── Routing ───

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        query = self.path.split("?")[1] if "?" in self.path else ""

        if path == "/api/arena/variant":
            self._log(_GREEN, "GET", path, "variant info")
            self._send_json(self.sim.get_variant_info())

        elif path == "/api/arena/signals":
            self._log(_CYAN, "GET", path, f"observe #{self.sim.observe_count + 1}")
            self._send_json(self.sim.get_signals())

        elif path == "/api/arena/scoreboard":
            self._log(_MAGENTA, "GET", path, "scoreboard")
            self._send_json(self.sim.get_scoreboard())

        elif path == "/api/arena/decisions":
            params = dict(p.split("=") for p in query.split("&") if "=" in p) if query else {}
            page = int(params.get("page", "1"))
            page_size = int(params.get("pageSize", "20"))
            self._log(_BLUE, "GET", path, f"page={page}")
            self._send_json(self.sim.get_decisions(page, page_size))

        else:
            self._log(_RED, "GET", path, "404")
            self._send_error(404, "Not found")

    def do_PUT(self) -> None:
        path = self.path.split("?")[0]

        if path == "/api/arena/variant/config":
            body = self._read_body()
            overrides = body.get("economyOverrides", {})
            reasoning = body.get("reasoning", "")
            result = self.sim.apply_config(overrides, reasoning)

            if result["accepted"]:
                clamped = result.get("clampedDeltas")
                clamp_info = f" (clamped: {list(clamped.keys())})" if clamped else ""
                self._log(
                    _GREEN,
                    "PUT",
                    path,
                    f"{_BG_GREEN}{_WHITE} ACCEPTED {_RESET} {overrides}{clamp_info}",
                )
            else:
                self._log(
                    _YELLOW,
                    "PUT",
                    path,
                    f"{_BG_RED}{_WHITE} REJECTED {_RESET} {result.get('rejectionReason', '')}",
                )

            self._send_json(result)
        else:
            self._log(_RED, "PUT", path, "404")
            self._send_error(404, "Not found")

    def do_POST(self) -> None:
        path = self.path.split("?")[0]

        if path == "/api/arena/heartbeat":
            body = self._read_body()
            self.sim.record_heartbeat(body.get("metadata"))
            self._log(_DIM, "POST", path, f"heartbeat #{self.sim.heartbeat_count}")
            self._send_json({})

        elif path == "/api/arena/webhooks":
            body = self._read_body()
            wh = self.sim.register_webhook(body.get("url", ""), body.get("events"))
            self._log(_MAGENTA, "POST", path, f"registered {wh['webhookId']}")
            self._send_json(wh)

        else:
            self._log(_RED, "POST", path, "404")
            self._send_error(404, "Not found")

    def do_DELETE(self) -> None:
        path = self.path.split("?")[0]

        if path.startswith("/api/arena/webhooks/"):
            wh_id = path.split("/")[-1]
            deleted = self.sim.delete_webhook(wh_id)
            status_msg = "deleted" if deleted else "not found"
            self._log(_YELLOW, "DELETE", path, status_msg)
            if deleted:
                self._send_json({})
            else:
                self._send_error(404, f"Webhook {wh_id} not found")
        else:
            self._log(_RED, "DELETE", path, "404")
            self._send_error(404, "Not found")


# ─── Server Entry Point ───

_BANNER = f"""
{_BOLD}{_CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║   {_WHITE}TendedLoop Arena — Local Sandbox Server{_CYAN}             ║
║                                                      ║
╚══════════════════════════════════════════════════════╝{_RESET}

  {_GREEN}Server running at:{_RESET}   http://localhost:{{port}}
  {_GREEN}Strategy token:{_RESET}      strat_demo_local
  {_GREEN}Rate limit:{_RESET}          {RATE_LIMIT_SECONDS}s (demo mode)
  {_GREEN}Delta limit:{_RESET}         {DELTA_LIMIT_PCT}%

  {_BOLD}Quick start:{_RESET}

    {_DIM}# In another terminal:{_RESET}
    ARENA_URL=http://localhost:{{port}} \\
    STRATEGY_TOKEN=strat_demo_local \\
    python examples/00_demo_sandbox.py

  {_DIM}Press Ctrl+C to stop.{_RESET}

{_DIM}{"─" * 56}{_RESET}
  {_DIM}TIME    METHOD PATH                          DETAILS{_RESET}
{_DIM}{"─" * 56}{_RESET}
"""


def run_demo_server(port: int = 7860) -> None:
    """Start the local mock Arena API server."""
    sim = ArenaSimulation()

    # Create handler class with shared simulation state
    handler_class = type("BoundHandler", (ArenaHandler,), {"sim": sim})

    server = HTTPServer(("0.0.0.0", port), handler_class)
    print(_BANNER.format(port=port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n  {_YELLOW}Server stopped.{_RESET}")
        print(
            f"  {_DIM}Session stats: {sim.observe_count} observations, "
            f"{sim.decision_count} accepted decisions, "
            f"{sim.heartbeat_count} heartbeats{_RESET}\n"
        )
    finally:
        server.server_close()


if __name__ == "__main__":
    run_demo_server()
