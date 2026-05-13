from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..deps import get_db
from ..schemas import PostCreate, PostUpdate, PostOut, PostCategory
from ..services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostOut)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return post_service.create_post(db, post)


@router.get("", response_model=List[PostOut])
def list_posts(
    community_id: Optional[int] = None,
    category: Optional[PostCategory] = None,
    search: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return post_service.list_posts(
        db, community_id, category, search, limit, offset
    )


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    try:
        return post_service.get_post_or_404(db, post_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")


@router.put("/{post_id}", response_model=PostOut)
def update_post(post_id: int, updated: PostCreate, db: Session = Depends(get_db)):
    try:
        return post_service.update_post(db, post_id, updated)
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")


@router.patch("/{post_id}", response_model=PostOut)
def patch_post(post_id: int, updates: PostUpdate, db: Session = Depends(get_db)):
    try:
        return post_service.patch_post(db, post_id, updates)
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    try:
        post_service.delete_post(db, post_id)
        return {"message": "Post deleted successfully", "deleted_post_id": post_id}
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")
