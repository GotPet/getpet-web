import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def test_task():
    return "Hello celery"
