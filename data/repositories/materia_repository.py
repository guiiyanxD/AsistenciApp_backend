from config.database import get_connection


class MateriaRepository:

    def crear(self, docente_id: str, nombre: str, codigo: str | None, descripcion: str | None) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO materia (docente_id, nombre, codigo, descripcion)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, docente_id, nombre, codigo, descripcion, creado_en
                    """,
                    (docente_id, nombre, codigo, descripcion),
                )
                conn.commit()
                return dict(cur.fetchone())

    def listar_por_docente(self, docente_id: str) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, nombre, codigo, descripcion, creado_en
                    FROM materia WHERE docente_id = %s
                    ORDER BY nombre
                    """,
                    (docente_id,),
                )
                return [dict(r) for r in cur.fetchall()]

    def buscar_por_id(self, materia_id: str, docente_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM materia WHERE id = %s AND docente_id = %s",
                    (materia_id, docente_id),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def actualizar(self, materia_id: str, docente_id: str, nombre: str, codigo: str | None, descripcion: str | None) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE materia SET nombre=%s, codigo=%s, descripcion=%s
                    WHERE id=%s AND docente_id=%s
                    RETURNING id, nombre, codigo, descripcion, creado_en
                    """,
                    (nombre, codigo, descripcion, materia_id, docente_id),
                )
                conn.commit()
                row = cur.fetchone()
                return dict(row) if row else None

    def eliminar(self, materia_id: str, docente_id: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM grupo
                    WHERE materia_id = %s AND activo = TRUE
                    """,
                    (materia_id,),
                )
                if cur.fetchone():
                    return False
                cur.execute(
                    "DELETE FROM materia WHERE id = %s AND docente_id = %s",
                    (materia_id, docente_id),
                )
                conn.commit()
                return cur.rowcount > 0

    def codigo_existe(self, docente_id: str, codigo: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM materia WHERE docente_id = %s AND codigo = %s",
                    (docente_id, codigo),
                )
                return cur.fetchone() is not None
