import psycopg2
import psycopg2.extras
from config.settings import Config


def get_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
