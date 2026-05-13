from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from .. import models
from ..schemas import PostCreate, PostUpdate, PostCategory


def create_post(db: Session, post_data: PostCreate) -> models.Post:
    now = datetime.utcnow()

    expires_at = post_data.expires_at
    if expires_at is None and post_data.category == PostCategory.food_services:
        expires_at = now + timedelta(hours=24)

    db_post = models.Post(
        title=post_data.title,
        body=post_data.body,
        category=post_data.category.value,
        community_id=post_data.community_id,
        author_id=post_data.author_id,
        is_pinned=post_data.is_pinned,
        created_at=now,
        updated_at=now,
        expires_at=expires_at,
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def list_posts(
    db: Session,
    community_id: Optional[int],
    category: Optional[PostCategory],
    search: Optional[str],
    limit: int,
    offset: int,
):
    now = datetime.utcnow()

    query = db.query(models.Post).filter(
        models.Post.is_deleted == False,
        or_(models.Post.expires_at == None, models.Post.expires_at > now),
    )

    if community_id is not None:
        query = query.filter(models.Post.community_id == community_id)

    if category is not None:
        query = query.filter(models.Post.category == category.value)

    if search is not None:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Post.title.ilike(like_pattern),
                models.Post.body.ilike(like_pattern),
            )
        )

    return (
        query.order_by(models.Post.is_pinned.desc(), models.Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_post_or_404(db: Session, post_id: int) -> models.Post:
    post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id, models.Post.is_deleted == False)
        .first()
    )
    if not post:
        raise ValueError("Post not found")
    return post


def update_post(db: Session, post_id: int, updated: PostCreate) -> models.Post:
    post = get_post_or_404(db, post_id)

    post.title = updated.title
    post.body = updated.body
    post.category = updated.category.value
    post.community_id = updated.community_id
    post.author_id = updated.author_id
    post.is_pinned = updated.is_pinned
    post.expires_at = updated.expires_at
    post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(post)
    return post


def patch_post(db: Session, post_id: int, updates: PostUpdate) -> models.Post:
    post = get_post_or_404(db, post_id)

    if updates.title is not None:
        post.title = updates.title

    if updates.body is not None:
        post.body = updates.body

    if updates.category is not None:
        post.category = updates.category.value

    if updates.is_pinned is not None:
        post.is_pinned = updates.is_pinned

    if "expires_at" in updates.__fields_set__:
        post.expires_at = updates.expires_at

    post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int):
    post = get_post_or_404(db, post_id)
    post.is_deleted = True
    post.updated_at = datetime.utcnow()
    db.commit()
