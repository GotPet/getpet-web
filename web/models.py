from __future__ import annotations

import json
import uuid
from _md5 import md5
from datetime import timedelta
from enum import Enum
from os.path import join
from typing import List, Optional

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.contrib.gis.db.models import PointField
from django.db import models
from django.db.models import Count, QuerySet
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from getpet import settings
from management.constants import Constants
from utils.models import SitemapImageEntry
from utils.utils import django_now, file_extension, full_path, try_parse_int

_SHELTER_GROUP_NAME = "Shelter"


class UserQuerySet(models.QuerySet):
    def annotate_with_app_statistics(self) -> QuerySet[User]:
        pets_likes_count = User.objects.annotate(
            pets_likes_count=models.Count(
                'users_pet_choices',
                filter=models.Q(users_pet_choices__is_favorite=True)
            )
        ).filter(pk=models.OuterRef('pk'))

        pets_dislikes_count = User.objects.annotate(
            pets_dislikes_count=models.Count(
                'users_pet_choices',
                filter=models.Q(users_pet_choices__is_favorite=False)
            )
        ).filter(pk=models.OuterRef('pk'))

        pets_getpet_requests_count = User.objects.annotate(
            pets_getpet_requests_count=models.Count(
                'get_pet_requests',
            )
        ).filter(pk=models.OuterRef('pk'))

        return self.annotate(
            pets_likes_count=models.Subquery(
                pets_likes_count.values('pets_likes_count'),
                output_field=models.DateTimeField()
            ),
            pets_dislikes_count=models.Subquery(
                pets_dislikes_count.values('pets_dislikes_count'),
                output_field=models.IntegerField()
            ),
            pets_getpet_requests_count=models.Subquery(
                pets_getpet_requests_count.values('pets_getpet_requests_count'),
                output_field=models.IntegerField()
            ),
        )

    def annotate_with_shelters_count(self) -> QuerySet[User]:
        shelters_count = User.objects.annotate(
            shelters_count=models.Count(
                'shelters',
            )
        ).filter(pk=models.OuterRef('pk'))

        return self.annotate(
            shelters_count=models.Subquery(
                shelters_count.values('shelters_count'),
                output_field=models.IntegerField()
            ),
        )


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    use_in_migrations = False


class User(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to='img/users/', verbose_name=_("Vartotojo nuotrauka"))
    social_image_url = models.URLField(blank=True, null=True)

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)

    def user_image_url(self):
        if self.social_image_url:
            return self.social_image_url

        return self.gravatar_url()

    def gravatar_url(self):
        g_hash = md5(str(self.email).encode('utf-8').lower()).hexdigest()
        return f"https://www.gravatar.com/avatar/{g_hash}?s=128&d=identicon"

    def extract_name(self):
        return self.get_full_name().split(' ')[0]

    def __str__(self):
        return self.get_full_name() or self.email or self.username


class CountryQuerySet(models.QuerySet):
    def annotate_with_pets_count(self):
        return self.annotate(total_pets=Count(
            'regions__shelters__pets',
        ))


class Country(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Šalies pavadinimas"))
    code = models.CharField(verbose_name=_("Šalies kodas"), max_length=2, unique=True,
                            help_text=_("Šalies kodas pagal ISO 3166 alpha 2 standartą pvz: lt, lv"))

    objects = CountryQuerySet.as_manager()

    class Meta:
        verbose_name = _("Šalis")
        verbose_name_plural = _("Šalys")
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = self.code.lower()

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Regiono pavadinimas"))
    full_name = models.CharField(max_length=100, verbose_name=_("Pilnas regiono pavadinimas"),
                                 help_text=_("Pavyzdžiui: Vilniaus regionas"))
    code = models.CharField(verbose_name=_("Regiono kodas"), max_length=32, unique=True,
                            help_text=_("Unikalus regiono kodas pvz: ankara"))
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="regions", verbose_name=_("Šalis"))

    class Meta:
        verbose_name = _("Regionas")
        verbose_name_plural = _("Regionai")
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = self.code.lower()

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class ShelterQuerySet(models.QuerySet):
    # https://stackoverflow.com/questions/56567841/django-count-and-sum-annotations-interfere-with-each-other
    def annotate_with_statistics(self) -> QuerySet[Shelter]:
        pets_updated_at_max = Shelter.objects.annotate(
            pets_updated_at_max=models.Max('pets__updated_at')
        ).filter(pk=models.OuterRef('pk'))

        pets_all_count = Shelter.objects.annotate(
            pets_all_count=models.Count('pets')
        ).filter(pk=models.OuterRef('pk'))

        pets_available_count = Shelter.objects.annotate(
            pets_available_count=models.Count('pets', filter=models.Q(pets__status=PetStatus.AVAILABLE))
        ).filter(pk=models.OuterRef('pk'))

        pets_likes_count = Shelter.objects.annotate(
            pets_likes_count=models.Count(
                'pets__users_pet_choices',
                filter=models.Q(pets__users_pet_choices__is_favorite=True)
            )
        ).filter(pk=models.OuterRef('pk'))

        pets_dislikes_count = Shelter.objects.annotate(
            pets_dislikes_count=models.Count(
                'pets__users_pet_choices',
                filter=models.Q(pets__users_pet_choices__is_favorite=False)
            )
        ).filter(pk=models.OuterRef('pk'))

        return self.annotate(
            pets_updated_at_max=models.Subquery(
                pets_updated_at_max.values('pets_updated_at_max'),
                output_field=models.DateTimeField()
            ),
            pets_all_count=models.Subquery(
                pets_all_count.values('pets_all_count'),
                output_field=models.IntegerField()
            ),
            pets_available_count=models.Subquery(
                pets_available_count.values('pets_available_count'),
                output_field=models.IntegerField()
            ),
            pets_likes_count=models.Subquery(
                pets_likes_count.values('pets_likes_count'),
                output_field=models.IntegerField()
            ),
            pets_dislikes_count=models.Subquery(
                pets_dislikes_count.values('pets_dislikes_count'),
                output_field=models.IntegerField()
            ),
        )


class SheltersManager(models.Manager):
    def get_queryset(self) -> ShelterQuerySet:
        return ShelterQuerySet(self.model, using=self._db).filter(is_published=True)


class Shelter(models.Model):
    def _shelter_square_logo_file(self, filename: str) -> str:
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-square-logo.{ext}"
        return join('img', 'web', 'shelter', slug, filename)

    name = models.CharField(max_length=50, verbose_name=_("Prieglaudos pavadinimas"))
    slug = models.SlugField(unique=True, editable=False)
    order = models.IntegerField(default=0, editable=False)

    legal_name = models.CharField(max_length=256, null=True, verbose_name=_("Įstaigos pavadinimas"))

    is_published = models.BooleanField(default=False, db_index=True, verbose_name=_("Paskelbta"),
                                       help_text=_("Pažymėjus prieglauda matoma viešai"))

    square_logo = models.ImageField(upload_to=_shelter_square_logo_file, verbose_name=_("Kvadratinis logotipas"))

    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="shelters", verbose_name=_("Regionas"))

    address = models.CharField(max_length=256, verbose_name=_("Prieglaudos adresas"))
    location = PointField(verbose_name=_("Vieta"))

    email = models.EmailField(verbose_name=_("Elektroninis paštas"))
    phone = models.CharField(max_length=24, verbose_name=_("Telefono numeris"))

    website = models.URLField(blank=True, null=True, verbose_name=_("Interneto svetainė"))
    facebook = models.URLField(blank=True, null=True, verbose_name=_("Facebook"))
    instagram = models.URLField(blank=True, null=True, verbose_name=_("Instagram"))

    authenticated_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to=models.Q(groups__name=_SHELTER_GROUP_NAME, is_staff=True, _connector=models.Q.OR),
        verbose_name=_("Vartotojai tvarkantys prieglaudos informaciją"),
        help_text=_("Priskirti vartotojai gali matyti prieglaudos gyvūnus ir juos tvarkyti.")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    objects = ShelterQuerySet.as_manager()
    available = SheltersManager()

    class Meta:
        verbose_name = _("Gyvūnų prieglauda")
        verbose_name_plural = _("Gyvūnų prieglaudos")
        default_related_name = "shelters"
        ordering = ("order", "id")
        index_together = [
            ("order", "id"),
        ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    @staticmethod
    def user_associated_shelters(user: AbstractBaseUser) -> QuerySet[Shelter]:
        if user.is_authenticated:
            return Shelter.objects.filter(authenticated_users=user)

        return Shelter.objects.none()

    @staticmethod
    def user_associated_shelter_by_id(user: AbstractBaseUser, shelter_id: int) -> Optional[Shelter]:
        return Shelter.user_associated_shelters(user).filter(id=shelter_id).first()

    @staticmethod
    def user_associated_shelter(request: HttpRequest) -> Optional[Shelter]:
        shelters = Shelter.user_associated_shelters(request.user)

        if cookie_shelter_id := try_parse_int(request.COOKIES.get(Constants.SELECTED_SHELTER_COOKIE_ID, None)):
            shelter_from_cookie = shelters.filter(id=cookie_shelter_id).first()

            if shelter_from_cookie:
                return shelter_from_cookie

        return shelters.first()

    def get_absolute_url(self) -> str:
        return reverse('web:shelter_profile', kwargs={'slug': self.slug})

    def edit_shelter_url(self) -> str:
        return reverse('management:shelters_update', kwargs={'pk': self.pk})

    def shelter_switch_form(self):
        from management.forms import ShelterSwitchForm
        form_action = reverse('management:shelters_switch', kwargs={'pk': self.pk})

        return ShelterSwitchForm(form_action=form_action)

    def switch_shelter_cookie(self, response: HttpResponse):
        expires = django_now() + timedelta(seconds=Constants.SELECTED_SHELTER_COOKIE_MAX_AGE)

        # noinspection PyTypeChecker
        response.set_cookie(
            Constants.SELECTED_SHELTER_COOKIE_ID,
            str(self.id),
            expires=expires.utctimetuple()
        )

    def json_ld(self) -> str:
        social_networks = [s for s in [self.facebook, self.instagram] if s]
        json_ld_object = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.name,
            "url": self.website if self.website else full_path(self.get_absolute_url()),
            "legalName": self.legal_name,
            "logo": full_path(self.square_logo.url),
            "email": self.email,
            "telephone": self.phone,
            "address": self.address,
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": self.phone,
                "email": self.email
            },
            "sameAs": social_networks
        }

        return json.dumps(json_ld_object, allow_nan=False)

    def __str__(self) -> str:
        return self.name


class PetType(Enum):
    DOG = "DOG"
    CAT = "CAT"


class PetStatus(models.IntegerChoices):
    AVAILABLE = 1, _('Laukia šeimininko')
    TAKEN_TEMPORARY = 2, _('Laikinai paimtas per GetPet')
    TAKEN_PERMANENTLY = 3, _('Paimtas visam laikui per GetPet')
    TAKEN_NOT_VIA_GETPET = 4, _('Paimtas ne per GetPet')
    TEMPORARY_NOT_LOOKING_FOR_HOME = 5, _('Laikinai neieško namų')


class PetGender(models.IntegerChoices):
    Male = 1, _('Patinas')
    Female = 2, _('Patelė')

    __empty__ = _('Nepatikslinta')


class PetSize(models.IntegerChoices):
    Small = 1, _('Mažas')
    Medium = 2, _('Vidutinis')
    Large = 3, _('Didelis')

    __empty__ = _('Nepatikslinta')


class PetQuerySet(models.QuerySet):
    def select_related_full_shelter(self) -> PetQuerySet:
        return self.select_related('shelter', 'shelter__region', 'shelter__region__country')

    def prefetch_related_photos_and_properties(self) -> PetQuerySet:
        return self.prefetch_related('profile_photos', 'properties')

    # Bug https://sentry.io/organizations/getpet/issues/1712664617/?project=1373034&query=is%3Aunresolved
    def available_or_owned_by_user(self, user: AbstractUser) -> PetQuerySet:
        available_filter = models.Q(status=PetStatus.AVAILABLE, shelter__is_published=True)

        if user.is_authenticated:
            return self.filter(available_filter | models.Q(shelter__authenticated_users=user))

        return self.filter(available_filter)

    def annotate_with_getpet_requests_count(self):
        getpet_requests_count = Pet.objects.annotate(
            getpet_requests_count=models.Count(
                'get_pet_requests',
            )
        ).filter(pk=models.OuterRef('pk'))

        return self.annotate(
            getpet_requests_count=models.Subquery(
                getpet_requests_count.values('getpet_requests_count'),
                output_field=models.IntegerField()
            )
        )

    def annotate_with_likes_and_dislikes(self):
        likes_count = Pet.objects.annotate(
            likes_count=models.Count(
                'users_pet_choices',
                filter=models.Q(users_pet_choices__is_favorite=True)
            )
        ).filter(pk=models.OuterRef('pk'))

        dislikes_count = Pet.objects.annotate(
            dislikes_count=models.Count(
                'users_pet_choices',
                filter=models.Q(users_pet_choices__is_favorite=False)
            )
        ).filter(pk=models.OuterRef('pk'))

        return self.annotate(
            likes_count=models.Subquery(
                likes_count.values('likes_count'),
                output_field=models.IntegerField()
            ),
            dislikes_count=models.Subquery(
                dislikes_count.values('dislikes_count'),
                output_field=models.IntegerField()
            ),
        )

    def filter_by_search_term(self, search_term: str):
        return self.filter(name__icontains=search_term)


class AvailablePetsManager(models.Manager):
    def get_queryset(self):
        return PetQuerySet(self.model, using=self._db).filter(status=PetStatus.AVAILABLE, shelter__is_published=True)


class Pet(models.Model):
    def _pet_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'web', 'pet', slug, filename)

    name = models.CharField(max_length=50, verbose_name=_("Gyvūno vardas"))
    slug = models.SlugField(editable=False)
    order = models.IntegerField(default=0, editable=False)

    status = models.SmallIntegerField(
        choices=PetStatus.choices,
        default=PetStatus.AVAILABLE,
        db_index=True,
        verbose_name=_("Gyvūno statusas"),
        help_text=_("Gyvūnai su statusu laukiantys šeimininko yra rodomi programėlėje.")
    )
    photo = models.ImageField(upload_to=_pet_photo_file, verbose_name=_("Vertikali gyvūno profilio nuotrauka"),
                              help_text=_("Rekomenduojamas profilio nuotraukos kraštinių santykis 3:4"))

    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='pets', verbose_name=_("Prieglauda"),
                                help_text=_("Prieglauda, kurioje šiuo metu randasi gyvūnas"))

    short_description = models.CharField(max_length=64, verbose_name=_("Trumpas aprašymas"), help_text=_(
        "Trumpas aprašymas apie gyvūną rodomas programėlės pagrindiniame ekrane skirtas pritraukti varototojus"
        " paspausti ant gyvūno profilio."))
    description = models.TextField(verbose_name=_("Aprašymas"),
                                   help_text=_("Gyvūno aprašymas matomas įėjus į gyvūno profilį."))

    information_for_getpet_team = models.TextField(
        null=True, blank=True,
        verbose_name=_("Informacija skirta GetPet komandai"),
        help_text=_("Įrašykite informaciją skirtą GetPet komandai pvz: žmogaus kontaktinę informaciją "
                    "dėl GetPet mentoriaus priskyrimo.")
    )

    special_information = models.TextField(
        verbose_name=_("Specialūs sveikatos poreikiai ir būklės"),
        blank=True,
        null=True,
        help_text=_(
            "Pavyzdžiui: amputuota galūnė, šlapimo nelaikymas, reikalingi medikamentai ir kita.")
    )

    gender = models.SmallIntegerField(
        verbose_name=_("Lytis"),
        choices=PetGender.choices,
    )
    age = models.PositiveSmallIntegerField(
        verbose_name=_("Amžius"),
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name=_("Svoris"),
        null=True,
        blank=True,
    )
    desexed = models.BooleanField(
        verbose_name=_("Kastruotas / sterilizuotas"),
        choices=(
            (None, _("Nepatikslinta")),
            (True, _("Taip")),
            (False, _("Ne")),
        ),
    )

    taken_at = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_('Paėmimo data'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_("Atnaujinimo data"))

    objects = PetQuerySet.as_manager()
    available = AvailablePetsManager()

    class Meta:
        verbose_name = _("Gyvūnas")
        verbose_name_plural = _("Gyvūnai")
        ordering = ("order", "id")
        index_together = [
            ("order", "id"),
        ]

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        orig: Optional[Pet] = None
        if self.pk is not None:
            orig = Pet.objects.get(pk=self.pk)

            if orig.status != self.status:
                if orig.status == PetStatus.AVAILABLE:
                    self.taken_at = django_now()
                elif self.status == PetStatus.AVAILABLE:
                    self.taken_at = None

        self.slug = slugify(self.name)
        self.short_description = self.short_description.rstrip('.')

        super().save(force_insert, force_update, using, update_fields)

        from web.tasks import on_pet_created_or_updated

        orig_status = orig.status if orig else None
        orig_status_text = orig.get_status_display() if orig else None

        on_pet_created_or_updated.delay(self.pk, orig_status, orig_status_text)

    def get_absolute_url(self) -> str:
        if hasattr(self, 'dog'):
            return self.dog.get_absolute_url()
        if hasattr(self, 'cat'):
            return self.cat.get_absolute_url()

        raise ValueError(f"Pet {self.pk} is not associated with cat or dog")

    def is_male(self) -> bool:
        return self.gender == PetGender.Male

    def desexed_status_text(self) -> Optional[str]:
        if self.gender == PetGender.Male and self.desexed is True:
            return _("kastruotas")
        elif self.gender == PetGender.Male and self.desexed is False:
            return _("nekastruotas")
        elif self.gender == PetGender.Female and self.desexed is True:
            return _("sterilizuota")
        elif self.gender == PetGender.Female and self.desexed is False:
            return _("nesterilizuota")

        return None

    def properties_list(self) -> List[str]:
        if hasattr(self, 'properties'):
            return [p.name for p in self.properties.all()]

        return []

    def description_including_all_information(self) -> str:
        return ""

    def all_photos(self) -> List[ImageFieldFile]:
        photos = [self.photo]

        for photo in self.profile_photos.all():
            photos.append(photo.photo)

        return photos

    def is_available(self) -> bool:
        return self.status == PetStatus.AVAILABLE and self.shelter.is_published

    def pet_status_badge_color_class(self) -> str:
        if self.status == PetStatus.AVAILABLE:
            return "badge-success"

        return "badge-primary"


class Dog(Pet):
    properties = models.ManyToManyField("web.DogProperty", blank=True, related_name="+",
                                        verbose_name=_("Šuns savybės"))
    size = models.SmallIntegerField(
        verbose_name=_("Dydis"),
        choices=PetSize.choices,
    )

    pet_type = PetType.DOG

    objects = PetQuerySet.as_manager()
    available = AvailablePetsManager()

    class Meta:
        verbose_name = _("Šuo")
        verbose_name_plural = _("Šunys")

    @staticmethod
    def all_dogs_from_shelter(shelter: Shelter) -> QuerySet[Dog]:
        queryset = Dog.objects.filter(shelter=shelter)
        return queryset

    def similar_dogs_from_same_shelter(self):
        return Dog.available.filter(shelter=self.shelter).exclude(pk=self.pk).order_by('?')[:3]

    def sitemap_image_entries(self) -> List[SitemapImageEntry]:
        images = [
            SitemapImageEntry(
                relative_url=self.photo.url,
                title=f"{_('Šuns')} {self.name} {_('profilio nuotrauka')}",
                caption=f"{_('Šuo')} {self.name} {_('iš')} {self.shelter.name} {_('pagrindinė profilio nuotrauka')}",
            )
        ]

        for i, photo in enumerate(self.profile_photos.all(), start=1):
            images.append(
                SitemapImageEntry(
                    relative_url=photo.photo.url,
                    title=f"{_('Šuns')} {self.name} {i} {_('nuotrauka')}",
                    caption=f"{_('Šuo')} {self.name} {_('iš')} {self.shelter.name} {_('nuotrauka')} {photo.order}",
                )
            )

        return images

    def get_absolute_url(self) -> str:
        return reverse('web:dog_profile', kwargs={'pk': self.pk, 'slug': self.slug})

    def edit_pet_url(self) -> str:
        return reverse('management:dogs_update', kwargs={'pk': self.pk})

    def description_including_all_information(self) -> str:
        description_parts = [self.description + "\n"]

        if self.gender:
            gender_part = f"{_('Lytis')}: {self.get_gender_display().lower()}"

            if desexed_text := self.desexed_status_text():
                gender_part += f" ({desexed_text})"

            description_parts.append(gender_part)

        if self.age:
            age_part = f"{_('Amžius')}: {_('apie')} {self.age} m."
            description_parts.append(age_part)

        if self.size:
            size_part = f"{_('Dydis')}: {self.get_size_display().lower()}"
            if self.weight:
                size_part += f" ({_('apie')} {self.weight} kg)"

            description_parts.append(size_part)

        properties = self.properties_list()
        if len(properties) > 0:
            properties_part = f"{_('Pastabos')}: {', '.join(properties).lower()}"
            description_parts.append(properties_part)

        if special_information := self.special_information:
            special_information_part = f"{_('Specialūs sveikatos poreikiai ir būklės')}:\n{special_information}"
            description_parts.append(special_information_part)

        return '\n'.join(description_parts).strip(' \n\t')

    @staticmethod
    def generate_pets(liked_pet_ids: List[int], disliked_pet_ids: List[int], region: Optional[str],
                      pet_type: PetType):
        queryset = (Cat if pet_type == PetType.CAT else Dog)
        queryset = queryset.available.prefetch_related('profile_photos', 'properties') \
            .select_related_full_shelter() \
            .exclude(pk__in=liked_pet_ids).order_by()

        if region:
            queryset = queryset.filter(shelter__region=region)

        new_pets = queryset.exclude(pk__in=disliked_pet_ids).order_by('?')

        return new_pets


class DogProperty(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name=_("Šuns savybė"))
    dogs = models.ManyToManyField(
        Dog,
        verbose_name=_("Gyvūnai"),
        through=Dog.properties.through,
        related_name="+",
        blank=True,
    )

    class Meta:
        verbose_name = _("Šuns savybė")
        verbose_name_plural = _("Šuns savybės")
        default_related_name = "+"
        ordering = ['name']

    def __str__(self):
        return self.name


class Cat(Pet):
    properties = models.ManyToManyField("web.CatProperty", blank=True, related_name="+",
                                        verbose_name=_("Savybės"))

    pet_type = PetType.CAT

    objects = PetQuerySet.as_manager()
    available = AvailablePetsManager()

    class Meta:
        verbose_name = _("Katė")
        verbose_name_plural = _("Katės")

    @staticmethod
    def all_cats_from_shelter(shelter: Shelter) -> QuerySet[Cat]:
        queryset = Cat.objects.filter(shelter=shelter)
        return queryset

    def similar_cats_from_same_shelter(self):
        return Cat.available.filter(shelter=self.shelter).exclude(pk=self.pk).order_by('?')[:3]

    def sitemap_image_entries(self) -> List[SitemapImageEntry]:
        images = [
            SitemapImageEntry(
                relative_url=self.photo.url,
                title=f"{_('Katės')} {self.name} {_('profilio nuotrauka')}",
                caption=f"{_('Katė')} {self.name} {_('iš')} {self.shelter.name} {_('pagrindinė profilio nuotrauka')}",
            )
        ]

        for i, photo in enumerate(self.profile_photos.all(), start=1):
            images.append(
                SitemapImageEntry(
                    relative_url=photo.photo.url,
                    title=f"{_('Katės')} {self.name} {i} {_('nuotrauka')}",
                    caption=f"{_('Katė')} {self.name} {_('iš')} {self.shelter.name} {_('nuotrauka')} {photo.order}",
                )
            )

        return images

    def description_including_all_information(self) -> str:
        description_parts = [self.description + "\n"]

        gender_part = f"{_('Lytis')}: {self.get_gender_display().lower()}"
        gender_part += f" ({self.desexed_status_text()})"

        description_parts.append(gender_part)

        if self.age:
            age_part = f"{_('Amžius')}: {_('apie')} {self.age} m."
            description_parts.append(age_part)

        if self.weight:
            size_part = f"Svoris: apie {self.weight} kg"

            description_parts.append(size_part)

        properties = self.properties_list()
        if len(properties) > 0:
            properties_part = f"{_('Pastabos')}: {', '.join(properties).lower()}"
            description_parts.append(properties_part)

        if special_information := self.special_information:
            special_information_part = f"{_('Specialūs sveikatos poreikiai ir būklės')}:\n{special_information}"
            description_parts.append(special_information_part)

        return '\n'.join(description_parts).strip(' \n\t')

    def get_absolute_url(self) -> str:
        return reverse('web:cat_profile', kwargs={'pk': self.pk, 'slug': self.slug})

    def edit_pet_url(self) -> str:
        return reverse('management:cats_update', kwargs={'pk': self.pk})


class CatProperty(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name=_("Katės savybė"))
    cats = models.ManyToManyField(
        Cat,
        verbose_name=_("Katės"),
        through=Cat.properties.through,
        related_name="+",
        blank=True,
    )

    class Meta:
        verbose_name = _("Katės savybė")
        verbose_name_plural = _("Kačių savybės")
        default_related_name = "+"
        ordering = ['name']

    def __str__(self):
        return self.name


class PetProfilePhoto(models.Model):
    def _pet_photo_file(self, filename):
        ext = file_extension(filename)

        if self.pet:
            slug = slugify(self.pet.name)

            filename = f"{slug}-photo-{self.order}.{ext}"
            return join('img', 'web', 'pet', slug, 'profile', filename)
        else:
            filename = f"{uuid.uuid4()}-photo.{ext}"
            return join('img', 'web', 'pet', 'all', 'profile', filename)

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, null=True, blank=True, related_name='profile_photos')
    photo = models.ImageField(upload_to=_pet_photo_file, verbose_name=_('Gyvūno profilio nuotrauka'))
    order = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_("Vartotojas")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Gyvūno profilio nuotrauka")
        verbose_name_plural = _("Gyvūnų profilio nuotraukos")
        ordering = ['order']

    def __str__(self):
        return self.photo.url


class GetPetRequestStatus(models.IntegerChoices):
    USER_WANTS_PET = 1, _('Noras paimti gyvūną')
    PET_TAKEN_TEMPORARY = 2, _('Gyvūnas laikinai pasiimtas')
    PET_RETURNED = 3, _("Gyvūnas gražintas po laikinos globos")
    PET_TAKEN_PERMANENTLY = 4, _("Gyvūnas pasiimtas visam laikui")


class GetPetRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Vartotojas"))
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name=_("Gyvūnas"))
    status = models.IntegerField(
        choices=GetPetRequestStatus.choices,
        default=GetPetRequestStatus.USER_WANTS_PET,
        verbose_name=_("Gyvūno statusas"),
        help_text=_("Pasirenkamas vienas iš gyvūno statusų pas potencialų šeimininką")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Noras priglausti gyvūną")
        verbose_name_plural = _("Norai priglausti gyvūnus")
        unique_together = ('user', 'pet')
        default_related_name = "get_pet_requests"


class UserPetChoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Vartotojas"))
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name=_("Gyvūnas"))
    is_favorite = models.BooleanField(verbose_name=_("Vartotojas pamėgo gyvūną"), db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Vartotojo gyvūno pasirinkimaas")
        verbose_name_plural = _("Vartotojų gyvūnų pasirinkimai")
        unique_together = ('user', 'pet')
        default_related_name = "users_pet_choices"
        ordering = ['-id']


class Mentor(models.Model):
    def _mentor_photo_file(self, filename):
        ext = file_extension(filename)

        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'web', 'menthor', filename)

    name = models.CharField(max_length=128, verbose_name=_("Vardas"))
    photo = models.ImageField(upload_to=_mentor_photo_file, verbose_name=_('Nuotrauka'))
    description = models.TextField(verbose_name=_("Aprašymas"))

    facebook = models.URLField(verbose_name=_("Facebook"), null=True, blank=True)
    instagram = models.URLField(verbose_name=_("Instagram"), null=True, blank=True)
    linkedin = models.URLField(verbose_name=_("LinkedIn"), null=True, blank=True)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Mentorius")
        verbose_name_plural = _("Mentoriai")
        ordering = ['order']

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    def _team_member_photo_file(self, filename):
        ext = file_extension(filename)

        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'web', 'team', filename)

    name = models.CharField(max_length=128, verbose_name=_("Vardas"))
    photo = models.ImageField(upload_to=_team_member_photo_file, verbose_name=_('Nuotrauka'))

    role = models.CharField(max_length=128, verbose_name=_("Rolė"))

    email = models.EmailField(verbose_name=_("El. paštas"))
    facebook = models.URLField(verbose_name=_("Facebook"))
    instagram = models.URLField(verbose_name=_("Instagram"), null=True, blank=True)
    linkedin = models.URLField(verbose_name=_("LinkedIn"), null=True, blank=True)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Komandos narys")
        verbose_name_plural = _("Komandos nariai")
        ordering = ['order']

    def __str__(self):
        return self.name
