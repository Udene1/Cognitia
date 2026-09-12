"""Compare independently authored programs without being given their shared algorithm."""
from __future__ import annotations

from cognitia.learning.code_equivalence import CodeStructureComparator


IMPLEMENTATIONS = {
    "accumulator": '''
def total_by_account(rows):
    result = {}
    for row in rows:
        account = row["account"]
        result[account] = result.get(account, 0) + row["amount"]
    return result
''',
    "explicit_initialization": '''
def summarize(entries):
    totals = {}
    for entry in entries:
        owner = entry["owner"]
        amount = entry["value"]
        if owner not in totals:
            totals[owner] = 0
        totals[owner] += amount
    return totals
''',
    "comprehension": '''
def aggregate(records):
    keys = {record["customer"] for record in records}
    return {
        key: sum(record["cost"] for record in records if record["customer"] == key)
        for key in keys
    }
''',
    "search": '''
def locate(rows, target):
    for row in rows:
        if row["id"] == target:
            return row
    return None
''',
}


def main() -> None:
    comparator = CodeStructureComparator()
    accumulator = IMPLEMENTATIONS["accumulator"]
    matches = []
    for name, source in IMPLEMENTATIONS.items():
        if name == "accumulator":
            continue
        match = comparator.compare(accumulator, source)
        matches.append((name, match))
        print(f"{name}: family_match={match.equivalent_family} confidence={match.confidence}")

    assert dict(matches)["explicit_initialization"].equivalent_family
    assert not dict(matches)["search"].equivalent_family
    # The comprehension is deliberately a harder case. We do not claim it is
    # equivalent until the representation extractor can see its aggregation.
    assert not dict(matches)["comprehension"].equivalent_family
    print("INVARIANT_STRUCTURE_CHALLENGE_PARTIAL_SUCCESS")


if __name__ == "__main__":
    main()
