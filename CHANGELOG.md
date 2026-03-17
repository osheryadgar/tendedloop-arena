# Changelog

All notable changes to the TendedLoop Arena SDK will be documented in this file.

## [0.1.0] - 2026-03-17

### Added

- Initial release of `tendedloop-agent` Python SDK
- `Agent` class with full Arena Strategy API support
  - `info()` — Get variant metadata and constraints
  - `observe()` — Get real-time engagement signals
  - `act()` — Submit config updates with guardrail handling
  - `heartbeat()` — Agent liveness signaling
  - `scoreboard()` — Experiment-wide variant comparison
  - `decisions()` — Paginated decision audit log
  - `run()` — Automated observe-decide-act loop with background heartbeat
- `ArenaEnv` Gymnasium-compatible environment wrapper
  - Standard `reset/step/render/close` interface
  - Configurable primary metric for reward computation
  - Compatible with Stable-Baselines3, RLlib, CleanRL
- Type-safe dataclasses: `Signals`, `ConfigUpdate`, `ConfigResult`, `VariantInfo`, `ScoreboardEntry`, `WebhookInfo`
- 5 example agent strategies:
  - Rule-based quickstart
  - Gymnasium RL loop
  - Multi-metric optimizer
  - LLM-powered agent (Claude)
  - Thompson Sampling (Bayesian bandit)
- Documentation: architecture, guardrails, metrics, strategies, FAQ
