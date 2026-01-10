import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from GUI.db.base import Base

if TYPE_CHECKING:
    from GUI.db.models.game import Games


DEFAULT_ELO = -1  # means "not asses yet"
DEFAULT_ELO_RD = 350
DEFAULT_ELO_VOLATILITY = 0.06


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False)
    disambiguator: Mapped[int] = mapped_column(Integer, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    elo: Mapped[int] = mapped_column(Integer, nullable=False, default=DEFAULT_ELO, index=True)
    elo_rd: Mapped[int] = mapped_column(Integer, nullable=False, default=DEFAULT_ELO_RD)
    elo_volatility: Mapped[float] = mapped_column(default=DEFAULT_ELO_VOLATILITY)

    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    draws: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    is_bot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("username", "disambiguator", name="uq_users_username_disambiguator"),
    )

    games_as_white: Mapped[list["Games"]] = relationship(
        "Games",
        foreign_keys="Games.white_id",
        back_populates="white",
    )

    games_as_black: Mapped[list["Games"]] = relationship(
        "Games",
        foreign_keys="Games.black_id",
        back_populates="black",
    )

    def __repr__(self) -> str:
        return f"<Users {self.username}#{self.disambiguator} elo={self.elo}>"
