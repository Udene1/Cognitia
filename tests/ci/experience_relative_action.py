from __future__ import annotations
import json
from pathlib import Path
from cognitia.experience import CognitiveState, EpistemicOutcome, Experience, ExperienceLedger, ExpectedConsequence, ObservedConsequence
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner

TRAIN = "The database outage caused the payment queue to stall. The database outage reduced worker throughput."
HELD_OUT = "The mirror coating change caused the telescope image to degrade. The mirror coating change reduced optical throughput."

def make_experience(outcome, action_text):
    description = {EpistemicOutcome.CONFIRMED: "The causal structure explained the observed outcome.", EpistemicOutcome.REFUTED: "The causal structure did not explain the observed outcome."}[outcome]
    return Experience(experience_id=f"relative-{outcome.value}", prior_state=CognitiveState(problem=TRAIN), action=action_text, rationale="selected from generated candidate actions", expected=ExpectedConsequence("The causal structure should explain the observed outcome."), observed=ObservedConsequence(description, outcome), state_update=CognitiveState(problem=TRAIN, evidence_ids=("training-result",)), provenance=("experience-relative-action",))

def snapshot(selector, actions, ledger):
    d = selector.select(HELD_OUT, actions, ledger)
    return {"selected": d.selected.action.query.objective, "candidates": [{"objective": x.action.query.objective, "priority": x.action.priority, "score": x.score, "relevant_ids": list(x.relevant_experience_ids), "rationale": x.rationale} for x in d.candidates]}

def run():
    selector = ExperienceAwareActionSelector()
    actions = ResearchSearchPlanner().plan(HELD_OUT, max_actions=4).actions
    if len(actions) < 2: raise AssertionError("experiment requires at least two competing actions")
    experienced_action = actions[0].query.objective
    conditions = {
        "empty": snapshot(selector, actions, ExperienceLedger()),
        "confirmed": snapshot(selector, actions, ExperienceLedger((make_experience(EpistemicOutcome.CONFIRMED, experienced_action),))),
        "refuted": snapshot(selector, actions, ExperienceLedger((make_experience(EpistemicOutcome.REFUTED, experienced_action),))),
    }
    orders = {k: [x["objective"] for x in v["candidates"]] for k,v in conditions.items()}
    result = {"question": "Can transferred experience change the relative value of competing evidence-seeking actions?", "protocol": "Hold problem and generated candidates fixed; vary only empty/confirmed/refuted experience. No expected winning action is supplied.", "problem": HELD_OUT, "candidate_count": len(actions), "experienced_action": experienced_action, "researcher_expected_action": None, "researcher_hypothesis_ids": (), "conditions": conditions, "observations": {"confirmed_changes_relative_order": orders["confirmed"] != orders["empty"], "refuted_changes_relative_order": orders["refuted"] != orders["empty"], "confirmed_changes_action": conditions["confirmed"]["selected"] != conditions["empty"]["selected"], "refuted_changes_action": conditions["refuted"]["selected"] != conditions["empty"]["selected"]}, "interpretation_boundary": "This tests the existing experience-to-action bridge without adding a cognitive abstraction or establishing semantic understanding."}
    p = Path(".ci/experience-relative-action.json"); p.parent.mkdir(exist_ok=True); p.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"); print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__": run()
