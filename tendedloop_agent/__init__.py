"""TendedLoop Arena Agent SDK — Python client for multi-agent gamification research."""

from .agent import Agent
from .env import ArenaEnv
from .types import (
    ConfigResult,
    ConfigUpdate,
    MetricSignal,
    ScoreboardEntry,
    Signals,
    VariantInfo,
    WebhookInfo,
)

__all__ = [
    "Agent",
    "ArenaEnv",
    "ConfigResult",
    "ConfigUpdate",
    "MetricSignal",
    "ScoreboardEntry",
    "Signals",
    "VariantInfo",
    "WebhookInfo",
]

__version__ = "0.1.0"
