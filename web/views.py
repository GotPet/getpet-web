from django.http import HttpResponse
from django.shortcuts import redirect, render


def index(request):
    return redirect('https://www.facebook.com/getpet.lt/')
    # return render(request, 'web/index.html')


def health_check(request):
    return HttpResponse("OK")
