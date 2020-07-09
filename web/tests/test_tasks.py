from django.test import TestCase

from web.models import Pet, PetStatus
from web.tasks import randomize_pets_order
from web.tests.factories import PetFactory


class RandomizePetOrderTest(TestCase):

    def setUp(self):
        self.pet1: Pet = PetFactory()
        self.pet2: Pet = PetFactory(status=PetStatus.TAKEN_NOT_VIA_GETPET)
        self.pet3: Pet = PetFactory()

    def test_order_is_updated(self):
        randomize_pets_order()

        order_ids = set(Pet.objects.values_list('order', flat=True))

        self.assertSetEqual(order_ids, {1, 2, 3})

    def test_updated_at_is_not_updated(self):
        randomize_pets_order()

        self.assertEqual(self.pet1.updated_at, Pet.objects.get(pk=self.pet1.pk).updated_at)
        self.assertEqual(self.pet2.updated_at, Pet.objects.get(pk=self.pet2.pk).updated_at)
        self.assertEqual(self.pet3.updated_at, Pet.objects.get(pk=self.pet3.pk).updated_at)
