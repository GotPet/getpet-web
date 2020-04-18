from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from management.forms import ShelterPetUpdateForm
from management.mixins import ViewPaginatorMixin
from management.utils import add_url_params
from web.models import Pet, Shelter


class ShelterPetsListView(LoginRequiredMixin, ViewPaginatorMixin, ListView):
    template_name = 'management/pets-list.html'
    model = Pet
    context_object_name = 'pets'
    ordering = ["-pk"]
    paginate_by = 100

    def get_queryset(self):
        shelter = Shelter.user_selected_shelter(self.request.user)
        return Pet.pets_from_shelter(shelter)

    def page_link(self, query_params, page):
        return add_url_params(reverse('management_pets_list') + query_params, {'page': page})


class ShelterPetUpdateView(LoginRequiredMixin, UpdateView):
    model = Pet
    template_name = 'management/pet-edit.html'
    context_object_name = 'pet'
    form_class = ShelterPetUpdateForm


@login_required
def no_associated_shelter(request) -> HttpResponse:
    return render(request, 'management/no-associated-shelter.html')
