import graphene
from django.utils import timezone
from graphene_mongo import MongoengineObjectType

from backend.models import *
from backend.utils import to_mongo_id


class BaseUserSchema(MongoengineObjectType):
    class Meta:
        model = BaseUser
        interfaces = (graphene.Node,)
        only_fields = ('username', 'first_name', 'last_name', 'email')


class UserSchema(MongoengineObjectType):
    class Meta:
        model = User
        interfaces = (graphene.Node,)
        exclude_fields = ('base_user',)

    username = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()

    follower_count = graphene.Int()
    following_count = graphene.Int()

    def resolve_username(self, info):
        if not self.base_user:
            self.reload('base_user')
        return self.base_user.username

    def resolve_first_name(self, info):
        if not self.base_user:
            self.reload('base_user')
        return self.base_user.first_name

    def resolve_last_name(self, info):
        if not self.base_user:
            self.reload('base_user')
        return self.base_user.last_name

    def resolve_email(self, info):
        if not self.base_user:
            self.reload('base_user')
        return self.base_user.email

    def resolve_follower_count(self, info):
        pipeline = [
            {"$match": {"_id": self.id}},
            {"$project": {"count": {"$size": "$follower"}}}
        ]
        data = list(User.objects.aggregate(pipeline))
        return data[0]['count']

    def resolve_following_count(self, info):
        pipeline = [
            {"$match": {"_id": self.id}},
            {"$project": {"count": {"$size": "$following"}}}
        ]
        data = list(User.objects.aggregate(pipeline))
        return data[0]['count']


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

    def resolve_is_like(self, info, user_id):
        user_id = to_mongo_id(user_id)
        return Photo.objects(Q(id=self.id) & Q(user_like=user_id)).count() != 0

    def resolve_url(self, info):
        if not self.file_name:
            self.reload('file_name')
        return "/media/" + self.file_name

    def resolve_date_time(self, info):
        return timezone.make_aware(self.date_time, timezone.utc)
