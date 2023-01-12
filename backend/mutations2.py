from typing import Optional, cast, Type

from algoliasearch_django import update_records
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction
from strawberry.types import Info
from strawberry_django import auth
from strawberry_django_plus import gql, relay
from strawberry_django_plus.relay import GlobalID

from . import models
from .models import Profile, Photo, Comment
from .types2 import UserType, CommentType, PhotoType

UserModel = cast(Type[User], get_user_model())


@gql.django.partial(UserModel)
class UserPartialInput(gql.NodeInputPartial):
    first_name: gql.auto
    last_name: gql.auto
    profile: "ProfileInput"


@gql.django.partial(models.Profile)
class ProfileInput:
    description: gql.auto


@gql.django.partial(models.Photo)
class PhotoUserLikeInput(gql.NodeInputPartial):
    user_like: gql.auto


# noinspection PyShadowingBuiltins
@gql.type
class Mutation:
    login: UserType = auth.login()

    logout = auth.logout()

    @relay.input_mutation
    @transaction.atomic
    def create_user(
            self,
            first_name: str,
            last_name: str,
            username: str,
            password: str,
            email: Optional[str] = "",
            description: Optional[str] = ""
    ) -> UserType:
        user = UserModel.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        Profile.objects.create(user=user, description=description)
        return cast(UserType, user)

    @relay.input_mutation
    def create_comment(self, info: Info, photo_id: GlobalID, comment: str) -> CommentType:
        new_comment = Comment.objects.create(
            comment=comment,
            user=info.context.request.user,
            photo_id=photo_id.node_id,
        )
        update_records(
            model=Photo,
            qs=Photo.objects.filter(pk=photo_id.node_id),
            photo_comments={'_operation': 'Add', 'value': comment}
        )
        return cast(CommentType, new_comment)

    @relay.input_mutation
    @transaction.atomic
    def update_profile(self, info: Info, id: GlobalID, first_name: str, last_name: str, description: str) -> UserType:
        user = id.resolve_node(info, ensure_type=UserModel)
        user.first_name = first_name
        user.last_name = last_name
        user.profile.description = description
        user.save()
        user.profile.save()
        return cast(UserType, user)

    @relay.input_mutation
    def update_photo_like(self, info: Info, photo_id: GlobalID, like: bool) -> PhotoType:
        user = info.context.request.user
        photo = photo_id.resolve_node(info, ensure_type=Photo)
        if like:
            photo.user_like.add(user)
            photo.like_by_me = [user]
        else:
            photo.user_like.remove(user)
            photo.like_by_me = []
        return cast(PhotoType, photo)
