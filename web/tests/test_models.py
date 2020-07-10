from unittest.mock import MagicMock

from django.test import SimpleTestCase

from web.models import Dog, PetGender, PetSize


class TestPetDescriptionIncludingAllInformationTestCase(SimpleTestCase):

    @staticmethod
    def _create_dog(**kwargs):
        dog = Dog(**kwargs)
        dog.properties_list = MagicMock(return_value=[])

        return dog

    def test_description_no_more_information(self):
        description = "description part 1\ndescription part2"
        pet = self._create_dog(description=description)

        self.assertEqual(pet.description_including_all_information(), description)

    def test_description_all_information(self):
        pet = self._create_dog(
            description="Man reikia kantraus ir supratingo mokytojo. Mokytojo, kuris išmokytų mėgautis paglostymais, ausyčių pakasymu, ilgais pasivaikščiojimais ir žmogaus draugija. Duok man šansą atgauti pasitikėjimą žmogumi ir tapti tau ištikimu draugu!",
            age=12,
            weight=2,
            size=PetSize.Medium,
            gender=PetGender.Male,
            desexed=True,
            special_information="Amputuota galūnė ir šlapimo nelaikymas."
        )
        pet.properties_list = MagicMock(
            return_value=[
                "Nemoka atlikti tualeto reikalų lauke",
                "nemoka vaikščioti su pavadėliu"
            ])

        expected_description = """
        Man reikia kantraus ir supratingo mokytojo. Mokytojo, kuris išmokytų mėgautis paglostymais, ausyčių pakasymu, ilgais pasivaikščiojimais ir žmogaus draugija. Duok man šansą atgauti pasitikėjimą žmogumi ir tapti tau ištikimu draugu!

Lytis: patinas (kastruotas)
Amžius: apie 12 m.
Dydis: vidutinis (apie 2 kg)
Pastabos: nemoka atlikti tualeto reikalų lauke, nemoka vaikščioti su pavadėliu
Specialūs sveikatos poreikiai ir būklės:
Amputuota galūnė ir šlapimo nelaikymas.
        """.strip()
        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_age(self):
        description = "description"
        expected_description = "description\n\nAmžius: apie 12 m."

        pet = self._create_dog(description=description, age=12)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_size(self):
        description = "description"
        expected_description = "description\n\nDydis: vidutinis"

        pet = self._create_dog(description=description, size=PetSize.Medium)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_size_and_weight(self):
        description = "description"
        expected_description = "description\n\nDydis: didelis (apie 25 kg)"

        pet = self._create_dog(description=description, size=PetSize.Large, weight=25)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_properties(self):
        description = "description"
        pet_properties_list = ['Bailus', 'Labai aktyvus']
        expected_description = "description\n\nPastabos: bailus, labai aktyvus"

        pet = self._create_dog(description=description)
        pet.properties_list = MagicMock(return_value=pet_properties_list)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_special_information(self):
        description = "description"
        expected_description = "description\n\nSpecialūs sveikatos poreikiai ir būklės:\nAmputuota galūnė"

        pet = self._create_dog(description=description, special_information="Amputuota galūnė")

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_gender_male(self):
        description = "description"
        expected_description = "description\n\nLytis: patinas"

        pet = self._create_dog(description=description, gender=PetGender.Male)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_gender_female(self):
        description = "description"
        expected_description = "description\n\nLytis: patelė"

        pet = self._create_dog(description=description, gender=PetGender.Female)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_gender_male_desexed(self):
        description = "description"
        expected_description = "description\n\nLytis: patinas (kastruotas)"

        pet = self._create_dog(description=description, gender=PetGender.Male, desexed=True)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_gender_female_desexed(self):
        description = "description"
        expected_description = "description\n\nLytis: patelė (sterilizuota)"

        pet = self._create_dog(description=description, gender=PetGender.Female, desexed=True)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_gender_male_not_desexed(self):
        description = "description"
        expected_description = "description\n\nLytis: patinas (nekastruotas)"

        pet = self._create_dog(description=description, gender=PetGender.Male, desexed=False)

        self.assertEqual(pet.description_including_all_information(), expected_description)

    def test_description_gender_female_not_desexed(self):
        description = "description"
        expected_description = "description\n\nLytis: patelė (nesterilizuota)"

        pet = self._create_dog(description=description, gender=PetGender.Female, desexed=False)

        self.assertEqual(pet.description_including_all_information(), expected_description)


