from config.database import get_connection


class GrupoRepository:

    def crear(self, periodo_id: str, materia_id: str, nombre: str,
              codigo_invitacion: str, cupo_maximo: int | None) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO grupo (periodo_academico_id, materia_id, nombre, codigo_invitacion, cupo_maximo)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, nombre, codigo_invitacion, cupo_maximo, activo, creado_en
                    """,
                    (periodo_id, materia_id, nombre, codigo_invitacion, cupo_maximo),
                )
                conn.commit()
                return dict(cur.fetchone())

    def listar_por_docente(self, docente_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT g.id, g.nombre, g.codigo_invitacion, g.cupo_maximo, g.activo, g.creado_en,
                           m.nombre AS materia_nombre, m.codigo AS materia_codigo,
                           p.nombre AS periodo_nombre, p.fecha_inicio, p.fecha_fin
                    FROM grupo g
                    JOIN materia m ON g.materia_id = m.id
                    JOIN periodo_academico p ON g.periodo_academico_id = p.id
                    WHERE p.docente_id = %s
                    ORDER BY g.creado_en DESC
                    """,
                    (docente_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    def buscar_por_id(self, grupo_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT g.*, m.nombre AS materia_nombre,
                           p.nombre AS periodo_nombre, p.fecha_inicio, p.fecha_fin, p.docente_id
                    FROM grupo g
                    JOIN materia m ON g.materia_id = m.id
                    JOIN periodo_academico p ON g.periodo_academico_id = p.id
                    WHERE g.id = %s
                    """,
                    (grupo_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def agregar_horario(self, grupo_id: str, dia_semana: str,
                        hora_inicio: str, hora_fin: str) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO horario_semanal (grupo_id, dia_semana, hora_inicio, hora_fin)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, dia_semana, hora_inicio, hora_fin
                    """,
                    (grupo_id, dia_semana, hora_inicio, hora_fin),
                )
                conn.commit()
                return dict(cur.fetchone())

    def listar_horarios(self, grupo_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, dia_semana, hora_inicio, hora_fin
                    FROM horario_semanal WHERE grupo_id = %s
                    ORDER BY dia_semana
                    """,
                    (grupo_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    def eliminar_horarios(self, grupo_id: str):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM horario_semanal WHERE grupo_id = %s",
                    (grupo_id,),
                )
                conn.commit()

    def crear_clases_batch(self, clases: list[dict]):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO clase (grupo_id, fecha, hora_inicio, hora_fin, tipo)
                    VALUES (%(grupo_id)s, %(fecha)s, %(hora_inicio)s, %(hora_fin)s, %(tipo)s)
                    ON CONFLICT (grupo_id, fecha, hora_inicio) DO NOTHING
                    """,
                    clases,
                )
                conn.commit()

    def listar_clases(self, grupo_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, fecha, hora_inicio, hora_fin, tipo, cancelada, observaciones, creado_en
                    FROM clase WHERE grupo_id = %s
                    ORDER BY fecha, hora_inicio
                    """,
                    (grupo_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    def eliminar_clases_futuras(self, grupo_id: str):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM clase WHERE grupo_id = %s AND fecha >= CURRENT_DATE",
                    (grupo_id,),
                )
                conn.commit()
    