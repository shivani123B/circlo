from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from .database import Base

class Community(Base):
    __tablename__ = "communities"

    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    pincode = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False,default= True)
    created_at = Column(DateTime, nullable=False,default=datetime.utcnow)


    users = relationship("User", back_populates="community")
    posts = relationship("Post", back_populates="community")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index= True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique = True, nullable= True)
    phone = Column(String(20), unique = True, nullable= True)
    flat_no = Column(String(10), nullable= True)
    block_name = Column(String(20), nullable=True)
    role = Column(String(20), nullable = False, default = "resident")
    password_hash = Column(String(255), nullable=False)
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    community = relationship("Community", back_populates="users")
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=True)
    category = Column(String(30), nullable=False)

    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    is_pinned = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime, nullable=True)

    community = relationship("Community", back_populates="posts")
    author = relationship("User", back_populates="posts")


     


