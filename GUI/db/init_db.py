import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from GUI.db.base import Base
from GUI.db.models import Users
from GUI.db.services.users import get_user_by_email, create_user

from hashlib import sha256  # DEV ONLY  # TODO : à remplacer plus tard


DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/chess_overdrive"

# DATABASE_URL = os.getenv("DATABASE_URL")
# if DATABASE_URL is None:
#     raise ValueError("DATABASE_URL can't be 'None'.")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def dev_hash_password(password: str) -> str:
    """⚠️ Hash simplifié DEV ONLY"""
    return sha256(password.encode("utf-8")).hexdigest()


DEBUG_USERS = [
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "email": "alice@test.local",
        "username": "Alice",
        "disambiguator": 1,
        "password": "alice",
        "is_bot": False,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "email": "bob@test.local",
        "username": "Bob",
        "disambiguator": 1,
        "password": "bob",
        "is_bot": False,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "email": "charlie@test.local",
        "username": "Charlie",
        "disambiguator": 1,
        "password": "charlie",
        "is_bot": False,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-00000000dead"),
        "email": "bot@test.local",
        "username": "Bot",
        "disambiguator": 0,
        "password": "bot",
        "is_bot": True,
    },
]


# INIT FUNCTION
def init_db():
    """
    À appeler au démarrage de la GUI.
    - crée les tables si absentes
    - crée les users de debug si absents
    """
    print("🧱 Initialisation de la base de données...")

    Base.metadata.create_all(bind=engine)
    print("✅ Tables OK")

    db = SessionLocal()

    try:
        for u in DEBUG_USERS:
            existing = get_user_by_email(db, u["email"])
            if existing:
                continue
            user = Users(
                id=u["id"],
                email=u["email"],
                username=u["username"],
                disambiguator=u["disambiguator"],
                password_hash=dev_hash_password(u["password"]),
                is_bot=u["is_bot"],
            )
            db.add(user)
            print(f"👤 User créé : {u['username']}#{u['disambiguator']}")
        db.commit()
        print("🎉 Initialisation DB terminée")
    finally:
        db.close()
