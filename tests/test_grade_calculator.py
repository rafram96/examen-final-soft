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
        attendance_policy=AttendancePolicy(percentage=100),
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
        attendance_policy=AttendancePolicy(percentage=70, min_required=80),
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
        attendance_policy=AttendancePolicy(percentage=100),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=True, extra_points_value=5),
    )

    assert result.extra_points_applied == 5
    assert result.final_grade == 20


def test_should_return_zero_average_when_no_evaluations() -> None:
    calculator = build_calculator()

    result = calculator.calculate(
        student_id="UTEC004",
        evaluations=[],
        attendance_policy=AttendancePolicy(percentage=100),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=False),
    )

    assert result.weighted_average == 0
    assert result.final_grade == 0


def test_should_fail_when_evaluation_weight_invalid() -> None:
    with pytest.raises(ValidationError):
        Evaluation(name="Invalid", score=10, weight=0)


def test_should_fail_when_attendance_is_negative() -> None:
    with pytest.raises(ValidationError):
        AttendancePolicy(percentage=-10)


def test_should_fail_when_attendance_is_over_100() -> None:
    with pytest.raises(ValidationError):
        AttendancePolicy(percentage=101)


def test_should_fail_when_min_required_attendance_is_invalid() -> None:
    with pytest.raises(ValidationError):
        AttendancePolicy(percentage=90, min_required=-1)
    
    with pytest.raises(ValidationError):
        AttendancePolicy(percentage=90, min_required=101)


def test_should_calculate_grade_with_exact_min_attendance() -> None:
    calculator = build_calculator()
    evaluations = [Evaluation(name="Exam", score=15, weight=100)]

    result = calculator.calculate(
        student_id="UTEC005",
        evaluations=evaluations,
        attendance_policy=AttendancePolicy(percentage=80, min_required=80),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=False),
    )

    assert result.attendance_penalty_applied is False
    assert result.final_grade == 15


def test_should_calculate_grade_with_below_min_attendance() -> None:
    calculator = build_calculator()
    evaluations = [Evaluation(name="Exam", score=15, weight=100)]

    result = calculator.calculate(
        student_id="UTEC006",
        evaluations=evaluations,
        attendance_policy=AttendancePolicy(percentage=79.9, min_required=80),
        extra_points_policy=ExtraPointsPolicy(all_years_teachers=False),
    )

    assert result.attendance_penalty_applied is True
    assert result.final_grade == 0


def test_should_fail_when_evaluation_score_invalid() -> None:
    with pytest.raises(ValidationError):
        Evaluation(name="Invalid", score=-1, weight=10)
    
    with pytest.raises(ValidationError):
        Evaluation(name="Invalid", score=21, weight=10)


def test_should_fail_when_evaluation_name_empty() -> None:
    with pytest.raises(ValidationError):
        Evaluation(name="", score=10, weight=10)
    
    with pytest.raises(ValidationError):
        Evaluation(name="   ", score=10, weight=10)


def test_should_fail_when_extra_points_negative() -> None:
    with pytest.raises(ValidationError):
        ExtraPointsPolicy(all_years_teachers=True, extra_points_value=-1)
