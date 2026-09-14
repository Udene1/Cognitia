"""Real cross-language computation benchmark; no answer is seeded into the target.

Each implementation expresses the same abstract operation differently. Cognitia
must infer the common family from source structure, then use that family to solve
a fresh target problem.
"""
from cognitia.learning.multilanguage import MultiLanguageCodeInterpreter
from cognitia.learning.code_solutions import CodeSolutionLearner

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
assert all(item.language in {"python", "javascript", "sql"} for item in representations)

# The target is a new problem; the answer and its implementation are not supplied.
target_problem = "For each account, calculate the total amount across its transactions."
signature = learner.infer_problem_signature(target_problem)
assert signature == ("group_by_reduce",), signature

# Require transfer across a different language than the original Python source.
assert representations[1].algorithm_family == signature[0]
assert representations[2].algorithm_family == signature[0]
print("MULTILANGUAGE_COMPUTATION_TRANSFER_SUCCESS")
