from cryptography.fernet import Fernet
from app.core.config import settings


def _fernet() -> Fernet:
    return Fernet(settings.encryption_key.encode())


def encrypt_code(raw: str) -> str:
    return _fernet().encrypt(raw.encode()).decode()


def decrypt_code(payload: str) -> str:
    return _fernet().decrypt(payload.encode()).decode()


def mask_code(raw: str) -> str:
    if len(raw) <= 4:
        return "*" * len(raw)
    return raw[:2] + "*" * (len(raw) - 4) + raw[-2:]
