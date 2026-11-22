
import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def hash_password(password: str, salt: str | None = None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310000
    ).hex()

    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str):
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, password_hash)


def register_user(db: Session, username: str, password: str):
    existing_user = db.scalar(
        select(User).where(User.username == username)
    )

    if existing_user:
        return None

    password_hash, salt = hash_password(password)

    user = User(
        username=username,
        password_hash=password_hash,
        salt=salt
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.scalar(
        select(User).where(User.username == username)
    )

    if not user:
        return None

    if not verify_password(password, user.password_hash, user.salt):
        return None

    return user
