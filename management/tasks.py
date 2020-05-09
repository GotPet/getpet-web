import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from web.models import Shelter

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def connect_super_users_to_shelters():
    connected = 0
    for user in get_user_model().objects.filter(is_superuser=True):
        for shelter in Shelter.objects.exclude(authenticated_users=user):
            shelter.authenticated_users.add(user)

            connected += 1

    return {
        'users_connected': connected
    }
