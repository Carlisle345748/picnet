import bson
from bson.objectid import ObjectId
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from .models import User, Photo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


def auth(func):
    def auth_user(*args, **kwargs):
        # if "user_id" not in args[0].session:
        #     return Response({'code': 1003, 'msg': 'user not logged in'}, status=401)
        return func(*args, **kwargs)

    return auth_user


@api_view(['GET'])
def test_count(request: Request):
    return Response({
        "user": User.objects.count(),
        "photo": Photo.objects.count(),
    })


@api_view(['GET'])
@auth
def users(request: Request):
    data = map(lambda x: {
        '_id': str(x.id),
        'first_name': x.first_name,
        'last_name': x.last_name,
    }, User.objects())
    return Response(data)


@api_view(['GET'])
@auth
def find_user(request: Request, user_id):
    result = User.objects(id=ObjectId(user_id))
    if result.count() == 0:
        return Response({"code": 1001, "msg": "user not found"})
    user = User.objects(id=ObjectId(user_id))[0].to_mongo()
    user['_id'] = str(user["_id"])
    return Response(user)


@api_view(['GET'])
@auth
def photo_of_user(request: Request, user_id):
    photos = Photo.objects(user_id=user_id)
    for p in photos:
        print(p.user_id.to_mongo())
    return Response(photos)


@api_view(["POST"])
@auth
def comments_of_photo(request: Request, photo_id):
    photo = Photo.objects.get(pk=ObjectId(photo_id))
    for c in photo.comments:
        c['date_time'] = timezone.make_aware(c['date_time'], timezone.timezone.utc)
    photo.comments.append({
        "_id": bson.ObjectId(),
        "comment": request.data["comment"],
        "user_id": ObjectId(request.session["user_id"]),
        "date_time": timezone.now(),
    })
    photo.save()
    return Response({"code": 0, "msg": "success"})


@api_view(["POST"])
@auth
@parser_classes([MultiPartParser])
def add_photo(request: Request):
    try:
        img: InMemoryUploadedFile = request.data['uploadedphoto']
        with open(f'{settings.MEDIA_ROOT}/{img.name}', 'wb') as f:
            f.write(img.file.read())

        photo = Photo.objects.create(
            file_name=img.name,
            date_time=timezone.now(),
            user=User.objects.get(pk=ObjectId(request.session['user_id'])),
            comments=[],
        )
        return Response({"_id": str(photo._id), "code": 0, "msg": "success"})
    except KeyError:
        return Response({"code": 1006, "msg": "photo not found"}, status=400)
    except Exception as e:
        print(e)
        return Response({"code": 1007, "msg": "save file failed"}, status=500)


@api_view(['POST'])
def add_user(request: Request):
    user = UserSerializer(data=request.data)
    if not user.is_valid():
        return Response({"code": 1010, "msg": "missing information", "err": user.errors}, status=400)

    if User.objects.filter(login_name=request.data['login_name']).count() != 0:
        return Response({"code": 1011, "msg": "login_name exist"}, status=400)

    user.save()
    return Response({"code": 0, "msg": "success"})


@api_view(['POST'])
def login(request: Request):
    try:
        login_name = request.data['login_name']
        user = User.objects.get(login_name=login_name)
        if request.data['password'] != user.password:
            return Response({'code': 1002, 'msg': 'incorrect password'}, status=400)
        request.session['user_id'] = str(user._id)
        return Response({'code': 0, 'msg': "success", '_id': str(user._id)})

    except User.DoesNotExist:
        return Response({'code': 1001, 'msg': 'invalid username'}, status=400)


@api_view(['POST'])
@auth
def logout(request: Request):
    del request.session['user_id']
    return Response({})
