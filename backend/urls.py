from django.urls import path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from graphene_file_upload.django import FileUploadGraphQLView

from backend.views import get_setting

app_name = 'backend'

urlpatterns = [
    path("graphql",  FileUploadGraphQLView.as_view(graphiql=True)),
    path("setting", get_setting),
    re_path(r".*", ensure_csrf_cookie(TemplateView.as_view(template_name="backend/index.html")), name="main"),
]
