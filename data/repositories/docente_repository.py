from config.database import get_connection


class DocenteRepository:

    def crear(self, nombre: str, email: str, password_hash: str, profesion: str) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO docente (nombre, email, password_hash, profesion)
                    VALUES (%s, %s, %s)
                    RETURNING id, nombre, email,  profesion, creado_en
                    """,
                    (nombre, email, password_hash, profesion),
                )
                conn.commit()
                return dict(cur.fetchone())

    def buscar_por_email(self, email: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM docente WHERE email = %s AND activo = TRUE",
                    (email,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def buscar_por_id(self, docente_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre, email, creado_en FROM docente WHERE id = %s AND activo = TRUE",
                    (docente_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def email_existe(self, email: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM docente WHERE email = %s",
                    (email,),
                )
                return cur.fetchone() is not None
