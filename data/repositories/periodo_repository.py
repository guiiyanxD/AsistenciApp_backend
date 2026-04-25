from config.database import get_connection


class PeriodoRepository:

    def crear(self, docente_id: str, nombre: str, tipo: str, fecha_inicio: str, fecha_fin: str) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO periodo_academico (docente_id, nombre, tipo, fecha_inicio, fecha_fin)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, nombre, tipo, fecha_inicio, fecha_fin, activo, creado_en
                    """,
                    (docente_id, nombre, tipo, fecha_inicio, fecha_fin),
                )
                conn.commit()
                return dict(cur.fetchone())

    def listar_por_docente(self, docente_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, nombre, tipo, fecha_inicio, fecha_fin, activo, creado_en
                    FROM periodo_academico WHERE docente_id = %s
                    ORDER BY fecha_inicio DESC
                    """,
                    (docente_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    def buscar_por_id(self, periodo_id: str, docente_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM periodo_academico WHERE id = %s AND docente_id = %s",
                    (periodo_id, docente_id),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def actualizar(self, periodo_id: str, docente_id: str, nombre: str, tipo: str,
                   fecha_inicio: str, fecha_fin: str, activo: bool) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE periodo_academico
                    SET nombre=%s, tipo=%s, fecha_inicio=%s, fecha_fin=%s, activo=%s
                    WHERE id=%s AND docente_id=%s
                    RETURNING id, nombre, tipo, fecha_inicio, fecha_fin, activo, creado_en
                    """,
                    (nombre, tipo, fecha_inicio, fecha_fin, activo, periodo_id, docente_id),
                )
                conn.commit()
                row = cur.fetchone()
                return dict(row) if row else None

    def eliminar(self, periodo_id: str, docente_id: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM periodo_academico WHERE id = %s AND docente_id = %s",
                    (periodo_id, docente_id),
                )
                conn.commit()
                return cur.rowcount > 0
