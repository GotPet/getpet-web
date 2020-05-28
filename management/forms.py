from abc import abstractmethod
from logging import getLogger
from typing import Optional, Type

from allauth.account.forms import BaseSignupForm, LoginForm as AllAuthLoginForm, \
    ResetPasswordForm as AllAuthResetPasswordForm, SignupForm as AllAuthSignupForm
from allauth.socialaccount.forms import SignupForm as AllAuthSocialSignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Layout, Submit
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.forms.utils import ErrorList
from django.forms.widgets import CheckboxSelectMultiple, ClearableFileInput, FileInput, RadioSelect, TextInput, Textarea
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from management.custom_layout_object import AppendedText, CardTitle, Formset, PlainTextFormField, PrependedText
from management.utils import find_first
from web.models import Pet, PetGender, PetProfilePhoto, PetQuerySet, PetStatus, Shelter

logger = getLogger(__name__)

_redirect_field_html = HTML("""
                  {% if redirect_field_value %}
                      <input type="hidden" name="{{ redirect_field_name }}"
                                   value="{{ redirect_field_value }}"/>
                  {% endif %}
                """)


def _remove_autofocus_and_placeholders(form: Type[BaseSignupForm]):
    for field_name in form.fields:
        form.fields[field_name].widget.attrs.pop("placeholder", None)


class WebFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label_class = 'text-uppercase text-fader fw-500 fs-11'
        self.field_template = 'management/widget/bootstrap-field.html'


class AccountFormHelper(WebFormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form_method = 'POST'
        self.form_class = "form-type-line"


class LoginForm(AllAuthLoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = AccountFormHelper()
        self.helper.form_action = 'account_login'

        self.helper.layout = Layout(
            _redirect_field_html,
            'login',
            'password',
            Field('remember', css_class='custom-control custom-checkbox'),
            Submit('submit', _("Sign In"), css_class='btn btn-bold btn-block btn-primary')
        )


class ShelterInfoUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WebFormHelper()
        self.helper.form_class = 'row'

        if self.instance and self.instance.square_logo:
            self.fields['square_logo'].widget.attrs['data-default-file'] = self.instance.square_logo.url

        self.helper.layout = Layout(
            Div(
                Div(
                    CardTitle(strong_text=_("Prieglaudos informacija")),
                    Div(
                        Div(
                            Div(
                                Div(
                                    'name',
                                    Field('is_published', css_class="custom-control custom-control-lg custom-checkbox"),
                                    'legal_name',
                                    'address',
                                    'region',
                                ), css_class='col-md-6'),
                            Div('square_logo', css_class='col-md-6'),
                            Div(PrependedText('phone', '<i class="ti-mobile"></i>'), css_class='col-md-6'),
                            Div(PrependedText('email', '<i class="ti-email"></i>'), css_class='col-md-6'),
                            Div(PrependedText('website', '<i class="fa fa-globe"></i>'), css_class='col-md-4'),
                            Div(PrependedText('facebook', '<i class="fa fa-facebook"></i>'), css_class='col-md-4'),
                            Div(PrependedText('instagram', '<i class="fa fa-instagram"></i>'), css_class='col-md-4'),

                            css_class='row'
                        ),
                        css_class='card-body'
                    ),
                    Div(
                        Submit("submit", _("Išsaugoti"), css_class="btn btn-flat btn-primary"),
                        css_class="card-footer text-right"
                    ),
                    css_class='card'
                ),
                css_class='col-12'
            ),
        )

    class Meta:
        model = Shelter
        fields = [
            'name',
            'square_logo',
            'legal_name',
            'is_published',
            'region',
            'address',
            'email',
            'phone',
            'website',
            'facebook',
            'instagram',
        ]
        widgets = {
            'square_logo': ClearableFileInput(attrs={
                'class': 'photo',
                'data-show-remove': 'false',
                'data-provide': "dropify",
            }),
        }
        help_texts = {
            'is_published': "",
        }
        labels = {
            'is_published': "Rodyti prieglaudą ir jos gyvūnus GetPet'e",
        }


class ShelterSwitchForm(forms.ModelForm):
    def __init__(self, form_action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WebFormHelper()
        self.helper.form_action = form_action

        self.helper.layout = Layout(
            Submit("switch", _("Perjungti prieglaudą"), css_class="btn btn-xs fs-10 btn-bold btn-primary"),
        )

    class Meta:
        model = Shelter

        fields = [
            'id',
        ]


class PetCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WebFormHelper()
        self.helper.form_class = 'row'

        read_only_date_divs = []
        if self.instance and self.instance.photo:
            photo_field = self.fields['photo']

            read_only_dates = {
                _('Sukūrimo data'): self.instance.created_at,
                _('Paskutinio atnaujinimo data'): self.instance.updated_at,
                _('Gyvūno paėmimo data'): self.instance.taken_at,
            }

            for label, value in read_only_dates.items():
                if value is not None:
                    div = Div(PlainTextFormField(label=label, value=value), css_class='col-md-4')
                    read_only_date_divs.append(div)

            photo_field.required = False
            photo_field.widget.attrs['data-default-file'] = self.instance.photo.url

        field_names_to_remove_none_choice = ['gender', 'size', 'desexed']
        for field_name in field_names_to_remove_none_choice:
            self.remove_none_choice(field_name)

        self.helper.layout = Layout(
            Div(
                Div(Formset('pet_photo_form_set'), css_class="d-none", css_id='pets-formset'),
                Div(
                    CardTitle(strong_text=_("Pagrindinė"), light_text=_("informacija")),
                    Div(
                        Div(
                            Div('name', css_class='col-md-6'),
                            Div('status', css_class='col-md-6'),

                            Div('short_description', css_class='col-12'),
                            Div('description', css_class='col-12'),

                            Div(AppendedText('age', 'm.'), css_class='col-md-6'),
                            Div(AppendedText('weight', 'kg'), css_class='col-md-6'),

                            Div('size', css_class='col-md-4'),
                            Div('gender', css_class='col-md-4'),
                            Div('desexed', css_class='col-md-4'),

                            *read_only_date_divs,

                            css_class='row'
                        ),
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                Div(
                    CardTitle(strong_text=_("Papildomos gyvūno nuotraukos")),
                    Div(
                        Div(css_id='dropzone', css_class='dropzone'),
                        HTML(_('Vilkite arba spauskite ir pridėkite gyvūno nuotraukas')),
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                css_class='col-lg-8'
            ),
            Div(
                Div(
                    CardTitle(
                        strong_text=_("Gyvūno profilio nuotrauka"),
                        html_after_text="""<span class="text-danger">*</span>"""
                    ),
                    Div('photo', css_class='card-body'),
                    css_class='card'
                ),
                Div(
                    CardTitle(strong_text=_("Gyvūno savybių"), light_text=_("informacija")),
                    Div(
                        Div(
                            Field('properties', css_class="custom-control custom-control-lg custom-checkbox"),
                            css_class="custom-controls-stacked"
                        ),
                        Div('special_information'),
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                Div(
                    CardTitle(strong_text=_("GetPet komandai skirta"), light_text=_("informacija")),
                    Div(
                        'information_for_getpet_team',
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                Div(
                    Div(
                        Submit(
                            'submit', _("Išsaugoti"),
                            css_class="btn btn-primary btn-bold btn-block btn-lg"
                        ),
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                css_class='col-lg-4'
            ),
        )

    def remove_none_choice(self, field_name: str):
        choices = list(self.fields[field_name].choices)

        none_choice = find_first(choices, lambda x: x[0] is None)
        if none_choice:
            choices.remove(none_choice)
        else:
            raise LookupError(f"Unable to find none choices in field {field_name}")

        self.fields[field_name].choices = choices
        self.fields[field_name].widget.choices = choices

    class Meta:
        model = Pet
        fields = [
            'name',
            'status',
            'photo',
            'short_description',
            'information_for_getpet_team',
            'description',
            'gender',
            'age',
            'size',
            'weight',
            'desexed',
            'properties',
            'special_information',
        ]
        widgets = {
            'photo': FileInput(attrs={
                'data-show-remove': 'false',
            }),
            'information_for_getpet_team': Textarea(
                attrs={'rows': 2}
            ),
            'description': Textarea(
                attrs={'rows': 6}
            ),
            'special_information': Textarea(
                attrs={'rows': 2}
            ),
            'short_description': TextInput(
                attrs={
                    'data-provide': "maxlength"
                }
            ),
            'properties': CheckboxSelectMultiple(),
            'size': RadioSelect(),
            'gender': RadioSelect(),
            'desexed': RadioSelect(),
        }
        labels = {
            'photo': "",
            'information_for_getpet_team': "",
            'properties': "",
        }


class PetProfilePhotoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WebFormHelper()
        self.helper.disable_csrf = True
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                'id',
                'order',
                'pet',
                'DELETE',
                css_class='pet-profile-photo'
            )
        )

    class Meta:
        model = PetProfilePhoto
        fields = ['id', 'pet', 'order', ]


class _BasePetProfilePhotoFormset(BaseInlineFormSet):
    def save_photos(self, pet: Pet):
        for pet_photo_form_data in self.cleaned_data:
            # None check is related to issue https://sentry.io/organizations/getpet/issues/1695417855/?project=1373034
            # Try to investigate why it happens with additional information
            pet_photo = pet_photo_form_data.get('id', None)
            if pet_photo is None:
                logger.warning(
                    "Pet photo is None",
                    exc_info=True,
                    extra={'data': self.data}
                )
                continue

            delete_photo = pet_photo_form_data['DELETE']

            if delete_photo:
                pet_photo.delete()
            elif pet_photo.pet is None:
                pet_photo.pet = pet
                pet_photo.save()


PetProfilePhotoFormSet = inlineformset_factory(Pet, PetProfilePhoto, form=PetProfilePhotoForm,
                                               formset=_BasePetProfilePhotoFormset, extra=0)


# TODO add recaptcha
class SignupForm(AllAuthSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = AccountFormHelper()
        self.helper.form_action = 'account_signup'

        self.helper.layout = Layout(
            _redirect_field_html,
            'email',
            'password1',
            'password2',
            Submit('submit', _("Sign Up"), css_class='btn btn-bold btn-block btn-primary')
        )

        _remove_autofocus_and_placeholders(self)


class SocialSignupForm(AllAuthSocialSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WebFormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-12'),
                css_class='row'
            ),
        )


class ResetPasswordForm(AllAuthResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = AccountFormHelper()
        self.helper.form_action = 'account_reset_password'

        self.helper.layout = Layout(
            _redirect_field_html,
            'email',
            Submit('submit', _("Reset My Password"), css_class='btn btn-bold btn-block btn-primary')
        )

        _remove_autofocus_and_placeholders(self)


class BaseFiltersForm(forms.Form):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)
        self.is_valid()

    @abstractmethod
    def filter_queryset(self, queryset):
        pass


class PetListFiltersForm(BaseFiltersForm):
    all_choice = [("", _("Visi"))]

    status = forms.ChoiceField(
        label=_("Gyvūno statusas"),
        choices=all_choice + [(str(k), str(v)) for k, v in PetStatus.choices],
        required=False,
        widget=RadioSelect
    )

    gender = forms.ChoiceField(
        label=_("Gyvūno lytis"),
        choices=all_choice + [(str(k), str(v)) for k, v in PetGender.choices if k is not None],
        required=False,
        widget=RadioSelect
    )

    missing_information = forms.ChoiceField(
        label=_("Trūksta informacijos"),
        choices=all_choice + [("yes", _("Taip"))],
        required=False,
        widget=RadioSelect
    )

    q = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)

        self.helper = WebFormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'aside-block'
        self.helper.layout = Layout(
            'status',
            'gender',
            'missing_information',
            'q',
            HTML("<hr>"),
            Div(
                HTML(
                    f"""<a href="{reverse("management:pets_list")}" 
                           class="button btn btn-sm btn-secondary">{_("Atstatyti")}</a>"""),
                Submit('', _("Filtruoti"), css_class='btn btn-sm btn-primary'),
                css_class='flexbox'
            )
        )

    def get_selected_status(self) -> Optional[PetStatus]:
        status_param = self.cleaned_data.get('status')

        if status_param:
            try:
                return PetStatus(int(status_param))
            except ValueError:
                return None

    def get_selected_gender(self) -> Optional[PetGender]:
        gender_param = self.cleaned_data.get('gender')

        if gender_param:
            try:
                return PetGender(int(gender_param))
            except ValueError:
                return None

    def get_search_term(self) -> Optional[str]:
        return self.cleaned_data.get('q')

    def is_missing_information(self) -> bool:
        return bool(self.cleaned_data.get('missing_information'))

    def filter_pet_status(self, queryset: PetQuerySet, status: PetStatus) -> PetQuerySet:
        return queryset.filter(status=status)

    def filter_pet_gender(self, queryset: PetQuerySet, gender: PetGender) -> PetQuerySet:
        return queryset.filter(gender=gender)

    def filter_missing_information(self, queryset: PetQuerySet) -> PetQuerySet:
        return queryset.filter(gender__isnull=True)

    def filter_by_search_term(self, queryset: PetQuerySet, search_term: str) -> PetQuerySet:
        return queryset.filter_by_search_term(search_term)

    def filter_queryset(self, queryset: PetQuerySet) -> PetQuerySet:
        if status := self.get_selected_status():
            queryset = self.filter_pet_status(queryset, status)

        if gender := self.get_selected_gender():
            queryset = self.filter_pet_gender(queryset, gender)

        if search_term := self.get_search_term():
            queryset = self.filter_by_search_term(queryset, search_term)

        if self.is_missing_information():
            queryset = self.filter_missing_information(queryset)

        return queryset
