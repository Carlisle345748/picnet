import hashlib
import secrets

from graphql import GraphQLError


def hash_password(password: str) -> (str, str):
    salt = secrets.token_hex(8)
    password_hash = hashlib.sha256((password+salt).encode(), usedforsecurity=True).hexdigest()
    return password_hash, salt


def check_password(password: str, salt: str, password_hash: str) -> bool:
    hashed = hashlib.sha256((password+salt).encode(), usedforsecurity=True).hexdigest()
    return hashed == password_hash


def login_required(func):
    def authenticate(*args, **kwargs):
        info = args[1]
        if "user_id" not in info.context.session:
            raise GraphQLError(message="user not logged in")
        return func(*args, **kwargs)

    return authenticate