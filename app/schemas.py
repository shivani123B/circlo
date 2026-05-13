from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class PostCategory(str,Enum):
    alerts = "alerts"
    buy_sell = "buy_sell"
    food_services = "food_services"
    jobs = "jobs"
    lost_and_found = "lost_and_found"
    ask_share = "ask_share"


class PostCreate(BaseModel):
    title:str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Short, clear title of the post of length 3-100chars"
    )
    body:Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Give the optional detailed description of post"
    )
    category:PostCategory
    community_id: int = Field(
        ...,
        description="ID of the community this post belongs to."
    )
    author_id: int = Field(
        ...,
        description="ID of the user who created this post."
    )
    is_pinned:bool = Field(
        default = False,
        description = "If true, this post will be shown above non-pinned posts."
    )
    expires_at:Optional[datetime] = Field(
        default = None,
        description = "Optional expiry date/time. After this, the post is treated as expired."
    )


class PostOut(BaseModel):
    id:int
    title:str
    body:Optional[str] = None
    category:PostCategory
    community_id: int
    author_id: int
    is_pinned:bool
    created_at:datetime
    updated_at:datetime
    expires_at:Optional[datetime] = None

    class Config:
        from_attributes = True

class PostUpdate(BaseModel):
    title:Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Short, clear title of the post of length 3-100chars"
    )
    body :Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Give the optional detailed description of post"
    )
    category:Optional[PostCategory] = None
    is_pinned:Optional[bool] = Field(
        default = None,
        description = "Updated pinned status."
    )
    expires_at:Optional[datetime]= Field(
        default = None,
        description = "Updated expiry date/time. Set to null to remove expiry."
    )


class UserCreate(BaseModel):
    full_name:str=Field(
        ...,
        min_length = 3,
        max_length = 100,
        description = "Full name of the resident(3-100 Characters)"
    )
    email:Optional[str]= Field(
        default=None,
        description="Email address (optional, but must be unique if provided)."
    )
    phone:Optional[str]=Field(
        default = None,
        description="Phone number (optional, but must be unique if provided)."
    )
    flat_no: Optional[str] = Field(
        default=None,
        description="Flat number, e.g. A-302."
    )
    block_name: Optional[str] = Field(
        default=None,
        description="Block or tower name, e.g. Block A."
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Plain text password (will be hashed before storing)."
    )
    community_id: int = Field(
        ...,
        description="ID of the community the user belongs to."
    )

class UserOut(BaseModel):
    id:int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    flat_no: Optional[str] = None
    block_name: Optional[str] = None
    role: str
    community_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email:Optional[str] = None
    phone:Optional[str] = None
    password:str

class CommunityCreate(BaseModel):
    name:str = Field(
        min_length = 3,
        max_length = 100,
        description = "Please provide the name of the community."
    )
    city:Optional[str]=Field(
        default = None,
        description = "City where the community is located."
    )
    address_line1 : Optional[str] = Field(
        default = None,
        description = "Main address line, e.g., 'Street name, area'."
    )
    address_line2: Optional[str]=Field(
        default=None,
        description = "Additional address info (optional)."
    )
    pincode: Optional[str] = Field(
        default=None,
        description="Postal code / PIN code."
    )

class CommunityOut(BaseModel):
    id: int
    name: str
    city: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    pincode: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
