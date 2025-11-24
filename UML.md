# Diagrama UML sugerido

Para documentar la solución puedes crear un diagrama de clases sencillo con los siguientes elementos:

1. **Evaluation** (`name`, `score`, `weight`)
   - Clase de entidad que valida los rangos permitidos.
2. **EvaluationRegistry** (`evaluations: List<Evaluation>`)
   - Métodos `add()` y `total_weight()`. Relación de composición con `Evaluation` (1..* hasta un máximo de 10).
3. **AttendancePolicy** (`has_reached_minimum: bool`)
   - Clase de valor sin comportamiento adicional.
4. **ExtraPointsPolicy** (`all_years_teachers: bool`, `extra_points_value: float`)
   - Método `resolve_points()`. Restricción de no negatividad.
5. **GradeCalculator**
   - Método `calculate(...)` que recibe las políticas y evaluaciones y devuelve `GradeCalculationResult`.
   - Dependencias hacia `Evaluation`, `AttendancePolicy`, `ExtraPointsPolicy`.
6. **GradeCalculationResult** (`student_id`, `weighted_average`, `extra_points_applied`, `final_grade`, etc.).
7. **grade_cli (Boundary)**
   - Representa la interfaz de consola. Utiliza `GradeCalculator` y actúa como actor Docente.

Relaciones clave:
- `GradeCalculator` usa (`<<uses>>`) `Evaluation`, `AttendancePolicy`, `ExtraPointsPolicy` y crea `GradeCalculationResult`.
- `grade_cli` depende de `GradeCalculator` y de las entidades para construir las entradas.
- `EvaluationRegistry` compone múltiples `Evaluation` y garantiza el RNF01.

Notas para el diagrama:
- Marca las constantes relevantes (por ejemplo `MAX_EVALUATIONS = 10`, `EXTRA_POINTS_VALUE = 1.0`) como estereotipos o notas UML.
- Indica el flujo principal del caso de uso referenciando al actor *Docente UTEC* apuntando al `grade_cli`.
- Opcionalmente agrega un diagrama de secuencia corto mostrando: Docente → CLI → GradeCalculator → Resultado.
