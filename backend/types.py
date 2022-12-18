import graphene
from graphene_django import DjangoObjectType

from backend.models import *
from backend.utils import to_model_id


class ProfileSchema(DjangoObjectType):
    class Meta:
        model = Profile
        interfaces = (graphene.Node,)
        fields = "__all__"
        filter_fields = ['user']

    follower_count = graphene.Int()
    following_count = graphene.Int()
    is_following = graphene.Boolean(user_id=graphene.ID(required=True))

    def resolve_follower_count(self, info):
        return self.follower.count()

    def resolve_following_count(self, info):
        return self.following.count()

    def resolve_is_following(self, info, user_id):
        return self.follower.filter(pk=to_model_id(user_id)).exists()


class UserSchema(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (graphene.Node,)
        fields = ('username', 'first_name', 'last_name', 'email')
        filter_fields = ['id', 'username']

    profile = graphene.Field(ProfileSchema)

    def resolve_profile(self, info):
        return self.profile


class CommentSchema(DjangoObjectType):
    class Meta:
        model = Comment
        interfaces = (graphene.Node,)
        fields = "__all__"


class PhotoSchema(DjangoObjectType):
    class Meta:
        model = Photo
        interfaces = (graphene.Node,)
        fields = "__all__"
        filter_fields = ['id', 'user']

    url = graphene.String()
    is_like = graphene.Boolean(user_id=graphene.ID(required=True))

    def resolve_is_like(self, info, user_id):
        return self.user_like.filter(pk=to_model_id(user_id)).exists()

    def resolve_url(self, info):
        return "/media/" + self.file_name
