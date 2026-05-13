from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db
from .. import models
from ..schemas import UserCreate, UserOut, UserLogin
from ..auth import hash_password, verify_password

router = APIRouter(tags=["users"])


@router.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
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
        flat_number=user.flat_number,
        block_name=user.block_name,
        role="resident",
        password_hash=hashed_pw,
        community_id=user.community_id,
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    if not credentials.email and not credentials.phone:
        raise HTTPException(status_code=400, detail="Provide email or phone.")

    query = db.query(models.User).filter(models.User.is_active == True)

    if credentials.email:
        query = query.filter(models.User.email == credentials.email)
    else:
        query = query.filter(models.User.phone == credentials.phone)

    user = query.first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    return {
        "message": "Login successful",
        "user_id": user.id,
        "full_name": user.full_name,
        "community_id": user.community_id,
    }
