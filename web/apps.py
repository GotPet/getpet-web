from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebConfig(AppConfig):
    name = 'web'
    verbose_name = _("Gyvūnų prieglaudų platforma")
