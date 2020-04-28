from pprint import pprint
from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from management.forms import PetListFiltersForm, PetProfilePhotoFormSet, ShelterPetUpdateForm
from management.mixins import UserWithAssociatedShelterMixin, ViewPaginatorMixin
from management.utils import add_url_params
from web.models import Pet, Shelter


class ShelterPetsListView(UserWithAssociatedShelterMixin, ViewPaginatorMixin, ListView):
    template_name = 'management/pets-list.html'
    model = Pet
    context_object_name = 'pets'
    ordering = ["-pk"]
    paginate_by = 50
    petListFiltersForm = None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # noinspection PyTypeChecker
        self.petListFiltersForm = PetListFiltersForm(request.GET)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        shelter = Shelter.user_selected_shelter(self.request.user)

        pets = Pet.pets_from_shelter(shelter, annotate_with_total_likes=True)

        return self.petListFiltersForm.filter_queryset(pets)

    def page_link(self, query_params, page):
        return add_url_params(reverse('management_pets_list') + query_params, {'page': page})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['filters_form'] = self.petListFiltersForm
        context['search_term'] = self.petListFiltersForm.get_search_term()

        return context


class ShelterPetUpdateView(UserWithAssociatedShelterMixin, UpdateView):
    model = Pet
    template_name = 'management/pet-edit.html'
    context_object_name = 'pet'
    form_class = ShelterPetUpdateForm

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        pet = context[self.context_object_name]
        if self.request.POST:
            context['pet_photo_form_set'] = PetProfilePhotoFormSet(self.request.POST, instance=pet)
        else:
            context['pet_photo_form_set'] = PetProfilePhotoFormSet(instance=pet)

        return context

    def get_success_url(self) -> str:
        return self.get_object().edit_pet_url()


@login_required
def no_associated_shelter(request) -> HttpResponse:
    return render(request, 'management/no-associated-shelter.html')
