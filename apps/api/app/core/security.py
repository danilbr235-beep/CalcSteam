from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(sub: str, minutes: int) -> str:
    payload = {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
