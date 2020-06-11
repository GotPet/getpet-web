from django_filters import rest_framework as filters

from web.models import Pet


class PetFilter(filters.FilterSet):
    pet_ids = filters.BaseInFilter(field_name="id", required=True)
    last_update = filters.IsoDateTimeFilter(field_name="updated_at", lookup_expr='gt', required=False)

    class Meta:
        model = Pet
        fields = ['pet_ids', 'last_update']
