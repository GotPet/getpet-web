from rest_framework import serializers

from web.models import Pet, Shelter


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = ['id', 'name', 'email', 'phone']


class PetListSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer()

    class Meta:
        model = Pet
        fields = ['id', 'name', 'photo', 'shelter', 'short_description', 'description']
