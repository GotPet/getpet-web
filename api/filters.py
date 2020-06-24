from django.db.models import Q
from django_filters import rest_framework as filters

from web.models import Pet


class PetFilter(filters.FilterSet):
    pet_ids = filters.BaseInFilter(field_name="id", required=True)
    last_update = filters.IsoDateTimeFilter(field_name="updated_at", method='filter_last_update', required=False)

    def filter_last_update(self, queryset, name, value):
        return queryset.filter(Q(updated_at__gt=value) | Q(shelter__updated_at__gt=value))

    class Meta:
        model = Pet
        fields = ['pet_ids', 'last_update']
