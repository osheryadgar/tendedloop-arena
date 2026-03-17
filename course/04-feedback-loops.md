# Lesson 4: Feedback Loops and PID Control

> **Example**: [`examples/06_pid_controller.py`](../examples/06_pid_controller.py)

## The Problem with Rules

The quickstart agent uses hard-coded thresholds: "if frequency < 2.0, boost by 15%." But what's special about 2.0? What about 15%? These are arbitrary.

Worse, rule-based agents **oscillate**. When frequency dips below 2.0, they boost. Frequency rises above 2.0, they stop. Frequency dips again, they boost again. This sawtooth pattern wastes update slots and confuses users.

## Enter PID Control

PID (Proportional-Integral-Derivative) control is a 100-year-old technique from engineering. It solves exactly this problem: **maintain a target value by continuously adjusting an input**.

Instead of "if below threshold, do X," PID asks: "how far are we from the target, how long have we been off, and are we getting closer or farther?"

### The Three Terms

```
output = Kp × error + Ki × integral(error) + Kd × derivative(measurement)
```

**Proportional (P)**: React to the current error.
- Error = target - current_value
- Large error → large correction
- Problem: can't eliminate steady-state error (always slightly off)

**Integral (I)**: React to accumulated past error.
- Sums up all past errors
- Even a tiny persistent error eventually produces a large integral
- Eliminates steady-state error
- Problem: can overshoot (integral "windup")

**Derivative (D)**: React to the rate of change.
- Looks at how fast the measurement is changing
- Dampens oscillation — if approaching the target quickly, reduce correction
- Problem: amplifies measurement noise

### Visual Intuition

```
Target: 3.0 scans/day
                                    ┌─── D term dampens overshoot
                                    v
    4 ┤     P term    ╭──────────────────
      │     drives   ╱
    3 ┤─ ─ ─target─╱─ ─ ─ ─ ─ ─ ─ ─ ─ ─
      │           ╱  I term eliminates
    2 ┤──────────╯   steady-state error
      │
    1 ┤
      └──────────────────────────────────
        t=0   t=5   t=10  t=15  t=20
```

## Code Deep Dive

### The PID Controller Class

```python
class PIDController:
    def __init__(self, setpoint, kp=0.5, ki=0.05, kd=0.1, dt=1.0,
                 integral_limit=20.0):
        self.setpoint = setpoint
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.integral_limit = integral_limit
        self._integral = 0.0
        self._prev_measurement = 0.0
        self._cycle = 0

    def update(self, current_value):
        error = self.setpoint - current_value

        # Integral (with anti-windup clamp)
        self._integral += error * self.dt
        self._integral = max(-self.integral_limit,
                             min(self.integral_limit, self._integral))

        # Derivative on measurement (avoids derivative kick)
        if self._cycle > 0:
            derivative = -(current_value - self._prev_measurement) / self.dt
        else:
            derivative = 0.0  # No derivative on first cycle
        self._prev_measurement = current_value
        self._cycle += 1

        output = self.kp * error + self.ki * self._integral + self.kd * derivative

        # Output clamping — prevents extreme corrections
        return max(-5.0, min(5.0, output))
```

Two subtle details:

1. **Anti-windup**: The integral is clamped to `±integral_limit`. Without this, if the error persists for many cycles, the integral grows huge and causes massive overshoot when the correction finally takes effect.

2. **Derivative on measurement**: Classic PID computes `d(error)/dt`, but if the setpoint changes, this creates a spike ("derivative kick"). Computing `d(measurement)/dt` instead avoids this.

### Converting PID Output to Config Changes

The PID outputs a value like +2.3 or -1.5. We convert this to a multiplier:

```python
adjustment = pid.update(freq.value)        # e.g., +2.3
multiplier = 1.0 + (adjustment / 10.0)     # e.g., 1.23
new_scan_xp = round(scan_xp * multiplier)  # e.g., 10 * 1.23 = 12
```

### Tuning Guide

| Symptom | Adjust |
|---------|--------|
| Too slow to respond | Increase Kp |
| Oscillating | Decrease Kp, increase Kd |
| Steady-state error | Increase Ki |
| Overshoot after correction | Decrease Ki, increase Kd |

For Arena's 60-second loop, start with: `Kp=0.5, Ki=0.05, Kd=0.1`

## When to Use PID

**Good for:**
- Maintaining a single target metric (e.g., "keep scan frequency at 3.0/day")
- Stable environments where the relationship between input and output is predictable
- When you have a clear target value in mind

**Not good for:**
- Multiple competing objectives (use multi-metric optimizer instead)
- Exploring unknown config spaces (use bandits instead)
- When you don't know the target value (use RL or bandits to discover it)

## Exercises

1. **Tune the gains**: Run the PID agent with `Kp=2.0, Ki=0.0, Kd=0.0` (P-only). Observe oscillation. Then add `Kd=0.5` and see it dampen.
2. **Add a second PID**: Create a second PID controller for retention rate and combine both outputs.
3. **Variable setpoint**: Make the setpoint increase over time (week 1: target 2.0, week 2: target 3.0) and watch the PID adapt.

## Next

In [Lesson 5](05-multi-objective.md), we'll tackle the harder problem of optimizing multiple metrics simultaneously.
