import graphene
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.db.models import Count, Q
from django_filters import FilterSet, OrderingFilter, CharFilter, BaseInFilter
from graphene_django import DjangoObjectType

from backend.models import *
from backend.utils import to_model_id


class ProfileSchema(DjangoObjectType):
    class Meta:
        model = Profile
        interfaces = (graphene.Node,)
        fields = "__all__"
        filter_fields = ['user']

    avatar = graphene.String()
    follower_count = graphene.Int()
    following_count = graphene.Int()
    is_following = graphene.Boolean(user_id=graphene.ID(default_value=""))

    def resolve_avatar(self, info):
        return self.avatar.url if self.avatar.name != "" else ""

    def resolve_follower_count(self, info):
        return self.follower.count()

    def resolve_following_count(self, info):
        return self.following.count()

    def resolve_is_following(self, info, user_id):
        if hasattr(self.user, 'is_following'):
            return self.user.is_following
        user_id = to_model_id(user_id) if user_id != "" else info.context.user.id
        return self.follower.filter(pk=user_id).exists()


class UserSchema(DjangoObjectType):
    rank = graphene.Float()

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

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.select_related("profile")

    def resolve_rank(self, info):
        return self.rank if hasattr(self, 'rank') else None


class StringInFilter(BaseInFilter, CharFilter):
    pass


class UserFilter(FilterSet):
    is_following = CharFilter(field_name="profile__follower", method="add_is_following")
    search = CharFilter(method='filter_search')
    order_by = OrderingFilter(fields=('rank',))
    id_in = StringInFilter(field_name="id", lookup_expr="in", method="filter_id_in")

    def filter_search(self, queryset, name, value):
        query = SearchQuery(value)
        vector = SearchVector('first_name', "last_name", weight='A') + SearchVector('profile__description', weight='B')
        return queryset.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0.1).distinct('id', 'rank')

    def add_is_following(self, queryset, name, value):
        user_id = int(to_model_id(value))
        return queryset.annotate(is_following=Count('profile__follower', filter=Q(profile__follower=user_id)))

    def filter_id_in(self, queryset, name, value):
        User.objects.filter()
        ids = [to_model_id(v) for v in value]
        return queryset.filter(id__in=ids)

    class Meta:
        model = User
        fields = ['id', 'username']


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
    rank = graphene.Float()
    ratio = graphene.Float()

    def resolve_ratio(self, info):
        return self.ratio if self.ratio != -1 else self.file_name.height / self.file_name.width

    def resolve_is_like(self, info, user_id):
        return self.user_like.filter(pk=to_model_id(user_id)).exists()

    def resolve_url(self, info):
        return self.file_name.url

    def resolve_like_count(self, info):
        return self.user_like.count()

    def resolve_comment_count(self, info):
        return self.comment_set.count()

    def resolve_rank(self, info):
        return self.rank if hasattr(self, 'rank') else None


class PhotoFilter(FilterSet):
    search = CharFilter(method='filter_search')
    order_by = OrderingFilter(fields=('date_time', 'rank'))

    def filter_search(self, queryset, name, value):
        query = SearchQuery(value)
        vector = SearchVector('description', 'location', 'tags__tag', weight='A')
        vector += SearchVector('comment__comment', weight='B')
        return queryset.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0.1).distinct('id', 'rank')

    class Meta:
        model = Photo
        fields = ['id', 'user']


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


class HotTag(graphene.ObjectType):
    tag = graphene.String()
    count = graphene.Int()
