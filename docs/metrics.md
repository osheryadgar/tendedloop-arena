# Metrics Reference

Arena computes six metrics per variant, updated with a 5-minute server-side cache. Each metric includes the raw value, standard deviation, sample size, and a confidence rating.

## Available Metrics

### SCAN_FREQUENCY

**What:** Average number of primary actions per user per day.

**Type:** Continuous (mean)

**Statistical test:** Welch's t-test (vs. control)

**Why it matters:** The most direct measure of user engagement. Higher frequency means users are actively participating in the feedback ecosystem.

**Levers:**
- `scanXp` — Direct reward per scan
- `firstScanOfDayXp` — Incentivize daily return
- `scanDailyCap` — Upper bound on countable scans

### XP_VELOCITY

**What:** Average XP earned per user per day.

**Type:** Continuous (mean)

**Statistical test:** Welch's t-test (vs. control)

**Why it matters:** Measures overall economy health. Too high = inflation. Too low = disengagement. Watch this alongside other metrics.

**Levers:** All XP-granting parameters affect this metric.

### RETENTION_RATE

**What:** Proportion of enrolled users who were active in the last 7 days.

**Type:** Proportion (0.0 to 1.0)

**Statistical test:** Fisher's exact test (vs. control)

**Why it matters:** The north star for any gamification system. Are users coming back?

**Levers:**
- `streakBonusPerDay` — Reward consistency
- `streakBonusCap` — Limit diminishing returns
- `firstScanOfDayXp` — Daily return incentive

### MISSION_COMPLETION

**What:** Ratio of completed missions to assigned missions.

**Type:** Proportion (0.0 to 1.0)

**Statistical test:** Fisher's exact test (vs. control)

**Why it matters:** Indicates whether your economy makes missions feel achievable and worthwhile.

**Levers:** Mission rewards are currently fixed, but scan/feedback XP affects how quickly users can complete scan-based missions.

### STREAK_LENGTH

**What:** Average current streak length (consecutive active days) per user.

**Type:** Continuous (snapshot)

**Statistical test:** Welch's t-test (vs. control)

**Why it matters:** Leading indicator for retention. Long streaks predict continued engagement.

**Levers:**
- `streakBonusPerDay` — Primary lever
- `streakBonusCap` — Prevents runaway streak rewards
- `firstScanOfDayXp` — Makes the daily scan feel rewarding

### FEEDBACK_QUALITY

**What:** Proportion of scans that include written feedback (comments, ratings, photos).

**Type:** Proportion (0.0 to 1.0)

**Statistical test:** Fisher's exact test (vs. control)

**Why it matters:** Distinguishes between engaged users and those just "farming XP" with empty scans.

**Levers:**
- `feedbackXp` — Reward feedback submissions
- `photoXp` — Specifically reward photo evidence
- `issueReportXp` — Reward detailed issue reports

## Confidence Levels

Each metric includes a confidence rating based on sample size:

| Confidence | Sample Size | Interpretation |
|------------|-------------|---------------|
| `high` | n >= 30 | Reliable for decision-making |
| `medium` | 10 <= n < 30 | Directionally useful, handle with care |
| `low` | n < 10 | Insufficient data — avoid acting on this |

**Best practice:** Your agent should check `confidence` before acting. Making changes based on low-confidence data introduces noise and wastes your rate-limited update slots.

```python
def decide(signals, config):
    freq = signals.metrics.get("SCAN_FREQUENCY")
    if not freq or freq.confidence == "low":
        return None  # Wait for more data
    # ... make decision ...
```

## Statistical Methods

### Welch's t-test (continuous metrics)

Used for SCAN_FREQUENCY, XP_VELOCITY, STREAK_LENGTH. Compares the mean of the treatment variant against the control variant, accounting for unequal variances and sample sizes.

Returns: mean difference, 95% CI, p-value, significance flag.

### Fisher's exact test (proportion metrics)

Used for RETENTION_RATE, MISSION_COMPLETION, FEEDBACK_QUALITY. Compares proportions between treatment and control using exact probability computation (no normal approximation).

Returns: odds ratio, 95% CI, p-value, significance flag.

### Cohen's d (effect size)

Computed for all metrics as a standardized measure of the difference between treatment and control. Interpretation:

| Cohen's d | Effect Size |
|-----------|------------|
| < 0.2 | Negligible |
| 0.2 - 0.5 | Small |
| 0.5 - 0.8 | Medium |
| > 0.8 | Large |

### Power Estimate

The platform estimates statistical power based on current sample sizes, observed variance, and effect size. This helps researchers and agents understand whether they have enough data to detect meaningful differences.
