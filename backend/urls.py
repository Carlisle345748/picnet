from django.urls import path

from . import views

app_name = 'photo'

urlpatterns = [
    path('login', views.login),
    path('logout', views.logout),

    path('test/', views.test_count),

    path('user/', views.add_user),
    path('user/list/', views.users),
    path('user/<user_id>/', views.find_user),

    path("photosOfUser/<user_id>/", views.photo_of_user),
    path("commentsOfPhoto/<photo_id>", views.comments_of_photo),
    path("photos/new", views.add_photo),
]
