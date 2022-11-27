import graphene
from django.utils import timezone
from graphene_mongo import MongoengineObjectType
from graphql import GraphQLError

from .models import User, Photo, Comment


class UserSchema(MongoengineObjectType):
    class Meta:
        model = User


class PhotoSchema(MongoengineObjectType):
    class Meta:
        model = Photo

    url = graphene.String()

    def resolve_url(self, info):
        return "/media/" + self.file_name

    def resolve_date_time(self, info):
        return timezone.make_aware(self.date_time, timezone.utc)


class CommentSchema(MongoengineObjectType):
    class Meta:
        model = Comment

    def resolve_date_time(self, info):
        return timezone.make_aware(self.date_time, timezone.utc)


class CreateComment(graphene.Mutation):
    class Arguments:
        user_id = graphene.String(required=True)
        photo_id = graphene.String(required=True)
        comment = graphene.String(required=True)

    comment = graphene.Field(CommentSchema)

    def mutate(self, info, user_id, photo_id, comment):
        photo = Photo.objects.get(id=photo_id)
        c = Comment(date_time=timezone.now(), comment=comment, user=User.objects.get(id=user_id))
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

        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            location=user_data.location,
            description=user_data.description,
            occupation=user_data.occupation,
            login_name=user_data.login_name,
            password=user_data.password,
        ).save()
        return CreateUser(user=user)


class Query(graphene.ObjectType):
    users = graphene.List(UserSchema)
    photos = graphene.List(PhotoSchema, user_id=graphene.String(required=True))

    photo = graphene.Field(PhotoSchema, id=graphene.String(required=True))
    user = graphene.Field(UserSchema, id=graphene.String(required=True))

    def resolve_photo(self, info, id):
        return Photo.objects.get(id=id)

    def resolve_user(self, info, id):
        return User.objects.get(id=id)

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_photos(self, info, user_id):
        return Photo.objects(user=user_id)


class Mutations(graphene.ObjectType):
    create_comment = CreateComment.Field()
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query,
                         mutation=Mutations,
                         types=[UserSchema, PhotoSchema, CommentSchema])
