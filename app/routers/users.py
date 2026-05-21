from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..auth import create_access_token, hash_password, verify_password
from ..deps import get_current_user, get_db
from ..schemas import TokenOut, UserCreate, UserLogin, UserOut, UserRole

router = APIRouter(tags=["users"])


@router.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    community = (
        db.query(models.Community)
        .filter(models.Community.id == user.community_id)
        .first()
    )
    if not community:
        raise HTTPException(status_code=404, detail="Community not found.")

    if user.email:
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered.")

    if user.phone:
        if db.query(models.User).filter(models.User.phone == user.phone).first():
            raise HTTPException(status_code=400, detail="Phone already registered.")

    hashed_pw = hash_password(user.password)

    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        flat_no=user.flat_no,
        block_name=user.block_name,
        role=UserRole.resident.value,
        password_hash=hashed_pw,
        community_id=user.community_id,
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=TokenOut)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    query = db.query(models.User).filter(models.User.is_active == True)

    if credentials.email:
        query = query.filter(models.User.email == credentials.email)
    else:
        query = query.filter(models.User.phone == credentials.phone)

    user = query.first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    access_token = create_access_token(subject=user.id)
    return TokenOut(access_token=access_token, user=UserOut.model_validate(user))


@router.get("/users/me", response_model=UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user
