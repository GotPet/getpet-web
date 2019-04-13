import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from getpet import settings


class Rank(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Pavadinimas"))
    order = models.IntegerField()

    class Meta:
        verbose_name = _("Rangas")
        verbose_name_plural = _("Rangai")
        ordering = ['order']

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField(verbose_name=_("Klausimo tekstas"))
    explanation = models.TextField(verbose_name=_("Klausimo paaiškinimas"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Žaidimo klausimas")
        verbose_name_plural = _("Žaidimo klausimai")

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=128, verbose_name=_("Atsakymo tekstas"))
    is_correct = models.BooleanField(default=False, verbose_name=_("Ar teisingas"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Klausimo atsakymas")
        verbose_name_plural = _("Klausimo atsakymai")

    def __str__(self):
        return self.text


class UserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="info")

    rank = models.ForeignKey(Rank, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Vartotojo informacija")
        verbose_name_plural = _("Vartotojų informacijos")

    def __str__(self):
        return str(self.user)


class GameStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name="games",
                                  verbose_name=_("Vartotojo informacija"))
    is_finished = models.BooleanField(default=False, verbose_name=_("Ar žaidimas baigtas"))

    answered = models.ManyToManyField(Answer, related_name='won_games', verbose_name=_("Pasirinkti teisingi atsakymai"))
    failed = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True, related_name="lost_games",
                               verbose_name=_("Pasirinktas neteisingas atsakymas"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sukūrimo data'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinimo data"))

    class Meta:
        verbose_name = _("Žaidimas")
        verbose_name_plural = _("Žaidimai")

    def __str__(self):
        return str(self.user_info)
