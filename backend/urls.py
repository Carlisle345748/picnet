from django.urls import path

from . import views

app_name = 'photo'

urlpatterns = [
    path('login', views.login),
    path('logout', views.logout),
    path("photos/new", views.add_photo),

    path('test/', views.test_count),
]
