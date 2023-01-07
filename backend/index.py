from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from backend.models import Profile, Photo


@register(Profile)
class UserModelIndex(AlgoliaIndex):
    fields = ('global_id', 'username', 'name', 'description', 'avatar_url')
    settings = {'searchableAttributes': ['username', 'name', 'description']}
    index_name = 'user'


@register(Photo)
class PhotoModelIndex(AlgoliaIndex):
    fields = ("global_id", "file_name", "url", "description", "location", "photo_tags", "photo_comments")
    settings = {'searchableAttributes': ['description', 'location"', 'photo_tags', 'photo_comments']}
    index_name = 'photo'
