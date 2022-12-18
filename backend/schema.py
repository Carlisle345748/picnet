from graphene_django.filter import DjangoFilterConnectionField

from .errors import ERR_NOT_LOGIN
from .mutation import *
from .utils import login_required


class AuthDjangoFilterConnectionField(DjangoFilterConnectionField):
    @classmethod
    def resolve_queryset(
            cls, conn, iterable, info, args, filtering_args, filterset_class
    ):
        if not info.context.user.is_authenticated:
            raise GraphQLError(message="user not logged in", extensions=ERR_NOT_LOGIN)
        return super().resolve_queryset(conn, iterable, info, args, filtering_args, filterset_class)


class Query(graphene.ObjectType):
    users = AuthDjangoFilterConnectionField(UserSchema)
    photos = AuthDjangoFilterConnectionField(PhotoSchema)
    profiles = AuthDjangoFilterConnectionField(ProfileSchema)

    photo = graphene.Field(PhotoSchema, id=graphene.ID(required=True))
    user = graphene.Field(UserSchema, id=graphene.ID(required=True))
    profile = graphene.Field(ProfileSchema, user_id=graphene.ID(required=True))

    @login_required
    def resolve_user(self, info, id):
        return User.objects.get(pk=to_model_id(id))

    @login_required
    def resolve_photo(self, info, id):
        return Photo.objects.get(pk=to_model_id(id))

    @login_required
    def resolve_profile(self, info, user_id):
        return Profile.objects.get(user_id=to_model_id(user_id))


class Mutations(graphene.ObjectType):
    create_comment = CreateComment.Field()
    create_user = CreateUser.Field()
    update_photo_like = UpdatePhotoLike.Field()
    update_follower = UpdateFollower.Field()
    login = Login.Field()
    logout = Logout.Field()


schema = graphene.Schema(query=Query, mutation=Mutations)
