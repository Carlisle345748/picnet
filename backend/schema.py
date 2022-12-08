import graphene
from django.utils import timezone
from graphene_mongo import MongoengineObjectType
from graphql import GraphQLError

from .models import User, Photo, Comment
from .utils import hash_password


def login_required(func):
    def authenticate(*args, **kwargs):
        info = args[1]
        if "user_id" not in info.context.session:
            raise GraphQLError(message="user not logged in")
        return func(*args, **kwargs)

    return authenticate


class UserSchema(MongoengineObjectType):
    class Meta:
        model = User
        exclude_fields = ['salt', 'password']

    follower_count = graphene.Int()
    following_count = graphene.Int()

    def resolve_follower_count(self, info):
        return len(self.follower)

    def resolve_following_count(self, info):
        return len(self.following)


class PhotoSchema(MongoengineObjectType):
    class Meta:
        model = Photo

    url = graphene.String()
    user_like = graphene.List(UserSchema, first=graphene.Int(default_value=None))
    is_like = graphene.Boolean(user_id=graphene.String(required=True))

    def resolve_user_like(self, info, first):
        return self.user_like[:first] if first is not None else self.user_like

    def resolve_is_like(self, info, user_id):
        return user_id in [str(u.id) for u in self.user_like]

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

    @login_required
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
        photo_id = graphene.String(required=True)
        user_id = graphene.String(required=True)
        like = graphene.Boolean(default_value=True)

    photo = graphene.Field(PhotoSchema)

    def mutate(self, info, photo_id, user_id, like):
        photo = Photo.objects.get(id=photo_id)
        photo.user_like = [user for user in photo.user_like if str(user.id) != user_id]
        if like:
            photo.user_like.append(User.objects.get(id=user_id))
        photo.save()
        return LikePhoto(photo=photo)


class Query(graphene.ObjectType):
    users = graphene.List(UserSchema)
    photos = graphene.List(PhotoSchema, user_id=graphene.String(default_value=None))

    photo = graphene.Field(PhotoSchema, id=graphene.String(required=True))
    user = graphene.Field(UserSchema, id=graphene.String(required=True))

    @login_required
    def resolve_photo(self, info, id):
        return Photo.objects.get(id=id)

    @login_required
    def resolve_user(self, info, id):
        return User.objects.get(id=id)

    @login_required
    def resolve_users(self, info):
        return User.objects.all()

    @login_required
    def resolve_photos(self, info, user_id):
        return Photo.objects(user=user_id) if user_id else Photo.objects()


class Mutations(graphene.ObjectType):
    create_comment = CreateComment.Field()
    create_user = CreateUser.Field()
    like_photo = LikePhoto.Field()


schema = graphene.Schema(query=Query,
                         mutation=Mutations,
                         types=[UserSchema, PhotoSchema, CommentSchema])
