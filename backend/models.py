from django.contrib.auth.models import User
from django.db import models
from strawberry import relay


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    avatar = models.ImageField(upload_to="avatar/")
    follower = models.ManyToManyField(User, related_name="follower")
    following = models.ManyToManyField(User, related_name="following")

    @property
    def global_id(self):
        return relay.to_base64("UserType", self.user.id)

    @property
    def name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar.name != "" else ""

    @property
    def username(self):
        return self.user.username


class PhotoTag(models.Model):
    tag = models.CharField(max_length=200, unique=True)


class Photo(models.Model):
    file = models.ImageField(upload_to="images/")
    ratio = models.FloatField(default=-1)
    date_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_like = models.ManyToManyField(User, related_name="user_like")
    description = models.CharField(max_length=400, default="")
    tags = models.ManyToManyField(PhotoTag)
    location = models.CharField(max_length=200, default="")

    class Meta:
        indexes = [models.Index(fields=["-date_time"])]

    @property
    def user_fullname(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def username(self):
        return self.user.username

    @property
    def global_id(self):
        return relay.to_base64("PhotoType", self.id)

    @property
    def url(self):
        return self.file.url

    @property
    def photo_tags(self):
        return [t.tag for t in self.tags.all()]

    @property
    def photo_comments(self):
        return [c.comment for c in self.comments.all()]


class Comment(models.Model):
    comment = models.CharField(default="", max_length=400)
    date_time = models.DateTimeField(auto_now_add=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
