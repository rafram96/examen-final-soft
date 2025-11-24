# Módulo de dominio para el cálculo de notas finales

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

# Constantes del sistema
MAX_EVALUATIONS = 10
MIN_SCORE = 0.0
MAX_SCORE = 20.0
MAX_FINAL_SCORE = 20.0
EXTRA_POINTS_VALUE = 1.0


class ValidationError(ValueError):
    # Error de validación del dominio
    pass


@dataclass(frozen=True)
class Evaluation:
    # Representa una evaluación con nota y peso relativo
    name: str
    score: float
    weight: float

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("El nombre de la evaluación no puede estar vacío.")
        if not (MIN_SCORE <= self.score <= MAX_SCORE):
            raise ValidationError(
                f"La nota debe estar entre {MIN_SCORE} y {MAX_SCORE}.")
        if self.weight <= 0:
            raise ValidationError("El peso debe ser mayor que 0.")


@dataclass
class EvaluationRegistry:
    # Registra las evaluaciones de un estudiante con límite de 10
    evaluations: List[Evaluation] = field(default_factory=list)

    def add(self, evaluation: Evaluation) -> None:
        if len(self.evaluations) >= MAX_EVALUATIONS:
            raise ValidationError(
                f"Solo se permiten {MAX_EVALUATIONS} evaluaciones por estudiante.")
        self.evaluations.append(evaluation)

    def extend(self, evaluations: Iterable[Evaluation]) -> None:
        for evaluation in evaluations:
            self.add(evaluation)

    def __len__(self) -> int:
        return len(self.evaluations)

    def total_weight(self) -> float:
        return sum(e.weight for e in self.evaluations)


@dataclass(frozen=True)
class AttendancePolicy:
    # Política de asistencia mínima
    has_reached_minimum: bool


@dataclass(frozen=True)
class ExtraPointsPolicy:
    # Política de puntos extra según acuerdo de docentes
    all_years_teachers: bool
    extra_points_value: float = EXTRA_POINTS_VALUE

    def __post_init__(self) -> None:
        if self.extra_points_value < 0:
            raise ValidationError("Los puntos extra no pueden ser negativos.")

    def resolve_points(self) -> float:
        return self.extra_points_value if self.all_years_teachers else 0.0


@dataclass(frozen=True)
class GradeCalculationResult:
    # Resultado del cálculo de nota final con detalles
    student_id: str
    evaluations: Sequence[Evaluation]
    weighted_average: float
    attendance_penalty_applied: bool
    extra_points_applied: float
    final_grade: float

    def as_dict(self) -> dict[str, float | str | bool]:
        return {
            "student_id": self.student_id,
            "evaluations": [e.__dict__ for e in self.evaluations],
            "weighted_average": round(self.weighted_average, 2),
            "attendance_penalty_applied": self.attendance_penalty_applied,
            "extra_points_applied": round(self.extra_points_applied, 2),
            "final_grade": round(self.final_grade, 2),
        }


class GradeCalculator:
    # Calcula la nota final aplicando reglas de negocio
    
    def calculate(
        self,
        *,
        student_id: str,
        evaluations: Sequence[Evaluation],
        attendance_policy: AttendancePolicy,
        extra_points_policy: ExtraPointsPolicy,
    ) -> GradeCalculationResult:
        if not student_id.strip():
            raise ValidationError("El código del estudiante es obligatorio.")

        if len(evaluations) > MAX_EVALUATIONS:
            raise ValidationError(
                f"Solo se permiten {MAX_EVALUATIONS} evaluaciones por estudiante.")

        weighted_average = self._calculate_weighted_average(evaluations)
        attendance_penalty = not attendance_policy.has_reached_minimum

        # Si no cumple asistencia, la nota final es 0
        if attendance_penalty:
            final_grade = 0.0
            extra_points = 0.0
        else:
            extra_points = extra_points_policy.resolve_points()
            # La nota final no puede superar el máximo permitido
            final_grade = min(MAX_FINAL_SCORE, weighted_average + extra_points)

        return GradeCalculationResult(
            student_id=student_id,
            evaluations=evaluations,
            weighted_average=weighted_average,
            attendance_penalty_applied=attendance_penalty,
            extra_points_applied=extra_points,
            final_grade=final_grade,
        )

    @staticmethod
    def _calculate_weighted_average(evaluations: Sequence[Evaluation]) -> float:
        if not evaluations:
            return 0.0

        total_weight = sum(e.weight for e in evaluations)
        if total_weight <= 0:
            raise ValidationError("La suma de los pesos debe ser mayor que 0.")

        weighted_sum = sum(e.score * e.weight for e in evaluations)
        return weighted_sum / total_weight
