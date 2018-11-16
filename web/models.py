from os.path import join

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

from getpet import settings
from web.utils import file_extension
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to='img/users/', verbose_name=_("Vartotojo nuotrauka"))

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)


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


class Pet(models.Model):
    def _pet_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'web', 'pet', slug, filename)

    name = models.CharField(max_length=64, verbose_name=_("Gyvūno vardas"))
    photo = models.ImageField(upload_to=_pet_photo_file, verbose_name=_("Gyvūno nuotrauka"))

    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='pets', verbose_name=_("Prieglauda"),
                                help_text=_("Prieglauda, kurioje šiuo metu randasi gyvūnas"))

    short_description = models.CharField(max_length=64, verbose_name=_("Trumpas aprašymas"), help_text=_(
        "Trumpas aprašymas apie gyvūną rodomas programėlės pagrindiniame ekrane skirtas pritraukti varototojus"
        " paspausti ant gyvūno profilio."))
    description = models.TextField(verbose_name=_("Aprašymas"),
                                   help_text=_("Gyvūno aprašymas matomas įėjus į gyvūno profilį."))
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Amžius"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Gyvūnas")
        verbose_name_plural = _("Gyvūnai")
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name


class PetProfilePhoto(models.Model):
    def _pet_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.pet.name)

        filename = f"{slug}-photo-{self.order}.{ext}"
        return join('img', 'web', 'pet', slug, 'profile', filename)

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='profile_photos')
    photo = models.ImageField(upload_to=_pet_photo_file, verbose_name=_('Gyvūno nuotrauka'))
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Gyvūno nuotrauka")
        verbose_name_plural = _("Gyvūnų nuotraukos")
        ordering = ['order']

    def __str__(self):
        return self.photo.url
