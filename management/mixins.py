from typing import Any, Dict

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import CreateView, ListView

from management.forms import PetListFiltersForm, PetProfilePhotoFormSet
from utils.utils import add_url_params


class UserWithAssociatedShelterMixin(UserPassesTestMixin, View):
    def test_func(self):
        # noinspection PyUnresolvedReferences
        return self.request.user_selected_shelter is not None

    def handle_no_permission(self):
        return redirect('management:shelters_no_associated_shelter')


class PetCreateViewMixin(CreateView):
    context_object_name = 'pet'
    action_type = 'create'

    # https://dev.to/zxenia/django-inline-formsets-with-class-based-views-and-crispy-forms-14o6
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # noinspection PyUnresolvedReferences
        context['pet_photo_form_set'] = PetProfilePhotoFormSet(data=self.request.POST or None,
                                                               instance=self.object)

        return context

    def get_success_url(self) -> str:
        # noinspection PyUnresolvedReferences
        return add_url_params(self.object.edit_pet_url(), {'success': self.action_type})

    def form_valid(self, form):
        # noinspection PyUnresolvedReferences
        form.instance.shelter = self.request.user_selected_shelter

        with transaction.atomic():
            pet = form.save()

            pet_photo_form_set = PetProfilePhotoFormSet(data=self.request.POST)
            if pet_photo_form_set.is_valid():
                pet_photo_form_set.save_photos(pet)

        return super().form_valid(form)


class PetsListViewMixin(ListView):
    context_object_name = 'pets'
    paginate_by = 30
    petListFiltersForm = None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # noinspection PyTypeChecker
        self.petListFiltersForm = PetListFiltersForm(request.GET)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['filters_form'] = self.petListFiltersForm
        context['search_term'] = self.petListFiltersForm.get_search_term()
        context['active_menu_item'] = 'pets_list'

        return context
