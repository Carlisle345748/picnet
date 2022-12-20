from django.urls import path

from . import views

app_name = 'photo'

urlpatterns = [
    path("photos/new", views.add_photo),
    path("user/avatar", views.update_avatar),
]
