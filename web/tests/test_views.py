from django.core.cache import cache
from django.test import TestCase

from web.models import PetStatus
from web.tests.factories import CatFactory, DogFactory, MentorFactory, ShelterFactory, TeamMemberFactory


class IndexViewTest(TestCase):

    def setUp(self):
        cache.clear()

    def test_index_status(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_pets(self):
        dog = DogFactory()
        dog_disabled = DogFactory(status=PetStatus.TAKEN_NOT_VIA_GETPET)

        response = self.client.get('/')

        self.assertContains(response, dog.name)
        self.assertContains(response, dog.short_description)

        self.assertNotContains(response, dog_disabled.name)

    def test_index_team_members(self):
        team_member = TeamMemberFactory()
        response = self.client.get('/')

        self.assertContains(response, team_member.name)
        self.assertContains(response, team_member.role)
        self.assertContains(response, team_member.email)
        self.assertContains(response, team_member.facebook)


class AllDogsListViewTest(TestCase):
    def test_all_dogs_list_view(self):
        pet1 = DogFactory()
        pet2 = DogFactory()

        response = self.client.get('/sunys/')
        self.assertContains(response, pet1.name)
        self.assertContains(response, pet2.name)


class AllCatsListViewTest(TestCase):
    def test_all_dogs_list_view(self):
        pet1 = CatFactory()
        pet2 = CatFactory()

        response = self.client.get('/kates/')
        self.assertContains(response, pet1.name)
        self.assertContains(response, pet2.name)


class DogProfileViewTest(TestCase):
    def test_dog_profile_view_does_not_exist(self):
        response = self.client.get('/sunys/1-bar/')

        self.assertEqual(response.status_code, 404)

    def test_dog_profile_view_does_disabled(self):
        pet_disabled = DogFactory(status=PetStatus.TAKEN_PERMANENTLY)

        response = self.client.get(f'/sunys/{pet_disabled.pk}-{pet_disabled.slug}/')

        self.assertEqual(response.status_code, 404)

    def test_dog_profile(self):
        shelter = ShelterFactory()
        pet1 = DogFactory(shelter=shelter)

        response = self.client.get(f'/sunys/{pet1.pk}-{pet1.slug}/')

        self.assertContains(response, shelter.name)
        self.assertContains(response, pet1.name)


class CatProfileViewTest(TestCase):
    def test_cat_profile_view_does_not_exist(self):
        response = self.client.get('/kates/1-bar/')

        self.assertEqual(response.status_code, 404)

    def test_cat_profile_view_does_disabled(self):
        pet_disabled = CatFactory(status=PetStatus.TAKEN_PERMANENTLY)

        response = self.client.get(f'/kates/{pet_disabled.pk}-{pet_disabled.slug}/')

        self.assertEqual(response.status_code, 404)

    def test_cat_profile(self):
        shelter = ShelterFactory()
        pet1 = CatFactory(shelter=shelter)

        response = self.client.get(f'/kates/{pet1.pk}-{pet1.slug}/')

        self.assertContains(response, shelter.name)
        self.assertContains(response, pet1.name)


class AllSheltersListViewTest(TestCase):
    def test_all_shelters_list_view(self):
        shelter1 = ShelterFactory()
        shelter2 = ShelterFactory()
        shelter_disabled = ShelterFactory(is_published=False)

        response = self.client.get('/globos-organizacijos/')
        self.assertContains(response, shelter1.get_absolute_url())
        self.assertContains(response, shelter2.get_absolute_url())
        self.assertNotContains(response, shelter_disabled.get_absolute_url())


class ShelterPetsListViewTest(TestCase):
    def test_shelter_pets_list_view_empty(self):
        shelter = ShelterFactory()
        response = self.client.get(f'/globos-organizacijos/{shelter.slug}/')

        self.assertEqual(response.status_code, 200)

    def test_shelter_pets_list_no_shelter(self):
        response = self.client.get('/globos-organizacijos/does-not-exist/')

        self.assertEqual(response.status_code, 404)

    def test_shelter_pets_list(self):
        shelter = ShelterFactory()
        dog = DogFactory(shelter=shelter)
        cat = CatFactory(shelter=shelter)
        dog_disabled = DogFactory(shelter=shelter, status=PetStatus.TAKEN_NOT_VIA_GETPET)
        cat_disabled = CatFactory(shelter=shelter, status=PetStatus.TAKEN_NOT_VIA_GETPET)

        response = self.client.get(f'/globos-organizacijos/{shelter.slug}/')

        self.assertContains(response, shelter.name)
        self.assertContains(response, dog.get_absolute_url())
        self.assertContains(response, cat.get_absolute_url())
        self.assertNotContains(response, dog_disabled.get_absolute_url())
        self.assertNotContains(response, cat_disabled.get_absolute_url())


class MentorListViewTest(TestCase):
    def test_mentor_list_view(self):
        mentor1 = MentorFactory()
        mentor2 = MentorFactory()

        response = self.client.get('/mentoriai/')

        self.assertContains(response, mentor1.name)
        self.assertContains(response, mentor2.name)


class SitemapTest(TestCase):
    def test_sitemap_status(self):
        shelter = ShelterFactory()
        dog = DogFactory()
        response = self.client.get('/sitemap.xml/')

        self.assertContains(response, shelter.get_absolute_url())
        self.assertContains(response, dog.get_absolute_url())
