import logging
from typing import Optional

from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.sitemaps import ping_google
from django.core.mail import send_mail

from getpet import settings
from utils.utils import Datadog
from web.models import GetPetRequest, Pet, PetStatus, Shelter, User, UserPetChoice

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


@shared_task(soft_time_limit=30)
def send_email_about_pet_status_update(pet_pk, old_pet_status_str):
    pet = Pet.objects.get(pk=pet_pk)

    send_mail(
        f'{pet} statusas pakeistas į {pet.get_status_display()}',
        f"""
{pet} gyvūno iš prieglaudos {pet.shelter} statusas {old_pet_status_str} pakeistas į {pet.get_status_display()}. \n
{pet.information_for_getpet_team}
        """.strip(),
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
    )

    return 1


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


@shared_task(soft_time_limit=10)
def on_pet_created_or_updated(pet_pk: int, old_pet_status: Optional[PetStatus], old_pet_status_text: Optional[str]):
    pet = Pet.objects.get(pk=pet_pk)
    _pet_status_to_send_email = (PetStatus.TAKEN_TEMPORARY, PetStatus.TAKEN_PERMANENTLY)

    if old_pet_status and old_pet_status != pet.status and pet.status in _pet_status_to_send_email:
        send_email_about_pet_status_update.delay(pet_pk=pet.pk, old_pet_status_str=old_pet_status_text)

    ping_google_about_sitemap_update.delay()


@shared_task(soft_time_limit=10, autoretry_for=(Exception,), retry_backoff=True)
def ping_google_about_sitemap_update():
    ping_google()


@shared_task(soft_time_limit=60, autoretry_for=(Exception,), retry_backoff=True)
def sync_product_metrics():
    Datadog().gauge('product.shelters.count', Shelter.objects.count())
    Datadog().gauge('product.shelters.available', Shelter.available.count())

    Datadog().gauge('product.users.registered', User.objects.filter(groups__name='Api').count())

    Datadog().gauge('product.dogs.getpet_requests', GetPetRequest.objects.count())
    Datadog().gauge('product.dogs.likes', UserPetChoice.objects.filter(is_favorite=True).count())
    Datadog().gauge('product.dogs.dislikes', UserPetChoice.objects.filter(is_favorite=False).count())

    for shelter in Shelter.available.all().annotate_with_statistics():
        Datadog().gauge('product.dogs.available', shelter.pets_available_count,
                        tags=[f'shelter:{shelter.slug}'])

    for shelter in Shelter.objects.all().annotate_with_statistics():
        Datadog().gauge('product.dogs.count', shelter.pets_all_count,
                        tags=[f'shelter:{shelter.slug}'])


@shared_task(soft_time_limit=60, autoretry_for=(Exception,), retry_backoff=True)
def randomize_pets_order():
    for i, pet in enumerate(Pet.objects.order_by('?'), start=1):
        pet.order = i
        pet.save(update_fields=('order',))

    return True


@shared_task(soft_time_limit=60, autoretry_for=(Exception,), retry_backoff=True)
def randomize_shelters_order():
    for i, shelter in enumerate(Shelter.objects.order_by('?'), start=1):
        shelter.order = i
        shelter.save(update_fields=('order',))

    return True
