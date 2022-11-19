from djongo import models

# Create your models here.


class User(models.Model):
    _id = models.ObjectIdField()
    first_name = models.CharField(max_length=256, blank=False)
    last_name = models.CharField(max_length=256, blank=False)
    location = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    occupation = models.CharField(max_length=256)
    login_name = models.CharField(max_length=256, blank=False)
    password = models.CharField(max_length=256, blank=False)


class Comment(models.Model):
    _id = models.ObjectIdField()
    comment = models.CharField(max_length=256)
    date_time = models.DateTimeField()
    user_id = models.GenericObjectIdField()

    class Meta:
        managed = False


class Photo(models.Model):
    _id = models.ObjectIdField()
    file_name = models.CharField(max_length=256)
    date_time = models.DateTimeField(auto_now_add=True, blank=False)
    comments = models.ArrayField(model_container=Comment)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
