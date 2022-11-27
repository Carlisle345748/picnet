"""photoshare URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from time import time as timer

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from graphene_django.views import GraphQLView


def auth(func):
    def auth_user(*args, **kwargs):
        if "user_id" not in args[0].session:
            return JsonResponse({'code': 1003, 'msg': 'user not logged in'}, status=401)
        return func(*args, **kwargs)
    return auth_user


def timing_middleware(next, root, info, **args):
    start = timer()
    return_value = next(root, info, **args)
    duration = round((timer() - start) * 1000, 2)
    parent_type_name = root._meta.name if root and hasattr(root, '_meta') and hasattr(root._meta, "name") else ''
    print(f"{parent_type_name}.{info.field_name}: {duration} ms")
    return return_value


urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path("admin/", admin.site.urls),
    # path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("graphql", auth(GraphQLView.as_view(graphiql=True, middleware=[timing_middleware]))),
    path("", include('backend.urls')),
    re_path(r".*", ensure_csrf_cookie(TemplateView.as_view(template_name="index.html")), name="main"),
]
