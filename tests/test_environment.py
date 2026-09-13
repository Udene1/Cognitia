from cognitia.environment import EnvironmentObservation, NullEnvironmentSource


def test_environment_observation_validates_reliability():
    observation = EnvironmentObservation("o1", "test", "fact", 0.8)
    assert observation.reliability == 0.8


def test_null_environment_is_explicitly_empty():
    assert NullEnvironmentSource().observe("anything") == ()
