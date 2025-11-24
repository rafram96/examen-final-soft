import pytest

from app.grade_calculator import (
    AttendancePolicy,
    Evaluation,
    ExtraPointsPolicy,
    GradeCalculator,
    ValidationError,
)


def build_calculator() -> GradeCalculator:
    return GradeCalculator()


def test_should_compute_weighted_average() -> None:
    calculator = build_calculator()
    evaluations = [
        Evaluation(name="Parcial", score=15, weight=40),
        Evaluation(name="Proyecto", score=18, weight=60),
    ]

    result = calculator.calculate(
        student_id="UTEC001",
        evaluations=evaluations,
        attendance_policy=AttendancePolicy(has_reached_minimum=True),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=False),
    )

    assert result.weighted_average == pytest.approx(16.8)
    assert result.final_grade == pytest.approx(16.8)


def test_should_drop_grade_when_attendance_missing() -> None:
    calculator = build_calculator()
    evaluations = [Evaluation(name="Final", score=19, weight=100)]

    result = calculator.calculate(
        student_id="UTEC002",
        evaluations=evaluations,
        attendance_policy=AttendancePolicy(has_reached_minimum=False),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=True),
    )

    assert result.attendance_penalty_applied is True
    assert result.final_grade == 0
    assert result.extra_points_applied == 0


def test_should_cap_extra_points_at_max_grade() -> None:
    calculator = build_calculator()
    evaluations = [Evaluation(name="Unico", score=20, weight=100)]

    result = calculator.calculate(
        student_id="UTEC003",
        evaluations=evaluations,
        attendance_policy=AttendancePolicy(has_reached_minimum=True),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=True, extra_points_value=5),
    )

    assert result.extra_points_applied == 5
    assert result.final_grade == 20


def test_should_return_zero_average_when_no_evaluations() -> None:
    calculator = build_calculator()

    result = calculator.calculate(
        student_id="UTEC004",
        evaluations=[],
        attendance_policy=AttendancePolicy(has_reached_minimum=True),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=False),
    )

    assert result.weighted_average == 0
    assert result.final_grade == 0


def test_should_fail_when_evaluation_weight_invalid() -> None:
    with pytest.raises(ValidationError):
        Evaluation(name="Invalid", score=10, weight=0)
