from __future__ import annotations

import uuid
from _md5 import md5
from os.path import join
from typing import Optional

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from getpet import settings
from management.utils import image_url_with_size_params
from web.utils import file_extension


class User(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to='img/users/', verbose_name=_("Vartotojo nuotrauka"))
    social_image_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)

    def user_image_url(self):
        if self.social_image_url:
            return self.social_image_url

        return self.gravatar_url()

    def gravatar_url(self):
        g_hash = md5(str(self.email).encode('utf-8').lower()).hexdigest()
        return f"https://www.gravatar.com/avatar/{g_hash}?s=128&d=identicon"

    def extract_name(self):
        return self.get_full_name().split(' ')[0]

    def __str__(self):
        name = self.get_full_name()

        return name if name else self.email


class CountryQuerySet(models.QuerySet):
    def annotate_with_pets_count(self):
        return self.annotate(total_pets=Count(
            'regions__shelters__pets',
        ))


class Country(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Šalies pavadinimas"))
    code = models.CharField(verbose_name=_("Šalies kodas"), max_length=2, unique=True,
                            help_text=_("Šalies kodas pagal ISO 3166 alpha 2 standartą pvz: lt, lv"))

    objects = CountryQuerySet.as_manager()

    class Meta:
        verbose_name = _("Šalis")
        verbose_name_plural = _("Šalys")
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = self.code.lower()

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Regiono pavadinimas"))
    code = models.CharField(verbose_name=_("Regiono kodas"), max_length=32, unique=True,
                            help_text=_("Unikalus regiono kodas pvz: ankara"))
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="regions", verbose_name=_("Šalis"))

    class Meta:
        verbose_name = _("Regionas")
        verbose_name_plural = _("Regionai")
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = self.code.lower()

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class ShelterQuerySet(models.QuerySet):
    pass


class SheltersManager(models.Manager):
    def get_queryset(self) -> ShelterQuerySet:
        return ShelterQuerySet(self.model, using=self._db).filter(is_published=True)


class Shelter(models.Model):
    def _shelter_square_logo_file(self, filename: str) -> str:
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-square-logo.{ext}"
        return join('img', 'web', 'shelter', slug, filename)

    name = models.CharField(max_length=128, verbose_name=_("Prieglaudos pavadinimas"))
    legal_name = models.CharField(max_length=256, null=True, verbose_name=_("Įstaigos pavadinimas"))

    is_published = models.BooleanField(default=True, db_index=True, verbose_name=_("Paskelbta"),
                                       help_text=_("Pažymėjus prieglauda matoma viešai"))

    square_logo = models.ImageField(upload_to=_shelter_square_logo_file, null=True, blank=True,
                                    verbose_name=_("Kvadratinis logotipas"))

    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="shelters", verbose_name=_("Regionas"))

    address = models.CharField(max_length=256, null=True, verbose_name=_("Adresas"))

    email = models.EmailField(verbose_name=_("Elektroninis paštas"))
    phone = models.CharField(max_length=24, verbose_name=_("Telefono numeris"))

    website = models.URLField(blank=True, null=True, verbose_name=_("Interneto svetainė"))
    facebook = models.URLField(blank=True, null=True, verbose_name=_("Facebook"))
    instagram = models.URLField(blank=True, null=True, verbose_name=_("Instagram"))

    authenticated_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                                 verbose_name=_("Vartotojai tvarkantys prieglaudos informaciją"),
                                                 help_text=_("Priskirti vartotojai gali matyti prieglaudos gyvūnus "
                                                             "ir juos tvarkyti."))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    objects = ShelterQuerySet.as_manager()
    available = SheltersManager()

    class Meta:
        verbose_name = _("Gyvūnų prieglauda")
        verbose_name_plural = _("Gyvūnų prieglaudos")
        ordering = ['-created_at', 'name']

    @staticmethod
    def user_associated_shelters(user: AbstractBaseUser):
        if user.is_authenticated:
            return Shelter.objects.filter(authenticated_users=user)

        return Shelter.objects.none()

    @staticmethod
    def user_selected_shelter(user: AbstractBaseUser,
                              shelter_id: int = None,
                              request: HttpRequest = None) -> Optional[Shelter]:
        shelters = Shelter.user_associated_shelters(user) if user.is_authenticated else Shelter.objects.none()

        if shelter_id is None and request:
            from management.middleware import AssociateSheltersMiddleware
            shelter_id = request.COOKIES.get(AssociateSheltersMiddleware.SELECTED_SHELTER_COOKIE_ID, None)

        if shelter_id:
            shelters = shelters.filter(id=shelter_id)

        return shelters.first()

    def edit_shelter_url(self) -> str:
        return reverse('management_shelter_info_update', kwargs={'pk': self.pk})

    def square_logo_medium_url(self) -> Optional[str]:
        if self.square_logo:
            return image_url_with_size_params(self.square_logo.url, size=64)

    def __str__(self):
        return self.name


class PetStatus(models.IntegerChoices):
    AVAILABLE = 1, _('Laukia šeimininko')
    TAKEN_TEMPORARY = 2, _('Laikinai paimtas per GetPet')
    TAKEN_PERMANENTLY = 3, _('Paimtas visam laikui per GetPet')
    TAKEN_NOT_VIA_GETPET = 4, _('Paimtas ne per GetPet')


class PetGender(models.IntegerChoices):
    Male = 1, _('Patinas')
    Female = 2, _('Patelė')

    __empty__ = _('Nepatikslinta')


class PetSize(models.IntegerChoices):
    Small = 1, _('Mažas')
    Medium = 2, _('Vidutinis')
    Large = 3, _('Didelis')

    __empty__ = _('Nepatikslinta')


class PetQuerySet(models.QuerySet):
    def select_related_full_shelter(self):
        return self.select_related('shelter', 'shelter__region', 'shelter__region__country')

    def annotate_with_total_likes(self):
        return self.annotate(
            total_likes=Count(
                'users_pet_choices',
                filter=models.Q(users_pet_choices__is_favorite=True)
            )
        )

    def filter_by_search_term(self, search_term: str):
        return self.filter(name__icontains=search_term)


class AvailablePetsManager(models.Manager):
    def get_queryset(self):
        return PetQuerySet(self.model, using=self._db).filter(status=PetStatus.AVAILABLE, shelter__is_published=True)


NULLABLE_BOOLEAN_FIELD_CHOICES = (
    (True, _("Taip")),
    (False, _("Ne")),
    (None, _("Nepatikslinta")),
)


class Pet(models.Model):
    def _pet_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'web', 'pet', slug, filename)

    name = models.CharField(max_length=64, verbose_name=_("Gyvūno vardas"))
    status = models.IntegerField(
        choices=PetStatus.choices,
        default=PetStatus.AVAILABLE,
        db_index=True,
        verbose_name=_("Gyvūno statusas"),
        help_text=_("Pažymėjus gyvūną, kaip laukiantį šeiminką jis bus rodomas programėlėje.")
    )
    photo = models.ImageField(upload_to=_pet_photo_file, verbose_name=_("Gyvūno nuotrauka"))

    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='pets', verbose_name=_("Prieglauda"),
                                help_text=_("Prieglauda, kurioje šiuo metu randasi gyvūnas"))

    short_description = models.CharField(max_length=64, verbose_name=_("Trumpas aprašymas"), help_text=_(
        "Trumpas aprašymas apie gyvūną rodomas programėlės pagrindiniame ekrane skirtas pritraukti varototojus"
        " paspausti ant gyvūno profilio."))
    description = models.TextField(verbose_name=_("Aprašymas"),
                                   help_text=_("Gyvūno aprašymas matomas įėjus į gyvūno profilį."))

    information_for_getpet_team = models.TextField(
        null=True, blank=True,
        verbose_name=_("Informacija skirta GetPet komandai"),
        help_text=_("Įrašykite informaciją skirtą GetPet komandai pvz: žmogaus kontaktinę informaciją "
                    "dėl GetPet mentoriaus priskyrimo.")
    )

    gender = models.IntegerField(
        verbose_name=_("Lytis"),
        choices=PetGender.choices,
        blank=True,
        null=True
    )
    age = models.IntegerField(
        verbose_name=_("Amžius"),
        blank=True,
        null=True
    )
    weight = models.IntegerField(
        verbose_name=_("Svoris"),
        blank=True,
        null=True
    )
    size = models.IntegerField(
        verbose_name=_("Dydis"),
        choices=PetSize.choices,
        blank=True,
        null=True
    )
    desexed = models.BooleanField(
        verbose_name=_("Kastruotas ar sterilizuotas"),
        choices=NULLABLE_BOOLEAN_FIELD_CHOICES,
        blank=True,
        null=True,
        help_text=_("Pažymėkite jei gyvūnas yra kastruotas arba sterilizuotas")
    )
    is_vaccinated = models.BooleanField(
        verbose_name=_("Vakcinuotas"),
        choices=NULLABLE_BOOLEAN_FIELD_CHOICES,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    objects = PetQuerySet.as_manager()
    available = AvailablePetsManager()

    class Meta:
        verbose_name = _("Gyvūnas")
        verbose_name_plural = _("Gyvūnai")
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name

    def is_available(self) -> bool:
        return self.status == PetStatus.AVAILABLE

    def pet_status_badge_color_class(self) -> str:
        if self.status == PetStatus.AVAILABLE:
            return "badge-success"

        return "badge-primary"

    @staticmethod
    def pets_from_shelter(shelter: Shelter, annotate_with_total_likes=False) -> QuerySet[Pet]:
        queryset = Pet.objects.filter(shelter=shelter).order_by('-pk')

        if annotate_with_total_likes:
            queryset = queryset.annotate_with_total_likes()

        return queryset

    def main_profile_medium(self) -> str:
        return image_url_with_size_params(self.photo.url, size=64)

    def edit_pet_url(self) -> str:
        return reverse('management_pet_update', kwargs={'pk': self.pk})

    @staticmethod
    def generate_pets(liked_pet_ids, disliked_pet_ids, region):
        queryset = Pet.available.prefetch_related('profile_photos') \
            .select_related_full_shelter() \
            .exclude(pk__in=liked_pet_ids).order_by()

        if region:
            queryset = queryset.filter(shelter__region=region)

        new_pets = queryset.exclude(pk__in=disliked_pet_ids).order_by('?')

        return new_pets


class PetProfilePhoto(models.Model):
    def _pet_photo_file(self, filename):
        ext = file_extension(filename)

        if self.pet:
            slug = slugify(self.pet.name)

            filename = f"{slug}-photo-{self.order}.{ext}"
            return join('img', 'web', 'pet', slug, 'profile', filename)
        else:
            filename = f"{uuid.uuid4()}-photo.{ext}"
            return join('img', 'web', 'pet', 'all', 'profile', filename)

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, null=True, blank=True, related_name='profile_photos')
    photo = models.ImageField(upload_to=_pet_photo_file, verbose_name=_('Gyvūno profilio nuotrauka'))
    order = models.PositiveIntegerField(default=0)

    def large_photo(self) -> str:
        return image_url_with_size_params(self.photo.url, size=120)

    class Meta:
        verbose_name = _("Gyvūno profilio nuotrauka")
        verbose_name_plural = _("Gyvūnų profilio nuotraukos")
        ordering = ['order']

    def __str__(self):
        return self.photo.url


class GetPetRequestStatus(models.IntegerChoices):
    USER_WANTS_PET = 1, _('Noras paimti gyvūną')
    PET_TAKEN_TEMPORARY = 2, _('Gyvūnas laikinai pasiimtas')
    PET_RETURNED = 3, _("Gyvūnas gražintas po laikinos globos")
    PET_TAKEN_PERMANENTLY = 4, _("Gyvūnas pasiimtas visam laikui")


class GetPetRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Vartotojas"))
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name=_("Gyvūnas"))
    status = models.IntegerField(
        choices=GetPetRequestStatus.choices,
        default=GetPetRequestStatus.USER_WANTS_PET,
        verbose_name=_("Gyvūno statusas"),
        help_text=_("Pasirenkamas vienas iš gyvūno statusų pas potencialų šeimininką")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Noras priglausti gyvūną")
        verbose_name_plural = _("Norai priglausti gyvūnus")
        unique_together = ('user', 'pet')
        default_related_name = "get_pet_requests"


class UserPetChoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Vartotojas"))
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name=_("Gyvūnas"))
    is_favorite = models.BooleanField(verbose_name=_("Vartotojas pamėgo gyvūną"), db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Vartotojo gyvūno pasirinkimaas")
        verbose_name_plural = _("Vartotojų gyvūnų pasirinkimai")
        unique_together = ('user', 'pet')
        default_related_name = "users_pet_choices"
        ordering = ['-id']
