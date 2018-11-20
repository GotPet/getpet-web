from django.urls import path

from web.views import health_check, index

urlpatterns = [
    path('', index, name="index"),
    path('health/', health_check, name="health_check"),
]
