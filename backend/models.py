from django.contrib.auth.models import User
from django.db import models
from mongoengine import *

connect('photo', username='root', password='123456', authentication_source='admin')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    avatar = models.CharField(default="/", max_length=200)
    follower = models.ManyToManyField(User, related_name="follower")
    following = models.ManyToManyField(User, related_name="following")


class Photo(models.Model):
    file_name = models.CharField(max_length=200)
    date_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_like = models.ManyToManyField(User, related_name="user_like")


class Comment(models.Model):
    comment = models.CharField(default="", max_length=200)
    date_time = models.DateTimeField(auto_now_add=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
