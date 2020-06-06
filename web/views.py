from typing import Any, Dict

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from utils.mixins import ViewPaginatorMixin
from utils.utils import add_url_params
from web.models import Pet, Shelter, TeamMember


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


class PetProfileView(DetailView):
    model = Pet
    context_object_name = 'pet'
    template_name = 'web/pet-profile.html'


def health_check(request):
    return HttpResponse("OK")
