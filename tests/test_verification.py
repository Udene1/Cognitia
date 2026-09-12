from cognitia.verification import VerificationOutcome, VerificationPlan, VerificationStep, execute_plan


def test_all_verified_steps_verify_claim():
    plan = VerificationPlan("candidate works", (VerificationStep("v1", "run invariant test", True),), 0.8)
    result = execute_plan(plan, lambda step: VerificationOutcome.VERIFIED)
    assert result.outcome is VerificationOutcome.VERIFIED


def test_failed_step_blocks_verification():
    plan = VerificationPlan("candidate works", (VerificationStep("v1", "run test", True), VerificationStep("v2", "run adversarial test", True)), 0.9)
    result = execute_plan(plan, lambda step: VerificationOutcome.FAILED if step.id == "v2" else VerificationOutcome.VERIFIED)
    assert result.outcome is VerificationOutcome.FAILED
