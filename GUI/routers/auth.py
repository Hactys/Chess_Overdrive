import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from GUI.auth.dependencies import get_current_user
from GUI.core.templates import templates
from GUI.db.models.user import Users
from GUI.db.services.session import get_db_session
from GUI.db.services.users import get_user_by_email
from GUI.db.services.users_sessions import create_session, validate_session, revoke_session
from GUI.db.services.security import verify_password
from GUI.auth.rate_limit import check_rate_limit, register_failure, clear_failures


router = APIRouter()

SESSION_COOKIE_NAME = "session_id"
SESSION_MAX_AGE = 7 * 24 * 3600  # 7 jours


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db_session)):
    """
    Page de login.
    Si l'utilisateur est déjà authentifié, redirige vers le lobby.
    """
    session_id = request.cookies.get("session_id")
    if session_id:
        try:
            session = validate_session(db, uuid.UUID(session_id))
            if session:
                return RedirectResponse(url="/", status_code=303)
        except Exception:
            pass  # cookie invalide → on affiche la page login

    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db_session),
):
    is_htmx = request.headers.get("HX-Request") == "true"
    ip = request.client.host  # type: ignore
    rate_key = f"{ip}:{email}"

    if not check_rate_limit(rate_key):
        if is_htmx:
            return (
                "<div>Trop de tentatives. Réessaie dans quelques minutes.</div>",
                status.HTTP_429_TOO_MANY_REQUESTS,
            )
        raise HTTPException(status_code=429, detail="Too many login attempts. Try later.")

    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        register_failure(rate_key)
        if is_htmx:
            return ("<div>Identifiants invalides</div>", status.HTTP_401_UNAUTHORIZED)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    clear_failures(rate_key)
    session = create_session(
        db, user=user, ip_address=ip, user_agent=request.headers.get("user-agent")
    )
    db.commit()

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=str(session.id),
        httponly=True,  # not accessible in JS
        secure=True,  # HTTPS only
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )

    if is_htmx:
        response.headers["HX-Redirect"] = "/"
        return ""

    return {
        "user_id": str(user.id),
        "username": user.username,
        "disambiguator": user.disambiguator,
        "elo": user.elo,
    }


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db_session)):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        response.delete_cookie(SESSION_COOKIE_NAME)
        return {"ok": True}

    session = validate_session(db, uuid.UUID(session_id))
    if session:
        revoke_session(db, session=session, reason="user")
        db.commit()

    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    is_htmx = request.headers.get("HX-Request") == "true"
    if is_htmx:
        response.headers["HX-Redirect"] = "/login"
        return ""
    return {"ok": True}


@router.get("/profile")
def profile(user: Users = Depends(get_current_user)):
    return {"username": user.username, "elo": user.elo}
