from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _


class PetProfilePhotoInlineFormset(BaseInlineFormSet):
    def is_valid(self):
        return super().is_valid() and \
               not any([bool(e) for e in self.errors])

    def clean(self):
        # get forms that actually have valid data
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise ValidationError(_("Būtina pridėti bent vieną gyvūno profilio nuotrauką."))
