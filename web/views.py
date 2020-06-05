from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from web.models import Pet, Shelter


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


class PetProfileView(DetailView):
    model = Pet
    context_object_name = 'pet'
    template_name = 'web/pet-profile.html'


def health_check(request):
    return HttpResponse("OK")
