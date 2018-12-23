from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_auth.registration.views import SocialConnectView
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Value, IntegerField

from api.authentication import FirebaseAuthentication
from api.filters import PetFilter
from api.serializers import PetFlatListSerializer, ShelterSerializer, FirebaseSerializer, TokenSerializer, \
    GeneratePetsRequestSerializer
from web.models import Pet, Shelter


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[]

))
class PetListView(ListAPIView):
    queryset = Pet.objects.select_related('shelter').prefetch_related('profile_photos')
    serializer_class = PetFlatListSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    authentication_classes = []

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PetFilter


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[]

))
class PetGenerateListView(CreateAPIView, ListModelMixin):
    serializer_class = PetFlatListSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    authentication_classes = []

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
    security=[]
))
class ShelterListView(ListAPIView):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []
    pagination_class = None


class FirebaseConnect(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FirebaseSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.create(serializer.data)
        result = TokenSerializer(token)

        return Response(result.data, status=status.HTTP_201_CREATED)


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter
    permission_classes = (AllowAny,)


class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter
    permission_classes = (AllowAny,)
