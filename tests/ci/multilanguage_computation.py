"""Real cross-language computation benchmark; no answer is seeded into the target.

Each implementation expresses the same abstract operation differently. Cognitia
must infer the common family, then execute that family against a fresh dataset.
"""
from cognitia.learning.code_solutions import CodeSolutionLearner
from cognitia.learning.computational_executor import execute_family
from cognitia.learning.multilanguage import MultiLanguageCodeInterpreter

interpreter = MultiLanguageCodeInterpreter()
learner = CodeSolutionLearner()

python_source = '''
def totals(rows):
    out = {}
    for row in rows:
        key = row["customer"]
        out[key] = out.get(key, 0) + row["amount"]
    return out
'''
js_source = '''
function totals(rows) {
  const out = {};
  for (const row of rows) {
    const key = row.customer;
    out[key] = (out[key] ?? 0) + row.amount;
  }
  return out;
}
'''
sql_source = '''
SELECT customer, SUM(amount) AS total
FROM purchases
GROUP BY customer;
'''

representations = [
    interpreter.interpret(python_source, language="python"),
    interpreter.interpret(js_source, language="javascript"),
    interpreter.interpret(sql_source, language="sql"),
]
families = {item.algorithm_family for item in representations}
assert families == {"group_by_reduce"}, representations

# The target is a new problem; neither its answer nor its implementation is supplied.
target_problem = "For each account, calculate the total amount across its transactions."
signature = learner.infer_problem_signature(target_problem)
assert signature == ("group_by_reduce",), signature

fresh_records = [
    {"account": "A", "value": 7},
    {"account": "B", "value": 11},
    {"account": "A", "value": 5},
    {"account": "C", "value": 3},
    {"account": "B", "value": 2},
]
result = execute_family(
    signature[0], fresh_records, key_field="account", value_field="value"
)
assert result == {"A": 12, "B": 13, "C": 3}, result
print("MULTILANGUAGE_COMPUTATION_TRANSFER_SUCCESS")
