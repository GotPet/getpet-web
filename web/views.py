from typing import Any, Dict

from django.http import HttpRequest, HttpResponse
from django.http.response import Http404
from django.shortcuts import render
from django.utils.functional import cached_property
from django.views.generic import DetailView, ListView, RedirectView, TemplateView
from sentry_sdk import last_event_id

from utils.mixins import ViewPaginatorMixin
from web.constants import Constants
from web.models import Dog, Mentor, Pet, Shelter, TeamMember


class IndexView(TemplateView):
    template_name = 'web/index.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['organization_json_ld'] = Constants.GETPET_ORGANIZATION_JSON_LD
        context['pets'] = Pet.available.order_by('?')[:3]
        context['team_members'] = TeamMember.objects.all()

        return context


class AllDogsListView(ViewPaginatorMixin, ListView):
    template_name = 'web/all-dogs.html'
    model = Dog
    context_object_name = 'pets'
    paginate_by = 18
    queryset = Dog.available.all()
    ordering = ("order", "id")


class AllSheltersListView(ViewPaginatorMixin, ListView):
    template_name = 'web/all-shelters.html'
    model = Shelter
    context_object_name = 'shelters'
    paginate_by = 18
    queryset = Shelter.available.select_related('region').all()
    ordering = ("order", "id")


class ShelterPetsListView(ViewPaginatorMixin, ListView):
    template_name = 'web/shelter-pets.html'
    model = Pet
    context_object_name = 'pets'
    paginate_by = 18
    ordering = ("order", "id")

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
    model = Dog
    queryset = Dog.available.all().select_related_full_shelter().prefetch_related_photos_and_properties()
    context_object_name = 'pet'
    template_name = 'web/dog-profile.html'
    query_pk_and_slug = True


class MentorListView(ListView):
    template_name = 'web/mentors.html'
    model = Mentor
    context_object_name = 'mentors'
    paginate_by = None
    queryset = Mentor.objects.all()


# Documents
class PrivacyPolicyDocumentView(RedirectView):
    url = 'https://drive.google.com/file/d/14zVkvxMJv5Egr8KruDWZWNBLLsWGAIuy/view'


class AboutGetPetDocumentView(RedirectView):
    url = 'https://drive.google.com/file/d/10rbMmDMjoeJHT6L8opQbZyzA75PrH1SK/view'


class FairUseRulesDocumentView(RedirectView):
    url = 'https://drive.google.com/file/d/1IZ0jFolYgCasnxUpE6tVIeuobgdkX3wp/view'


# Status codes
def handler400(request: HttpRequest, *args, **argv) -> HttpResponse:
    return render(request, "web/status_codes/status-code-400.html", status=400)


def handler403(request: HttpRequest, *args, **argv) -> HttpResponse:
    return render(request, "web/status_codes/status-code-403.html", status=403)


def handler404(request: HttpRequest, *args, **argv) -> HttpResponse:
    return render(request, "web/status_codes/status-code-404.html", status=404)


def handler500(request: HttpRequest, *args, **argv) -> HttpResponse:
    return render(request, "web/status_codes/status-code-500.html", {
        'sentry_event_id': last_event_id(),
    }, status=500)


# Health check
def health_check(request) -> HttpResponse:
    return HttpResponse("OK")
