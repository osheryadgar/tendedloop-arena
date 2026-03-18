# Why Your Agent Oscillates (and How a 100-Year-Old Formula Fixes It)

Here's a dirty secret about AI: sometimes the best algorithm is from 1922.

If you followed along with the [previous post](/blog/02-first-agent-in-15-lines.md), you built a rule-based agent that boosts scan XP when engagement is low and does nothing when it's fine. Clean, simple, 15 lines. You ran it, felt smart, and then watched it do this:

```
Scan frequency over time:

  4.0 |
      |           *           *
  3.0 |         *   *       *   *       *
      |       *       *   *       *   *
  2.0 |─ ─ ─*─ ─ ─ ─ ─ * ─ ─ ─ ─ ─ *─ ─ ─   <-- threshold
      |     *
  1.0 |   *
      +──────────────────────────────────────
       t=0      t=5      t=10     t=15
```

That zigzag is called **oscillation**, and every rule-based agent does it. Frequency drops below 2.0, your agent boosts XP, frequency goes up, your agent stops boosting, frequency drifts back down, your agent boosts again. Boost, drop, boost, drop. Forever.

The fix comes from 1922, from a Russian-American engineer named Nicolas Minorsky who was trying to solve a completely different problem: how to keep a ship pointed in the right direction.

## The Ship Steering Problem

Minorsky was working on automatic ship steering for the US Navy. The challenge: when a gust of wind pushes a ship off course, how should the steering mechanism respond?

The naive approach (our rule-based agent) is: "if the ship is pointing left of the target, turn the rudder right." That works, but the ship overshoots. Then you turn left. It overshoots again. The ship zigzags across the ocean, never quite settling on its heading.

Minorsky's insight was that you need to consider three things, not one:

1. **How far off am I right now?** (Proportional)
2. **How long have I been off?** (Integral)
3. **Am I getting closer or farther?** (Derivative)

He called this **PID control**: Proportional, Integral, Derivative. And it turned out to be so useful that today PID controllers are everywhere -- cruise control in your car, temperature regulation in your oven, altitude hold in drones. It's arguably the most deployed algorithm in human history.

## PID with a Thermostat

Before we get to code, let me explain PID with something you already understand: a thermostat.

Your apartment is 18C. You want it at 22C. The heater has a dial from 0 to 10.

**P (Proportional): How far off am I?**

The error is 22 - 18 = 4 degrees. A proportional controller says: "I'm 4 degrees off, so I'll turn the dial to 4." If you were only 1 degree off, you'd turn it to 1. Simple and intuitive.

The problem: pure P-control gets you *close* but never *there*. As you approach 22C, the error shrinks, the heater output shrinks, and heat loss to the outside world balances out the reduced heating. You settle at 21.5C and stay there. This is called **steady-state error**.

**I (Integral): How long have I been off?**

The integral term sums up all past errors. Even if you're only 0.5 degrees off, after 20 minutes of being 0.5 degrees off, the integral has accumulated 10 degree-minutes of error. That accumulated frustration pushes the dial higher, eventually closing the gap completely.

The problem: if the integral accumulates too much (say, the heater was broken for an hour), it takes a long time to "unwind," and the temperature overshoots past 22C before settling back.

**D (Derivative): Am I getting closer?**

The derivative term looks at the *rate of change*. If the temperature is at 21C and rising fast, the derivative says "we're approaching the target quickly, ease off the heater now so we don't overshoot." If temperature is at 21C and flat, the derivative is zero and contributes nothing.

This is the term that eliminates oscillation. It's like braking when you see a stop sign ahead instead of slamming the brakes when you reach it.

## The Formula

The entire PID controller is one equation:

```
output = Kp * error  +  Ki * integral(error)  +  Kd * derivative(measurement)
```

Where:
- `error` = target - current_value
- `integral` = running sum of past errors
- `derivative` = rate of change of the measurement
- `Kp`, `Ki`, `Kd` = tuning knobs (you choose these)

That's it. Three multiplications and two additions. Let's build it.

## The Code

Here's a PID controller for Arena in about 20 lines:

```python
class PIDController:
    def __init__(self, target, kp=0.5, ki=0.05, kd=0.1):
        self.target = target
        self.kp, self.ki, self.kd = kp, ki, kd
        self.integral = 0.0
        self.prev_measurement = None

    def update(self, current_value):
        error = self.target - current_value

        # I: accumulate error over time (with anti-windup)
        self.integral += error
        self.integral = max(-20.0, min(20.0, self.integral))

        # D: rate of change of the measurement
        if self.prev_measurement is not None:
            derivative = -(current_value - self.prev_measurement)
        else:
            derivative = 0.0
        self.prev_measurement = current_value

        # PID output
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return max(-5.0, min(5.0, output))  # clamp to sane range
```

Let's trace through a concrete scenario.

## Walking Through the Math

Say our target scan frequency is 3.0 scans per user per day, and right now we're at 1.8.

**Cycle 1: current = 1.8**

```
error      = 3.0 - 1.8 = 1.2
integral   = 0.0 + 1.2 = 1.2
derivative = 0.0  (first cycle, no previous measurement)

output = 0.5 * 1.2  +  0.05 * 1.2  +  0.1 * 0.0
       = 0.6        +  0.06        +  0.0
       = 0.66
```

We convert this to a config multiplier: `1.0 + (0.66 / 10) = 1.066`. So `scanXp` goes from 10 to `round(10 * 1.066)` = 11. A modest 10% bump.

**Cycle 5: current = 2.5 (improving!)**

```
error      = 3.0 - 2.5 = 0.5
integral   = 3.8 + 0.5 = 4.3  (accumulated over 5 cycles)
derivative = -(2.5 - 2.3) = -0.2  (rising, so negative = good)

output = 0.5 * 0.5  +  0.05 * 4.3  +  0.1 * (-0.2)
       = 0.25       +  0.215       +  (-0.02)
       = 0.445
```

Notice what's happening: the P term shrunk (we're closer to target), but the I term grew (we've been below target for 5 cycles). The D term is negative -- it's **braking** because we're approaching the target. This is what prevents overshoot.

**Cycle 10: current = 3.1 (slightly over target)**

```
error      = 3.0 - 3.1 = -0.1
integral   = 4.0 + (-0.1) = 3.9  (starting to unwind)
derivative = -(3.1 - 3.0) = -0.1

output = 0.5 * (-0.1) + 0.05 * 3.9 + 0.1 * (-0.1)
       = -0.05        + 0.195      + (-0.01)
       = 0.135
```

We're *slightly* above target, so the P term is negative (pull back). But the integral is still positive from all those cycles below target, keeping us pushing slightly forward. The system gracefully settles around 3.0 instead of oscillating.

## Anti-Windup: The Gotcha That Breaks Everything

See this line?

```python
self.integral = max(-20.0, min(20.0, self.integral))
```

That's **anti-windup**, and without it, your agent will eventually do something catastrophic.

Here's the scenario: imagine your agent has been running for 100 cycles and the scan frequency has been stuck at 1.0 the whole time (maybe there's a bug, or it's a holiday and nobody's in the office). Each cycle adds `error = 2.0` to the integral. After 100 cycles, your integral is 200.

Now people come back to the office. Frequency starts climbing. But the integral has 200 points of "frustration" stored up. It takes *forever* to unwind. Meanwhile, the PID output is maxed out, pushing scanXp higher and higher. By the time the integral finally crosses zero, you've massively overshot.

The clamp at 20.0 prevents this. The integral can express "we've been off-target for a while" but it can't express "we've been off-target so long that I've completely lost my mind."

## Putting It All Together

Here's the complete Arena agent with PID control. Save this as `pid_agent.py` and run it against the sandbox:

```python
from tendedloop_agent import Agent, ConfigUpdate, Signals

class PIDController:
    def __init__(self, target, kp=0.5, ki=0.05, kd=0.1):
        self.target = target
        self.kp, self.ki, self.kd = kp, ki, kd
        self.integral = 0.0
        self.prev_measurement = None

    def update(self, current_value):
        error = self.target - current_value
        self.integral = max(-20, min(20, self.integral + error))
        if self.prev_measurement is not None:
            derivative = -(current_value - self.prev_measurement)
        else:
            derivative = 0.0
        self.prev_measurement = current_value
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return max(-5.0, min(5.0, output))

pid = PIDController(target=3.0)

def decide(signals: Signals, current_config: dict) -> ConfigUpdate | None:
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if not freq or freq.confidence == "low":
        return None

    adjustment = pid.update(freq.value)
    if abs(adjustment) < 0.1:
        return None  # close enough to target, don't bother

    multiplier = 1.0 + (adjustment / 10.0)
    new_xp = max(5, min(25, round(current_config["scanXp"] * multiplier)))

    if new_xp == current_config["scanXp"]:
        return None

    return ConfigUpdate(
        economy_overrides={"scanXp": new_xp},
        reasoning=f"PID: freq={freq.value:.2f}, target=3.0, adj={adjustment:+.2f}, scanXp->{new_xp}",
    )

with Agent(api_url="http://localhost:7860", strategy_token="strat_demo_local") as agent:
    agent.run(decide, poll_interval=65, max_iterations=20)
```

Run the sandbox in one terminal (`python -m tendedloop_agent demo`) and this agent in another.

## Tuning Guide

The three gains -- `Kp`, `Ki`, `Kd` -- determine your agent's personality:

| Symptom | What to adjust |
|---------|---------------|
| Reacts too slowly, takes forever to correct | Increase `Kp` |
| Oscillates around the target | Increase `Kd` (or decrease `Kp`) |
| Settles close but never exactly at target | Increase `Ki` |
| Overshoots and rings back and forth | Decrease `Ki`, increase `Kd` |

Start with `Kp=0.5, Ki=0.05, Kd=0.1`. These work well for Arena's 60-second polling loop. If your agent is too timid, double `Kp`. If it oscillates, double `Kd`.

A common beginner mistake is cranking up all three gains. High gains make the controller aggressive -- fast to respond, but prone to instability. In control theory, there's a fundamental tradeoff between speed and stability. Start conservative.

## When NOT to Use PID

PID is great for one thing: maintaining a single metric at a target value. It's not the right tool when:

- **You don't know the target.** If you don't know whether 3.0 or 5.0 is the right scan frequency, PID can't help. Use bandit algorithms to *discover* the target first.
- **You have multiple objectives.** PID for scan frequency and PID for retention can fight each other -- one wants to increase XP, the other wants to decrease it. Multi-objective optimization needs different tools.
- **The relationship is nonlinear.** PID assumes that increasing scanXp by 10% will increase frequency by some proportional amount. If the relationship is more complex (e.g., there's a saturation point), PID will struggle.

## What's Next

PID controls one metric. But Arena gives you six metrics and ten tunable parameters. What if boosting scan frequency tanks retention? What if increasing streak bonuses helps retention but reduces feedback quality?

That's the explore-exploit dilemma, and it's where things get really interesting. Bandit algorithms, Bayesian optimization, and ensemble methods all have something to say about it. But that's for the next series.

For now, you have two working agents: a 15-line rule-based agent and a PID controller. Run them both against the sandbox. Compare their behavior. The PID agent will converge smoothly to its target while the rule-based agent zigzags. That difference is the difference between a thermostat and a light switch.

## Try It Yourself

```bash
# Terminal 1
pip install tendedloop-arena
python -m tendedloop_agent demo

# Terminal 2
python pid_agent.py
```

Experiments to try:

1. **P-only controller.** Set `Ki=0` and `Kd=0`. Watch it get close but never reach the target.
2. **Remove anti-windup.** Change the clamp to `±1000`. Run for 20 cycles and watch the overshoot.
3. **Dual PID.** Add a second `PIDController(target=0.7)` for `RETENTION_RATE` and combine both outputs. How do you handle conflicts when one wants to increase XP and the other wants to decrease it?

---

*This is part 3 of the [TendedLoop Arena](https://github.com/osheryadgar/tendedloop-arena) blog series. [Part 1](/blog/01-the-problem-nobody-tells-you.md) covered the problem. [Part 2](/blog/02-first-agent-in-15-lines.md) built your first agent. The full workshop has 15 lessons covering bandits, RL, LLM agents, and production safety patterns.*
