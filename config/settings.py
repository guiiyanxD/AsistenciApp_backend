import os
from urllib.parse import urlparse


class Config:
    _db_url = os.environ.get("DATABASE_URL")

    if _db_url:
        _parsed = urlparse(_db_url)
        DB_HOST     = _parsed.hostname
        DB_PORT     = _parsed.port or 5432
        DB_NAME     = _parsed.path.lstrip("/")
        DB_USER     = _parsed.username
        DB_PASSWORD = _parsed.password
    else:
        DB_HOST     = os.environ.get("DB_HOST", "localhost")
        DB_PORT     = int(os.environ.get("DB_PORT", 5432))
        DB_NAME     = os.environ.get("DB_NAME", "asistencia_db")
        DB_USER     = os.environ.get("DB_USER", "asistencia_user")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "asistencia_pass")

    JWT_SECRET       = os.environ.get("JWT_SECRET", "cambia_este_secreto_en_produccion")
    JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", 24))

    SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.environ.get("PORT") or os.environ.get("SERVER_PORT", 8000))
