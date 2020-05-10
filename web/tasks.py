from django.core.mail import send_mail

from getpet import settings

import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from web.models import Shelter, Pet

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def connect_super_users_to_shelters(shelter_pk=None):
    connected = 0

    for user in get_user_model().objects.filter(is_superuser=True):
        shelters = Shelter.objects.exclude(authenticated_users=user)
        if shelter_pk:
            shelters = shelters.filter(pk=shelter_pk)

        for shelter in shelters:
            shelter.authenticated_users.add(user)

            connected += 1

    return {
        'users_connected': connected
    }


def send_email_about_pet_status_update(pet_id, old_pet_status):
    pet = Pet.objects.get(pk=pet_id)

    send_mail(
        f'{pet} gyvūno statusas pakeistas',
        f"{pet} gyvūno iš prieglaudos {pet.shelter} statusas \"{old_pet_status.label}\" "
        f"pakeistas į \"{pet.status.label}\".",
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        fail_silently=True
    )
