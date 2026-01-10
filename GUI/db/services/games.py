import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Games, Users
from db.models.game import GameStatus, TerminationReason


# Game lifecycle
def create_game(db: Session, *, white: Users, black: Users, seed: int, rated: bool = True) -> Games:
    game = Games(
        status=GameStatus.ONGOING,
        seed=seed,
        white_id=white.id,
        black_id=black.id,
        white_elo_before=white.elo,
        black_elo_before=black.elo,
        moves="",
        rated=rated,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def append_move(game: Games, move_notation: str) -> None:
    """
    Append-only : évite toute réécriture coûteuse.
    """
    if game.moves:
        game.moves += "\n"
    game.moves += move_notation


# Fin de partie
def finish_game(
    db: Session,
    *,
    game: Games,
    winner: Users | None,
    termination_reason: TerminationReason,
    white_elo_after: int,
    black_elo_after: int,
    final_state: dict,
):
    game.status = GameStatus.FINISHED
    game.finished_at = datetime.now(timezone.utc)
    game.termination_reason = termination_reason
    game.winner_id = winner.id if winner else None
    game.white_elo_after = white_elo_after
    game.black_elo_after = black_elo_after
    game.final_state = final_state

    db.add(game)


def abort_game(db: Session, *, game: Games, reason: str = "aborted"):
    game.status = GameStatus.ABORTED
    game.finished_at = datetime.now(timezone.utc)
    game.termination_reason = None
    db.add(game)


# Queries orientées UI
def get_game_by_id(db: Session, game_id: uuid.UUID) -> Games | None:
    return db.get(Games, game_id)


def get_recent_games_for_user(db: Session, *, user_id: uuid.UUID, limit: int = 20) -> list[Games]:
    stmt = (
        select(Games)
        .where((Games.white_id == user_id) | (Games.black_id == user_id))
        .order_by(Games.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def get_ongoing_games_for_user(db: Session, *, user_id: uuid.UUID) -> list[Games]:
    stmt = select(Games).where(
        Games.status == GameStatus.ONGOING,
        (Games.white_id == user_id) | (Games.black_id == user_id),
    )
    return list(db.scalars(stmt))
