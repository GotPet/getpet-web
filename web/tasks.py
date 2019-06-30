from django.core.mail import send_mail

from getpet import settings
from web.models import Pet


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
