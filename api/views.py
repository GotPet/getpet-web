from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from api.filters import PetFilter
from api.serializers import FirebaseSerializer, GeneratePetsRequestSerializer, PetFlatListSerializer, \
    PetProfilePhotoUploadSerializer, ShelterPetSerializer, TokenSerializer, \
    UserPetChoiceSerializer, \
    CountryWithRegionSerializer
from web.models import Pet, UserPetChoice, GetPetRequest, Country


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all countries and regions.",
    security=[]
))
class CountriesAndRegionsListView(ListAPIView):
    queryset = Country.objects.prefetch_related('regions').order_by('name')
    serializer_class = CountryWithRegionSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[]
))
class PetListView(ListAPIView):
    queryset = Pet.objects.prefetch_related('profile_photos', 'properties').select_related_full_shelter().order_by(
        '-pk')
    serializer_class = PetFlatListSerializer
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
            disliked_pet_ids=serializer.data['disliked_pets'],
            region=serializer.data['region_code'],
        )

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_description="Saves pet choice on swipe.",
))
class UserPetChoiceView(LoggingMixin, UpdateAPIView):
    serializer_class = UserPetChoiceSerializer
    permission_classes = (IsAuthenticated,)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        return UserPetChoice.objects.filter(
            user=self.request.user,
            pet__id=self.request.data.get('pet')
        ).first()


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_description="Saves shelter pet request.",
))
class ShelterPetView(LoggingMixin, UpdateAPIView):
    serializer_class = ShelterPetSerializer
    permission_classes = (IsAuthenticated,)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        return GetPetRequest.objects.filter(
            user=self.request.user,
            pet__id=self.request.data.get('pet')
        ).first()


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="Upload pet profile photo.",
))
class PetProfilePhotoView(CreateAPIView):
    serializer_class = PetProfilePhotoUploadSerializer
    # TODO Change to ShelterAuthenticated
    permission_classes = (IsAuthenticated,)
    authentication_classes = [SessionAuthentication]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@method_decorator(name='post', decorator=swagger_auto_schema(
    security=[],
    request_body=FirebaseSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description="Returns API token from Firebase ID token for API calls.",
            schema=TokenSerializer
        )
    }
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
