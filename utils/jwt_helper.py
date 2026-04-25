import jwt
import datetime
from config.settings import Config


def generar_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.datetime.utcnow() + datetime.timedelta(
        hours=Config.JWT_EXPIRY_HOURS
    )
    return jwt.encode(data, Config.JWT_SECRET, algorithm="HS256")


def verificar_token(token: str) -> dict:
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
