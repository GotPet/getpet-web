import csv
import sys

from django.core.management import BaseCommand

from web.models import UserPetChoice


class Command(BaseCommand):
    def handle(self, *args, **options):
        choices = UserPetChoice.objects.filter(pet__dog__isnull=False).select_related('user', 'pet')

        writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
        writer.writerow(
            ["pet_id", "pet_created_at", "user_id", "user_joined_date", "is_pet_favorited", "user_choice_created_at",
             "user_choice_updated_at"])

        for choice in choices:
            writer.writerow(
                [choice.pet.id,
                 choice.pet.created_at.isoformat(),
                 choice.user.id,
                 choice.user.date_joined,
                 1 if choice.is_favorite else 0,
                 choice.created_at.isoformat(),
                 choice.updated_at.isoformat()]
            )
