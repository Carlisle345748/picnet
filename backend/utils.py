import hashlib
import secrets

from django.core.files.storage import FileSystemStorage
from graphene.relay.node import from_global_id
from graphql import GraphQLError
from strawberry_django_plus import relay

from backend.errors import ERR_NOT_LOGIN

fs = FileSystemStorage()


def hash_password(password: str) -> (str, str):
    salt = secrets.token_hex(8)
    password_hash = hashlib.sha256((password + salt).encode(), usedforsecurity=True).hexdigest()
    return password_hash, salt


def check_password(password: str, salt: str, password_hash: str) -> bool:
    hashed = hashlib.sha256((password + salt).encode(), usedforsecurity=True).hexdigest()
    return hashed == password_hash


def login_required(func):
    def authenticate(*args, **kwargs):
        info = args[1]
        if not info.context.user.is_authenticated:
            raise GraphQLError(message="user not logged in", extensions=ERR_NOT_LOGIN)
        return func(*args, **kwargs)

    return authenticate


def to_model_id(global_id: str) -> str:
    return relay.from_base64(global_id)[1]


def save_image(img) -> str:
    img_hash = hashlib.md5(img.read()).hexdigest()
    suffix = img.name[img.name.rindex(".") + 1:]
    filename = f'{img_hash}.{suffix}'
    if not fs.exists(filename):
        img.seek(0)
        fs.save(filename, img)
    return filename
