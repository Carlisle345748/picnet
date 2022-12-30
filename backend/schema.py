from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from django.db.models import Count

from .aws import AWSQuery
from .errors import ERR_NOT_LOGIN
from .mutation import *

WHITE_LIST = ['login', 'logout', 'createUser', '__schema']


class HotTagsQuery(graphene.ObjectType):
    top_tags = graphene.List(HotTag,
                             text=graphene.String(default_value=""),
                             top_n=graphene.Int(default_value=5))

    def resolve_top_tags(self, _, top_n, text):
        tags = PhotoTag.objects
        if text != "":
            tags = tags.filter(tag__istartswith=text)
        tags = tags.annotate(Count('photo')).filter(photo__count__gte=1).order_by("-photo__count")[:top_n]
        return [HotTag(tag=t.tag, count=t.photo__count) for t in tags]


class DataModelQuery(graphene.ObjectType):
    users = DjangoFilterConnectionField(UserSchema, filterset_class=UserFilter)
    photos = DjangoFilterConnectionField(PhotoSchema, filterset_class=PhotoFilter)
    profiles = DjangoFilterConnectionField(ProfileSchema)
    feeds = DjangoFilterConnectionField(FeedSchema, filterset_class=FeedFilter)

    photo = relay.Node.Field(PhotoSchema)
    user = relay.Node.Field(UserSchema)
    profile = relay.Node.Field(ProfileSchema)


class Query(DataModelQuery, HotTagsQuery, AWSQuery, graphene.ObjectType):
    pass


class Mutations(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_photo_like = UpdatePhotoLike.Field()
    update_follower = UpdateFollower.Field()
    update_profile = UpdateProfile.Field()

    upload_photo = UploadPhoto.Field()
    upload_avatar = UploadAvatar.Field()

    delete_photo = DeletePhoto.Field()
    delete_comment = DeleteComment.Field()

    create_user = CreateUser.Field()
    login = Login.Field()
    logout = Logout.Field()


class AuthorizationMiddleware:
    def __init__(self):
        self.white_list = WHITE_LIST

    def resolve(self, next, root, info, **args):
        if root is None:
            if info.field_name not in self.white_list and not info.context.user.is_authenticated:
                raise GraphQLError(message="user not login", extensions=ERR_NOT_LOGIN)
        return next(root, info, **args)


schema = graphene.Schema(query=Query, mutation=Mutations)
