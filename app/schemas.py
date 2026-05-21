import re
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator


# Lightweight, dependency-free format checks. Strict enough to catch typos and
# obviously-malformed input; intentionally not full RFC compliance.
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")
PINCODE_REGEX = re.compile(r"^\d{4,10}$")


def _normalize_email(value):
    if value is None:
        return None
    value = str(value).strip().lower()
    if value == "":
        return None
    if not EMAIL_REGEX.match(value):
        raise ValueError("Invalid email format.")
    return value


def _normalize_phone(value):
    if value is None:
        return None
    value = re.sub(r"\s+", "", str(value))
    if value == "":
        return None
    if not PHONE_REGEX.match(value):
        raise ValueError("Invalid phone format. Use 7-15 digits, optionally prefixed with +.")
    return value


class UserRole(str, Enum):
    resident = "resident"
    admin = "admin"


class PostCategory(str, Enum):
    alerts = "alerts"
    buy_sell = "buy_sell"
    food_services = "food_services"
    jobs = "jobs"
    lost_and_found = "lost_and_found"
    ask_share = "ask_share"


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Short, clear title of the post of length 3-100chars",
    )
    body: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Give the optional detailed description of post",
    )
    category: PostCategory
    community_id: int = Field(
        ...,
        description="ID of the community this post belongs to.",
    )
    is_pinned: bool = Field(
        default=False,
        description="If true, this post will be shown above non-pinned posts.",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiry date/time. After this, the post is treated as expired.",
    )

    @field_validator("expires_at")
    @classmethod
    def expires_at_must_be_future(cls, value):
        if value is None:
            return value
        now = datetime.now(timezone.utc) if value.tzinfo else datetime.utcnow()
        if value <= now:
            raise ValueError("expires_at must be in the future.")
        return value


class PostOut(BaseModel):
    id: int
    title: str
    body: Optional[str] = None
    category: PostCategory
    community_id: int
    author_id: int
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Short, clear title of the post of length 3-100chars",
    )
    body: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Give the optional detailed description of post",
    )
    category: Optional[PostCategory] = None
    is_pinned: Optional[bool] = Field(
        default=None,
        description="Updated pinned status.",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Updated expiry date/time. Set to null to remove expiry.",
    )

    @field_validator("expires_at")
    @classmethod
    def expires_at_must_be_future(cls, value):
        if value is None:
            return value
        now = datetime.now(timezone.utc) if value.tzinfo else datetime.utcnow()
        if value <= now:
            raise ValueError("expires_at must be in the future.")
        return value


class UserCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Full name of the resident(3-100 Characters)",
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address (optional, but must be unique if provided).",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number (optional, but must be unique if provided).",
    )
    flat_no: Optional[str] = Field(
        default=None,
        description="Flat number, e.g. A-302.",
    )
    block_name: Optional[str] = Field(
        default=None,
        description="Block or tower name, e.g. Block A.",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain text password (will be hashed before storing).",
    )
    community_id: int = Field(
        ...,
        description="ID of the community the user belongs to.",
    )

    @field_validator("email", mode="before")
    @classmethod
    def _validate_email(cls, value):
        return _normalize_email(value)

    @field_validator("phone", mode="before")
    @classmethod
    def _validate_phone(cls, value):
        return _normalize_phone(value)

    @model_validator(mode="after")
    def require_email_or_phone(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least one of email or phone.")
        return self


class UserOut(BaseModel):
    id: int
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
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def _validate_email(cls, value):
        return _normalize_email(value)

    @field_validator("phone", mode="before")
    @classmethod
    def _validate_phone(cls, value):
        return _normalize_phone(value)

    @model_validator(mode="after")
    def require_email_or_phone(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least one of email or phone.")
        return self


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class CommunityCreate(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100,
        description="Please provide the name of the community.",
    )
    city: Optional[str] = Field(
        default=None,
        description="City where the community is located.",
    )
    address_line1: Optional[str] = Field(
        default=None,
        description="Main address line, e.g., 'Street name, area'.",
    )
    address_line2: Optional[str] = Field(
        default=None,
        description="Additional address info (optional).",
    )
    pincode: Optional[str] = Field(
        default=None,
        description="Postal code / PIN code.",
    )

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value):
        if value is None:
            return value
        value = str(value).strip()
        if value == "":
            return None
        if not PINCODE_REGEX.match(value):
            raise ValueError("Invalid pincode. Must be 4-10 digits.")
        return value


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
