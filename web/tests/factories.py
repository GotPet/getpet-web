from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from faker import Factory
import factory
from faker.providers import BaseProvider

from web.models import Country, Dog, Mentor, Pet, PetGender, PetSize, PetStatus, Region, Shelter, TeamMember

faker = Factory.create()


class DjangoGeoPointProvider(BaseProvider):

    def geo_point(self, **kwargs):
        kwargs['coords_only'] = True
        coords = factory.Faker('local_latlng', **kwargs).generate()
        return Point(x=float(coords[1]), y=float(coords[0]))


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name',)

    name = factory.Faker('user_name')


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('code',)

    name = 'Lithuania'
    code = 'lt'


class RegionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ('code',)

    name = factory.Faker('city')
    code = name
    country = factory.SubFactory(CountryFactory)


class ShelterFactory(factory.DjangoModelFactory):
    factory.Faker.add_provider(DjangoGeoPointProvider)

    class Meta:
        model = Shelter

    name = factory.Faker('company')
    is_published = True
    square_logo = factory.django.ImageField(color='green')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    address = factory.Faker('address')
    location = factory.Faker('geo_point', country_code='LT')
    region = factory.SubFactory(RegionFactory)

    @factory.post_generation
    def authenticated_users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for user in extracted:
                self.authenticated_users.add(user)


class PetFactory(factory.DjangoModelFactory):
    class Meta:
        model = Pet

    name = factory.Faker('first_name')
    photo = factory.django.ImageField(color='blue')
    shelter = factory.SubFactory(ShelterFactory)
    status = PetStatus.AVAILABLE
    short_description = factory.Faker('text', max_nb_chars=64)
    description = factory.Faker('text')
    gender = PetGender.Male
    age = factory.Faker('pyint')
    weight = factory.Faker('pyint')
    size = PetSize.Medium
    desexed = factory.Faker('boolean')


class DogFactory(PetFactory):
    class Meta:
        model = Dog

    dog_size = PetSize.Medium


class TeamMemberFactory(factory.DjangoModelFactory):
    class Meta:
        model = TeamMember

    name = factory.Faker('name')
    photo = factory.django.ImageField(color='blue')
    role = factory.Faker('sentence')

    email = factory.Faker('email')
    facebook = factory.Faker('url')
    linkedin = factory.Faker('url')
    instagram = factory.Faker('url')


class MentorFactory(factory.DjangoModelFactory):
    class Meta:
        model = Mentor

    name = factory.Faker('name')
    photo = factory.django.ImageField(color='blue')
    description = factory.Faker('sentence')

    facebook = factory.Faker('url')
    linkedin = factory.Faker('url')
    instagram = factory.Faker('url')
