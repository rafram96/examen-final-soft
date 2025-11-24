# Interfaz de consola para el calculador de notas

from __future__ import annotations

from app.grade_calculator import (
    AttendancePolicy,
    Evaluation,
    EvaluationRegistry,
    ExtraPointsPolicy,
    GradeCalculator,
    ValidationError,
)


def prompt_non_empty(prompt: str) -> str:
    # Solicita entrada no vacía hasta obtener valor válido
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("El valor no puede estar vacío. Intenta nuevamente.")


def prompt_float(prompt: str, *, minimum: float | None = None, maximum: float | None = None) -> float:
    # Solicita un número flotante dentro de los límites opcionales
    while True:
        try:
            value = float(input(prompt))
            if minimum is not None and value < minimum:
                raise ValueError
            if maximum is not None and value > maximum:
                raise ValueError
            return value
        except ValueError:
            min_text = f" >= {minimum}" if minimum is not None else ""
            max_text = f" <= {maximum}" if maximum is not None else ""
            print(f"Ingresa un número válido{min_text}{max_text}.")


def prompt_bool(prompt: str) -> bool:
    # Solicita respuesta sí/no hasta obtener valor válido
    while True:
        value = input(f"{prompt} (s/n): ").strip().lower()
        if value in {"s", "si", "sí", "y"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Responde con 's' o 'n'.")


def collect_evaluations() -> list[Evaluation]:
    # Recopila las evaluaciones del estudiante validando cada entrada
    registry = EvaluationRegistry()
    total = int(prompt_float("¿Cuántas evaluaciones registrarás? (0-10): ", minimum=0, maximum=10))
    for index in range(1, total + 1):
        while True:
            print(f"\nEvaluación {index}")
            name = prompt_non_empty("Nombre: ")
            score = prompt_float("Nota (0-20): ", minimum=0, maximum=20)
            weight = prompt_float("Peso relativo (ej. 20 para 20%): ", minimum=0.1)
            try:
                registry.add(Evaluation(name=name, score=score, weight=weight))
                break
            except ValidationError as exc:
                print(f"Error: {exc}. Vuelve a ingresar la evaluación.")
    return registry.evaluations


def main() -> None:
    print("===== CS-GradeCalculator =====")
    student_id = prompt_non_empty("Código del estudiante: ")
    evaluations = collect_evaluations()
    has_attendance = prompt_bool("¿Cumplió la asistencia mínima?")
    extra_points_agreement = prompt_bool(
        "¿Todos los docentes del año aprobaron los puntos extra?"
    )

    calculator = GradeCalculator()
    try:
        result = calculator.calculate(
            student_id=student_id,
            evaluations=evaluations,
            attendance_policy=AttendancePolicy(has_reached_minimum=has_attendance),
            extra_points_policy=ExtraPointsPolicy(all_years_teachers=extra_points_agreement),
        )
    except ValidationError as exc:
        print(f"No se pudo calcular la nota: {exc}")
        return

    print("\n===== Resultado =====")
    print(f"Estudiante: {result.student_id}")
    print(f"Promedio ponderado: {result.weighted_average:.2f}")
    print(f"Puntos extra aplicados: {result.extra_points_applied:.2f}")
    if result.attendance_penalty_applied:
        print("Penalización: Sin asistencia mínima, nota final = 0")
    print(f"Nota final: {result.final_grade:.2f}")


if __name__ == "__main__":
    main()
