from django.urls import path

from management import views

app_name = 'management'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('pets/', views.PetListRedirectView.as_view(), name="pets_list"),

    path('dogs/', views.DogsListView.as_view(), name="dogs_list"),
    path('dogs/<int:pk>/', views.DogUpdateView.as_view(), name="dogs_update"),
    path('dogs/create/', views.DogCreateView.as_view(), name="dogs_create"),

    path('cats/', views.CatsListView.as_view(), name="cats_list"),
    path('cats/<int:pk>/', views.CatUpdateView.as_view(), name="cats_update"),
    path('cats/create/', views.CatCreateView.as_view(), name="cats_create"),

    path('shelters/', views.SheltersListView.as_view(), name="shelters_list"),
    path('shelters/<int:pk>/', views.ShelterInfoUpdateView.as_view(), name="shelters_update"),
    path('shelters/<int:pk>/switch/', views.ShelterSwitchView.as_view(), name="shelters_switch"),
    path('shelters/no-associated-shelter/', views.no_associated_shelter, name="shelters_no_associated_shelter"),

    path('instruction/', views.PlatformInstructionsDocumentView.as_view(), name="instruction"),
]
