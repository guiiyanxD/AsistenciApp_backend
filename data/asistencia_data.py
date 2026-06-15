import datetime
from config.database import get_connection


class AsistenciaData:

    def buscar_clase_activa(self, grupo_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, grupo_id, fecha, hora_inicio, hora_fin, tipo, cancelada
                    FROM clase
                    WHERE grupo_id = %s
                      AND fecha = CURRENT_DATE
                      AND cancelada = FALSE
                      AND hora_inicio <= CURRENT_TIME
                      AND hora_fin   >= CURRENT_TIME
                    ORDER BY hora_inicio
                    LIMIT 1
                    """,
                    (grupo_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def buscar_clase_por_id(self, clase_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM clase WHERE id = %s",
                    (clase_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def existe_asistencia(self, clase_id: str, inscripcion_id: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM asistencia
                    WHERE clase_id = %s AND inscripcion_id = %s
                    """,
                    (clase_id, inscripcion_id),
                )
                return cur.fetchone() is not None

    def crear(self, clase_id: str, inscripcion_id: str,
              latitud: float | None, longitud: float | None,
              precision_metros: float | None) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO asistencia
                        (clase_id, inscripcion_id, estado,
                         latitud, longitud, precision_metros, fecha_marcado)
                    VALUES (%s, %s, 'presente', %s, %s, %s, NOW())
                    RETURNING id, clase_id, inscripcion_id, estado,
                              latitud, longitud, precision_metros, fecha_marcado
                    """,
                    (clase_id, inscripcion_id, latitud, longitud, precision_metros),
                )
                conn.commit()
                return dict(cur.fetchone())

    def listar_por_clase(self, clase_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT a.id, a.estado, a.fecha_marcado,
                           a.latitud, a.longitud, a.precision_metros,
                           e.nombre AS estudiante_nombre,
                           e.email  AS estudiante_email
                    FROM asistencia a
                    JOIN inscripcion i ON a.inscripcion_id = i.id
                    JOIN estudiante  e ON i.estudiante_id  = e.id
                    WHERE a.clase_id = %s
                    ORDER BY e.nombre
                    """,
                    (clase_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    def listar_por_grupo_y_estudiante(self, grupo_id: str,
                                      estudiante_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT a.id, a.estado, a.fecha_marcado,
                           c.fecha, c.hora_inicio, c.hora_fin, c.tipo
                    FROM asistencia a
                    JOIN inscripcion i ON a.inscripcion_id = i.id
                    JOIN clase       c ON a.clase_id       = c.id
                    WHERE i.grupo_id      = %s
                      AND i.estudiante_id = %s
                    ORDER BY c.fecha DESC, c.hora_inicio DESC
                    """,
                    (grupo_id, estudiante_id),
                )
                return [dict(r) for r in cur.fetchall()]

    def resumen_por_grupo(self, grupo_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.id   AS estudiante_id,
                        e.nombre AS estudiante_nombre,
                        e.email  AS estudiante_email,
                        COUNT(DISTINCT c.id)                             AS total_clases,
                        COUNT(DISTINCT a.clase_id)
                            FILTER (WHERE a.estado = 'presente')         AS presentes,
                        ROUND(
                            COUNT(DISTINCT a.clase_id)
                                FILTER (WHERE a.estado = 'presente')::numeric
                            / NULLIF(COUNT(DISTINCT c.id), 0) * 100, 1
                        )                                                AS porcentaje
                    FROM inscripcion i
                    JOIN estudiante e ON i.estudiante_id = e.id
                    JOIN clase c      ON c.grupo_id = i.grupo_id
                                     AND c.cancelada = FALSE
                                     AND c.fecha <= CURRENT_DATE
                    LEFT JOIN asistencia a ON a.clase_id      = c.id
                                          AND a.inscripcion_id = i.id
                    WHERE i.grupo_id = %s AND i.activa = TRUE
                    GROUP BY e.id, e.nombre, e.email
                    ORDER BY e.nombre
                    """,
                    (grupo_id,),
                )
                return [dict(r) for r in cur.fetchall()]
