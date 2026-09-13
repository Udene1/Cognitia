from cognitia.environment import EnvironmentObservation
from cognitia.parallel_investigation import InvestigationTask, ParallelInvestigator


class Source:
    def __init__(self, name):
        self.name = name

    def observe(self, objective, limit):
        return (EnvironmentObservation(self.name + "-obs", self.name, objective, 0.9, ()),)


investigator = ParallelInvestigator({"web": Source("web"), "simulation": Source("simulation"), "local": Source("local")}, max_workers=3)
results = investigator.investigate((
    InvestigationTask("web-check", "find external evidence", "web"),
    InvestigationTask("simulation-check", "simulate competing model", "simulation"),
    InvestigationTask("local-check", "inspect local evidence", "local"),
))
assert all(result.error is None for result in results)
assert len(investigator.merge(results)) == 3
print("PARALLEL_MULTI_ENVIRONMENT_SUCCESS")
print("ENVIRONMENTS:", [result.environment for result in results])
