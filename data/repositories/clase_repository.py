from config.database import get_connection


class ClaseRepository:

    # ------------------------------------------------------------------
    # Lectura
    # ------------------------------------------------------------------

    def buscar_por_id(self, clase_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.grupo_id, c.fecha, c.hora_inicio, c.hora_fin,
                           c.tipo, c.cancelada, c.observaciones, c.creado_en,
                           g.periodo_academico_id,
                           p.docente_id
                    FROM clase c
                    JOIN grupo g ON c.grupo_id = g.id
                    JOIN periodo_academico p ON g.periodo_academico_id = p.id
                    WHERE c.id = %s
                    """,
                    (clase_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def listar_por_grupo(self, grupo_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, fecha, hora_inicio, hora_fin,
                           tipo, cancelada, observaciones, creado_en
                    FROM clase
                    WHERE grupo_id = %s
                    ORDER BY fecha, hora_inicio
                    """,
                    (grupo_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # Etiquetar (cambiar tipo)
    # ------------------------------------------------------------------

    def actualizar_tipo(self, clase_id: str, tipo: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE clase SET tipo = %s
                    WHERE id = %s
                    RETURNING id, tipo, cancelada, fecha, hora_inicio, hora_fin
                    """,
                    (tipo, clase_id),
                )
                conn.commit()
                row = cur.fetchone()
                return dict(row) if row else None

    # ------------------------------------------------------------------
    # Cancelar / restaurar
    # ------------------------------------------------------------------

    def cancelar(self, clase_id: str, observaciones: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE clase
                    SET cancelada = TRUE, observaciones = %s
                    WHERE id = %s
                    RETURNING id, cancelada, observaciones, fecha,
                              hora_inicio, hora_fin, tipo
                    """,
                    (observaciones, clase_id),
                )
                conn.commit()
                row = cur.fetchone()
                return dict(row) if row else None

    def restaurar(self, clase_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE clase
                    SET cancelada = FALSE, observaciones = NULL
                    WHERE id = %s
                    RETURNING id, cancelada, observaciones, fecha,
                              hora_inicio, hora_fin, tipo
                    """,
                    (clase_id,),
                )
                conn.commit()
                row = cur.fetchone()
                return dict(row) if row else None

    # ------------------------------------------------------------------
    # Crear clase extraordinaria
    # ------------------------------------------------------------------

    def crear_extraordinaria(self, grupo_id: str, fecha: str,
                              hora_inicio: str, hora_fin: str,
                              tipo: str, observaciones: str | None) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO clase
                        (grupo_id, fecha, hora_inicio, hora_fin, tipo, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, grupo_id, fecha, hora_inicio, hora_fin,
                              tipo, cancelada, observaciones, creado_en
                    """,
                    (grupo_id, fecha, hora_inicio, hora_fin, tipo, observaciones),
                )
                conn.commit()
                return dict(cur.fetchone())

    def existe_clase_en_horario(self, grupo_id: str, fecha: str,
                                hora_inicio: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM clase
                    WHERE grupo_id = %s AND fecha = %s AND hora_inicio = %s
                    """,
                    (grupo_id, fecha, hora_inicio),
                )
                return cur.fetchone() is not None

    # ------------------------------------------------------------------
    # Asistencias de una clase (tiempo real)
    # ------------------------------------------------------------------

    def asistencias_con_ausentes(self, clase_id: str) -> list[dict]:
        """
        Retorna TODOS los estudiantes inscritos en el grupo de la clase,
        marcando quiénes asistieron y quiénes están ausentes.
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.id          AS estudiante_id,
                        e.nombre      AS estudiante_nombre,
                        e.email       AS estudiante_email,
                        a.id          AS asistencia_id,
                        a.estado,
                        a.fecha_marcado,
                        a.latitud,
                        a.longitud
                    FROM inscripcion i
                    JOIN estudiante e ON i.estudiante_id = e.id
                    LEFT JOIN asistencia a
                        ON  a.inscripcion_id = i.id
                        AND a.clase_id       = %s
                    JOIN clase c ON c.id = %s
                    WHERE i.grupo_id = c.grupo_id
                      AND i.activa   = TRUE
                    ORDER BY e.nombre
                    """,
                    (clase_id, clase_id),
                )
                return [dict(r) for r in cur.fetchall()]
