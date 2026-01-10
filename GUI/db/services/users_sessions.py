import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session as DB_Session

from GUI.db.models import Sessions, Users


# CONFIG
SESSION_DURATION = timedelta(days=7)
SESSION_REFRESH_THRESHOLD = timedelta(hours=1)


# CREATION
def create_session(
    db: DB_Session,
    *,
    user: Users,
    ip_address: str | None,
    user_agent: str | None,
    duration: timedelta = SESSION_DURATION,
) -> Sessions:
    now = datetime.now(timezone.utc)
    session = Sessions(
        user_id=user.id,
        created_at=now,
        last_seen_at=now,
        expires_at=now + duration,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
    )
    db.add(session)
    return session


# LOOKUP / VALIDATION
def get_active_session(db: DB_Session, session_id: uuid.UUID) -> Sessions | None:
    stmt = select(Sessions).where(Sessions.id == session_id, Sessions.is_active.is_(True))
    return db.scalar(stmt)


def validate_session(db: DB_Session, session_id: uuid.UUID) -> Sessions | None:
    """
    Validation complète :
    - existe
    - active
    - non expirée
    """
    session = get_active_session(db, session_id)
    if not session:
        return None
    if session.is_expired():
        revoke_session(db, session=session, reason="expired")
        return None
    return session


# REFRESH / TOUCH
def touch_session(db: DB_Session, *, session: Sessions, refresh: bool = True) -> None:
    """
    - met à jour last_seen_at
    - prolonge expires_at si proche de l'expiration
    """
    now = datetime.now(timezone.utc)
    session.last_seen_at = now
    if refresh and session.expires_at - now < SESSION_REFRESH_THRESHOLD:
        session.expires_at = now + SESSION_DURATION
    db.add(session)


# LOGOUT / REVOCATION
def revoke_session(db: DB_Session, *, session: Sessions, reason: str = "user") -> None:
    session.is_active = False
    session.revoked_at = datetime.now(timezone.utc)
    session.logout_reason = reason
    db.add(session)


def revoke_all_sessions_for_user(
    db: DB_Session, *, user_id: uuid.UUID, reason: str = "security"
) -> int:
    """
    Utile pour :
    - changement de mot de passe
    - ban
    - admin kick
    """
    stmt = (
        update(Sessions)
        .where(
            Sessions.user_id == user_id,
            Sessions.is_active.is_(True),
        )
        .values(
            is_active=False,
            revoked_at=datetime.now(timezone.utc),
            logout_reason=reason,
        )
    )
    result = db.execute(stmt)
    return result.rowcount
