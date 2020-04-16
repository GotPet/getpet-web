from django.urls import path

from management.views import index

urlpatterns = [
    path('', index, name="index"),
]
