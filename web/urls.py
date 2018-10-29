from django.urls import path
from django.views.generic import RedirectView

from web.views import health_check

urlpatterns = [
    path('', RedirectView.as_view(url="https://play.google.com/store/apps/details?id=lt.getpet.getpet"), name="index"),
    path('health/', health_check, name="health_check"),
]
