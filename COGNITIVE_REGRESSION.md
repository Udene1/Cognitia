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

## Epistemic boundary

Passing a benchmark establishes only that the candidate performed better on that defined benchmark. It does not establish universal cognitive improvement.

Promotion therefore records:

- the baseline build
- the candidate build
- the target benchmark and improvement
- every protected benchmark
- observed regressions
- allowed tolerance
- the promotion decision and reason

This creates the foundation for reproducible cognitive builds and later build manifests.
