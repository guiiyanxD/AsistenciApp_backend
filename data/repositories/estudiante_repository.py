from config.database import get_connection


class EstudianteRepository:

    def crear(self, nombre: str, email: str, password_hash: str) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO estudiante (nombre, email, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, nombre, email, creado_en
                    """,
                    (nombre, email, password_hash),
                )
                conn.commit()
                return dict(cur.fetchone())

    def buscar_por_email(self, email: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM estudiante WHERE email = %s AND activo = TRUE",
                    (email,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def buscar_por_id(self, estudiante_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre, email, creado_en FROM estudiante WHERE id = %s AND activo = TRUE",
                    (estudiante_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def email_existe(self, email: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM estudiante WHERE email = %s",
                    (email,),
                )
                return cur.fetchone() is not None
