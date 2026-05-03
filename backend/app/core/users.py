from pathlib import Path
from typing import Dict, Optional
import json
import secrets
import hashlib

USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"


def _ensure_users_file() -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps({}))


def _load_users() -> Dict[str, dict]:
    _ensure_users_file()
    try:
        return json.loads(USERS_FILE.read_text())
    except Exception:
        return {}


def _save_users(users: Dict[str, dict]) -> None:
    USERS_FILE.write_text(json.dumps(users, indent=2))


def create_user(username: str, email: Optional[str], password: str) -> dict:
    users = _load_users()
    if username in users:
        raise ValueError("username_taken")

    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    users[username] = {"username": username, "email": email, "salt": salt, "password_hash": pwd_hash}
    _save_users(users)
    return {"username": username, "email": email}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    users = _load_users()
    user = users.get(username)
    if not user:
        return None
    salt = user.get("salt")
    stored_hash = user.get("password_hash")
    if not salt or not stored_hash:
        return None
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    if secrets.compare_digest(pwd_hash, stored_hash):
        return {"username": user.get("username"), "email": user.get("email")}
    return None
