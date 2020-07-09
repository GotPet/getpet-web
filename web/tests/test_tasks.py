from django.test import TestCase

from web.models import Pet, PetStatus, Shelter
from web.tasks import randomize_pets_order, randomize_shelters_order
from web.tests.factories import PetFactory, ShelterFactory


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


class RandomizeShelterOrderTest(TestCase):

    def setUp(self):
        self.shelter1 = ShelterFactory()
        self.shelter2 = ShelterFactory(is_published=False)

    def test_order_is_updated(self):
        randomize_shelters_order()

        order_ids = set(Shelter.objects.values_list('order', flat=True))

        self.assertSetEqual(order_ids, {1, 2})

    def test_updated_at_is_not_updated(self):
        randomize_shelters_order()

        self.assertEqual(self.shelter1.updated_at, Shelter.objects.get(pk=self.shelter1.pk).updated_at)
        self.assertEqual(self.shelter2.updated_at, Shelter.objects.get(pk=self.shelter2.pk).updated_at)
