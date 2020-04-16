from django.urls import path

from management.views import ShelterPetsListView

urlpatterns = [
    path('', ShelterPetsListView.as_view(), name="index"),
]
