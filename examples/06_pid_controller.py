"""
TendedLoop Arena — PID Controller Agent

Classic proportional-integral-derivative controller that maintains
a target metric value by continuously adjusting economy parameters.

PID is ideal for Arena because:
- It requires no training data (works from cycle 1)
- It handles the slow feedback loop gracefully (minutes, not milliseconds)
- It's well-understood, debuggable, and battle-tested in control systems
- The integral term prevents steady-state error
- The derivative term dampens oscillation

Strategy:
  - Define a setpoint (target scan frequency)
  - Compute error = setpoint - current_value each cycle
  - Adjust scanXp using PID output: Kp*error + Ki*integral + Kd*derivative

Run:
    pip install git+https://github.com/osheryadgar/tendedloop-arena.git
    export STRATEGY_TOKEN=strat_your_token_here
    python examples/06_pid_controller.py
"""

import logging
import os

from tendedloop_agent import Agent, ConfigUpdate, Signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ARENA_URL = os.environ.get("ARENA_URL", "https://api.tendedloop.com")
TOKEN = os.environ.get("STRATEGY_TOKEN", "strat_your_token_here")


# ─── PID Controller ───


class PIDController:
    """
    Discrete PID controller with anti-windup and output clamping.

    Tuning guide:
      Kp: Proportional gain. Higher = faster response, more overshoot.
      Ki: Integral gain. Higher = eliminates steady-state error, but can oscillate.
      Kd: Derivative gain. Higher = dampens oscillation, but amplifies noise.

    For Arena's slow loop (~60s cycles), start conservative:
      Kp=0.5, Ki=0.05, Kd=0.1
    """

    def __init__(
        self,
        setpoint: float,
        kp: float = 0.5,
        ki: float = 0.05,
        kd: float = 0.1,
        dt: float = 1.0,
        output_min: float = -5.0,
        output_max: float = 5.0,
        integral_limit: float = 20.0,
    ):
        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = (
            dt  # Time step (normalized; set to 1.0 when gains are pre-tuned for your poll_interval)
        )
        self.output_min = output_min
        self.output_max = output_max
        self.integral_limit = integral_limit

        self._integral = 0.0
        self._prev_measurement = 0.0
        self._cycle = 0

    def update(self, current_value: float) -> float:
        """Compute PID output given current measurement."""
        error = self.setpoint - current_value

        # Integral with anti-windup clamp (scaled by dt)
        self._integral += error * self.dt
        self._integral = max(-self.integral_limit, min(self.integral_limit, self._integral))

        # Derivative-on-measurement (avoids derivative kick on setpoint change)
        derivative = -(current_value - self._prev_measurement) / self.dt if self._cycle > 0 else 0.0
        self._prev_measurement = current_value
        self._cycle += 1

        # PID output
        output = self.kp * error + self.ki * self._integral + self.kd * derivative

        # Clamp output
        return max(self.output_min, min(self.output_max, output))


# ─── Configuration ───

# Target: 3.0 scans per user per day
TARGET_SCAN_FREQUENCY = 3.0

# PID controllers for different levers
scan_pid = PIDController(setpoint=TARGET_SCAN_FREQUENCY, kp=0.5, ki=0.05, kd=0.1)


# ─── Decision Logic ───


def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    """Use PID output to adjust scanXp proportionally."""
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if not freq or freq.confidence == "low":
        print("  Waiting for sufficient data...")
        return None

    # PID computes how much to adjust
    adjustment = scan_pid.update(freq.value)

    scan_xp = current_config.get("scanXp", 10)
    # Convert PID output to a multiplier: +5 output -> +50% boost, -5 -> -50%
    multiplier = 1.0 + (adjustment / 10.0)
    new_scan_xp = round(scan_xp * multiplier)

    # Don't propose no-ops
    if new_scan_xp == scan_xp:
        print(f"  PID output={adjustment:+.2f}, no change needed (freq={freq.value:.2f})")
        return None

    error = TARGET_SCAN_FREQUENCY - freq.value
    print(
        f"  PID: error={error:+.2f}, output={adjustment:+.2f}, "
        f"scanXp {scan_xp}->{new_scan_xp} (freq={freq.value:.2f})"
    )

    return ConfigUpdate(
        economy_overrides={"scanXp": new_scan_xp},
        reasoning=(
            f"PID control: freq={freq.value:.2f}, target={TARGET_SCAN_FREQUENCY}, "
            f"error={error:+.2f}, output={adjustment:+.2f}"
        ),
    )


# ─── Main ───


def main():
    print("TendedLoop Arena — PID Controller Agent")
    print("=" * 40)
    print(f"  Target scan frequency: {TARGET_SCAN_FREQUENCY}/day")
    print(f"  PID gains: Kp={scan_pid.kp}, Ki={scan_pid.ki}, Kd={scan_pid.kd}")
    print()

    with Agent(api_url=ARENA_URL, strategy_token=TOKEN) as agent:
        info = agent.info()
        print(f"  Variant:    {info.variant_name}")
        print(f"  Experiment: {info.experiment_name}")
        print()

        agent.run(decide, poll_interval=60, max_iterations=100)


if __name__ == "__main__":
    main()
