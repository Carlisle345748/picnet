from typing import List, Optional

from django.core.files.storage import default_storage
from django.db.models import Count
from strawberry import UNSET
from strawberry_django.optimizer import DjangoOptimizerExtension

from backend.aws import AWSQuery
from backend.models import PhotoTag
from backend.mutations import Mutation
from backend.types import *
from backend.directive import IsAuthenticated


@strawberry.type
class CostumeQuery:

    @strawberry.field
    def background_image(self) -> str:
        return default_storage.url('background.png')

    @strawberry.field(extensions=[IsAuthenticated()])
    def top_tags(self, top_n: Optional[int] = 5, text: Optional[str] = UNSET) -> List[HotTag]:
        tags = PhotoTag.objects
        if text is not UNSET:
            tags = tags.filter(tag__istartswith=text)
        tags = tags.annotate(Count('photo')).filter(photo__count__gte=1).order_by("-photo__count")[:top_n]
        return [HotTag(tag=t.tag, count=t.photo__count) for t in tags]


@strawberry.type
class ModelQuery:
    user: Optional[UserType] = strawberry_django.node(extensions=[IsAuthenticated()])

    users: ListConnectionWithTotalCount[UserType] = strawberry_django.connection(extensions=[IsAuthenticated()])

    profile: Optional[relay.Node] = strawberry_django.node(extensions=[IsAuthenticated()])

    profiles: ListConnectionWithTotalCount[ProfileType] = strawberry_django.connection(extensions=[IsAuthenticated()])

    photo: Optional[PhotoType] = strawberry_django.node(extensions=[IsAuthenticated()])

    photos: ListConnectionWithTotalCount[PhotoType] = strawberry_django.connection(extensions=[IsAuthenticated()])

    comment: Optional[CommentType] = strawberry_django.node(extensions=[IsAuthenticated()])

    feeds: ListConnectionWithTotalCount[FeedType] = strawberry_django.connection(extensions=[IsAuthenticated()])


@strawberry.type
class Query(ModelQuery, CostumeQuery, AWSQuery):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ],
)
