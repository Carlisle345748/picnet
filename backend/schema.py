from graphene_mongo import MongoengineConnectionField

from .mutation import *
from .utils import login_required


class MongoengineAuthConnectionField(MongoengineConnectionField):
    def default_resolver(self, _root, info, required_fields=None, resolved=None, **args):
        if "user_id" not in info.context.session:
            raise GraphQLError(message="user not logged in")
        return super().default_resolver(_root, info, required_fields, resolved, **args)


class Query(graphene.ObjectType):
    users = MongoengineAuthConnectionField(UserSchema)
    photos = MongoengineAuthConnectionField(PhotoSchema)

    photo = graphene.Field(PhotoSchema, id=graphene.ID(required=True))
    user = graphene.Field(UserSchema, id=graphene.ID(required=True))

    @login_required
    def resolve_user(self, info, id):
        return User.objects.get(id=to_mongo_id(id))

    @login_required
    def resolve_photo(self, info, id):
        return Photo.objects.get(id=to_mongo_id(id))


class Mutations(graphene.ObjectType):
    create_comment = CreateComment.Field()
    create_user = CreateUser.Field()
    like_photo = LikePhoto.Field()
    login = Login.Field()
    logout = Logout.Field()


schema = graphene.Schema(query=Query,
                         mutation=Mutations,
                         types=[UserSchema, PhotoSchema, CommentSchema])
