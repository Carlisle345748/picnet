from mongoengine import *
from datetime import datetime

connect('photo', username='root', password='123456', authentication_source='admin')


class User(Document):
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)
    location = StringField()
    description = StringField()
    occupation = StringField()
    login_name = StringField(required=True)
    password = StringField(required=True)

    meta = {'collection': 'backend_user'}


class Comment(EmbeddedDocument):
    comment = StringField(required=True)
    date_time = DateTimeField(required=True, default=datetime.utcnow)
    user = ReferenceField(User, required=True)


class Photo(Document):
    file_name = StringField(required=True)
    date_time = DateTimeField(required=True, default=datetime.utcnow)
    comments = ListField(EmbeddedDocumentField(Comment))
    user = ReferenceField(User, required=True)
    user_like = ListField(ReferenceField(User), default=[])

    meta = {'collection': 'backend_photo'}
