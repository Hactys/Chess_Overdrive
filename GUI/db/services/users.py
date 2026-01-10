import uuid
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from db.models import Users


# Lookup / Auth
def get_user_by_id(db: Session, user_id: uuid.UUID) -> Users | None:
    return db.get(Users, user_id)


def get_user_by_email(db: Session, email: str) -> Users | None:
    stmt = select(Users).where(Users.email == email)
    return db.scalar(stmt)


def get_user_by_username(db: Session, username: str, disambiguator: int) -> Users | None:
    stmt = select(Users).where(
        Users.username == username,
        Users.disambiguator == disambiguator,
    )
    return db.scalar(stmt)


# Account lifecycle
def create_user(
    db: Session,
    *,
    email: str,
    username: str,
    disambiguator: int,
    password_hash: str,
    is_bot: bool = False,
) -> Users:
    user = Users(
        email=email,
        username=username,
        disambiguator=disambiguator,
        password_hash=password_hash,
        is_bot=is_bot,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_last_login(db: Session, user_id: uuid.UUID) -> None:
    stmt = (
        update(Users)
        .where(Users.id == user_id)
        .values(last_login=datetime.now(timezone.utc))  # for timezone aware registry
    )
    db.execute(stmt)
    db.commit()


# ELO & stats (appelé à la FIN d'une partie)
def apply_game_result_to_users(
    db: Session,
    *,
    white: Users,
    black: Users,
    white_elo_after: int,
    black_elo_after: int,
    winner_id: uuid.UUID | None,
):
    """
    Met à jour les stats et ELO des deux joueurs.
    À appeler STRICTEMENT dans la transaction de fin de partie.
    """
    white.games_played += 1
    black.games_played += 1
    white.elo = white_elo_after
    black.elo = black_elo_after

    if winner_id is None:
        white.draws += 1
        black.draws += 1
    elif winner_id == white.id:
        white.wins += 1
        black.losses += 1
    else:
        black.wins += 1
        white.losses += 1

    db.add_all([white, black])
