from config.database import get_connection


class AdminData:

    def crear(self, nombre: str, email: str, password_hash: str, cargo: str, area: str) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO administrador (nombre, email, password_hash, cargo, area)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, nombre, email, cargo, area, creado_en
                    """,
                    (nombre, email, password_hash, cargo, area),
                )
                conn.commit()
                return dict(cur.fetchone())

    def buscar_por_email(self, email: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM administrador WHERE email = %s AND activo = TRUE",
                    (email,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def email_existe(self, email: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM administrador WHERE email = %s",
                    (email,),
                )
                return cur.fetchone() is not None
