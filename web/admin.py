from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from reversion.admin import VersionAdmin

from web.forms import PetProfilePhotoInlineFormset
from web.models import Shelter, Pet, PetProfilePhoto, User

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
    list_display = ['name', 'photo', 'short_description', 'shelter', 'age', 'created_at', 'updated_at']
    list_select_related = ['shelter']

    inlines = [
        PetProfilePhotoInline
    ]
