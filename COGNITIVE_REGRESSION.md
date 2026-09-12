# Cognitive Regression

Cognitia must not promote a new cognitive build solely because it improves the capability that motivated the change.

A candidate build must be evaluated against the same benchmark used for the target capability and against protected benchmarks for capabilities that already worked.

## Promotion rule

```text
candidate improves target capability
        AND
protected capabilities remain within regression tolerance
        ↓
eligible for promotion
```

A regression tolerance of zero is the default. A non-zero tolerance must be explicit and justified by the benchmark policy.

## Regression does not mean discard

A regression is a **promotion blocker, not a deletion command**.

When a candidate improves a valuable new capability but damages an existing capability, Cognitia must retain the candidate as a candidate build and put it into a balancing state:

```text
new capability improves
        ↓
protected capability regresses
        ↓
DO NOT MERGE into active cognitive build
        ↓
RETAIN candidate
        ↓
repair / balance / selectively integrate
        ↓
benchmark again
        ↓
only then promote
```

This is important because the new capability may itself be valuable. Throwing it away would destroy information about what changed and would force Cognitia to rediscover the capability later.

The candidate therefore has two separate states:

- **Capability state:** what the candidate can do.
- **Promotion state:** whether those capabilities are safe to merge into the active cognitive build.

A candidate can be highly capable and still not be promotion-ready.

## Balancing is multi-objective

Cognitia should eventually search for a balanced candidate rather than optimizing one benchmark independently. A candidate should be evaluated across the capability portfolio and, where useful, against Pareto-style trade-offs.

The objective is not:

> maximize the newest capability at any cost.

It is:

> improve Cognitia's useful capability frontier without silently destroying capabilities it already possessed.

Selective integration may eventually allow a new capability to be retained while only the harmful change is removed, provided the resulting build is independently benchmarked.

## Epistemic boundary

Passing a benchmark establishes only that the candidate performed better on that defined benchmark. It does not establish universal cognitive improvement.

Promotion therefore records:

- the baseline build
- the candidate build
- the target benchmark and improvement
- every protected benchmark
- observed regressions
- allowed tolerance
- candidate disposition
- the promotion decision and reason

This creates the foundation for reproducible cognitive builds and later build manifests.
