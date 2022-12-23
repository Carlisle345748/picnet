from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from django.db import transaction

from .errors import *
from .models import Photo, Feed
from .utils import save_image


@api_view(["POST"])
@login_required
@transaction.atomic()
def add_photo(request: Request):
    if not request.user.is_authenticated:
        return Response(ERR_NOT_LOGIN, status=400)
    try:
        filename = save_image(request.FILES['uploadedphoto'])
        photo = Photo(file_name=filename, user=request.user)
        photo.save()
        followers = request.user.profile.follower.all()
        for follower in followers:
            feed = Feed(user=follower, photo=photo)
            feed.save()
        return Response({"id": str(photo.id), "code": 0, "msg": "success"})
    except KeyError:
        return Response(ERR_PHOTO_NOT_FOUND, status=400)


@api_view(["POST"])
@login_required
def update_avatar(request: Request):
    if not request.user.is_authenticated:
        return Response(ERR_NOT_LOGIN, status=400)
    try:
        filename = save_image(request.FILES['UploadAvatar'])
        profile = request.user.profile
        profile.avatar = "/media/" + filename
        profile.save()
        return Response({"code": 0, "msg": "success"})
    except KeyError:
        return Response(ERR_PHOTO_NOT_FOUND, status=400)


@api_view(["POST"])
def login(request: Request):
    user = authenticate(username=request.data['username'], password=request.data['password'])
    if user is None:
        return Response(ERR_LOGIN, status=400)
    auth_login(request, user)


@api_view(["POST"])
def logout(request: Request):
    auth_logout(request)
    return Response({"code": 0, "msg": "success"})
