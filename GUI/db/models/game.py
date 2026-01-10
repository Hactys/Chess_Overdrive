import uuid
from enum import Enum
from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from GUI.db.base import Base

if TYPE_CHECKING:
    from GUI.db.models.user import Users


class GameStatus(str, Enum):
    ONGOING = "ongoing"
    FINISHED = "finished"
    ABORTED = "aborted"
    CANCELED = "canceled"


class TerminationReason(str, Enum):
    CHECKMATE = "checkmate"
    TIMEOUT = "timeout"
    RESIGN = "resign"
    WITHDRAWAL = "withdrawal"
    DRAW = "draw"


class Games(Base):
    __tablename__ = "games"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        SQLEnum(GameStatus, name="game_status"), nullable=False, index=True
    )

    seed: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # seed for the game RNG, use it in replay
    white_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    white: Mapped["Users"] = relationship(
        "User", foreign_keys=[white_id], back_populates="games_as_white"
    )
    black_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    black: Mapped["Users"] = relationship(
        "User", foreign_keys=[black_id], back_populates="games_as_black"
    )
    winner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    white_elo_before: Mapped[int] = mapped_column(Integer, nullable=False)
    black_elo_before: Mapped[int] = mapped_column(Integer, nullable=False)
    white_elo_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    black_elo_after: Mapped[int | None] = mapped_column(Integer, nullable=True)

    moves: Mapped[str] = mapped_column(Text, nullable=False)  # custom PGN
    final_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    termination_reason: Mapped[str | None] = mapped_column(
        SQLEnum(TerminationReason, name="game_termination_reason"), nullable=True
    )
    rated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint("white_id != black_id", name="ck_game_different_players"),
        CheckConstraint(
            "winner_id IS NULL OR winner_id IN (white_id, black_id)", name="ck_game_winner_valid"
        ),
        CheckConstraint(
            "(status = 'finished' AND termination_reason IS NOT NULL) OR "
            "(status != 'finished' AND termination_reason IS NULL)",
            name="ck_game_status_vs_termination",
        ),
        CheckConstraint(
            "(status = 'finished' AND winner_id IS NOT NULL) OR (status != 'finished')",
            name="ck_game_winner_finished_only",
        ),
    )

    def __repr__(self) -> str:
        return f"<Game {self.id} ({self.status}) : {self.white_id} vs {self.black_id}>"
