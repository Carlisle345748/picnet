from typing import cast, Type, Iterable

import strawberry.django
import strawberry_django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from strawberry import auto
from strawberry import relay
from strawberry.types import Info
from strawberry import Parent
from strawberry_django.relay import ListConnectionWithTotalCount

from . import models
from .models import Photo

UserModel = cast(Type[AbstractUser], get_user_model())


@strawberry.django.filter(UserModel, lookups=True)
class UserFilter:
    id: auto
    username: auto


@strawberry.django.order(models.Photo)
class PhotoOrder:
    date_time: auto


@strawberry.django.filter(models.Photo)
class PhotoFiler:
    user: auto


@strawberry_django.type(models.Profile)
class ProfileType(relay.Node):
    user: "UserType"
    description: auto
    follower: ListConnectionWithTotalCount["UserType"] = strawberry_django.connection()
    following: ListConnectionWithTotalCount["UserType"] = strawberry_django.connection()

    @strawberry_django.field(name="avatar", only=["avatar"])
    @staticmethod
    def avatar_url(parent: Parent[models.Profile]) -> str:
        return parent.avatar_url

    @strawberry_django.field(prefetch_related=["follower"])
    @staticmethod
    def is_following(parent: Parent[models.Profile], info: Info) -> bool:
        return parent.follower.filter(pk=info.context.request.user.id).exists()


@strawberry_django.type(models.PhotoTag)
class PhotoTagType(relay.Node):
    tag: auto


@strawberry_django.type(models.Photo, order=PhotoOrder, filters=PhotoFiler)
class PhotoType(relay.Node):
    file: auto
    ratio: auto
    date_time: auto
    user: "UserType"
    user_like: ListConnectionWithTotalCount["UserType"] = strawberry_django.connection()
    description: auto
    tags: ListConnectionWithTotalCount[PhotoTagType] = strawberry_django.connection()
    location: auto
    comments: "ListConnectionWithTotalCount[CommentType]" = strawberry_django.connection(name="comments")

    @strawberry_django.field(only=["file"])
    @staticmethod
    def url(parent: Parent[models.Photo]) -> str:
        return parent.file.url

    @strawberry_django.field(prefetch_related=["user_like"])
    @staticmethod
    def is_like(parent: Parent[models.Photo], info: Info) -> bool:
        return parent.user_like.filter(pk=info.context.request.user.id).exists()

    @strawberry_django.field(only=["file", "ratio"])
    @staticmethod
    def ratio(parent: Parent[models.Photo]) -> float:
        return parent.ratio if parent.ratio != -1 else parent.file.height / parent.file.width


@strawberry_django.type(UserModel, filters=UserFilter, select_related="profile")
class UserType(relay.Node):
    username: auto
    first_name: auto
    last_name: auto
    email: auto
    profile: "ProfileType"

    @strawberry_django.connection(ListConnectionWithTotalCount[PhotoType], filters=PhotoFiler, order=PhotoOrder)
    @staticmethod
    def photos(parent: Parent[UserModel]) -> Iterable["PhotoType"]:
        return Photo.objects.filter(user_id=parent.id)


@strawberry_django.type(models.Comment)
class CommentType(relay.Node):
    comment: auto
    date_time: auto
    photo: "PhotoType"
    user: "UserType"


@strawberry.django.order(models.Feed)
class FeedOrder:
    date_time: auto


@strawberry.django.filter(models.Feed)
class FeedFilter:
    user: "UserType"


@strawberry_django.type(models.Feed, order=FeedOrder, filters=FeedFilter)
class FeedType(relay.Node):
    user: "UserType"
    photo: "PhotoType"
    date_time: auto


@strawberry.type
class HotTag:
    tag: str
    count: int


@strawberry.type
class Location:
    full_address: str
    main: str
    secondary: str
