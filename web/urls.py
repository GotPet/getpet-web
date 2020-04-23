from django.urls import path
from django.views.generic import RedirectView

from web.views import health_check, index

urlpatterns = [
    path('', index, name="index"),
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon/favicon.ico', permanent=False)),
    path('health/', health_check, name="health_check"),
]
