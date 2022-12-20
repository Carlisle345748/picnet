import hashlib
import secrets
from typing import List

from django.conf import settings
from graphene.relay.node import from_global_id
from graphene.utils.str_converters import to_snake_case
from graphene_mongo.utils import get_query_fields as get_fields
from graphql import GraphQLError, GraphQLResolveInfo
from mongoengine.base import TopLevelDocumentMetaclass

from backend.errors import ERR_NOT_LOGIN


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
    return from_global_id(global_id).id


def get_query_fields(info: GraphQLResolveInfo, model: TopLevelDocumentMetaclass, depth=0) -> List[str]:
    def collect(f: dict, d: int = 0):
        return f if d == 0 else collect(f[next(iter(f))], d - 1)

    query_fields = []
    fields = collect(get_fields(info), depth)
    for field in fields:
        if to_snake_case(field) in model._fields_ordered:
            query_fields.append(to_snake_case(field))
    return query_fields


def save_image(img) -> str:
    img_hash = hashlib.md5(img.file.read()).hexdigest()
    suffix = img.name[img.name.rindex(".") + 1:]
    filename = f'{img_hash}.{suffix}'

    with open(f'{settings.MEDIA_ROOT}/{filename}', 'wb') as f:
        img.file.seek(0)
        f.write(img.file.read())
    return filename
