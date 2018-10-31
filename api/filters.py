from django_filters import rest_framework as filters

from web.models import Pet


class PetFilter(filters.FilterSet):
    exclude_pet_ids = filters.BaseInFilter(field_name="id", exclude=True)

    class Meta:
        model = Pet
        fields = []
