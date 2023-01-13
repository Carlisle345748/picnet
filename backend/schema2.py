from typing import List, Optional

from django.core.files.storage import default_storage
from django.db.models import Count
from strawberry import UNSET
from strawberry_django_plus.directives import SchemaDirectiveExtension
from strawberry_django_plus.optimizer import DjangoOptimizerExtension

from backend.aws import AWSQuery
from backend.models import PhotoTag
from backend.mutations2 import Mutation
from backend.types2 import *


@gql.type
class CostumeQuery:

    @gql.field()
    def background_image(self) -> str:
        return default_storage.url('background.png')

    @gql.field(directives=[IsAuthenticated()])
    def top_tags(self, top_n: Optional[int] = 5, text: Optional[str] = UNSET) -> List[HotTag]:
        tags = PhotoTag.objects
        if text is not UNSET:
            tags = tags.filter(tag__istartswith=text)
        tags = tags.annotate(Count('photo')).filter(photo__count__gte=1).order_by("-photo__count")[:top_n]
        return [HotTag(tag=t.tag, count=t.photo__count) for t in tags]


@gql.type
class ModelQuery:
    user: Optional[UserType] = gql.django.node(directives=[IsAuthenticated()])

    users: relay.Connection[UserType] = gql.django.connection(directives=[IsAuthenticated()])

    profile: Optional[relay.Node] = gql.django.node()

    profiles: relay.Connection[ProfileType] = gql.django.connection()

    photo: Optional[PhotoType] = gql.django.node()

    photos: relay.Connection[PhotoType] = gql.django.connection()

    comment: Optional[CommentType] = gql.django.node()

    feeds: relay.Connection[FeedType] = gql.django.connection()


@gql.type
class Query(ModelQuery, CostumeQuery, AWSQuery):
    pass


schema = gql.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        SchemaDirectiveExtension,
        DjangoOptimizerExtension,
    ],
)
