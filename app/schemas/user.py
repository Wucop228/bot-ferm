from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    login: EmailStr
    project_id: UUID
    env: str
    domain: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID
    locktime: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
