from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from api.filters import PetFilter
from api.serializers import FirebaseSerializer, GeneratePetsRequestSerializer, PetFlatListSerializer, ShelterSerializer, \
    TokenSerializer
from web.models import Pet, Shelter


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[],
    deprecated=True
))
class PetListView(ListAPIView):
    queryset = Pet.objects.select_related('shelter').prefetch_related('profile_photos')
    serializer_class = PetFlatListSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    filterset_class = PetFilter


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="Generated pets to swipe.",
    security=[],
    request_body=GeneratePetsRequestSerializer,
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Returns generated pets list.",
            schema=PetFlatListSerializer
        )
    }
))
class PetGenerateListView(LoggingMixin, CreateAPIView, ListModelMixin):
    serializer_class = PetFlatListSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    def get_queryset(self):
        serializer = GeneratePetsRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        return Pet.generate_pets(
            liked_pet_ids=serializer.data['liked_pets'],
            disliked_pet_ids=serializer.data['disliked_pets']
        )

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all shelters.",
    security=[],
    deprecated=True
))
class ShelterListView(ListAPIView):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


@method_decorator(name='post', decorator=swagger_auto_schema(
    security=[],
))
class FirebaseConnect(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FirebaseSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.create(serializer.data)
        result = TokenSerializer(token)

        return Response(result.data, status=status.HTTP_201_CREATED)
