from enum import unique
from os.path import join

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

from getpet import settings
from web.utils import file_extension
from django.utils.translation import gettext_lazy as _
from enumfields import IntEnum, EnumIntegerField


class User(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to='img/users/', verbose_name=_("Vartotojo nuotrauka"))

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)

    def __str__(self):
        name = self.get_full_name()

        return name if name else self.email


class Shelter(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Prieglaudos pavadinimas"))
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

    def __str__(self):
        return self.name


@unique
class PetStatus(IntEnum):
    AVAILABLE = 1
    TAKEN_TEMPORARY = 2
    TAKEN_PERMANENTLY = 3
    TAKEN_NOT_VIA_GETPET = 4

    class Labels:
        AVAILABLE = _('Laukia šeimininko')
        TAKEN_TEMPORARY = _('Laikinai paimtas per GetPet')
        TAKEN_PERMANENTLY = _('Paimtas visam laikui per GetPet')
        TAKEN_NOT_VIA_GETPET = _('Paimtas ne per GetPet')


class PetQuerySet(models.QuerySet):
    pass


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
    status = EnumIntegerField(PetStatus, default=PetStatus.AVAILABLE, db_index=True,
                              verbose_name=_("Gyvūno statusas"),
                              help_text=_("Pažymėjus gyvūną, kaip laukiantį šeiminką jis bus rodomas programėlėje."))
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

    # Return already disliked pets
    @staticmethod
    def generate_pets(liked_pet_ids, disliked_pet_ids):
        queryset = Pet.objects.select_related('shelter') \
            .prefetch_related('profile_photos') \
            .exclude(pk__in=liked_pet_ids).order_by()

        new_pets = queryset.exclude(pk__in=disliked_pet_ids).annotate(
            priority=models.Value(1, output_field=models.IntegerField())
        ).order_by('?')

        # already_disliked_pets = queryset.filter(pk__in=disliked_pet_ids).annotate(
        #     priority=models.Value(2, output_field=models.IntegerField())
        # )

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


@unique
class GetPetRequestStatus(IntEnum):
    USER_WANTS_PET = 1
    PET_TAKEN_TEMPORARY = 2
    PET_RETURNED = 3
    PET_TAKEN_PERMANENTLY = 4

    class Labels:
        USER_WANTS_PET = _('Noras paimti gyvūną')
        PET_TAKEN_TEMPORARY = _('Gyvūnas laikinai pasiimtas')
        PET_RETURNED = _("Gyvūnas gražintas po laikinos globos")
        PET_TAKEN_PERMANENTLY = _("Gyvūnas pasiimtas visam laikui")


class GetPetRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_("Vartotojas"))
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name=_("Gyvūnas"))
    status = EnumIntegerField(GetPetRequestStatus, default=GetPetRequestStatus.USER_WANTS_PET,
                              verbose_name=_("Gyvūno statusas"),
                              help_text=_("Pasirenkamas vienas iš gyvūno statusų pas potencialų šeimininką"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Noras priglausti gyvūną")
        verbose_name_plural = _("Norai priglausti gyvūnus")
        unique_together = ('user', 'pet')
        default_related_name = "get_pet_requests"


class UserPetChoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_("Vartotojas"))
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
