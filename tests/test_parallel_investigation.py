from cognitia.environment import EnvironmentObservation
from cognitia.parallel_investigation import InvestigationTask, ParallelInvestigator


class Source:
    def __init__(self, name):
        self.name = name

    def observe(self, objective, limit):
        return (EnvironmentObservation(f"{self.name}-1", self.name, objective, 0.8, ()),)


def test_investigates_multiple_environments_and_preserves_order():
    investigator = ParallelInvestigator({"web": Source("web"), "local": Source("local")}, max_workers=2)
    results = investigator.investigate((
        InvestigationTask("a", "find evidence A", "web"),
        InvestigationTask("b", "measure evidence B", "local"),
    ))
    assert [item.task_id for item in results] == ["a", "b"]
    assert {item.environment for item in results} == {"web", "local"}
    assert len(investigator.merge(results)) == 2


def test_missing_environment_is_explicit_capability_failure():
    result = ParallelInvestigator({"web": Source("web")}).investigate(
        (InvestigationTask("a", "objective", "sensor"),)
    )[0]
    assert result.error == "environment_unavailable"
    assert result.observations == ()
