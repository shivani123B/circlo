from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db
from .. import models
from ..auth import hash_password

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    default_community_name = "Alpha Gardens"
    default_city = "Hyderabad"

    community = (
        db.query(models.Community)
        .filter(models.Community.name == default_community_name, models.Community.city == default_city)
        .first()
    )

    if not community:
        community = models.Community(
            name=default_community_name,
            city=default_city,
            address_line1="Default address line 1",
            address_line2="Default address line 2",
            pincode="500001",
            is_active=True,
        )
        db.add(community)
        db.commit()
        db.refresh(community)

    default_email = "admin@alphagardens.local"

    user = db.query(models.User).filter(models.User.email == default_email).first()

    created_user_now = False
    if not user:
        created_user_now = True
        default_password = "admin123"
        user = models.User(
            full_name="Alpha Admin",
            email=default_email,
            phone="9999999999",
            flat_number="A-101",
            block_name="Block A",
            role="admin",
            password_hash=hash_password(default_password),
            community_id=community.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "message": "Seed data ready",
        "community": {"id": community.id, "name": community.name, "city": community.city},
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "community_id": user.community_id,
            "default_password_if_new": "admin123" if created_user_now else None,
        },
    }
