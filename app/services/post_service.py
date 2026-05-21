from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from .. import models
from ..schemas import PostCreate, PostUpdate, PostCategory, UserRole


def _is_admin(user: models.User) -> bool:
    return user.role == UserRole.admin.value


def _assert_member_of_community(user: models.User, community_id: int) -> None:
    if _is_admin(user):
        return
    if user.community_id != community_id:
        raise PermissionError("You can only post in your own community.")


def _assert_can_modify(post: models.Post, user: models.User) -> None:
    if _is_admin(user):
        return
    if post.author_id != user.id:
        raise PermissionError("You can only modify your own posts.")


def create_post(
    db: Session,
    post_data: PostCreate,
    author: models.User,
) -> models.Post:
    _assert_member_of_community(author, post_data.community_id)

    community = (
        db.query(models.Community)
        .filter(models.Community.id == post_data.community_id)
        .first()
    )
    if community is None:
        raise ValueError("Community not found")

    now = datetime.utcnow()

    expires_at = post_data.expires_at
    if expires_at is None and post_data.category == PostCategory.food_services:
        expires_at = now + timedelta(hours=24)

    db_post = models.Post(
        title=post_data.title,
        body=post_data.body,
        category=post_data.category.value,
        community_id=post_data.community_id,
        author_id=author.id,
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


def update_post(
    db: Session,
    post_id: int,
    updated: PostCreate,
    current_user: models.User,
) -> models.Post:
    post = get_post_or_404(db, post_id)
    _assert_can_modify(post, current_user)

    # Author of the post does not change on update; community can only change
    # to a community the caller is a member of (admins can move freely).
    _assert_member_of_community(current_user, updated.community_id)

    post.title = updated.title
    post.body = updated.body
    post.category = updated.category.value
    post.community_id = updated.community_id
    post.is_pinned = updated.is_pinned
    post.expires_at = updated.expires_at
    post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(post)
    return post


def patch_post(
    db: Session,
    post_id: int,
    updates: PostUpdate,
    current_user: models.User,
) -> models.Post:
    post = get_post_or_404(db, post_id)
    _assert_can_modify(post, current_user)

    if updates.title is not None:
        post.title = updates.title

    if updates.body is not None:
        post.body = updates.body

    if updates.category is not None:
        post.category = updates.category.value

    if updates.is_pinned is not None:
        post.is_pinned = updates.is_pinned

    if "expires_at" in updates.model_fields_set:
        post.expires_at = updates.expires_at

    post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int, current_user: models.User):
    post = get_post_or_404(db, post_id)
    _assert_can_modify(post, current_user)

    post.is_deleted = True
    post.updated_at = datetime.utcnow()
    db.commit()
