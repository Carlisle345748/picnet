import hashlib
import secrets


def hash_password(password: str) -> (str, str):
    salt = secrets.token_hex(8)
    password_hash = hashlib.sha256((password+salt).encode(), usedforsecurity=True).hexdigest()
    return password_hash, salt


def check_password(password: str, salt: str, password_hash: str) -> bool:
    hashed = hashlib.sha256((password+salt).encode(), usedforsecurity=True).hexdigest()
    return hashed == password_hash
