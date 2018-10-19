from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to='img/users/')

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)
