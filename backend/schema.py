from graphene_mongo import MongoengineConnectionField

from .mutation import *
from .utils import login_required, get_query_fields


class MongoengineAuthConnectionField(MongoengineConnectionField):
    def default_resolver(self, _root, info, required_fields=None, resolved=None, **args):
        if not info.context.user.is_authenticated:
            raise GraphQLError(message="user not logged in")
        return super().default_resolver(_root, info, required_fields, resolved, **args)


class Query(graphene.ObjectType):
    users = MongoengineAuthConnectionField(UserSchema)
    photos = MongoengineAuthConnectionField(PhotoSchema)

    photo = graphene.Field(PhotoSchema, id=graphene.ID(required=True))
    user = graphene.Field(UserSchema, id=graphene.ID(required=True))

    @login_required
    def resolve_user(self, info, id):
        required_fields = get_query_fields(info, User)
        return User.objects.only(*required_fields).get(id=to_mongo_id(id))

    @login_required
    def resolve_photo(self, info, id):
        required_fields = get_query_fields(info, Photo)
        return Photo.objects.only(*required_fields).get(id=to_mongo_id(id))


class Mutations(graphene.ObjectType):
    create_comment = CreateComment.Field()
    create_user = CreateUser.Field()
    like_photo = LikePhoto.Field()
    login = Login.Field()
    logout = Logout.Field()


schema = graphene.Schema(query=Query, mutation=Mutations)
