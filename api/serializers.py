from logging import getLogger

from django.db.models import Q
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.firebase import Firebase
from web.models import GetPetRequest, Pet, PetProfilePhoto, Shelter, User, UserPetChoice

logger = getLogger()


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = ['id', 'name', 'email', 'phone']


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

    def update(self, instance, validated_data):
        raise RuntimeError("Unsupported operation")

    def create(self, validated_data):
        raise RuntimeError("Unsupported operation")


class PetFlatListSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer()
    profile_photos = PetProfilePhotoSerializer(many=True)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'photo', 'shelter', 'short_description', 'description', 'profile_photos']


class UserPetChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPetChoice
        fields = ['pet', 'is_favorite']


class ShelterPetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetPetRequest
        fields = ['pet', ]


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

        email = firebase_user.email.lower()

        user = User.objects.filter(Q(username=firebase_user.uid) | Q(email=email)).first()
        if user:
            user.first_name = firebase_user.display_name
            user.save()
        else:
            user = User.objects.update_or_create(username=firebase_user.uid, defaults={
                'email': email,
                'first_name': firebase_user.display_name
            })

        token = Token.objects.filter(user=user).first()
        if token is None:
            token = Token(user=user)
            token.save()

        return token
