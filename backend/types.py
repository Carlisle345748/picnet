import graphene
from graphene_django import DjangoObjectType

from backend.models import *
from backend.utils import to_model_id
from django_filters import FilterSet, OrderingFilter


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
        fields = ('username', 'first_name', 'last_name', 'email', 'profile')
        filter_fields = ['id', 'username']

    @classmethod
    def get_node(cls, info, id):
        try:
            return cls._meta.model.objects.select_related('profile').get(id=id)
        except cls._meta.model.DoesNotExist:
            return None


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
    like_count = graphene.Int()
    comment_count = graphene.Int()

    def resolve_is_like(self, info, user_id):
        return self.user_like.filter(pk=to_model_id(user_id)).exists()

    def resolve_url(self, info):
        return "/media/" + self.file_name

    def resolve_like_count(self, info):
        return self.user_like.count()

    def resolve_comment_count(self, info):
        return self.comment_set.count()


class PhotoFilter(FilterSet):
    class Meta:
        model = Photo
        fields = ['id', 'user']

    order_by = OrderingFilter(
        fields=('date_time',)
    )


class FeedSchema(DjangoObjectType):
    class Meta:
        model = Feed
        interfaces = (graphene.Node,)


class FeedFilter(FilterSet):
    class Meta:
        model = Feed
        fields = ['user']

    order_by = OrderingFilter(
        fields=('date_time',)
    )
