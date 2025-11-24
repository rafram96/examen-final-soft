import pytest

from app.grade_calculator import Evaluation, EvaluationRegistry, ValidationError


def test_registry_should_reject_more_than_ten_evaluations() -> None:
    registry = EvaluationRegistry()
    for index in range(10):
        registry.add(Evaluation(name=f"Eval {index}", score=10, weight=10))

    with pytest.raises(ValidationError):
        registry.add(Evaluation(name="Eval extra", score=15, weight=5))


def test_evaluation_dict_representation() -> None:
    evaluation = Evaluation(name="Proyecto", score=18.5, weight=40)
    assert evaluation.__dict__ == {
        "name": "Proyecto",
        "score": 18.5,
        "weight": 40,
    }
