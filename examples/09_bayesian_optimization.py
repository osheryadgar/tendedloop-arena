"""
TendedLoop Arena — Bayesian Optimization Agent

Sample-efficient black-box optimization using a surrogate model
(Gaussian Process) to find the best economy configuration with
minimal evaluations.

Why Bayesian Optimization for Arena:
  - Arena's feedback loop is slow (minutes to hours for metrics to shift)
  - Each evaluation is "expensive" (affects real users)
  - We need to find good configs in very few iterations
  - BO is designed exactly for this: optimize expensive black-box functions

How it works:
  1. Maintain a history of (config, reward) pairs
  2. Fit a surrogate model (GP) to predict reward for unseen configs
  3. Use an acquisition function (Expected Improvement) to select
     the next config that balances exploration and exploitation
  4. Evaluate, observe reward, update model, repeat

This implementation uses a simple RBF kernel GP without heavy dependencies.
For production use, consider scikit-optimize or BoTorch.

Run:
    pip install "tendedloop-agent[rl] @ git+https://github.com/osheryadgar/tendedloop-arena.git"
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/09_bayesian_optimization.py
"""

import logging
import os

import numpy as np

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")


# ─── Search Space ───
# Define the parameters to optimize and their ranges.
# BO will search within these bounds.

PARAMS = {
    "scanXp": (5, 25),
    "feedbackXp": (8, 30),
    "streakBonusPerDay": (3, 15),
    "firstScanOfDayXp": (8, 25),
}

N_INITIAL_RANDOM = 5  # Random exploration before fitting GP


# ─── Simple Bayesian Optimizer ───


class BayesianOptimizer:
    """
    Bayesian Optimization with RBF kernel GP and Expected Improvement.

    This is a minimal implementation for demonstration. For serious work,
    use scikit-optimize, BoTorch, or Ax.
    """

    def __init__(self, param_bounds: dict[str, tuple[int, int]], noise: float = 0.1):
        self.param_names = list(param_bounds.keys())
        self.bounds = np.array([param_bounds[k] for k in self.param_names])
        self.noise = noise
        self.X: list[np.ndarray] = []  # Observed configs (normalized [0,1])
        self.y: list[float] = []  # Observed rewards

    def normalize(self, config: dict[str, float]) -> np.ndarray:
        """Normalize config values to [0, 1] based on bounds."""
        vals = [config.get(k, (b[0] + b[1]) / 2) for k, b in zip(self.param_names, self.bounds)]
        return np.array([(v - lo) / (hi - lo) for v, (lo, hi) in zip(vals, self.bounds)])

    def denormalize(self, x: np.ndarray) -> dict[str, int]:
        """Convert [0, 1] array back to integer config values."""
        config = {}
        for i, (name, (lo, hi)) in enumerate(zip(self.param_names, self.bounds)):
            config[name] = round(lo + x[i] * (hi - lo))
        return config

    def suggest(self) -> dict[str, int]:
        """Suggest the next config to evaluate."""
        # Random exploration phase
        if len(self.X) < N_INITIAL_RANDOM:
            x = np.random.uniform(0, 1, len(self.param_names))
            return self.denormalize(x)

        # Find config that maximizes Expected Improvement
        best_y = max(self.y)
        best_ei = -1.0
        best_x = None

        # Random search over candidate points (simple but effective)
        candidates = np.random.uniform(0, 1, (200, len(self.param_names)))
        for x in candidates:
            mu, sigma = self._predict(x)
            ei = self._expected_improvement(mu, sigma, best_y)
            if ei > best_ei:
                best_ei = ei
                best_x = x

        if best_x is None:
            best_x = np.random.uniform(0, 1, len(self.param_names))

        return self.denormalize(best_x)

    def observe(self, config: dict[str, float], reward: float):
        """Record an observation."""
        self.X.append(self.normalize(config))
        self.y.append(reward)

    def _rbf_kernel(self, x1: np.ndarray, x2: np.ndarray, length_scale: float = 0.3) -> float:
        """Radial Basis Function kernel."""
        dist_sq = np.sum((x1 - x2) ** 2)
        return np.exp(-dist_sq / (2 * length_scale**2))

    def _predict(self, x: np.ndarray) -> tuple[float, float]:
        """Predict mean and std at point x using GP."""
        n = len(self.X)
        if n == 0:
            return 0.0, 1.0

        x_arr = np.array(self.X)
        y_arr = np.array(self.y)

        # Kernel matrix + noise
        kern = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                kern[i, j] = self._rbf_kernel(x_arr[i], x_arr[j])
        kern += self.noise**2 * np.eye(n)

        # Kernel vector k(x, X)
        k = np.array([self._rbf_kernel(x, x_arr[i]) for i in range(n)])

        # GP predictive mean and variance
        try:
            kern_inv = np.linalg.inv(kern)
        except np.linalg.LinAlgError:
            return float(np.mean(y_arr)), 1.0

        mu = float(k @ kern_inv @ y_arr)
        sigma_sq = 1.0 - float(k @ kern_inv @ k)
        sigma = max(np.sqrt(max(sigma_sq, 0)), 1e-6)

        return mu, sigma

    def _expected_improvement(
        self, mu: float, sigma: float, best_y: float, xi: float = 0.01
    ) -> float:
        """Expected Improvement acquisition function."""
        z = (mu - best_y - xi) / sigma
        # Approximate Phi(z) and phi(z) without scipy
        phi = np.exp(-0.5 * z**2) / np.sqrt(2 * np.pi)
        big_phi = 0.5 * (1 + np.tanh(z * np.sqrt(2 / np.pi) * (1 + 0.044715 * z**2)))
        return float(sigma * (z * big_phi + phi))

    def best_config(self) -> tuple[dict[str, int], float]:
        """Return the best observed config and its reward."""
        if not self.y:
            return self.denormalize(np.full(len(self.param_names), 0.5)), 0.0
        best_idx = int(np.argmax(self.y))
        return self.denormalize(self.X[best_idx]), self.y[best_idx]


# ─── Decision Logic ───

optimizer = BayesianOptimizer(PARAMS)
pending_config: dict[str, int] | None = None


def compute_reward(signals: Signals) -> float:
    """Composite reward from signals."""
    score = 0.0
    freq = signals.metrics.get("SCAN_FREQUENCY")
    ret = signals.metrics.get("RETENTION_RATE")
    qual = signals.metrics.get("FEEDBACK_QUALITY")

    if freq and freq.confidence != "low":
        score += min(freq.value / 5.0, 1.0) * 0.4
    if ret and ret.confidence != "low":
        score += ret.value * 0.35
    if qual and qual.confidence != "low":
        score += qual.value * 0.25

    return score


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """Bayesian Optimization decision function."""
    global pending_config

    reward = compute_reward(signals)
    phase = "explore" if len(optimizer.X) < N_INITIAL_RANDOM else "optimize"

    # Record previous evaluation
    if pending_config is not None:
        optimizer.observe(pending_config, reward)
        best_config, best_reward = optimizer.best_config()
        print(f"  Observed reward={reward:.3f} | Best so far={best_reward:.3f}")
        print(f"  Best config: {best_config}")

    # Suggest next config
    suggestion = optimizer.suggest()
    pending_config = suggestion

    print(f"\n  Phase: {phase} ({len(optimizer.X)}/{N_INITIAL_RANDOM + 50} evaluations)")
    print(f"  Suggested: {suggestion}")

    return ConfigUpdate(
        economy_overrides=suggestion,
        reasoning=f"Bayesian Optimization ({phase}): {suggestion}",
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — Bayesian Optimization Agent")
    print("=" * 47)
    print()
    print("  Search space:")
    for name, (lo, hi) in PARAMS.items():
        print(f"    {name}: [{lo}, {hi}]")
    print(f"  Initial random samples: {N_INITIAL_RANDOM}")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print()

        agent.run(decide, poll_interval=120, max_iterations=50)

        # Final results
        best_config, best_reward = optimizer.best_config()
        print("\nBest configuration found:")
        for k, v in best_config.items():
            print(f"  {k}: {v}")
        print(f"  Reward: {best_reward:.3f}")
        print(f"  Total evaluations: {len(optimizer.X)}")


if __name__ == "__main__":
    main()
