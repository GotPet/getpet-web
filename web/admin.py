from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from enumfields.admin import EnumFieldListFilter
from reversion.admin import VersionAdmin

from web.models import GetPetRequest, Pet, PetProfilePhoto, Shelter, User, UserPetChoice

admin.site.site_header = _('GetPet Administravimas')
admin.site.site_title = admin.site.site_header


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_getpet_requests=Count('get_pet_requests'),
        )

    list_display = [
        'username', 'email', 'first_name', 'last_name', 'total_getpet_requests', 'is_staff']

    def total_getpet_requests(self, obj):
        return obj.total_getpet_requests

    total_getpet_requests.admin_order_field = "total_getpet_requests"
    total_getpet_requests.short_description = _("GetPet paspaudimai")


class PetInline(admin.StackedInline):
    model = Pet


@admin.register(Shelter)
class ShelterAdmin(VersionAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'email', 'phone', 'created_at', 'updated_at']
    raw_id_fields = ['authenticated_users']

    inlines = [
        PetInline
    ]


class PetProfilePhotoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PetProfilePhoto


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
    list_filter = [('status', EnumFieldListFilter), 'shelter__name', ]

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
        super().save_model(request, obj, form, change)

        if change and 'status' in form.changed_data:
            from web.tasks import send_email_about_pet_status_update

            send_email_about_pet_status_update(obj.pk)


@admin.register(GetPetRequest)
class GetPetRequestAdmin(VersionAdmin):
    list_display = ['user', 'pet', 'status', 'created_at']
    raw_id_fields = ['user', 'pet']
    list_select_related = ['user', 'pet', ]
    list_filter = [('status', EnumFieldListFilter), 'pet__shelter__name', ]

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
