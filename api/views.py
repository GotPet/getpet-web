from django.utils.decorators import method_decorator
from drf_multiple_model.views import ObjectMultipleModelAPIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import PetFilter
from api.mixins import ApiLoggingMixin
from api.serializers import CountryWithRegionSerializer, FirebaseSerializer, GeneratePetsRequestSerializer, \
    PetFlatListSerializer, PetProfilePhotoUploadSerializer, ShelterPetSerializer, TokenSerializer, \
    UserPetChoiceSerializer
from web.models import Cat, Country, Dog, GetPetRequest, PetType, UserPetChoice


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all countries and regions.",
    security=[]
))
class CountriesAndRegionsListView(ApiLoggingMixin, ListAPIView):
    queryset = Country.objects.prefetch_related('regions').order_by('name')
    serializer_class = CountryWithRegionSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[],
    deprecated=True,
))
class PetListView(ListAPIView):
    queryset = Dog.objects.prefetch_related('profile_photos', 'properties').select_related_full_shelter().order_by(
        '-pk')
    serializer_class = PetFlatListSerializer
    permission_classes = (AllowAny,)

    filterset_class = PetFilter


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[]
))
class SelectedPetsListView(ObjectMultipleModelAPIView):
    querylist = [
        {
            'queryset': Dog.objects.prefetch_related('profile_photos',
                                                     'properties').select_related_full_shelter().order_by('-pk'),
            'serializer_class': PetFlatListSerializer,
            'label': 'dogs',
        },
        {
            'queryset': Cat.objects.prefetch_related('profile_photos',
                                                     'properties').select_related_full_shelter().order_by('-pk'),
            'serializer_class': PetFlatListSerializer,
            'label': 'cats',
        },
    ]
    permission_classes = (AllowAny,)
    serializer_class = PetFlatListSerializer
    filterset_class = PetFilter
    pagination_class = None

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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
class PetGenerateListView(ApiLoggingMixin, CreateAPIView, ListModelMixin):
    serializer_class = PetFlatListSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    def get_queryset(self):
        serializer = GeneratePetsRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        pet_type = PetType(serializer.data['pet_type'])

        return Dog.generate_pets(
            liked_pet_ids=serializer.data['liked_pets'],
            disliked_pet_ids=serializer.data['disliked_pets'],
            region=serializer.data['region_code'],
            pet_type=pet_type
        )

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_description="Saves pet choice on swipe.",
))
class UserPetChoiceView(ApiLoggingMixin, UpdateAPIView):
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
class ShelterPetView(ApiLoggingMixin, UpdateAPIView):
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
class FirebaseConnect(ApiLoggingMixin, CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FirebaseSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.create(serializer.data)
        result = TokenSerializer(token)

        return Response(result.data, status=status.HTTP_201_CREATED)
