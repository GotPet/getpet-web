from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="start_game",
    security=[]
))
class PetListView(Create):
    queryset = Pet.objects.select_related('shelter').prefetch_related('profile_photos').order_by('-pk')
    serializer_class = PetFlatListSerializer
    permission_classes = (AllowAny,)

    filterset_class = PetFilter