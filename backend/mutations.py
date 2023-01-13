from typing import Optional, cast, Type, List

from algoliasearch_django import update_records, save_record
from algoliasearch_django.decorators import disable_auto_indexing
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from graphql import GraphQLError
from strawberry.file_uploads import Upload
from strawberry.types import Info
from strawberry_django import auth
from strawberry_django_plus import gql
from strawberry_django_plus.mutations import resolvers
from strawberry_django_plus.relay import GlobalID

from .errors import ERR_USERNAME_EXIST, ERR_LOGIN
from .models import Profile, Photo, Comment, PhotoTag, Feed
from .types import UserType, CommentType, PhotoType, ProfileType

UserModel = cast(Type[User], get_user_model())


@gql.type
class UpdateFollowerResult:
    user: UserType
    follow_user: UserType


# noinspection PyShadowingBuiltins
@gql.type
class Mutation:
    logout = auth.logout()

    @gql.django.mutation(handle_django_errors=False)
    def login(self, info: Info, username: str, password: str) -> UserType:
        request = info.context.request
        user = authenticate(request, username=username, password=password)
        if user is None:
            logout(request)
            raise GraphQLError(message="incorrect username or password", extensions=ERR_LOGIN)
        login(request, user)
        return cast(UserType, user)

    @gql.django.input_mutation(handle_django_errors=False)
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
        try:
            user = UserModel.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            Profile.objects.create(user=user, description=description)
            return cast(UserType, user)
        except IntegrityError:
            raise GraphQLError(message="username already exist", extensions=ERR_USERNAME_EXIST)

    @gql.django.input_mutation(handle_django_errors=False)
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

    @gql.django.input_mutation(handle_django_errors=False)
    @transaction.atomic
    def update_profile(self, info: Info, first_name: str, last_name: str, description: str) -> UserType:
        user = info.context.request.user
        user.first_name = first_name
        user.last_name = last_name
        user.profile.description = description
        user.save()
        user.profile.save()
        return cast(UserType, user)

    @gql.django.input_mutation(handle_django_errors=False)
    @transaction.atomic
    def update_photo_like(self, info: Info, photo_id: GlobalID, like: bool) -> PhotoType:
        user = info.context.request.user
        photo = Photo.objects.get(pk=photo_id.node_id)
        if like:
            photo.user_like.add(user)
        else:
            photo.user_like.remove(user)
        return cast(PhotoType, photo)

    @gql.django.input_mutation(handle_django_errors=False)
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

    @gql.django.input_mutation(handle_django_errors=False)
    def delete_photo(self, info: Info, id: GlobalID) -> PhotoType:
        photo = Photo.objects.get(pk=id.node_id)
        return cast(PhotoType, resolvers.delete(info, photo))

    @gql.django.input_mutation(handle_django_errors=False)
    def delete_comment(self, info: Info, id: GlobalID) -> CommentType:
        comment = Comment.objects.get(pk=id.node_id)
        comment = resolvers.delete(info, comment)

        qs = Photo.objects.filter(pk=comment.photo_id)
        update_records(model=Photo, qs=qs, photo_comments=qs[0].photo_comments())
        return cast(CommentType, comment)

    @gql.django.input_mutation(handle_django_errors=False)
    def upload_avatar(self, info: Info, avatar: Upload) -> ProfileType:
        profile = info.context.request.user.profile
        profile.avatar = avatar
        profile.save()
        return cast(ProfileType, profile)

    @gql.django.input_mutation(handle_django_errors=False)
    @disable_auto_indexing(model=Photo)
    @transaction.atomic
    def upload_photo(
            self,
            info: Info,
            photo: Upload,
            description: str,
            location: str,
            tags: List[str],
            ratio: float
    ) -> PhotoType:
        user = info.context.request.user
        photo = Photo(
            file=photo,
            ratio=ratio,
            user=user,
            description=description,
            location=location
        )
        photo.save()

        for tagName in tags:
            tag, _ = PhotoTag.objects.get_or_create(tag=tagName)
            photo.tags.add(tag)

        save_record(photo)

        followers = user.profile.follower.all()
        feeds = [Feed(user=follower, photo=photo) for follower in followers]
        Feed.objects.bulk_create(feeds)
        return cast(PhotoType, photo)
