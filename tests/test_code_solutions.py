from cognitia.learning.code_solutions import CodeSolutionLearner


SOURCE = '''
def total_by_customer(purchases):
    totals = {}
    for purchase in purchases:
        customer = purchase["customer"]
        totals[customer] = totals.get(customer, 0) + purchase["amount"]
    return totals
'''


def test_code_solution_learner_derives_logic_from_source():
    experience = CodeSolutionLearner().experience(
        problem="sum purchase amounts by customer",
        source=SOURCE,
        outcome_kind="positive",
        outcome_description="tests passed on held-out purchase data",
    )

    assert experience.context["solution_implementation"] == "group_by_reduce"
    assert experience.context["problem_signature"] == ("group_by_reduce",)
    assert experience.context["solution_logic"] == (
        "partition records by key",
        "combine values within each key",
        "emit one result per key",
    )
    assert experience.observation["algorithm_family"] == "group_by_reduce"
