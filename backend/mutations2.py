from typing import Optional, cast, Type

from algoliasearch_django import update_records
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction
from strawberry.types import Info
from strawberry_django import auth
from strawberry_django_plus import gql, relay
from strawberry_django_plus.mutations import resolvers
from strawberry_django_plus.relay import GlobalID

from .directive import IsAuthenticated
from .models import Profile, Photo, Comment
from .types2 import UserType, CommentType, PhotoType

UserModel = cast(Type[User], get_user_model())


@gql.type
class UpdateFollowerResult:
    user: UserType
    follow_user: UserType


# noinspection PyShadowingBuiltins
@gql.type
class Mutation:
    login: UserType = auth.login()

    logout = auth.logout()

    @relay.input_mutation(directives=[IsAuthenticated()])
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
    @transaction.atomic
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
    @transaction.atomic
    def update_photo_like(self, info: Info, photo_id: GlobalID, like: bool) -> PhotoType:
        user = info.context.request.user
        photo = Photo.objects.get(pk=photo_id.node_id)
        if like:
            photo.user_like.add(user)
        else:
            photo.user_like.remove(user)
        return cast(PhotoType, photo)

    @relay.input_mutation
    @transaction.atomic
    def update_follower(self, info: Info, user_id: GlobalID, follow: bool) -> UpdateFollowerResult:
        logged_in_user: User = info.context.request.user
        follow_user: User = UserModel.objects.get(pk=user_id.node_id)
        if follow:
            logged_in_user.profile.following.add(follow_user)
            follow_user.profile.follower.add(logged_in_user)
        else:
            logged_in_user.profile.following.remove(follow_user)
            follow_user.profile.follower.remove(logged_in_user)
        return UpdateFollowerResult(user=logged_in_user, follow_user=follow_user)

    @relay.input_mutation
    def delete_photo(self, info: Info, id: GlobalID) -> PhotoType:
        photo = Photo.objects.get(pk=id.node_id)
        return cast(PhotoType, resolvers.delete(info, photo))

    @relay.input_mutation
    def delete_comment(self, info: Info, id: GlobalID) -> CommentType:
        comment = Comment.objects.get(pk=id.node_id)
        comment = resolvers.delete(info, comment)

        qs = Photo.objects.filter(pk=comment.photo_id)
        update_records(model=Photo, qs=qs, photo_comments=qs[0].photo_comments())
        return cast(CommentType, comment)
