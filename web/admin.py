from typing import Any

from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.decorators import login_required
from django.db.models.base import Model
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from getpet import settings
from web.models import Country, GetPetRequest, Mentor, Pet, PetProfilePhoto, PetProperty, Region, Shelter, TeamMember, \
    User, \
    UserPetChoice
from web.tasks import connect_super_users_to_shelters

admin.site.site_header = _('GetPet Administravimas')
admin.site.site_title = admin.site.site_header

if not settings.DEBUG:
    admin.site.login = login_required(admin.site.login)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'full_name', 'email', 'shelters_count', 'pets_likes_count', 'pets_dislikes_count', 'pets_getpet_requests_count',
        'is_active', 'is_staff', 'date_joined']

    def get_queryset(self, request):
        # noinspection PyUnresolvedReferences
        return super().get_queryset(request).annotate_with_app_statistics().annotate_with_shelters_count()

    def full_name(self, obj) -> str:
        return str(obj)

    full_name.short_description = _("Vardas")

    def pets_likes_count(self, obj):
        return obj.pets_likes_count

    pets_likes_count.admin_order_field = "pets_likes_count"
    pets_likes_count.short_description = _("Patiko")

    def pets_dislikes_count(self, obj):
        return obj.pets_dislikes_count

    pets_dislikes_count.admin_order_field = "pets_dislikes_count"
    pets_dislikes_count.short_description = _("Nepatiko")

    def pets_getpet_requests_count(self, obj):
        return obj.pets_getpet_requests_count

    pets_getpet_requests_count.admin_order_field = "pets_getpet_requests_count"
    pets_getpet_requests_count.short_description = _("GetPet paspaudimai")

    def shelters_count(self, obj):
        return obj.shelters_count

    shelters_count.admin_order_field = "shelters_count"
    shelters_count.short_description = _("Valdomos prieglaudos")


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', ]
    list_display = ['name', 'email', 'phone', 'region', 'address', 'created_at', 'updated_at']
    filter_horizontal = ['authenticated_users']
    autocomplete_fields = ['region']
    list_select_related = ['region']
    list_filter = ['region']

    def log_change(self, request: HttpRequest, object: Model, message: Any) -> LogEntry:
        connect_super_users_to_shelters.delay(shelter_pk=object.pk)

        return super().log_change(request, object, message)

    def log_addition(self, request: HttpRequest, object: Model, message: Any) -> LogEntry:
        connect_super_users_to_shelters.delay(shelter_pk=object.pk)

        return super().log_addition(request, object, message)


class RegionInline(admin.StackedInline):
    model = Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code', ]
    list_display = ['name', 'code', 'country']
    list_select_related = ['country']
    autocomplete_fields = ['country']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).annotate_with_pets_count()

    search_fields = ['name', 'code', ]
    list_display = ['name', 'code', 'total_pets', ]

    inlines = [
        RegionInline
    ]

    def total_pets(self, obj):
        return obj.total_pets

    total_pets.admin_order_field = "total_pets"
    total_pets.short_description = _("Gyvūnų skaičius")


class PetProfilePhotoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PetProfilePhoto
    raw_id_fields = ['created_by']


class GetPetRequestInline(admin.TabularInline):
    model = GetPetRequest
    fields = ['user', 'full_name', 'email', 'status', 'created_at']
    raw_id_fields = ['user']
    readonly_fields = ['full_name', 'email', 'created_at']
    extra = 0

    def full_name(self, obj):
        return obj.user.get_full_name()

    full_name.short_description = _("Vartotojo vardas ir pavardė")

    def email(self, obj):
        return obj.user.email

    email.short_description = _("El. pašto adresas")


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    list_display = [
        'name',
        'status',
        'photo',
        'shelter',
        'short_description',
        'likes_count',
        'dislikes_count',
        'likes_ratio',
        'getpet_requests_count',
        'created_at',
        'updated_at',
    ]

    list_select_related = ['shelter']
    list_filter = ['status', 'shelter__name', ]

    inlines = [
        PetProfilePhotoInline,
        GetPetRequestInline
    ]

    def get_queryset(self, request):
        # noinspection PyUnresolvedReferences
        return super().get_queryset(request). \
            annotate_with_likes_and_dislikes(). \
            annotate_with_getpet_requests_count()

    def getpet_requests_count(self, obj):
        return obj.getpet_requests_count

    getpet_requests_count.admin_order_field = "getpet_requests_count"
    getpet_requests_count.short_description = _("Norai priglausti")

    def likes_count(self, obj):
        return obj.likes_count

    likes_count.admin_order_field = "likes_count"
    likes_count.short_description = _("Patinka skaičius")

    def dislikes_count(self, obj):
        return obj.dislikes_count

    dislikes_count.admin_order_field = "dislikes_count"
    dislikes_count.short_description = _("Nepatinka skaičius")

    def likes_ratio(self, obj):
        total_pet_likes = self.likes_count(obj)
        total = total_pet_likes + self.dislikes_count(obj)

        return round(total_pet_likes * 100.0 / total, 2) if total else None

    likes_ratio.short_description = _("% patinka")


@admin.register(GetPetRequest)
class GetPetRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'pet', 'status', 'created_at']
    raw_id_fields = ['user', 'pet']
    list_select_related = ['user', 'pet', ]
    list_filter = ['status', 'pet__shelter__name', ]


@admin.register(UserPetChoice)
class UserPetChoiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'pet', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user', 'pet']
    list_select_related = ['user', 'pet']
    list_filter = ['is_favorite', 'created_at']


@admin.register(PetProfilePhoto)
class PetProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ['pet', 'photo', 'order', ]
    raw_id_fields = ['pet', 'created_by']
    list_select_related = ['pet', 'created_by']


@admin.register(PetProperty)
class PetPropertyAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    filter_horizontal = ['pets']


@admin.register(TeamMember)
class TeamMemberAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'role', 'photo', 'email', ]


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo', ]
