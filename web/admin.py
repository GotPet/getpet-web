from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from enumfields.admin import EnumFieldListFilter
from reversion.admin import VersionAdmin

from web.forms import PetProfilePhotoInlineFormset
from web.models import Shelter, Pet, PetProfilePhoto, User, GetPetRequest

admin.site.register(User, UserAdmin)


class PetInline(admin.StackedInline):
    model = Pet


@admin.register(Shelter)
class ShelterAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'email', 'phone', 'created_at', 'updated_at']

    inlines = [
        PetInline
    ]


class PetProfilePhotoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PetProfilePhoto
    formset = PetProfilePhotoInlineFormset


@admin.register(Pet)
class PetAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'photo', 'short_description', 'shelter', 'created_at', 'updated_at']
    list_select_related = ['shelter']

    inlines = [
        PetProfilePhotoInline
    ]


@admin.register(GetPetRequest)
class GetPetRequestAdmin(VersionAdmin):
    list_display = ['user', 'pet', 'status']
    list_select_related = ['user', 'pet']
    list_filter = [('status', EnumFieldListFilter)]
