from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from sentry_sdk import last_event_id

from management.forms import PetCreateUpdateForm, PetListFiltersForm, PetProfilePhotoFormSet, ShelterInfoUpdateForm
from management.mixins import UserWithAssociatedShelterMixin, ViewPaginatorMixin
from management.utils import add_url_params
from web.models import Pet, Shelter


class IndexView(UserWithAssociatedShelterMixin):

    # noinspection PyMethodMayBeStatic
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        associated_shelters = Shelter.user_associated_shelters(request.user)

        if associated_shelters.count() > 1:
            return redirect('management:shelters_list')

        return redirect('management:pets_list')


class ShelterPetsListView(UserWithAssociatedShelterMixin, ViewPaginatorMixin, ListView):
    template_name = 'management/pets-list.html'
    model = Pet
    context_object_name = 'pets'
    ordering = ["-pk"]
    paginate_by = 30
    petListFiltersForm = None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # noinspection PyTypeChecker
        self.petListFiltersForm = PetListFiltersForm(request.GET)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # noinspection PyUnresolvedReferences
        shelter = self.request.user_selected_shelter

        pets = Pet.pets_from_shelter(shelter, annotate_with_likes_and_dislikes=True)

        return self.petListFiltersForm.filter_queryset(pets)

    def page_link(self, query_params, page):
        return add_url_params(reverse('management:pets_list') + query_params, {'page': page})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['filters_form'] = self.petListFiltersForm
        context['search_term'] = self.petListFiltersForm.get_search_term()
        context['active_menu_item'] = 'pets_list'

        return context


class SheltersListView(UserWithAssociatedShelterMixin, ListView):
    template_name = 'management/shelters-list.html'
    model = Shelter
    context_object_name = 'shelters'
    ordering = ["-pk"]
    paginate_by = None

    def get_queryset(self):
        return Shelter.user_associated_shelters(self.request.user).select_related('region').annotate_with_statistics()


class ShelterSwitchView(UserWithAssociatedShelterMixin, SingleObjectMixin):
    model = Shelter

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # noinspection PyTypeChecker
        selected_shelter: Shelter = self.get_object()
        response = redirect("management:pets_list")

        selected_shelter.switch_shelter_cookie(response)

        return response

    def get_queryset(self):
        return Shelter.user_associated_shelters(self.request.user)


class ShelterPetCreateView(UserWithAssociatedShelterMixin, CreateView):
    model = Pet
    template_name = 'management/pet-create.html'
    form_class = PetCreateUpdateForm
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
        # noinspection PyUnresolvedReferences
        return Pet.pets_from_shelter(self.request.user_selected_shelter)

    def form_valid(self, form):
        # noinspection PyUnresolvedReferences
        form.instance.shelter = self.request.user_selected_shelter

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


@login_required(redirect_field_name=None)
def no_associated_shelter(request: HttpRequest) -> HttpResponse:
    return render(request, 'management/no-associated-shelter.html')


def handler400(request: HttpRequest, *args, **argv) -> HttpResponse:
    return render(request, "management/status_codes/status-code-400.html", status=400)


def handler403(request: HttpRequest, *args, **argv) -> HttpResponse:
    return render(request, "management/status_codes/status-code-403.html", status=403)


def handler404(request: HttpRequest, *args, **argv) -> HttpResponse:
    return render(request, "management/status_codes/status-code-404.html", status=404)


def handler500(request: HttpRequest, *args, **argv):
    return render(request, "management/status_codes/status-code-500.html", {
        'sentry_event_id': last_event_id(),
    }, status=500)
