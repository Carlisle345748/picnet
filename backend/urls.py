from django.urls import path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from graphene_file_upload.django import FileUploadGraphQLView

app_name = 'backend'

urlpatterns = [
    path("graphql",  FileUploadGraphQLView.as_view(graphiql=True)),
    re_path(r".*", ensure_csrf_cookie(TemplateView.as_view(template_name="backend/index.html")), name="main"),
]
