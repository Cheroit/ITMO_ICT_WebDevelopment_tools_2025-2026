from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from core.security import decode_access_token, hash_password, verify_password
from db.connection import get_session
from models import User, UserPasswordChange, UserRead


router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload.get("sub"))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/", response_model=list[UserRead])
def users_list(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[User]:
    return session.exec(select(User)).all()


@router.get("/me", response_model=UserRead)
def users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/change-password")
def change_password(
    password_data: UserPasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.password_hash = hash_password(password_data.new_password)
    session.add(current_user)
    session.commit()
    return {"ok": True}
