from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from management.forms import PetListFiltersForm, PetProfilePhotoFormSet, ShelterInfoUpdateForm, \
    ShelterPetCreateUpdateForm
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
        context['active_menu_item'] = 'pets_list'

        return context


class ShelterPetCreateView(UserWithAssociatedShelterMixin, CreateView):
    model = Pet
    template_name = 'management/pet-create.html'
    form_class = ShelterPetCreateUpdateForm
    context_object_name = 'pet'

    # https://dev.to/zxenia/django-inline-formsets-with-class-based-views-and-crispy-forms-14o6
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # noinspection PyUnresolvedReferences
        context['pet_photo_form_set'] = PetProfilePhotoFormSet(data=self.request.POST or None,
                                                               instance=self.object)

        return context

    def get_success_url(self) -> str:
        # noinspection PyUnresolvedReferences
        return self.object.edit_pet_url()

    def get_queryset(self) -> models.query.QuerySet:
        shelter = Shelter.user_selected_shelter(self.request.user)

        return Pet.pets_from_shelter(shelter)

    def form_valid(self, form):
        form.instance.shelter = Shelter.user_selected_shelter(self.request.user, request=self.request)

        with transaction.atomic():
            pet = form.save()

            pet_photo_form_set = PetProfilePhotoFormSet(data=self.request.POST)
            if pet_photo_form_set.is_valid():
                pet_photo_form_set.save_photos(pet)

        return super().form_valid(form)


class ShelterPetUpdateView(ShelterPetCreateView, UpdateView):
    template_name = 'management/pet-edit.html'


class ShelterInfoUpdateView(UserWithAssociatedShelterMixin, UpdateView):
    model = Shelter
    template_name = 'management/shelter-info-edit.html'
    context_object_name = 'shelter'
    form_class = ShelterInfoUpdateForm

    def get_queryset(self) -> models.query.QuerySet:
        return Shelter.user_associated_shelters(self.request.user)

    def get_success_url(self) -> str:
        # noinspection PyUnresolvedReferences
        return self.get_object().edit_shelter_url()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'shelter'

        return context


@login_required
def no_associated_shelter(request) -> HttpResponse:
    return render(request, 'management/no-associated-shelter.html')
