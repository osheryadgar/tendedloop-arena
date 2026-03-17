"""Shared test fixtures and mock transport for Arena SDK tests."""

import httpx
import pytest

from tendedloop_agent import Agent, ArenaEnv


def mock_transport(responses: dict):
    """Create a mock transport that returns predefined responses.

    Responses can be:
      - dict: returned as 200 JSON
      - tuple(int, dict): returned with custom status code
      - callable(request) -> httpx.Response: custom handler
    """

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method

        key = f"{method} {path}"
        if key in responses:
            resp_data = responses[key]
            if callable(resp_data):
                return resp_data(request)
            if isinstance(resp_data, tuple):
                return httpx.Response(resp_data[0], json=resp_data[1])
            return httpx.Response(200, json=resp_data)

        # Match partial paths (for query string endpoints)
        for route_key, response_data in responses.items():
            route_method, route_path = route_key.split(" ", 1)
            if route_method == method and path.startswith(route_path):
                if callable(response_data):
                    return response_data(request)
                if isinstance(response_data, tuple):
                    return httpx.Response(response_data[0], json=response_data[1])
                return httpx.Response(200, json=response_data)

        return httpx.Response(404, json={"success": False, "error": "Not found"})

    return httpx.MockTransport(handler)


MOCK_VARIANT = {
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
}

MOCK_SIGNALS = {
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
}

MOCK_ACT_ACCEPTED = {
    "success": True,
    "data": {
        "accepted": True,
        "appliedConfig": {"scanXp": 12},
        "decisionLogId": "dec_001",
        "nextAllowedUpdate": "2025-01-15T11:00:00Z",
    },
}

STANDARD_RESPONSES = {
    "GET /api/arena/variant": MOCK_VARIANT,
    "GET /api/arena/signals": MOCK_SIGNALS,
    "PUT /api/arena/variant/config": MOCK_ACT_ACCEPTED,
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


def make_agent(responses: dict | None = None) -> Agent:
    """Create an Agent with mock transport."""
    a = Agent(api_url="https://api.test.com", strategy_token="strat_test")
    original_client = a._client
    a._client = httpx.Client(
        base_url="https://api.test.com",
        headers=original_client.headers,
        transport=mock_transport(responses or STANDARD_RESPONSES),
    )
    original_client.close()
    return a


def make_env(responses: dict | None = None, **kwargs) -> ArenaEnv:
    """Create an ArenaEnv with mock transport."""
    e = ArenaEnv(api_url="https://api.test.com", strategy_token="strat_test", **kwargs)
    original_client = e._agent._client
    e._agent._client = httpx.Client(
        base_url="https://api.test.com",
        headers=original_client.headers,
        transport=mock_transport(responses or STANDARD_RESPONSES),
    )
    original_client.close()
    return e


@pytest.fixture
def agent():
    """Create an Agent with standard mock responses."""
    a = make_agent()
    yield a
    a._client.close()


@pytest.fixture
def env():
    """Create an ArenaEnv with standard mock responses."""
    e = make_env(primary_metric="SCAN_FREQUENCY")
    yield e
    e.close()
