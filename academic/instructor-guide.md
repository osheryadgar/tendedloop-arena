# Instructor Guide

A comprehensive guide for instructors who want to use TendedLoop Arena in their courses, workshops, or research labs.

---

## 1. Quick Start for Instructors

You want to use Arena in your course next semester. Here is what to do, in order:

### Before the Semester

1. **Get a TendedLoop account.** Sign up at [tendedloop.com](https://tendedloop.com). The free tier includes 1 building, which is sufficient for most lab setups.

2. **Complete the setup wizard.** Create at least one building with amenities and QR codes. This is the real-world environment your students' agents will optimize.

3. **Decide on your course format.** Arena supports four integration models (see [Section 2](#2-course-integration-options) below). Pick the one that fits your schedule.

4. **Create an experiment.** In the [Dashboard](https://app.tendedloop.com), go to **Admin > Research > Experiments** and create a new experiment with Agent Mode enabled. Create N treatment variants (one per team) plus 1 control.

5. **Configure guardrails.** Start conservative for first-time students — 120-minute update intervals, 15% delta limits. See the [Classroom Guide](classroom-guide.md) for recommended settings by experience level.

6. **Download manifests.** Each variant produces a manifest JSON file containing a `strategyToken`. Download one per team.

7. **Prepare your syllabus.** Point students to the [Workshop](../workshop/README.md) for self-study and the relevant example agents in `examples/`.

### First Day of Class

1. **Distribute tokens.** Give each team their manifest file. Emphasize: tokens go in environment variables, never in code.

2. **Verify connectivity.** Have every team run the quickstart example (`01_quickstart.py`) to confirm their token works and they can observe signals.

3. **Pre-class practice (optional).** Assign the local sandbox as homework before the first lab: `python -m tendedloop_agent demo` lets students experiment with the SDK without consuming experiment resources.

4. **Set expectations.** Share the primary metric they should optimize, the experiment duration, and the grading rubric.

### During the Experiment

1. **Monitor the dashboard.** Check heartbeat status, decision logs, and metric trends at least once per class session.

2. **Hold office hours.** Most agent bugs surface in the first 48 hours. Be available.

3. **Use the scoreboard.** Project `agent.scoreboard()` output during class to create competition and discussion.

### After the Experiment

1. **Export data.** Download metrics, decision logs, and statistical results from the Dashboard.

2. **Grade.** Use the rubrics in [Section 4](#4-grading-rubrics) below.

3. **Debrief.** Have teams present their strategies and results. The decision audit log is invaluable for understanding what each agent actually did.

---

## 2. Course Integration Options

### Option A: Full 14-Week Course

Use one of the two semester-length courses in the [Academic Program](../academic/README.md):

| Course | Focus | Best For |
|--------|-------|----------|
| [Course A: Multi-Agent Systems](../academic/course-a-multi-agent-systems.md) | Agent theory, game theory, bandits, RL, mechanism design | CS/AI departments |
| [Course B: Computational Gamification](../academic/course-b-gamification-design.md) | Reward modeling, behavioral economics, engagement optimization | CS/AI or HCI departments |

Both courses include the 8-session workshop as the practical lab component (15% of the grade). Students build increasingly sophisticated agents throughout the semester, culminating in a competitive experiment in the final weeks.

**Recommended schedule:**
- Weeks 1-10: Lectures + assignments. Students work through workshop sessions 1-6 in parallel.
- Weeks 11-12: Launch the competitive experiment. Students run their agents.
- Weeks 13-14: Analysis, presentations, and writeups.

### Option B: 8-Session Workshop

Use the standalone [Workshop](../workshop/README.md) as a focused hands-on course. Each session is 2-3 hours.

| Session | Topic | What Students Build |
|---------|-------|-------------------|
| 1 | Setup and Orientation | Verify connectivity, understand the system |
| 2 | First Agent | Rule-based observe-decide-act agent |
| 3 | Control Theory | PID controller for engagement targets |
| 4 | Bandit Algorithms | UCB1 and explore-then-exploit agents |
| 5 | Bayesian Approaches | Thompson Sampling, contextual bandits |
| 6 | Advanced Optimization | Bayesian Optimization, RL with Gymnasium |
| 7 | AI Agents and Ensembles | LLM-powered agents, Hedge ensemble |
| 8 | Safety and Competition | Production patterns, final competition |

**Best for:** Graduate seminars, research lab workshops, summer schools, or intensive bootcamps.

**Timing:** Can run weekly (8 weeks), biweekly (4 weeks), or as a compressed 4-day intensive.

### Option C: Single Lab Assignment (3 Hours)

A self-contained lab that can be dropped into any AI, ML, or software engineering course.

**Pre-lab (30 min):** Students read [Lesson 01](../workshop/01-what-is-arena.md) and [Lesson 02](../workshop/02-the-arena-environment.md) before class.

**In-lab schedule:**

| Time | Activity |
|------|----------|
| 0:00-0:20 | Introduction: What is Arena? Live demo of the observe-decide-act loop. |
| 0:20-0:40 | Setup: Install SDK, configure tokens, run `01_quickstart.py`. |
| 0:40-1:30 | Build: Each team writes a custom `decide()` function. Start with rule-based, extend to bandit or PID if time allows. |
| 1:30-1:45 | Break |
| 1:45-2:30 | Run: Launch agents against the live experiment. Monitor the scoreboard together. |
| 2:30-2:50 | Debrief: Compare strategies. Discuss what worked and why. Review decision logs. |
| 2:50-3:00 | Wrap-up: Assign the writeup (due next class). |

**Deliverables:** Agent code + 1-page writeup (strategy, results, lessons learned).

**Best for:** A single lab session in an existing AI, software engineering, or data science course.

### Option D: Capstone Project Component

Arena works well as a capstone or final project platform where students demonstrate mastery of course concepts.

**Structure:**

1. **Proposal (week 1):** Team submits a 1-page hypothesis about which gamification strategy will maximize their chosen metric, with justification from course theory.

2. **Implementation (weeks 2-4):** Team builds their agent, incorporating at least two distinct algorithmic techniques from the course (e.g., bandit + PID, RL + LLM reasoning).

3. **Experiment run (weeks 3-5):** Agent runs against the live experiment for at least 7 days.

4. **Final report (week 5-6):** 8-10 page paper covering hypothesis, design, implementation, results, and statistical analysis. Use the [Research Project Rubric](#research-project-100-points) for grading.

5. **Presentation (week 6):** 15-minute team presentation with live demo.

**Best for:** Senior capstone courses, graduate project courses, or independent study.

---

## 3. Experiment Setup Checklist

### Pre-Semester Preparation

- [ ] **TendedLoop account created** at [app.tendedloop.com](https://app.tendedloop.com)
- [ ] **Building configured** with at least one location, amenities, and QR codes
- [ ] **Experiment created** in Admin > Research > Experiments
  - [ ] Hypothesis documented
  - [ ] Primary metric selected (SCAN_FREQUENCY is recommended for first-time use)
  - [ ] N treatment variants created (one per team), each with Agent Mode enabled
  - [ ] 1 control variant created (no agent — uses default config)
  - [ ] Schedule set (start date after first lab session, duration covers the assignment period)
- [ ] **Guardrails configured** per variant

  | Setting | First-Time Students | Experienced Teams | Advanced Research |
  |---------|-------------------|------------------|-------------------|
  | `updateIntervalMin` | 120 | 60 | 5 |
  | `deltaLimitPct` | 15 | 50 | 80 |

- [ ] **Manifests downloaded** (one JSON file per treatment variant)
- [ ] **SDK installation tested** on the lab machines or verified that students can install via pip

### Token Distribution

Each team receives exactly one strategy token (contained in their manifest JSON file). Here is how to distribute them securely:

**Option 1: Secure file share (recommended)**
Upload each manifest to a course LMS (Canvas, Moodle, Blackboard) as a per-team assignment attachment. Only the assigned team can access their file.

**Option 2: In-class handout**
Print each manifest on a separate sheet. Hand one to each team lead during the first lab session. Collect and shred unused sheets.

**Option 3: Encrypted email**
Email each team lead their manifest file. Emphasize: do not forward, do not commit to version control.

**Security reminders for students:**
- Store the token in an environment variable: `export STRATEGY_TOKEN=strat_...`
- Add `.env` and any manifest files to `.gitignore`
- Never hardcode the token in source code
- Tokens are scoped to one variant — a team cannot affect other teams' experiments
- Tokens expire when the experiment is archived

### Monitoring During the Assignment

**What to watch for:**

| Signal | Where to Check | Action |
|--------|---------------|--------|
| Heartbeat timeout (agent stopped) | Dashboard > Experiment > Health | Contact the team — their agent likely crashed |
| No decisions after 24h | Dashboard > Experiment > Variants | Team may not have started; follow up |
| 4+ consecutive max-delta changes | Decision log | Likely a bug — agent is oscillating without observing |
| Retention drop below 30% | Metrics panel | Consider activating the circuit breaker for that variant |
| All variants converging to same config | Config comparison | Suggest teams use different starting conditions or strategies |

**When to intervene:**

- **Circuit breaker:** Use this if a variant's metrics drop dangerously. It freezes the variant at its current config. The team can still observe but cannot act until you release the breaker.
- **Reach out early:** Most issues happen in the first 48 hours. A quick Slack message or email can save a team days of frustration.
- **Do not intervene on strategy.** If a team's agent is performing poorly but not causing harm, let it run. Poor performance is a learning outcome.

---

## 4. Grading Rubrics

### Lab Assignment (100 Points)

For single lab sessions or short assignments (Option C or individual workshop sessions).

| Criterion | Points | What to Evaluate |
|-----------|--------|-----------------|
| **Agent Runs Successfully** | 20 | Agent connects, authenticates, and completes the observe-decide-act loop without crashing. Heartbeat remains active for the duration of the assignment. |
| **Observes Correctly** | 15 | Agent reads signals and correctly interprets metric values, confidence levels, and sample sizes. Does not act on low-confidence data without justification. |
| **Acts with Reasoning** | 20 | Every `act()` call includes a meaningful `reasoning` string that explains *why* the change was made. Reasoning references specific metric values or trends, not generic statements. |
| **Handles Rejections Gracefully** | 15 | Agent correctly handles clamped responses (adjusts expectations), rate limiting (backs off), and circuit breaker activation (stops acting). No crash on any rejection type. |
| **Code Quality** | 15 | Clean, readable code. Proper use of environment variables for tokens. Error handling (try/except with meaningful fallback). Comments explaining strategy logic. Follows Python conventions. |
| **Written Analysis** | 15 | 1-page writeup covering: what strategy was used, what happened during the run, what the decision log reveals, and what the student would change next time. |

**Grade boundaries:** A: 90+, B: 80-89, C: 70-79, D: 60-69, F: below 60.

### Research Project (100 Points)

For capstone projects, graduate research, or extended assignments (Option D).

| Criterion | Points | What to Evaluate |
|-----------|--------|-----------------|
| **Hypothesis Formulation** | 15 | Clear, falsifiable hypothesis stated before the experiment begins. Grounded in theory (e.g., "Increasing streak bonuses beyond 2x base XP will decrease retention due to overjustification effect, per Ryan & Deci 2000"). Prediction is specific and testable. |
| **Experimental Design** | 20 | Appropriate choice of primary and secondary metrics. Justification for guardrail settings. Consideration of confounding variables. Power analysis or sample size discussion. Clear control condition. Pre-registration of analysis plan. |
| **Implementation Quality** | 20 | Agent implements the stated strategy correctly. Code is modular, tested, and well-documented. Uses appropriate algorithmic techniques (bandit, RL, control theory, LLM). Handles edge cases (no data, low confidence, rate limiting). |
| **Statistical Analysis** | 20 | Correct application of statistical tests (Welch's t-test or Fisher's exact as appropriate). Effect sizes reported (Cohen's d). Confidence intervals included. Multiple comparison correction if testing multiple metrics. Honest reporting of non-significant results. |
| **Written Report** | 25 | 8-10 page paper with: abstract, introduction and motivation, related work, methodology, results with visualizations, discussion of findings, limitations, and future work. Publication-quality figures. Proper citations. |

**Grade boundaries:** A: 90+, B: 80-89, C: 70-79, D: 60-69, F: below 60.

### Competitive Tournament (100 Points)

For multi-team competitions where agents compete head-to-head in a shared experiment.

| Criterion | Points | What to Evaluate |
|-----------|--------|-----------------|
| **Final Metric Performance** | 30 | Rank-based scoring on the primary metric at experiment end. 1st place: 30 pts, 2nd: 27, 3rd: 24, 4th: 21, then -3 per rank. Minimum 15 pts for any agent that ran successfully for the full duration. Ties broken by secondary metric. |
| **Strategy Sophistication** | 25 | Does the agent use a principled approach (not just random tuning)? Evaluation considers: algorithmic foundation (bandit, RL, control theory, LLM reasoning), adaptiveness to changing conditions, multi-objective balancing, and creative use of available signals. A simple strategy executed well scores higher than a complex strategy executed poorly. |
| **Code Quality** | 20 | Clean, readable, well-structured code. Proper error handling and graceful degradation. Environment variable usage for secrets. Modular design (strategy logic separated from SDK plumbing). Appropriate use of logging. No hardcoded values that should be configurable. |
| **Presentation / Writeup** | 25 | 10-minute presentation or 3-5 page writeup covering: strategy overview (with diagrams), key design decisions and their rationale, results analysis (with charts), what worked and what did not, and what the team would do differently. Peer evaluation component: each team rates other teams' presentations (contributes 5 of the 25 points). |

**Grade boundaries:** A: 90+, B: 80-89, C: 70-79, D: 60-69, F: below 60.

> **Tip:** For classes with 8+ teams, consider percentile-based scoring instead: top 25% = 30 pts, 25-50% = 25 pts, 50-75% = 20 pts, bottom 25% = 17 pts. This reduces the penalty for teams in larger classes.

**Tournament logistics:**
- All teams start at the same time (experiment launch).
- The experiment runs for a fixed duration (recommended: 7-14 days).
- The scoreboard is visible to all teams throughout (fosters competition).
- Final rankings are computed from the experiment's statistical analysis, not raw metric values.

---

## 5. Common Pitfalls and Solutions

### Students Hardcoding Tokens

**Symptom:** Token appears in committed source code or shared repositories.

**Solution:** On day one, require all teams to:
1. Store the token in an environment variable: `export STRATEGY_TOKEN=strat_...`
2. Load it in code: `token = os.environ["STRATEGY_TOKEN"]`
3. Add to `.gitignore`: `.env`, `*.json` manifest files
4. If a token is accidentally committed, rotate it immediately from the Dashboard (revoke the old manifest and issue a new one).

**Prevention:** Include a `.env.example` file in the assignment starter repo with `STRATEGY_TOKEN=strat_paste_your_token_here`.

### Agents Doing Nothing

**Symptom:** Agent connects and observes but never calls `act()`. Decision log is empty.

**Common causes:**
- **Confidence gating too conservative.** The agent waits for `confidence == "high"` but the experiment is too new or has too few users to ever reach high confidence. Solution: accept `"medium"` confidence, or use a time-based fallback ("if no high-confidence data after 6 hours, act on medium").
- **Thresholds never triggered.** The rule-based conditions (e.g., `if freq < 2.0`) never fire because the baseline is already above the threshold. Solution: have students log the observed values first, then set thresholds based on actual data.
- **Bug in decide function.** The function returns `None` on every path. Solution: add a `print()` or log statement showing the decision path taken.

### All Agents Converging to the Same Config

**Symptom:** After a few rounds, all variants have nearly identical economy configs.

**Causes:** Teams used the same algorithm with the same starting conditions, and the system has a single global optimum that all agents find.

**Solutions:**
- Assign different starting configs to each variant (vary the initial `scanXp`, `streakBonusPerDay`, etc. in the experiment setup).
- Require teams to use different algorithmic families (e.g., one team uses PID, another uses Thompson Sampling, another uses an LLM agent).
- Add secondary objectives: one team optimizes SCAN_FREQUENCY, another optimizes RETENTION_RATE, a third optimizes FEEDBACK_QUALITY.

### Rate Limiting Frustration

**Symptom:** Students complain that their agent's `act()` calls are being rejected with `RATE_LIMITED`.

**Explanation:** The `updateIntervalMin` guardrail enforces a minimum time between config changes. This is intentional — it prevents agents from making hundreds of changes per hour, which would make the experiment uninterpretable.

**Solutions:**
- Explain *why* rate limiting exists: each config change needs time to affect user behavior before you can measure the result. Changing config every 5 minutes means you never observe the effect of any single change.
- Set `poll_interval` in `agent.run()` to match or exceed `updateIntervalMin`. If the interval is 60 minutes, poll every 60 minutes.
- Use the time between updates for observation and analysis, not just waiting. Have the agent log signals, compute trends, and prepare the next decision.

### Agent Crashes Overnight

**Symptom:** Agent runs fine during the lab session but crashes at 3 AM with a network error.

**Solutions:**
- Use `agent.run()` instead of a manual loop — it has built-in retry logic (re-raises after 5 consecutive errors).
- Run the agent on a server or cloud VM rather than a laptop that goes to sleep.
- For classroom settings, emphasize that agents do not need to run 24/7. Running during daytime hours when users are active is sufficient.
- For debugging, use the local sandbox (`python -m tendedloop_agent demo`) to test agent logic without affecting the live experiment.
- Add error handling: catch `httpx.HTTPError`, log it, wait, retry.

### Students Cannot Interpret Results

**Symptom:** Teams report "our agent won" based on raw metric values without statistical context.

**Solutions:**
- Require students to report effect sizes (Cohen's d), not just raw means.
- Teach the difference between statistical significance and practical significance.
- Point students to the experiment's built-in statistical analysis (Welch's t-test, Fisher's exact test, confidence intervals).
- Require reporting of sample sizes and confidence levels alongside any metric claim.

---

## 6. Academic Licensing and Contact

### Free Tier

The TendedLoop free tier includes:
- 1 building with up to 10 amenities and QR codes
- Full experiment functionality with Agent Mode
- Up to 5 variants per experiment
- All SDK features and API access

This is sufficient for most classroom lab setups with up to 4 teams competing.

### Academic Discounts

For larger deployments (multiple buildings, more QR codes, longer experiments, or campus-wide research programs), academic discounts are available:
- Multi-building experiments for cross-location studies
- Extended experiment durations for semester-long research
- Higher QR code limits for large-scale deployments
- Priority support during exam periods

### Contact

| Purpose | Contact |
|---------|---------|
| Academic partnerships and discounts | [research@tendedloop.com](mailto:research@tendedloop.com) |
| Technical support | [support@tendedloop.com](mailto:support@tendedloop.com) |
| Bug reports and feature requests | [GitHub Issues](https://github.com/osheryadgar/tendedloop-arena/issues) |

### Citing This Work

If you use TendedLoop Arena in your research or course materials, please cite:

```bibtex
@software{tendedloop_arena,
  title={TendedLoop Arena: Multi-Agent Gamification Research Platform},
  author={Yadgar, Osher},
  year={2026},
  url={https://github.com/osheryadgar/tendedloop-arena},
  license={MIT}
}
```

---

## Related Resources

- [Classroom & Lab Guide](classroom-guide.md) — Step-by-step experiment setup, token distribution, and monitoring
- [Workshop (8 sessions)](../workshop/README.md) — The hands-on curriculum students follow
- [Academic Program](../academic/README.md) — Full 14-week syllabi for Course A (Multi-Agent Systems) and Course B (Computational Gamification)
- [Strategies Guide](strategies.md) — Algorithmic strategies for building effective agents
- [FAQ](faq.md) — Common questions and troubleshooting
