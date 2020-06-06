from django.contrib.auth import get_user_model
from faker import Factory
import factory

from web.models import Country, Region, Shelter

faker = Factory.create()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('code',)

    name = factory.Faker('country')
    code = factory.Faker('country_code')


class RegionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ('code',)

    name = factory.Faker('city')
    code = name
    country = factory.SubFactory(CountryFactory)


class ShelterFactory(factory.DjangoModelFactory):
    class Meta:
        model = Shelter

    name = factory.Faker('company')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    address = factory.Faker('address')
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    region = factory.SubFactory(RegionFactory)

    @factory.post_generation
    def authenticated_users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for user in extracted:
                self.authenticated_users.add(user)
