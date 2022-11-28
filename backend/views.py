import hashlib

from bson.objectid import ObjectId
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import User, Photo


def auth(func):
    def auth_user(*args, **kwargs):
        if "user_id" not in args[0].session:
            return Response({'code': 1003, 'msg': 'user not logged in'}, status=401)
        return func(*args, **kwargs)
    return auth_user


@api_view(['GET'])
def test_count(request: Request):
    return Response({
        "user": User.objects.count(),
        "photo": Photo.objects.count(),
    })


@api_view(["POST"])
@auth
def add_photo(request: Request):
    try:
        img = request.FILES['uploadedphoto']

        img_hash = hashlib.md5(img.file.read()).hexdigest()
        suffix = img.name[img.name.rindex(".")+1:]
        filename = f'{img_hash}.{suffix}'

        with open(f'{settings.MEDIA_ROOT}/{filename}', 'wb') as f:
            img.file.seek(0)
            f.write(img.file.read())

        photo = Photo.objects.create(
            file_name=filename,
            date_time=timezone.now(),
            user=User.objects.get(pk=ObjectId(request.session['user_id'])),
            comments=[],
        )
        return Response({"id": str(photo.id), "code": 0, "msg": "success"})
    except KeyError:
        return Response({"code": 1006, "msg": "photo not found"}, status=400)
    except Exception as e:
        print(e)
        return Response({"code": 1007, "msg": "save file failed"}, status=500)


@api_view(['POST'])
def login(request: Request):
    login_name = request.data['login_name']
    user = User.objects(login_name=login_name)
    if not user:
        return Response({'code': 1001, 'msg': 'user not exist'}, status=400)
    user = user[0]
    if request.data['password'] != user.password:
        return Response({'code': 1002, 'msg': 'incorrect password'}, status=400)
    request.session['user_id'] = str(user.id)
    return Response({'code': 0, 'msg': "success", 'id': str(user.id)})


@api_view(['POST'])
@auth
def logout(request: Request):
    del request.session['user_id']
    return Response({})
