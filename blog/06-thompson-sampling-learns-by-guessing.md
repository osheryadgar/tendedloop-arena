# Thompson Sampling: The Algorithm That Learns by Guessing

Here is a counterintuitive claim: the best way to explore is randomly.

Not uniformly random — that would be equivalent to picking dishes blindfolded at the restaurant from the first post. I mean *strategically* random. Random in a way that automatically spends more time on promising options and less time on options you have already figured out.

Thompson Sampling does exactly this. It is one of the most effective bandit algorithms ever discovered. It has near-optimal theoretical guarantees. It consistently outperforms UCB1 in practice. And the core logic fits in six lines of Python.

Oh, and it was invented in 1933.

## Start With a Coin

Imagine I hand you a coin and ask: "What is the probability it lands heads?"

You do not know. It could be a fair coin (50/50) or it could be biased. So you flip it 10 times and get 7 heads.

What is the probability of heads? Your gut says "probably around 0.7." But you are not certain — 10 flips is not that many. If you had gotten 70 heads out of 100 flips, you would be much more confident about 0.7.

This "probably around 0.7, but I am not sure" feeling is exactly what a Beta distribution captures. It is a probability distribution *over probabilities* — a way of expressing your uncertainty about an unknown rate.

After 7 heads and 3 tails, your belief is described by Beta(8, 4). The "8" is 7 successes + 1 (the prior), and "4" is 3 failures + 1. The shape looks like a hill centered around 0.67, with tails stretching out to reflect your remaining uncertainty.

Here is what different Beta distributions look like:

```
Beta(1,1)         Beta(4,2)         Beta(21,6)        Beta(2,8)
"I know nothing"  "Probably good"   "Very confident"   "Probably bad"

  |  --------      |     /\          |        /\       |  /\
  | |        |     |    /  \         |       /  \      | /  \
  | |        |     |   /    \        |      /    \     |/    \
  | |        |     |  /      \       |     /      \    |      \
  | |        |     | /        \      |    /        \   |       \
  +-+--------+-    +------------    +---------------   +----------
  0          1     0           1    0             1    0          1
```

Beta(1,1) is flat — you have no idea whether the coin is biased. Beta(4,2) leans right — you think heads is more likely but you are not sure. Beta(21,6) is a sharp spike — you are very confident the heads rate is around 0.77. Beta(2,8) leans left — you think this coin mostly lands tails.

The wider the distribution, the more uncertain you are. The narrower it is, the more data you have.

## Every Arm Gets Its Own Coin

In the multi-armed bandit setup, each arm has its own unknown success rate. Maybe Arm 0 (Balanced economy config) produces a "good" outcome 60% of the time. Maybe Arm 1 (Scan-Heavy) produces one 75% of the time. You do not know these rates — you have to learn them.

Thompson Sampling maintains a separate Beta distribution for each arm. Initially, they all start at Beta(1,1) — complete ignorance. As you pull arms and observe outcomes, each arm's distribution gets updated:

- **Good outcome (success):** alpha goes up by 1. The distribution shifts right.
- **Bad outcome (failure):** beta goes up by 1. The distribution shifts left.

After a few rounds, each arm has its own shaped distribution reflecting what you have seen so far.

## The Algorithm in One Sentence

**Sample one random number from each arm's Beta distribution, then play the arm whose sample was highest.**

That is it. That is the entire algorithm. Let me walk through five rounds so you can see how it plays out.

### Round 1: Total Ignorance

All arms start at Beta(1,1). We sample from each:

```
Arm 0 (Balanced):    Beta(1,1) → sample = 0.42
Arm 1 (Scan-Heavy):  Beta(1,1) → sample = 0.87  ← highest
Arm 2 (Quality):     Beta(1,1) → sample = 0.31
Arm 3 (Streaks):     Beta(1,1) → sample = 0.65
```

We play Arm 1. Outcome: success (engagement improved).
Update Arm 1: Beta(1,1) becomes Beta(2,1).

### Round 2: Arm 1 Has a Slight Edge

```
Arm 0: Beta(1,1) → sample = 0.55
Arm 1: Beta(2,1) → sample = 0.73  ← highest (distribution leans right now)
Arm 2: Beta(1,1) → sample = 0.19
Arm 3: Beta(1,1) → sample = 0.44
```

Arm 1 wins again. Outcome: failure (engagement dropped).
Update Arm 1: Beta(2,1) becomes Beta(2,2).

### Round 3: Arm 1 is Back to Uncertain

```
Arm 0: Beta(1,1) → sample = 0.78  ← highest
Arm 1: Beta(2,2) → sample = 0.41  (one win, one loss — uncertain)
Arm 2: Beta(1,1) → sample = 0.62
Arm 3: Beta(1,1) → sample = 0.33
```

Arm 0 wins this time. Outcome: success.
Update Arm 0: Beta(1,1) becomes Beta(2,1).

### Round 4: Competition Heats Up

```
Arm 0: Beta(2,1) → sample = 0.82  ← highest
Arm 1: Beta(2,2) → sample = 0.55
Arm 2: Beta(1,1) → sample = 0.71
Arm 3: Beta(1,1) → sample = 0.29
```

Arm 0 again. Outcome: success.
Update Arm 0: Beta(2,1) becomes Beta(3,1).

### Round 5: Arm 0 Pulls Ahead

```
Arm 0: Beta(3,1) → sample = 0.91  ← highest (strong track record)
Arm 1: Beta(2,2) → sample = 0.38
Arm 2: Beta(1,1) → sample = 0.84  (untried arms can still sample high!)
Arm 3: Beta(1,1) → sample = 0.60
```

Arm 0 is dominating. But notice Arm 2 sampled 0.84 — it has never been tried, so its distribution is wide, which means it can sample anywhere. Eventually, it will sample highest and get a chance to prove itself.

This is the magic of Thompson Sampling. Good arms get played more because their distributions are peaked at high values. But uncertain arms occasionally sample high and get explored. No explicit exploration term, no fixed schedule, no parameter to tune. Just randomness, doing exactly the right thing.

## Why Randomness is a Feature

UCB1 is deterministic. Given the same history of rewards, it always picks the same arm. This makes it predictable and easy to debug. But it has a subtle weakness: it can get stuck spending too many pulls on arms that are *close* in quality, because the confidence bounds stay wide when arms look similar.

Thompson Sampling is stochastic. Even with the same history, it might pick a different arm because the samples are random. This sounds like a bug, but it is actually a feature for two reasons.

First, the randomness naturally breaks ties. When two arms look similar, Thompson Sampling flips between them roughly in proportion to how likely each is to be the best. UCB1, by contrast, has to keep pulling both to shrink their confidence intervals, which can be wasteful.

Second, stochastic selection makes your agent harder to exploit in competitive settings. Remember the poker post — Pluribus deliberately randomizes its play to prevent opponents from predicting its strategy. Thompson Sampling gives your Arena agent the same property for free.

## The 90-Year Nap

Here is my favorite part of the Thompson Sampling story.

William R. Thompson published this algorithm in 1933, in a paper about clinical trials. He proposed: for each treatment, maintain a probability distribution over its effectiveness. Sample from each distribution, give the patient the treatment whose sample was highest. Update based on the outcome.

Mathematically, it was elegant. Practically, it made intuitive sense. And then... nothing happened.

For nearly 70 years, the statistics and operations research communities largely ignored Thompson Sampling. Why? Because they could not *prove* it worked. The standard approach in bandit theory was to derive regret bounds — mathematical guarantees on worst-case performance. UCB1 got its proof in 2002 (Auer, Cesa-Bianchi, Fischer). Thompson Sampling did not get comparable proofs until 2012 (Agrawal and Goyal) and 2013 (Kaufmann, Korda, Munos).

For decades, mathematicians looked at Thompson Sampling and said "it seems to work, but we cannot prove it, so we cannot recommend it." Meanwhile, UCB1 had clean proofs, so it dominated the literature. Only when the proofs finally arrived did the community accept what practitioners had known all along: Thompson Sampling is not just good — it is often *better* than UCB1.

The lesson: sometimes an algorithm is so simple that the field assumes it cannot be sophisticated enough to work. Thompson Sampling's six-line core does not look like a breakthrough. But it is.

## The Code

Here is Thompson Sampling in Python, adapted from the Arena example:

```python
class ThompsonSampler:
    def __init__(self, n_arms):
        self.alphas = [1.0] * n_arms   # successes + 1
        self.betas  = [1.0] * n_arms   # failures + 1

    def select_arm(self):
        samples = [random.betavariate(a, b)
                    for a, b in zip(self.alphas, self.betas)]
        return max(range(len(samples)), key=lambda i: samples[i])

    def update(self, arm, success):
        if success:
            self.alphas[arm] += 1
        else:
            self.betas[arm] += 1
```

That is the entire algorithm. The `select_arm` method is two lines: sample from each arm's Beta distribution, pick the highest. The `update` method is three lines: increment alpha on success, beta on failure.

In the Arena context, "success" means the composite engagement metric improved after deploying that arm's economy config. "Failure" means it did not. The threshold is simple — did things get better or not?

## Thompson Sampling vs. UCB1: When to Use Which

Both algorithms achieve logarithmic regret. Both are well-studied and well-understood. Here is how to choose:

| Factor | Thompson Sampling | UCB1 |
|--------|-------------------|------|
| Convergence speed | Often faster | Slightly slower |
| Deterministic? | No (stochastic) | Yes |
| Parameters to tune | None (prior is usually Beta(1,1)) | c (exploration constant) |
| Debuggability | Harder (random choices) | Easier (same input = same output) |
| Similar arms | Converges faster | Explores more (can be wasteful) |
| Competitive settings | Better (unpredictable) | Worse (predictable) |
| Theoretical guarantees | Proven optimal (since 2012) | Proven optimal (since 2002) |
| Implementation complexity | Very low | Low |

My recommendation: start with Thompson Sampling. It requires no parameter tuning (UCB1's `c` matters and picking the wrong value can hurt), it naturally handles the competitive dynamics of multi-agent experiments, and it tends to find the best arm faster.

Use UCB1 when you need deterministic, reproducible decisions — for example, if you need to explain to a stakeholder exactly why the agent picked a specific configuration on a specific round.

## The Binary Reward Question

One thing you might have noticed: Thompson Sampling (in its Beta-Bernoulli form) needs binary outcomes — success or failure. But Arena gives you continuous metrics like scan frequency (3.2 scans/day) and retention rate (0.74).

The simplest conversion: did the composite score improve compared to last round? If yes, success. If no, failure.

```python
improved = current_composite > previous_composite
sampler.update(arm, reward=improved)
```

This throws away information (a huge improvement and a tiny improvement both count as "success"), but it works surprisingly well. The Beta distribution accumulates evidence across many rounds, so the lost granularity averages out.

More sophisticated approaches exist — Gaussian Thompson Sampling uses Normal distributions to handle continuous rewards directly, and quantile thresholding defines success as "top 25% of all observed rewards." But for Arena, the simple binary approach is a strong default.

## What is Next

So far, we have been choosing between discrete arms — fixed economy configurations that the agent selects from a menu. Arm 0 or Arm 1 or Arm 2. Each arm is a complete package, predefined by you.

But what if you do not want to predefine the menu? What if you want your agent to discover that the optimal scanXp is exactly 13.7, not the 12 or 18 you happened to put in your arm list? What if you want to tune continuous parameters, sliding them up and down to find the precise sweet spot?

That is a fundamentally different problem. You leave the world of multi-armed bandits and enter the world of Bayesian optimization and LLM-powered agents — agents that can reason about the parameter space, propose new configurations they have never seen before, and navigate continuous tradeoffs.

The bandit algorithms gave your agent a brain for choosing between options. The next step gives it imagination.
