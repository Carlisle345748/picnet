from django.contrib.auth import authenticate, login, logout
from djongo.database import IntegrityError
from graphql import GraphQLError

from backend.errors import ERR_USERNAME_EXIST, ERR_LOGIN
from backend.types import *
from backend.utils import login_required, to_model_id


class CreateComment(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        photo_id = graphene.ID(required=True)
        comment = graphene.String(required=True)

    comment = graphene.Field(CommentSchema)

    @login_required
    def mutate(self, info, user_id, photo_id, comment):
        new_comment = Comment(
            comment=comment,
            user=User.objects.get(pk=to_model_id(user_id)),
            photo=Photo.objects.get(pk=to_model_id(photo_id))
        )
        new_comment.save()
        return CreateComment(comment=new_comment)


class UserInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)
    email = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    description = graphene.String(required=True)


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

    @login_required
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

    @login_required
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


class Logout(graphene.Mutation):
    class Argument:
        pass

    msg = graphene.String()

    def mutate(self, info):
        logout(info.context)
        return Logout(msg="success")
