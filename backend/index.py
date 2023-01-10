from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from backend.models import Profile, Photo


@register(Profile)
class UserModelIndex(AlgoliaIndex):
    fields = ('global_id', 'username', 'name', 'description', 'avatar_url')
    settings = {'searchableAttributes': ['username', 'name', 'unordered(description)']}
    index_name = 'user'


@register(Photo)
class PhotoModelIndex(AlgoliaIndex):
    fields = ("global_id", "file_name", "url", "description", "location",
              "photo_tags", "photo_comments", "user_fullname", "username")
    settings = {
        'searchableAttributes': [
            'unordered(description)',
            'unordered(location)',
            'unordered(photo_tags)',
            'user_fullname',
            'username',
            'unordered(photo_comments)'
        ],
        'removeStopWords': ['en', 'zh']
    }
    index_name = 'photo'
