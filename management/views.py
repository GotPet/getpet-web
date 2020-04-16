from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView

from web.models import Pet, Shelter


# Todo add check for associated shelter
class ShelterPetsListView(ListView):
    template_name = 'management/index.html'
    model = Pet
    context_object_name = 'pets'
    paginate_by = 50

    def get_queryset(self):
        shelter = Shelter.user_selected_shelter(self.request.user)
        return Pet.pets_from_shelter(shelter)


@login_required
def no_associated_shelter(request) -> HttpResponse:
    return render(request, 'management/no-associated-shelter.html')
