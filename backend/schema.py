import graphene
from graphene_mongo import MongoengineObjectType, MongoengineConnectionField
from graphql_relay import from_global_id

from .models import User, Photo, Comment


class UserSchema(MongoengineObjectType):
    class Meta:
        model = User
        interfaces = (graphene.Node,)


class PhotoSchema(MongoengineObjectType):
    class Meta:
        model = Photo
        interfaces = (graphene.Node,)
        filter_fields = {
            'file_name': ['in', 'exact', 'icontains', 'istartswith'],
            'id': ['in']
        }


class CommentSchema(MongoengineObjectType):
    class Meta:
        model = Comment
        interfaces = (graphene.Node,)


class Query(graphene.ObjectType):
    node = graphene.Node.Field()

    # users = MongoengineConnectionField(UserSchema)
    users = graphene.List(UserSchema)
    photos = MongoengineConnectionField(PhotoSchema)

    photo = graphene.Field(PhotoSchema, id=graphene.String())
    user = graphene.Field(UserSchema, id=graphene.String())

    def resolve_photo(self, info, id):
        return Photo.objects.get(id=from_global_id(id).id)

    def resolve_user(self, info, id):
        return User.objects.get(id=from_global_id(id).id)

    def resolve_users(self, info):
        return User.objects.all()


schema = graphene.Schema(query=Query, types=[UserSchema, PhotoSchema, CommentSchema])
