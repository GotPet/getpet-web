from typing import Any, Dict

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from utils.mixins import ViewPaginatorMixin
from utils.utils import add_url_params
from web.models import Pet, PetQuerySet, Shelter, TeamMember


def index(request):
    if request.user.is_authenticated:
        return redirect('web:demo')

    return redirect('https://www.facebook.com/getpet.lt/')


class IndexView(ListView):
    template_name = 'web/index.html'
    model = Pet
    context_object_name = 'pets'

    def get_queryset(self):
        shelter = Shelter.objects.filter(name='Linksmosios pėdutės').first()

        pets = Pet.available.order_by('?')

        if shelter is not None:
            pets = pets.filter(shelter=shelter)

        return pets[:6]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['team_members'] = TeamMember.objects.all()

        return context


class AllPetsListView(ViewPaginatorMixin, ListView):
    template_name = 'web/all-pets.html'
    model = Pet
    context_object_name = 'pets'
    paginate_by = 18
    queryset = Pet.available.all()
    ordering = '?'

    def page_link(self, query_params, page):
        return add_url_params(reverse('web:all_pets') + query_params, {'page': page})


class AllSheltersListView(ViewPaginatorMixin, ListView):
    template_name = 'web/all-shelters.html'
    model = Shelter
    context_object_name = 'shelters'
    paginate_by = 18
    queryset = Shelter.available.all()
    ordering = '-id'

    def page_link(self, query_params, page):
        return add_url_params(reverse('web:all_shelters') + query_params, {'page': page})


class ShelterPetsListView(ViewPaginatorMixin, ListView):
    template_name = 'web/all-pets.html'
    model = Pet
    context_object_name = 'pets'
    paginate_by = 18
    queryset = Pet.available.all()
    ordering = '?'

    def page_link(self, query_params, page):
        return add_url_params(reverse('web:all_pets') + query_params, {'page': page})


class PetProfileView(DetailView):
    model = Pet
    queryset = Pet.available.all()
    context_object_name = 'pet'
    template_name = 'web/pet-profile.html'
    query_pk_and_slug = True


def health_check(request):
    return HttpResponse("OK")
