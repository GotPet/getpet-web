from django.http import HttpResponse


def index(request):
    return HttpResponse("OK")


def health_check(request):
    return HttpResponse("OK")
