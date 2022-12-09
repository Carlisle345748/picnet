import graphene
from django.utils import timezone
from graphene_mongo import MongoengineObjectType

from backend.models import *
from backend.utils import to_mongo_id


class UserSchema(MongoengineObjectType):
    class Meta:
        model = User
        exclude_fields = ['salt', 'password']
        interfaces = (graphene.Node, )

    follower_count = graphene.Int()
    following_count = graphene.Int()

    def resolve_follower_count(self, info):
        return len(self.follower)

    def resolve_following_count(self, info):
        return len(self.following)


class CommentSchema(MongoengineObjectType):
    class Meta:
        model = Comment
        interfaces = (graphene.Node,)

    def resolve_date_time(self, info):
        return timezone.make_aware(self.date_time, timezone.utc)


class PhotoSchema(MongoengineObjectType):
    class Meta:
        model = Photo
        interfaces = (graphene.Node,)

    url = graphene.String()
    is_like = graphene.Boolean(user_id=graphene.ID(required=True))

    def resolve_user_like(self, info, first):
        return self.user_like[:first] if first is not None else self.user_like

    def resolve_is_like(self, info, user_id):
        return to_mongo_id(user_id) in [str(u.id) for u in self.user_like]

    def resolve_url(self, info):
        return "/media/" + self.file_name

    def resolve_date_time(self, info):
        return timezone.make_aware(self.date_time, timezone.utc)
