from os.path import join

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

from web.utils import file_extension


class User(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to='img/users/')

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)


class Shelter(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=24)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Shelters"
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name


class Pet(models.Model):
    def _pet_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'web', 'pet', filename)

    name = models.CharField(max_length=64)
    photo = models.ImageField(upload_to=_pet_photo_file)

    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='pets')

    short_description = models.CharField(max_length=64)
    description = models.TextField()
    age = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Pets"
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name
