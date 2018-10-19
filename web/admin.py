from django.contrib import admin
from reversion.admin import VersionAdmin

from web.models import Shelter, Pet


class PetInline(admin.StackedInline):
    model = Pet


@admin.register(Shelter)
class ShelterAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'email', 'phone', 'created_at', 'updated_at']

    inlines = [
        PetInline
    ]


@admin.register(Pet)
class PetAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'photo', 'short_description', 'shelter', 'age', 'created_at', 'updated_at']
    list_select_related = ['shelter']

    inlines = [

    ]
