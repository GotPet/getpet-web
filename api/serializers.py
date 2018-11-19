from abc import ABC
from logging import getLogger

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.firebase import Firebase
from web.models import Pet, Shelter, PetProfilePhoto, User

logger = getLogger()


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = ['id', 'name', 'email', 'phone']


class PetProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetProfilePhoto
        fields = ['photo']


class PetListSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer()
    profile_photos = PetProfilePhotoSerializer(many=True)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'photo', 'shelter', 'short_description', 'description', 'profile_photos']


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

        user, is_created = User.objects.update_or_create(username=firebase_user.uid, defaults={
            'email': email,
            'first_name': firebase_user.display_name
        })

        token = Token.objects.filter(user=user).first()
        if token is None:
            token = Token(user=user)
            token.save()

        return token
