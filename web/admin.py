from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from getpet import settings
from web.models import Country, GetPetRequest, Pet, PetProfilePhoto, PetProperty, Region, Shelter, User, UserPetChoice

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
class ShelterAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'email', 'phone', 'created_at', 'updated_at']
    raw_id_fields = ['authenticated_users']
    autocomplete_fields = ['region']


class RegionInline(admin.StackedInline):
    model = Region


@admin.register(Region)
class RegionAdmin(VersionAdmin):
    search_fields = ['name', 'code', ]
    list_display = ['name', 'code', 'country']
    list_select_related = ['country']
    autocomplete_fields = ['country']


@admin.register(Country)
class CountryAdmin(VersionAdmin):
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
class PetAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = [
        'name',
        'status',
        'photo',
        'shelter',
        'short_description',
        'total_pet_likes',
        'total_pet_dislikes',
        'likes_ratio',
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
        queryset = super().get_queryset(request).annotate(
            total_pet_likes=Count('users_pet_choices', filter=Q(users_pet_choices__is_favorite=True)),
            total_pet_dislikes=Count('users_pet_choices', filter=Q(users_pet_choices__is_favorite=False)),
        )

        if request.user.is_superuser:
            return queryset

        shelters = Shelter.objects.filter(authenticated_users=request.user)
        return queryset.filter(shelter__in=shelters)

    def total_pet_likes(self, obj):
        return obj.total_pet_likes

    total_pet_likes.admin_order_field = "total_pet_likes"
    total_pet_likes.short_description = _("Patinka skaičius")

    def total_pet_dislikes(self, obj):
        return obj.total_pet_dislikes

    total_pet_dislikes.admin_order_field = "total_pet_dislikes"
    total_pet_dislikes.short_description = _("Nepatinka skaičius")

    def likes_ratio(self, obj):
        total_pet_likes = self.total_pet_likes(obj)
        total = total_pet_likes + self.total_pet_dislikes(obj)

        return round(total_pet_likes * 100.0 / total, 2) if total else None

    likes_ratio.short_description = _("% patinka")

    def save_model(self, request, obj, form, change):
        old_pet = Pet.objects.filter(pk=obj.pk).first() if change else None

        super().save_model(request, obj, form, change)

        if change and 'status' in form.changed_data:
            from web.tasks import send_email_about_pet_status_update

            send_email_about_pet_status_update(obj.pk, old_pet.status)


@admin.register(GetPetRequest)
class GetPetRequestAdmin(VersionAdmin):
    list_display = ['user', 'pet', 'status', 'created_at']
    raw_id_fields = ['user', 'pet']
    list_select_related = ['user', 'pet', ]
    list_filter = ['status', 'pet__shelter__name', ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.is_superuser:
            return queryset

        shelters = Shelter.objects.filter(authenticated_users=request.user)
        return queryset.filter(pet__shelter__in=shelters)


@admin.register(UserPetChoice)
class UserPetChoiceAdmin(VersionAdmin):
    list_display = ['user', 'pet', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user', 'pet']
    list_select_related = ['user', 'pet']
    list_filter = ['is_favorite', 'created_at']


@admin.register(PetProfilePhoto)
class PetProfilePhotoAdmin(VersionAdmin):
    list_display = ['pet', 'photo', 'order', ]
    raw_id_fields = ['pet', 'created_by']
    list_select_related = ['pet', 'created_by']


@admin.register(PetProperty)
class PetPropertyAdmin(VersionAdmin):
    list_display = ['name', ]
    filter_horizontal = ['pets']
