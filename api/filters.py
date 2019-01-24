from django_filters import rest_framework as filters

from web.models import Pet


class PetFilter(filters.FilterSet):
    pet_ids = filters.BaseInFilter(field_name="id", required=True)

    class Meta:
        model = Pet
        fields = []
