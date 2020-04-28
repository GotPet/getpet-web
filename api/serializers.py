from logging import getLogger

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.firebase import Firebase
from api.utils import first
from web.models import GetPetRequest, Pet, PetProfilePhoto, Shelter, User, UserPetChoice, Country, Region

logger = getLogger()


class CountryWithoutRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'code', ]


class RegionWithCountrySerializer(serializers.ModelSerializer):
    country = CountryWithoutRegionSerializer()

    class Meta:
        model = Region
        fields = ['name', 'code', 'country', ]


class ShelterSerializer(serializers.ModelSerializer):
    region = RegionWithCountrySerializer()

    class Meta:
        model = Shelter
        fields = ['id', 'name', 'email', 'phone', 'region', ]


class PetProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetProfilePhoto
        fields = ['photo']


class GeneratePetsRequestSerializer(serializers.Serializer):
    liked_pets = serializers.ListField(
        child=serializers.IntegerField()
    )

    disliked_pets = serializers.ListField(
        child=serializers.IntegerField()
    )

    region_code = serializers.SlugRelatedField(
        queryset=Region.objects.all(),
        slug_field='code',
        required=False,
        allow_null=True,
    )

    def update(self, instance, validated_data):
        raise RuntimeError("Unsupported operation")

    def create(self, validated_data):
        raise RuntimeError("Unsupported operation")


class RegionWithoutCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name', 'code', ]


class CountryWithRegionSerializer(serializers.ModelSerializer):
    regions = RegionWithoutCountrySerializer(many=True)

    class Meta:
        model = Country
        fields = ['name', 'code', 'regions', ]


class PetFlatListSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer()
    profile_photos = PetProfilePhotoSerializer(many=True)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'is_available', 'photo', 'shelter', 'short_description', 'description',
                  'profile_photos']


class UserPetChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPetChoice
        fields = ['pet', 'is_favorite']


class ShelterPetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetPetRequest
        fields = ['pet', ]


class PetProfilePhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetProfilePhoto
        fields = ['id', 'photo', 'order']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['key']


class FirebaseSerializer(serializers.Serializer):
    id_token = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        firebase = Firebase()
        id_token = validated_data['id_token']

        decoded_token = firebase.verify_id_token(id_token)

        uid = decoded_token.get('uid')
        firebase_user = firebase.get_user(uid)

        email = firebase_user.email
        if not email:
            provider_data = first(firebase_user.provider_data, lambda x: x.email)
            if provider_data:
                email = provider_data.email

        if email:
            email = email.lower()

        user = User.objects.filter(username=firebase_user.uid).first()
        if user is None:
            user = User.objects.filter(email=email).first()

        if user:
            user.last_name = firebase_user.display_name
            user.save()
        else:
            user, _ = User.objects.update_or_create(username=firebase_user.uid, defaults={
                'email': email,
                'last_name': firebase_user.display_name
            })

        token = Token.objects.filter(user=user).first()
        if token is None:
            token = Token(user=user)
            token.save()

        return token
