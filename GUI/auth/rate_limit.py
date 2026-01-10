import time
from collections import defaultdict

FAILED_LOGINS = defaultdict(list)

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 5 * 60  # 5 minutes


def check_rate_limit(key: str) -> bool:
    """
    key = ip ou ip+email
    retourne True si autorisé
    """
    now = time.time()
    attempts = FAILED_LOGINS[key]
    FAILED_LOGINS[key] = [t for t in attempts if now - t < WINDOW_SECONDS]  # purge

    return len(FAILED_LOGINS[key]) < MAX_ATTEMPTS


def register_failure(key: str):
    FAILED_LOGINS[key].append(time.time())


def clear_failures(key: str):
    FAILED_LOGINS.pop(key, None)
