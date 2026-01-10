import uuid
from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session

from GUI.db.services.session import get_db_session
from GUI.db.services.users_sessions import validate_session, touch_session
from GUI.db.models import Users


def get_current_user(request: Request, db: Session = Depends(get_db_session)) -> Users:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401)

    session = validate_session(db, uuid.UUID(session_id))
    if not session:
        raise HTTPException(status_code=401)

    touch_session(db, session=session)
    db.commit()

    return session.user
