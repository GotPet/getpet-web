from urllib.parse import urljoin

from django.conf.urls import url
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from getpet import settings
from rukla.api import NewGameView, FinishGameView

public_api_url_patterns = [
    path('v1/game/start/', NewGameView.as_view(), name="api_rukla_start_game"),
    path('v1/game/finish/<uuid:game_id>/', FinishGameView.as_view(), name="api_rukla_finish_game"),
]

private_api_url_patterns = []

schema_view = get_schema_view(
    openapi.Info(
        title="Kario kelias API",
        default_version='v1',
        description="""Kario kelias API.<br>""",
    ),
    validators=['flex', ],
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=None if settings.DEBUG else urljoin(settings.BASE_DOMAIN, "/api/"),
)

urlpatterns = public_api_url_patterns + private_api_url_patterns + [
    url(r'(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=None), name='api'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]
