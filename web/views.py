from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView

from web.models import Pet


def index(request):
    return redirect('https://www.facebook.com/getpet.lt/')
    # return render(request, 'web/index.html')


class PetProfileView(DetailView):
    model = Pet
    context_object_name = 'pet'
    template_name = 'web/pet-profile.html'


def health_check(request):
    return HttpResponse("OK")
