import dataclasses
from typing import Any, Callable

from graphql import GraphQLError
from strawberry import Private
from strawberry.types import Info
from strawberry_django.permissions import DjangoPermissionExtension
from strawberry_django.utils.typing import UserType

from backend.errors import ERR_NOT_LOGIN


class IsAuthenticated(DjangoPermissionExtension):
    message: Private[str] = dataclasses.field(default="user is not authenticated.")

    def resolve_for_user(  # pragma: no cover
            self,
            resolver: Callable,
            user: UserType,
            *,
            info: Info,
            source: Any,
    ):
        if not user.is_authenticated or not user.is_active:
            raise GraphQLError(message=self.message, extensions=ERR_NOT_LOGIN)

        return resolver()
