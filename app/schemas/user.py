from datetime import datetime
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    uid: str
    email: str | None = None
    display_name: str | None = None
    photo_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    photo_url: str | None = Field(default=None, max_length=2048)
