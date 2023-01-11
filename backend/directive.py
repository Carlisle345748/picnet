import dataclasses
import functools
from typing import Any

import strawberry
from graphql import GraphQLResolveInfo, GraphQLError
from strawberry import Private
from strawberry.schema_directive import Location
from strawberry.utils.await_maybe import AwaitableOrValue
from strawberry_django_plus.directives import SchemaDirectiveHelper
from strawberry_django_plus.permissions import ConditionDirective, clear_checker
from strawberry_django_plus.utils import aio
from strawberry_django_plus.utils.typing import UserType

from backend.errors import ERR_NOT_LOGIN


@strawberry.schema_directive(
    locations=[Location.FIELD_DEFINITION],
    description="Can only be resolved by authenticated users.",
)
class IsAuthenticated(ConditionDirective):
    """Mark a field as only resolvable by authenticated users."""

    message: Private[str] = dataclasses.field(default="user is not authenticated.")

    def check_condition(
            self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ) -> bool:
        return user.is_authenticated and user.is_active

    def resolve_retval(
            self,
            helper: SchemaDirectiveHelper,
            root: Any,
            info: GraphQLResolveInfo,
            retval: Any,
            auth_ok: AwaitableOrValue[bool],
    ):
        # If this is not bool, assume async. Avoid is_awaitable since it is slow
        if not isinstance(auth_ok, bool):
            return aio.resolve_async(
                auth_ok,
                functools.partial(self.resolve_retval, helper, root, info, retval),
            )

        # Make sure any chained resolvers will not try to validate the result again
        clear_checker()

        if auth_ok:
            if callable(retval):
                retval = retval()
            return retval

        raise GraphQLError(message=self.message, extensions=ERR_NOT_LOGIN)
