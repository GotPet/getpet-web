from django.test import TestCase

from web.tests.factories import CatFactory, DogFactory, GroupFactory, ShelterFactory, UserFactory


class DogsListViewTest(TestCase):

    def setUp(self):
        self.shelterGroup = GroupFactory(name='Shelter')

    def test_dogs_list_view_with_associated_shelters(self):
        user_associated_to_shelter1 = UserFactory(groups=[self.shelterGroup])

        shelter1 = ShelterFactory(authenticated_users=[user_associated_to_shelter1])
        shelter2 = ShelterFactory()

        shelter1pet1 = DogFactory(shelter=shelter1)
        shelter1pet2 = DogFactory(shelter=shelter1)
        shelter2pet1 = DogFactory(shelter=shelter2)

        self.client.force_login(user_associated_to_shelter1)

        response = self.client.get('/admin/dogs/')

        self.assertContains(response, shelter1pet1.edit_pet_url())
        self.assertContains(response, shelter1pet2.edit_pet_url())
        self.assertNotContains(response, shelter2pet1.edit_pet_url())

    def test_pets_list_view_without_associated_shelters(self):
        user_with_no_associated_shelters = UserFactory(groups=[self.shelterGroup])

        self.client.force_login(user_with_no_associated_shelters)

        response = self.client.get('/admin/dogs/')

        self.assertEqual(response.status_code, 302)


class CatsListViewTest(TestCase):

    def setUp(self):
        self.shelterGroup = GroupFactory(name='Shelter')

    def test_cats_list_view_with_associated_shelters(self):
        user_associated_to_shelter1 = UserFactory(groups=[self.shelterGroup])

        shelter1 = ShelterFactory(authenticated_users=[user_associated_to_shelter1])
        shelter2 = ShelterFactory()

        shelter1pet1 = CatFactory(shelter=shelter1)
        shelter1pet2 = CatFactory(shelter=shelter1)
        shelter2pet1 = CatFactory(shelter=shelter2)

        self.client.force_login(user_associated_to_shelter1)

        response = self.client.get('/admin/cats/')

        self.assertContains(response, shelter1pet1.edit_pet_url())
        self.assertContains(response, shelter1pet2.edit_pet_url())
        self.assertNotContains(response, shelter2pet1.edit_pet_url())

    def test_cats_list_view_without_associated_shelters(self):
        user_with_no_associated_shelters = UserFactory(groups=[self.shelterGroup])

        self.client.force_login(user_with_no_associated_shelters)

        response = self.client.get('/admin/cats/')

        self.assertEqual(response.status_code, 302)
