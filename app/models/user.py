import uuid
from datetime import datetime
from typing import Optional


from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID, CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    login: Mapped[str] = mapped_column(
        CITEXT(),
        unique=True,
        index=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )

    env: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str] = mapped_column(String, nullable=False)

    locktime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
