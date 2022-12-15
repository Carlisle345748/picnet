from mongoengine import *
from datetime import datetime

connect('photo', username='root', password='123456', authentication_source='admin')


class BaseUser(Document):
    id = IntField(db_field='id')
    obj_id = ObjectIdField(db_field='_id')
    first_name = StringField()
    last_name = StringField()
    username = StringField()
    password = StringField()
    email = StringField()
    is_active = BooleanField()
    is_staff = BooleanField()
    is_superuser = BooleanField()
    last_login = StringField()
    date_joined = DateTimeField()

    meta = {'collection': 'auth_user', 'id_field': 'obj_id'}


class User(Document):
    base_user = LazyReferenceField(BaseUser, passthrough=True)
    description = StringField()
    avatar = StringField(default="/")
    follower = ListField(LazyReferenceField('User'), default=[])
    following = ListField(LazyReferenceField('User'), default=[])

    meta = {'collection': 'backend_user'}


class Comment(EmbeddedDocument):
    comment = StringField(required=True)
    date_time = DateTimeField(required=True, default=datetime.utcnow)
    user = LazyReferenceField(User, required=True)


class Photo(Document):
    file_name = StringField(required=True)
    date_time = DateTimeField(required=True, default=datetime.utcnow)
    comments = ListField(EmbeddedDocumentField(Comment))
    user = LazyReferenceField(User, required=True)
    user_like = ListField(LazyReferenceField(User), default=[])

    meta = {'collection': 'backend_photo'}
