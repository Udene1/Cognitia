from cognitia.learning.code_equivalence import CodeStructureComparator


IMPLEMENTATION_A = '''
def totals(rows):
    result = {}
    for row in rows:
        key = row["account"]
        result[key] = result.get(key, 0) + row["value"]
    return result
'''

IMPLEMENTATION_B = '''
def aggregate(entries):
    totals = {}
    for entry in entries:
        account = entry["owner"]
        amount = entry["price"]
        if account not in totals:
            totals[account] = 0
        totals[account] += amount
    return totals
'''

IMPLEMENTATION_C = '''
def declarative(records):
    keys = {record["customer"] for record in records}
    return {
        key: sum(record["cost"] for record in records if record["customer"] == key)
        for key in keys
    }
'''


def test_independently_written_grouped_aggregations_share_structure():
    match = CodeStructureComparator().compare(IMPLEMENTATION_A, IMPLEMENTATION_B)
    assert match.equivalent_family
    assert "iterate records" in match.shared_operations
    assert "iteration" in match.shared_control_flow
    assert match.confidence > 0.5


def test_different_syntax_with_same_reduction_structure_is_grouped():
    match = CodeStructureComparator().compare(IMPLEMENTATION_A, IMPLEMENTATION_C)
    assert match.equivalent_family
    assert match.confidence > 0.5


def test_different_computation_is_not_grouped_as_same_family():
    search = '''
def find(rows, target):
    for row in rows:
        if row["id"] == target:
            return row
    return None
'''
    match = CodeStructureComparator().compare(IMPLEMENTATION_A, search)
    assert not match.equivalent_family
