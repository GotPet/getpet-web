from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from web.models import Pet, Shelter


class StaticSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.8

    def items(self):
        return ['web:index', 'web:all_dogs', 'web:all_shelters', ]

    def location(self, item):
        return reverse(item)


class ShelterSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.6

    def items(self):
        return Shelter.available.order_by('-pk')

    @staticmethod
    def lastmod(shelter: Shelter):
        return shelter.updated_at


class PetSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.7

    def items(self):
        return Pet.available.order_by('-pk')

    @staticmethod
    def lastmod(pet: Pet):
        return pet.updated_at
