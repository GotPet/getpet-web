from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


@login_required()
def index(request):
    print("Labas")
    return render(request, 'management/index.html')
