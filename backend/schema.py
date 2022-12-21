from graphene_django.filter import DjangoFilterConnectionField

from .errors import ERR_NOT_LOGIN
from .mutation import *

WHITE_LIST = ['login', 'logout', 'create_user']


class Query(graphene.ObjectType):
    users = DjangoFilterConnectionField(UserSchema)
    photos = DjangoFilterConnectionField(PhotoSchema)
    profiles = DjangoFilterConnectionField(ProfileSchema)

    photo = graphene.relay.Node.Field(PhotoSchema)
    user = graphene.Field(UserSchema, id=graphene.ID(required=True))
    profile = graphene.Field(ProfileSchema, user_id=graphene.ID(required=True))

    def resolve_user(self, info, id):
        return User.objects.select_related('profile').get(pk=to_model_id(id))

    def resolve_profile(self, info, user_id):
        return Profile.objects.select_related('user').get(user_id=to_model_id(user_id))


class Mutations(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_photo_like = UpdatePhotoLike.Field()
    update_follower = UpdateFollower.Field()
    update_profile = UpdateProfile.Field()

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
