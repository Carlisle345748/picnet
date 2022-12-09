from graphql import GraphQLError

from backend.types import *
from backend.utils import login_required, hash_password, check_password, to_mongo_id


class CreateComment(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        photo_id = graphene.ID(required=True)
        comment = graphene.String(required=True)

    comment = graphene.Field(CommentSchema)

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
    login_name = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    location = graphene.String(required=True)
    description = graphene.String(required=True)
    occupation = graphene.String(required=True)


class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput(required=True)

    user = graphene.Field(UserSchema)

    def mutate(self, info, user_data):
        if User.objects(login_name=user_data.login_name).count() != 0:
            raise GraphQLError(message="login name exist")

        password_hash, salt = hash_password(user_data.password)
        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            location=user_data.location,
            description=user_data.description,
            occupation=user_data.occupation,
            login_name=user_data.login_name,
            password=password_hash,
            salt=salt
        ).save()
        return CreateUser(user=user)


class LikePhoto(graphene.Mutation):
    class Arguments:
        photo_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)
        like = graphene.Boolean(default_value=True)

    photo = graphene.Field(PhotoSchema)

    def mutate(self, info, photo_id, user_id, like):
        user_id = to_mongo_id(user_id)
        photo_id = to_mongo_id(photo_id)
        photo = Photo.objects.get(id=photo_id)
        photo.user_like = [user for user in photo.user_like if str(user.id) != user_id]
        if like:
            photo.user_like.append(User.objects.get(id=user_id))
        photo.save()
        return LikePhoto(photo=photo)


class Login(graphene.Mutation):
    class Arguments:
        login_name = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserSchema)

    def mutate(self, info, login_name, password):
        user = User.objects(login_name=login_name)
        if not user:
            raise GraphQLError("user not exist", extensions={"code": 1001, "msg": "user not exist"})
        user = user[0]

        if not check_password(password, user.salt, user.password):
            raise GraphQLError("incorrect password", extensions={"code": 1002, "msg": "incorrect password"})

        info.context.session['user_id'] = str(user.id)
        return Login(user=user)


class Logout(graphene.Mutation):
    class Argument:
        pass

    msg = graphene.String()

    def mutate(self, info):
        del info.context.session['user_id']
        return Logout(msg="success")
