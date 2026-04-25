from config.database import get_connection


class InscripcionRepository:

    def buscar_grupo_por_codigo(self, codigo: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT g.id, g.nombre, g.activo, g.cupo_maximo, g.codigo_invitacion,
                           m.nombre AS materia_nombre,
                           p.nombre AS periodo_nombre,
                           p.fecha_inicio, p.fecha_fin, p.activo AS periodo_activo
                    FROM grupo g
                    JOIN materia m ON g.materia_id = m.id
                    JOIN periodo_academico p ON g.periodo_academico_id = p.id
                    WHERE g.codigo_invitacion = %s
                    """,
                    (codigo.upper(),),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def contar_inscritos(self, grupo_id: str) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) AS total FROM inscripcion
                    WHERE grupo_id = %s AND activa = TRUE
                    """,
                    (grupo_id,),
                )
                return cur.fetchone()["total"]

    def existe_inscripcion(self, grupo_id: str, estudiante_id: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM inscripcion
                    WHERE grupo_id = %s AND estudiante_id = %s
                    """,
                    (grupo_id, estudiante_id),
                )
                return cur.fetchone() is not None

    def crear(self, grupo_id: str, estudiante_id: str) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO inscripcion (grupo_id, estudiante_id)
                    VALUES (%s, %s)
                    RETURNING id, grupo_id, estudiante_id, fecha_inscripcion, activa
                    """,
                    (grupo_id, estudiante_id),
                )
                conn.commit()
                return dict(cur.fetchone())

    def listar_por_estudiante(self, estudiante_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT i.id, i.fecha_inscripcion, i.activa,
                           g.id AS grupo_id, g.nombre AS grupo_nombre,
                           g.codigo_invitacion,
                           m.nombre AS materia_nombre,
                           p.nombre AS periodo_nombre,
                           p.fecha_inicio, p.fecha_fin
                    FROM inscripcion i
                    JOIN grupo g ON i.grupo_id = g.id
                    JOIN materia m ON g.materia_id = m.id
                    JOIN periodo_academico p ON g.periodo_academico_id = p.id
                    WHERE i.estudiante_id = %s AND i.activa = TRUE
                    ORDER BY i.fecha_inscripcion DESC
                    """,
                    (estudiante_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    def buscar_por_id(self, inscripcion_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM inscripcion WHERE id = %s AND activa = TRUE",
                    (inscripcion_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def buscar_inscripcion_activa(self, grupo_id: str, estudiante_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM inscripcion
                    WHERE grupo_id = %s AND estudiante_id = %s AND activa = TRUE
                    """,
                    (grupo_id, estudiante_id),
                )
                row = cur.fetchone()
                return dict(row) if row else None
