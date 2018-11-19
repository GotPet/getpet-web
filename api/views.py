from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_auth.registration.views import SocialConnectView
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.authentication import FirebaseAuthentication
from api.filters import PetFilter
from api.serializers import PetListSerializer, ShelterSerializer, FirebaseSerializer, TokenSerializer
from web.models import Pet, Shelter


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all pets.",
    security=[]

))
class PetListView(ListAPIView):
    queryset = Pet.objects.select_related('shelter').prefetch_related('profile_photos')
    serializer_class = PetListSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    authentication_classes = (FirebaseAuthentication,)

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PetFilter


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all shelters.",
    security=[]
))
class ShelterListView(ListAPIView):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = (AllowAny,)
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
