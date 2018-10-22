from rest_framework import serializers

from web.models import Pet, Shelter


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = ['id', 'name', 'email', 'phone']


class PetListSerializer(serializers.ModelSerializer):
    shelter_id = serializers.PrimaryKeyRelatedField(source='shelter', read_only=True)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'photo', 'shelter_id', 'short_description', 'description']
