import graphene
from graphene_mongo import MongoengineObjectType
from backend.models import *
from django.utils import timezone


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


class CommentSchema(MongoengineObjectType):
    class Meta:
        model = Comment

    def resolve_date_time(self, info):
        return timezone.make_aware(self.date_time, timezone.utc)


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