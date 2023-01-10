from django.contrib.auth import authenticate, login, logout
from django.db import transaction, IntegrityError
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from algoliasearch_django import save_record, get_adapter, AlgoliaIndex
from algoliasearch_django.decorators import disable_auto_indexing

from backend.errors import ERR_USERNAME_EXIST, ERR_LOGIN, ERR_ALREADY_DELETE
from backend.types import *
from backend.utils import to_model_id


class ProfileInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    description = graphene.String(default="")


class UpdateProfile(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        profile_data = ProfileInput(required=True)

    user = graphene.Field(UserSchema)

    def mutate(self, info, user_id, profile_data: ProfileInput):
        user = User.objects.select_related('profile').get(pk=to_model_id(user_id))
        user.first_name = profile_data.first_name
        user.last_name = profile_data.last_name
        user.profile.description = profile_data.description
        user.profile.save()
        user.save()
        return UpdateProfile(user=user)


class CreateComment(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        photo_id = graphene.ID(required=True)
        comment = graphene.String(required=True)

    comment = graphene.Field(CommentSchema)

    def mutate(self, info, user_id, photo_id, comment):
        qs = Photo.objects.filter(pk=to_model_id(photo_id))
        new_comment = Comment(
            comment=comment,
            user=User.objects.get(pk=to_model_id(user_id)),
            photo=qs[0]
        )
        new_comment.save()

        photo_index: AlgoliaIndex = get_adapter(Photo)
        photo_index.update_records(
            qs=qs,
            photo_comments={'_operation': 'Add', 'value': comment}
        )

        return CreateComment(comment=new_comment)


class UserInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)
    email = graphene.String(default="")
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    description = graphene.String(default="")


class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput(required=True)

    user = graphene.Field(UserSchema)

    def mutate(self, info, user_data):
        try:
            user = User.objects.create_user(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            Profile(user=user, description=user_data.description).save()
            return CreateUser(user=user)
        except IntegrityError:
            raise GraphQLError(message="username already exist", extensions=ERR_USERNAME_EXIST)


class UpdatePhotoLike(graphene.Mutation):
    class Arguments:
        photo_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)
        like = graphene.Boolean(default_value=True)

    photo = graphene.Field(PhotoSchema)

    def mutate(self, info, photo_id, user_id, like):
        user = User.objects.get(pk=to_model_id(user_id))
        photo = Photo.objects.get(pk=to_model_id(photo_id))
        if like:
            photo.user_like.add(user)
        else:
            photo.user_like.remove(user)
        return UpdatePhotoLike(photo=photo)


class UpdateFollower(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        follow_id = graphene.ID(required=True)
        follow = graphene.Boolean(required=True)

    user = graphene.Field(UserSchema)
    follow_user = graphene.Field(UserSchema)

    def mutate(self, info, user_id, follow_id, follow):
        user = User.objects.get(pk=to_model_id(user_id))
        follow_user = User.objects.get(pk=to_model_id(follow_id))
        if follow:
            user.profile.following.add(follow_user)
            follow_user.profile.follower.add(user)
        else:
            user.profile.following.remove(follow_user)
            follow_user.profile.follower.remove(user)
        return UpdateFollower(user=user, follow_user=follow_user)


class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserSchema)

    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise GraphQLError(message="incorrect username or password", extensions=ERR_LOGIN)
        login(info.context, user)
        return Login(user=user)


class UploadPhoto(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        description = graphene.String(required=True)
        location = graphene.String(required=True)
        tags = graphene.List(graphene.String, required=True)
        image = Upload(required=True)
        ratio = graphene.Float(required=True)

    photo = graphene.Field(PhotoSchema)

    def mutate(self, info, user_id, description, location, tags, image, ratio):
        with transaction.atomic(), disable_auto_indexing():
            user = User.objects.get(pk=to_model_id(user_id))
            photo = Photo(
                file_name=image,
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

            return UploadPhoto(photo=photo)


class UploadAvatar(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        avatar = Upload(required=True)

    profile = graphene.Field(ProfileSchema)

    def mutate(self, info, user_id, avatar):
        profile = Profile.objects.get(user_id=to_model_id(user_id))
        profile.avatar = avatar
        profile.save()
        return UploadAvatar(profile=profile)


class DeletePhoto(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        photo_id = graphene.ID(required=True)

    code = graphene.Int()
    msg = graphene.String()

    def mutate(self, info, user_id, photo_id):
        try:
            photo = Photo.objects.get(pk=to_model_id(photo_id), user_id=to_model_id(user_id))
            photo.delete()
            return DeletePhoto(code=0, msg="success")
        except Photo.DoesNotExist:
            return DeletePhoto(code=ERR_ALREADY_DELETE['code'], msg=ERR_ALREADY_DELETE['msg'])


class DeleteComment(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        comment_id = graphene.ID(required=True)

    code = graphene.Int()
    msg = graphene.String()

    def mutate(self, info, user_id, comment_id):
        try:
            comment = Comment.objects.get(
                pk=to_model_id(comment_id),
                user_id=to_model_id(user_id)
            )
            comment.delete()

            qs = Photo.objects.filter(pk=comment.photo_id)
            photo_index: AlgoliaIndex = get_adapter(Photo)
            photo_index.update_records(qs, photo_comments=qs[0].photo_comments())

            return DeleteComment(code=0, msg="success")
        except Comment.DoesNotExist:
            return DeleteComment(code=ERR_ALREADY_DELETE['code'], msg=ERR_ALREADY_DELETE['msg'])


class Logout(graphene.Mutation):
    class Argument:
        pass

    msg = graphene.String()

    def mutate(self, info):
        logout(info.context)
        return Logout(msg="success")
