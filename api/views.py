from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api.serializers import PetListSerializer
from web.models import Pet


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[]

))
class PoliticianInfoListView(ListAPIView):
    queryset = Pet.objects.select_related('shelter')
    serializer_class = PetListSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
