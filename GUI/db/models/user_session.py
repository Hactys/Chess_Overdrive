import uuid
from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from GUI.db.base import Base

if TYPE_CHECKING:
    from db.models.user import Users


class Sessions(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    logout_reason: Mapped[str | None] = mapped_column(Text)

    user: Mapped["Users"] = relationship("Users")

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    def __repr__(self) -> str:
        return f"<Session {self.id} user={self.user_id} active={self.is_active}>"
