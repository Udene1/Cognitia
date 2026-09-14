from cognitia.discovery_prediction import Prediction
from cognitia.environment import EnvironmentObservation
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge_navigation import KnowledgeGuidedRouter, ResearchRouteMemory, RouteExperience
from cognitia.parallel_investigation import InvestigationTask


knowledge = (
    KnowledgeItem(
        subject="latency anomaly",
        predicate="best evidence environment",
        value="controlled experiment",
        source=KnowledgeSource("validated_discovery", "experiment-routing", 1.0),
        scope="validated_discovery",
    ),
    KnowledgeItem(
        subject="latency anomaly",
        predicate="model environment",
        value="simulation",
        source=KnowledgeSource("validated_discovery", "simulation-routing", 0.9),
        scope="validated_discovery",
    ),
)

memory = ResearchRouteMemory([
    RouteExperience("latency anomaly caused by cache", "experiment", 1.0, 4),
    RouteExperience("latency anomaly caused by cache", "web", 0.1, 4),
])

router = KnowledgeGuidedRouter(knowledge, memory=memory)
tasks = (
    InvestigationTask("web", "search reported causes", "web"),
    InvestigationTask("simulation", "test model consequences", "simulation"),
    InvestigationTask("experiment", "run controlled isolation test", "experiment"),
)

ranked = router.rank("latency anomaly caused by cache", tasks)
print([(item.environment, round(item.score, 3), item.rationale) for item in ranked])
assert ranked[0].environment == "experiment"
assert ranked[0].learned > ranked[1].learned

ordered = router.order("latency anomaly caused by cache", tasks)
assert ordered[0].environment == "experiment"
assert set(task.environment for task in ordered) == {"web", "simulation", "experiment"}

# Routing is allowed to become more efficient without becoming a truth gate.
# The router still returns every candidate environment, including unseen routes.
exploration = router.rank("unknown cryptographic failure", tasks)
assert len(exploration) == 3
assert all(item.score >= 0 for item in exploration)

# Successful outcomes update the route prior; they do not mutate knowledge.
memory.record(RouteExperience("unknown cryptographic failure", "simulation", 0.8, 1))
assert memory.score("unknown cryptographic failure", "simulation") > 0

path = ".ci/route-memory.json"
memory.save(path)
recovered = ResearchRouteMemory.load(path)
assert recovered.score("unknown cryptographic failure", "simulation") > 0

print("KNOWLEDGE_GUIDED_ROUTING_CAPABILITY_PROOF_SUCCESS")
