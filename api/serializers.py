from rest_framework import serializers

from web.models import Pet, Shelter, PetProfilePhoto


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
