from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db
from .. import models
from ..schemas import CommunityCreate, CommunityOut

router = APIRouter(prefix="/communities", tags=["communities"])


@router.post("", response_model=CommunityOut)
def create_community(community: CommunityCreate, db: Session = Depends(get_db)):
    query = db.query(models.Community).filter(models.Community.name == community.name)
    if community.city:
        query = query.filter(models.Community.city == community.city)

    existing = query.first()
    if existing:
        raise HTTPException(status_code=400, detail="Community already exists in this city.")

    db_community = models.Community(
        name=community.name,
        city=community.city,
        address_line1=community.address_line1,
        address_line2=community.address_line2,
        pincode=community.pincode,
        is_active=True,
    )

    db.add(db_community)
    db.commit()
    db.refresh(db_community)
    return db_community


@router.get("", response_model=List[CommunityOut])
def list_communities(
    city: Optional[str] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(models.Community)

    if not include_inactive:
        query = query.filter(models.Community.is_active == True)

    if city is not None:
        query = query.filter(models.Community.city == city)

    return query.order_by(models.Community.name.asc()).all()


@router.get("/{community_id}", response_model=CommunityOut)
def get_community(community_id: int, db: Session = Depends(get_db)):
    community = db.query(models.Community).filter(models.Community.id == community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return community
