from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from django.db import DatabaseError
from graphql import GraphQLError

from backend.types import *
from backend.utils import login_required, to_mongo_id, get_query_fields


class CreateComment(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        photo_id = graphene.ID(required=True)
        comment = graphene.String(required=True)

    comment = graphene.Field(CommentSchema)

    # TODO only query necessary field
    # TODO use add_to_set
    @login_required
    def mutate(self, info, user_id, photo_id, comment):
        photo = Photo.objects.get(id=to_mongo_id(photo_id))
        c = Comment(
            date_time=timezone.now(),
            comment=comment,
            user=User.objects.get(id=to_mongo_id(user_id))
        )
        photo.comments.append(c)
        photo.save()
        return CreateComment(comment=c)


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
            auth_user = AuthUser.objects.create_user(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            base_user = BaseUser.objects.only('id').get(id=auth_user.id)
            user = User(base_user=base_user, description=user_data.description).save()
            return CreateUser(user=user)
        except DatabaseError:
            raise GraphQLError(message="username already exist",
                               extensions={"code": 1002, "msg": "username already exist"})


class LikePhoto(graphene.Mutation):
    class Arguments:
        photo_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)
        like = graphene.Boolean(default_value=True)

    photo = graphene.Field(PhotoSchema)

    def mutate(self, info, photo_id, user_id, like):
        user_id = to_mongo_id(user_id)
        photo_id = to_mongo_id(photo_id)
        if like:
            Photo.objects(id=photo_id).update_one(add_to_set__user_like=user_id)
        else:
            Photo.objects(id=photo_id).update_one(pull__user_like=user_id)
        required_fields = get_query_fields(info, Photo, depth=1)
        return LikePhoto(photo=Photo.objects.only(*required_fields).get(id=photo_id))


class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserSchema)

    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise GraphQLError(message="incorrect username or password",
                               extensions={"code": 1001, "msg": "incorrect username or password"})
        login(info.context, user)
        base_user = BaseUser.objects.only('id').get(id=user.id)
        required_fields = get_query_fields(info, User, depth=1)
        return Login(user=User.objects.only(*required_fields).get(base_user=base_user))


class Logout(graphene.Mutation):
    class Argument:
        pass

    msg = graphene.String()

    def mutate(self, info):
        logout(info.context)
        return Logout(msg="success")
