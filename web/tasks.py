from django.core.mail import send_mail

from getpet import settings
from web.models import Pet


def send_email_about_pet_status_update(pet_id):
    pet = Pet.objects.get(pk=pet_id)

    send_mail(
        f'{pet} gyvūno statusas pakeistas',
        f'{pet} gyvūno iš prieglaudos {pet.shelter} statusas pakeistas.',
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        fail_silently=True
    )
