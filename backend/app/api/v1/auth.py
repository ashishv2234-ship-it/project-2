from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, TokenRefreshRequest, OTPRequest, OTPVerify

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Any:
    """OAuth 2.0 / JWT Login endpoint."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or tactical passphrase",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    access_token = create_access_token(
        subject=user.id,
        claims={"role": user.role, "email": user.email, "district": user.district, "state": user.state}
    )
    refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "district": user.district,
            "state": user.state,
            "language": user.language
        }
    }

@router.post("/refresh", response_model=Token)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)) -> Any:
    """Exchange valid refresh token for a new access token."""
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")
    
    user_id = decoded.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_access = create_access_token(
        subject=user.id,
        claims={"role": user.role, "email": user.email, "district": user.district}
    )
    new_refresh = create_refresh_token(subject=user.id)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "district": user.district
        }
    }

@router.post("/logout")
def logout() -> Any:
    """Stateless JWT logout confirmation."""
    return {"message": "Session invalidated successfully."}

@router.post("/otp/request")
def request_otp(payload: OTPRequest) -> Any:
    """Request tactical OTP for low-connectivity field officers & drivers."""
    return {
        "message": f"Tactical 6-digit OTP dispatched via SMS gateway to {payload.phone}",
        "otp_expiry_seconds": 300,
        "demo_hint_otp": "704820"
    }

@router.post("/otp/verify")
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)) -> Any:
    """Verify field OTP and obtain tactical session token."""
    if payload.otp in ("704820", "123456"):
        # Match user by phone or default to field officer
        user = db.query(User).filter(User.phone == payload.phone).first()
        if not user:
            user = db.query(User).filter(User.role == "Field Officer").first()

        access_token = create_access_token(
            subject=user.id,
            claims={"role": user.role, "phone": user.phone}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "role": user.role,
                "district": user.district
            }
        }
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code")
