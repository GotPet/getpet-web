from __future__ import annotations

from _md5 import md5
from os.path import join
from typing import Optional

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, QuerySet
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from getpet import settings
from management.utils import add_url_params
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


class Shelter(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Prieglaudos pavadinimas"))
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="shelters", verbose_name=_("Regionas"))
    email = models.EmailField(verbose_name=_("Elektroninis paštas"))
    phone = models.CharField(max_length=24, verbose_name=_("Telefono numeris"))
    authenticated_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                                 verbose_name=_("Vartotojai tvarkantys prieglaudos informaciją"),
                                                 help_text=_("Priskirti vartotojai gali matyti prieglaudos gyvūnus "
                                                             "ir juos tvarkyti."))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Gyvūnų prieglauda")
        verbose_name_plural = _("Gyvūnų prieglaudos")
        ordering = ['-created_at', 'name']

    @staticmethod
    def user_selected_shelter(user: AbstractBaseUser) -> Optional[Shelter]:
        if user.is_authenticated:
            return Shelter.objects.filter(authenticated_users=user).first()

        return None

    def __str__(self):
        return self.name


class PetStatus(models.IntegerChoices):
    AVAILABLE = 1, _('Laukia šeimininko')
    TAKEN_TEMPORARY = 2, _('Laikinai paimtas per GetPet')
    TAKEN_PERMANENTLY = 3, _('Paimtas visam laikui per GetPet')
    TAKEN_NOT_VIA_GETPET = 4, _('Paimtas ne per GetPet')


class PetQuerySet(models.QuerySet):
    def select_related_full_shelter(self):
        return self.select_related('shelter', 'shelter__region', 'shelter__region__country')


class AvailablePetsManager(models.Manager):
    def get_queryset(self):
        return PetQuerySet(self.model, using=self._db).filter(status=PetStatus.AVAILABLE)


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

    @staticmethod
    def pets_from_shelter(shelter: Shelter) -> QuerySet[Pet]:
        queryset = Pet.objects.filter(shelter=shelter).order_by('-pk')

        return queryset

    def main_profile_image(self, size=None) -> str:
        return add_url_params(self.photo.url, {'w': size, 'h': size})

    def main_profile_medium(self) -> str:
        return self.main_profile_image(size=64)

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
        slug = slugify(self.pet.name)

        filename = f"{slug}-photo-{self.order}.{ext}"
        return join('img', 'web', 'pet', slug, 'profile', filename)

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='profile_photos')
    photo = models.ImageField(upload_to=_pet_photo_file, verbose_name=_('Gyvūno profilio nuotrauka'))
    order = models.PositiveIntegerField(default=0)

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
    is_favorite = models.BooleanField(verbose_name=_("Vartotojas pamėgo gyvūną"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Vartotojo gyvūno pasirinkimaas")
        verbose_name_plural = _("Vartotojų gyvūnų pasirinkimai")
        unique_together = ('user', 'pet')
        default_related_name = "users_pet_choices"
        ordering = ['-id']
