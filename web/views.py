from typing import Any, Dict

from django.http import HttpResponse
from django.http.response import Http404
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import DetailView, ListView

from utils.mixins import ViewPaginatorMixin
from web.models import Pet, Shelter, TeamMember


def index(request) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('web:demo')

    return redirect('https://www.facebook.com/getpet.lt/')


class IndexView(ListView):
    template_name = 'web/index.html'
    model = Pet
    context_object_name = 'pets'

    def get_queryset(self):
        return Pet.available.order_by('?')[:3]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['team_members'] = TeamMember.objects.all()

        return context


class AllDogsListView(ViewPaginatorMixin, ListView):
    template_name = 'web/all-dogs.html'
    model = Pet
    context_object_name = 'pets'
    paginate_by = 18
    queryset = Pet.available.all()
    ordering = '-pk'


class AllSheltersListView(ViewPaginatorMixin, ListView):
    template_name = 'web/all-shelters.html'
    model = Shelter
    context_object_name = 'shelters'
    paginate_by = 18
    queryset = Shelter.available.select_related('region').all()
    ordering = '-id'


class ShelterPetsListView(ViewPaginatorMixin, ListView):
    template_name = 'web/shelter-pets.html'
    model = Pet
    context_object_name = 'pets'
    paginate_by = 18
    ordering = '-pk'
    allow_empty = False

    def get_queryset(self):
        return Pet.available.filter(shelter=self.selected_shelter).all()

    @cached_property
    def selected_shelter(self) -> Shelter:
        slug = self.kwargs.get('slug', None)
        if slug is None:
            raise ValueError("No slug argument given")

        shelter = Shelter.available.filter(slug=slug).first()

        if shelter is None:
            raise Http404(f"Unable to find shelter")

        return shelter

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)

        context_data['shelter'] = self.selected_shelter

        return context_data


class DogProfileView(DetailView):
    model = Pet
    queryset = Pet.available.all().select_related_full_shelter().prefetch_related_photos_and_properties()
    context_object_name = 'pet'
    template_name = 'web/dog-profile.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)

        context_data['similar_pets'] = self.object.similar_pets_from_same_shelter()

        return context_data


def privacy_policy(request) -> HttpResponse:
    return redirect('https://drive.google.com/file/d/14zVkvxMJv5Egr8KruDWZWNBLLsWGAIuy/view')


def about_getpet(request) -> HttpResponse:
    return redirect('https://drive.google.com/file/d/10rbMmDMjoeJHT6L8opQbZyzA75PrH1SK/view')


def fair_use_rules(request) -> HttpResponse:
    return redirect('https://drive.google.com/file/d/1IZ0jFolYgCasnxUpE6tVIeuobgdkX3wp/view')


def health_check(request) -> HttpResponse:
    return HttpResponse("OK")
