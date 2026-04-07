from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.security import create_access_token, hash_password, verify_password
from db.connection import get_session
from models import TokenResponse, User, UserCreate, UserLogin, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register_user(
    user: UserCreate, session: Session = Depends(get_session)
) -> User:
    existing_user = session.exec(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login", response_model=TokenResponse)
def login_user(user: UserLogin, session: Session = Depends(get_session)) -> TokenResponse:
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(db_user.id, db_user.username)
    return TokenResponse(access_token=token)
