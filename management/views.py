from typing import Any, Dict, Optional

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.views.generic import RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from management.forms import CatCreateUpdateForm, DogCreateUpdateForm, ShelterInfoUpdateForm
from management.mixins import PetCreateViewMixin, PetsListViewMixin, UserWithAssociatedShelterMixin
from utils.mixins import ViewPaginatorMixin
from web.models import Cat, Dog, Shelter


class IndexView(UserWithAssociatedShelterMixin):

    # noinspection PyMethodMayBeStatic
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        associated_shelters = Shelter.user_associated_shelters(request.user)

        if associated_shelters.count() > 1:
            return redirect('management:shelters_list')

        return redirect('management:pets_list')


class PetListRedirectView(UserWithAssociatedShelterMixin, RedirectView):

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        # noinspection PyUnresolvedReferences
        shelter = self.request.user_selected_shelter

        if Dog.all_dogs_from_shelter(shelter).exists():
            self.pattern_name = 'management:dogs_list'
        else:
            self.pattern_name = 'management:cats_list'

        return super().get_redirect_url(*args, **kwargs)


# Dogs
class DogsListView(UserWithAssociatedShelterMixin, ViewPaginatorMixin, PetsListViewMixin):
    template_name = 'management/dogs-list.html'
    model = Dog

    def get_queryset(self):
        # noinspection PyUnresolvedReferences
        shelter = self.request.user_selected_shelter

        pets = Dog.all_dogs_from_shelter(shelter).order_by("status", "-pk")

        return self.petListFiltersForm.filter_queryset(pets)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'dogs_list'

        return context


class DogCreateView(UserWithAssociatedShelterMixin, PetCreateViewMixin):
    model = Dog
    template_name = 'management/pet-create.html'
    form_class = DogCreateUpdateForm

    def get_queryset(self) -> models.query.QuerySet:
        # noinspection PyUnresolvedReferences
        return Dog.all_dogs_from_shelter(self.request.user_selected_shelter)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'dogs_list'

        return context


class DogUpdateView(DogCreateView, UpdateView):
    template_name = 'management/pet-edit.html'
    action_type = 'update'


# Cats
class CatsListView(UserWithAssociatedShelterMixin, ViewPaginatorMixin, PetsListViewMixin):
    template_name = 'management/cats-list.html'
    model = Cat

    def get_queryset(self):
        # noinspection PyUnresolvedReferences
        shelter = self.request.user_selected_shelter

        pets = Cat.all_cats_from_shelter(shelter).order_by("status", "-pk")

        return self.petListFiltersForm.filter_queryset(pets)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'cats_list'

        return context


class CatCreateView(UserWithAssociatedShelterMixin, PetCreateViewMixin):
    model = Cat
    template_name = 'management/pet-create.html'
    form_class = CatCreateUpdateForm

    def get_queryset(self) -> models.query.QuerySet:
        # noinspection PyUnresolvedReferences
        return Cat.all_cats_from_shelter(self.request.user_selected_shelter)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'cats_list'

        return context


class CatUpdateView(CatCreateView, UpdateView):
    template_name = 'management/pet-edit.html'
    action_type = 'update'


# Shelters
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


class PlatformInstructionsDocumentView(RedirectView):
    url = 'https://drive.google.com/file/d/15LFi_Ci1PYhSCunp9Iz6dhcqCcGcpReN/view?usp=sharing'


@login_required(redirect_field_name=None)
def no_associated_shelter(request: HttpRequest) -> HttpResponse:
    return render(request, 'management/no-associated-shelter.html')
