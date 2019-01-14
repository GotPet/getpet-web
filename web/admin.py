from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from enumfields.admin import EnumFieldListFilter
from reversion.admin import VersionAdmin

from web.models import Shelter, Pet, PetProfilePhoto, User, GetPetRequest, UserPetChoice
from django.utils.translation import gettext_lazy as _

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


class GetPetRequestInline(admin.TabularInline):
    model = GetPetRequest
    fields = ['user', 'full_name', 'status', 'created_at']
    readonly_fields = ['user', 'full_name', 'created_at']
    extra = 0

    def full_name(self, obj):
        return obj.user.get_full_name()

    full_name.short_description = _("Vartotojo vardas ir pavardė")


@admin.register(Pet)
class PetAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'status', 'photo', 'short_description', 'shelter', 'created_at', 'updated_at']
    list_select_related = ['shelter']
    list_filter = [('status', EnumFieldListFilter), 'shelter__name', ]

    inlines = [
        PetProfilePhotoInline,
        GetPetRequestInline
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change and 'status' in form.changed_data:
            from web.tasks import send_email_about_pet_status_update

            send_email_about_pet_status_update(obj.pk)


@admin.register(GetPetRequest)
class GetPetRequestAdmin(VersionAdmin):
    list_display = ['user', 'pet', 'status', 'created_at']
    raw_id_fields = ['user', 'pet']
    list_select_related = ['user', 'pet']
    list_filter = [('status', EnumFieldListFilter)]


@admin.register(UserPetChoice)
class UserPetChoiceAdmin(VersionAdmin):
    list_display = ['user', 'pet', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user', 'pet']
    list_select_related = ['user', 'pet']
    list_filter = ['is_favorite', 'created_at']
