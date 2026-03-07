import base64
import hashlib

import bcrypt


def _pre_hash(plain_password: str) -> bytes:
    """SHA-256 pre-hash to bypass bcrypt's 72-byte input limit."""
    digest = hashlib.sha256(plain_password.encode()).digest()
    return base64.b64encode(digest)


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(_pre_hash(plain_password), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_pre_hash(plain_password), hashed_password.encode())

