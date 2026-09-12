from cognitia.learning.code_representation import PythonCodeInterpreter


GROUP_BY_CODE = '''
def total_by_customer(purchases):
    totals = {}
    for purchase in purchases:
        customer = purchase["customer"]
        totals[customer] = totals.get(customer, 0) + purchase["amount"]
    return totals
'''


def test_interpreter_extracts_group_by_reduce_structure_without_labels():
    representation = PythonCodeInterpreter().interpret(GROUP_BY_CODE)

    assert representation.algorithm_family == "group_by_reduce"
    assert representation.confidence > 0.9
    assert "iterate records" in representation.operations
    assert "maintain keyed accumulator" in representation.operations
    assert representation.data_flow[-3:] == (
        "partition records by key",
        "combine values within each key",
        "emit one result per key",
    )
    assert representation.epistemic_status == "inference"


def test_interpreter_does_not_claim_unknown_code_is_known_algorithm():
    representation = PythonCodeInterpreter().interpret("""
def do_thing(value):
    return value + 1
""")

    assert representation.algorithm_family == "unknown"
    assert representation.confidence < 0.5
