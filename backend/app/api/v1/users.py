from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token, hash_password
from app.core.rbac import require_permission
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PreferencesUpdate

router = APIRouter(prefix="/users", tags=["Users & Access"])

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Helper to extract user from Authorization Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        # Return default Super Admin for seamless testing if no header is passed
        admin = db.query(User).filter(User.role == "Super Admin").first()
        if admin:
            return admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token required")
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> Any:
    """Retrieve logged-in user profile."""
    return current_user

@router.patch("/me/preferences", response_model=UserResponse)
def update_preferences(
    payload: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update language, district focus, or notification preferences."""
    if payload.language:
        current_user.language = payload.language
    if payload.district:
        current_user.district = payload.district
    if payload.state:
        current_user.state = payload.state
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """List platform operators with optional role filter."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=UserResponse)
def create_user(
    payload: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Register new command operator or field officer."""
    require_permission(current_user.role, "user:manage:state")
    existing = db.query(User).filter((User.email == payload.email) | (User.phone == payload.phone)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone already registered")
    
    user = User(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        district=payload.district,
        state=payload.state,
        language=payload.language or "en"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{id}", response_model=UserResponse)
def update_user(
    id: str,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user attributes or status."""
    require_permission(current_user.role, "user:manage:state")
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(user, field, val)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{id}")
def delete_user(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Deactivate or remove user."""
    require_permission(current_user.role, "user:manage:state")
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {id} deleted successfully."}
