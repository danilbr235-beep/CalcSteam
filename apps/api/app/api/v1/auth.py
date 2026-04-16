from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_token, verify_password
from app.db.session import get_db
from app.models.models import User
from app.schemas.auth import LoginRequest, TokenPair
from app.services.audit_service import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    log_action(db, user.id, "auth.login", "user", str(user.id), {})
    return TokenPair(
        access_token=create_token(str(user.id), 30),
        refresh_token=create_token(str(user.id), 60 * 24),
    )


@router.post("/logout")
def logout():
    return {"ok": True}


@router.post("/refresh", response_model=TokenPair)
def refresh(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.jwt_secret, algorithms=["HS256"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return TokenPair(
        access_token=create_token(str(sub), 30),
        refresh_token=create_token(str(sub), 60 * 24),
    )


@router.post("/2fa/verify")
def verify_2fa():
    return {"ok": True}
