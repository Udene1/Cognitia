"""Integrated research batch: search, investigate, validate, persist, recover."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from cognitia.discovery_artifact import DiscoveryArtifact, DurableDiscoveryArtifacts
from cognitia.discovery_experiments import DiscriminatingExperimentSelector
from cognitia.discovery_prediction import Prediction
from cognitia.discovery_search import DiscoverySearchEngine, SearchBudget
from cognitia.discovery_structure import ModelElement, StructuralModel
from cognitia.durable import SQLiteCognitiveJournal
from cognitia.environment import EnvironmentObservation
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore
from cognitia.web_evidence import WebEvidenceEvaluator

model = StructuralModel(id="engine", elements=(ModelElement("load", "variable", "load"), ModelElement("temp", "variable", "temperature")))
search = DiscoverySearchEngine().search(model, budget=SearchBudget(max_candidates=8, max_depth=2))
assert search and any(item.depth == 2 for item in search)

predictions = (
    Prediction("p1", "h1", "load=high", "temperature rises", "temperature stable"),
    Prediction("p2", "h2", "load=high", "temperature stable", "temperature rises"),
)
experiment = DiscriminatingExperimentSelector().select(predictions, priors=(0.8, 0.2))
assert experiment and 0 < experiment.expected_information_gain < 1

now = datetime.now(timezone.utc)
evidence = WebEvidenceEvaluator().assess((
    EnvironmentObservation("w1", "provider:test", "measurement", 0.95, (("expires_at", (now + timedelta(days=1)).isoformat()),)),
    EnvironmentObservation("w2", "provider:test", "measurement", 0.95, ()),
), now=now)
assert evidence[0].accepted and evidence[1].reason == "duplicate"

with tempfile.TemporaryDirectory() as root:
    db = Path(root) / "cognition.db"
    item = KnowledgeItem("temperature", "responds_to", "high_load", KnowledgeSource("experiment", "exp-1"), id="knowledge-1")
    with SQLiteCognitiveJournal(db) as journal:
        store = ValidatedKnowledgeStore(journal)
        store.promote(item, (KnowledgeTest("test-1", item.id, True, 1.0),))
        DurableDiscoveryArtifacts(journal).record(DiscoveryArtifact(id="d-1", title="engine anomaly", observation_ids=("o-1",), experiment_id=experiment.id))
    with SQLiteCognitiveJournal(db) as journal:
        assert ValidatedKnowledgeStore(journal).recover()[0]["id"] == item.id
        assert DurableDiscoveryArtifacts(journal).all()[0]["id"] == "d-1"

print("MULTI_STEP_SEARCH_SUCCESS")
print("DISCRIMINATING_EXPERIMENT_IG:", experiment.expected_information_gain)
print("WEB_EVIDENCE_GATE_SUCCESS")
print("VALIDATED_KNOWLEDGE_RESTART_SUCCESS")
print("DISCOVERY_ARTIFACT_RESTART_SUCCESS")
print("LLM_DEPENDENCY: NONE")
