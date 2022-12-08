from graphene_mongo import MongoengineConnectionField

from .mutation import *
from .utils import login_required


class MongoengineAuthConnectionField(MongoengineConnectionField):
    def default_resolver(self, _root, info, required_fields=None, resolved=None, **args):
        if "user_id" not in info.context.session:
            raise GraphQLError(message="user not logged in")
        return super().default_resolver(_root, info, required_fields, resolved, **args)


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
    login = Login.Field()
    logout = Logout.Field()


schema = graphene.Schema(query=Query,
                         mutation=Mutations,
                         types=[UserSchema, PhotoSchema, CommentSchema])
