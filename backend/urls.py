from django.urls import path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.conf import settings
from django.views.generic import TemplateView
from strawberry.django.views import GraphQLView

from backend.schema import schema

app_name = 'backend'

graphql_view = GraphQLView.as_view(schema=schema, graphiql=settings.DEBUG, allow_queries_via_get=False)

urlpatterns = [
    path("graphql", csrf_exempt(graphql_view) if settings.DEBUG else graphql_view),
    re_path(r".*", ensure_csrf_cookie(TemplateView.as_view(template_name="backend/index.html")), name="main"),
]
