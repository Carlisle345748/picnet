from abc import ABC
from typing import cast, Type, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import Prefetch
from strawberry_django import auth
from strawberry_django_plus import gql
from strawberry_django_plus.directives import SchemaDirectiveExtension
from strawberry_django_plus.gql import relay
from strawberry_django_plus.optimizer import DjangoOptimizerExtension

from . import models
from .directive import IsAuthenticated

UserModel = cast(Type[AbstractUser], get_user_model())


@gql.django.filter(UserModel, lookups=True)
class UserFilter:
    id: gql.auto
    username: gql.auto


@gql.django.type(UserModel, filters=UserFilter)
class UserType(relay.Node, ABC):
    username: gql.auto
    first_name: gql.auto
    last_name: gql.auto
    email: gql.auto
    profile: "ProfileType"
    photo_set: "relay.Connection[PhotoType]" = gql.django.connection(name="photos")


@gql.django.type(models.Profile, directives=[IsAuthenticated()])
class ProfileType(relay.Node, ABC):
    user: "UserType"
    description: gql.auto
    follower: relay.Connection[UserType]
    following: relay.Connection[UserType]

    @gql.django.field(only=["avatar"])
    def avatar(self, root: models.Profile) -> str:
        return root.avatar.url if root.avatar.name != "" else ""

    @gql.django.field(prefetch_related=[
        lambda info: Prefetch(
            "follower",
            queryset=UserModel.objects.filter(pk=info.context.request.user.id),
            to_attr="followed_by_me"
        )
    ])
    def is_following(self) -> bool:
        return len(self.followed_by_me) > 0


@gql.django.type(models.PhotoTag, directives=[IsAuthenticated()])
class PhotoTagType(relay.Node, ABC):
    tag: gql.auto


@gql.django.order(models.Photo)
class PhotoOrder:
    date_time: gql.auto


@gql.django.type(models.Photo, directives=[IsAuthenticated()], order=PhotoOrder)
class PhotoType(relay.Node, ABC):
    file_name: gql.auto
    ratio: gql.auto
    date_time: gql.auto
    user: "UserType"
    user_like: relay.Connection[UserType]
    description: gql.auto
    tags: relay.Connection[PhotoTagType]
    location: gql.auto
    comment_set: "relay.Connection[CommentType]" = gql.django.connection(name="comments")

    @gql.django.field(only=["file_name"])
    def url(self, root: models.Photo) -> str:
        return root.file_name.url

    @gql.django.field(
        prefetch_related=[
            lambda info: Prefetch(
                "user_like",
                queryset=UserModel.objects.filter(info.context.request.user.id),
                to_attr="like_by_me")
        ]
    )
    def is_like(self) -> bool:
        return len(self.like_by_me) > 0

    @gql.django.field(only=["file_name", "ratio"])
    def ratio(self, root: models.Photo) -> float:
        return root.ratio if root.ratio != -1 else root.file_name.height / root.file_name.width


@gql.django.type(models.Comment, directives=[IsAuthenticated()])
class CommentType(relay.Node, ABC):
    comment: gql.auto
    date_time = gql.auto
    photo: "PhotoType"
    user: "UserType"


@gql.django.order(models.Feed)
class FeedOrder:
    date_time: gql.auto


@gql.django.type(models.Feed, directives=[IsAuthenticated()], order=FeedOrder)
class FeedType(relay.Node, ABC):
    user: "UserType"
    photo: "PhotoType"
    date_time: gql.auto


@gql.type
class Query:
    user: Optional[UserType] = gql.django.node(directives=[IsAuthenticated()])

    users: relay.Connection[UserType] = gql.django.connection(directives=[IsAuthenticated()])

    profile: Optional[relay.Node] = gql.django.node()

    profiles: relay.Connection[ProfileType] = gql.django.connection()

    photo: Optional[PhotoType] = gql.django.node()

    photos: relay.Connection[PhotoType] = gql.django.connection()

    feeds: relay.Connection[FeedType] = gql.django.connection()


@gql.type
class Mutation:
    login: UserType = auth.login()
    logout = auth.logout()


schema = gql.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        SchemaDirectiveExtension,
        DjangoOptimizerExtension,
    ],
)
