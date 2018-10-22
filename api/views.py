from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api.serializers import PetListSerializer, ShelterSerializer
from web.models import Pet, Shelter


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[]

))
class PetListView(ListAPIView):
    queryset = Pet.objects.select_related('shelter')
    serializer_class = PetListSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all shelters.",
    security=[]

))
class ShelterListView(ListAPIView):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
