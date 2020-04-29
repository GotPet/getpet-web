from abc import abstractmethod
from typing import Optional, Type

from allauth.account.forms import BaseSignupForm, LoginForm as AllAuthLoginForm, \
    ResetPasswordForm as AllAuthResetPasswordForm, SignupForm as AllAuthSignupForm
from allauth.socialaccount.forms import SignupForm as AllAuthSocialSignupForm
from crispy_forms.bootstrap import AppendedText as BaseAppendedText, PrependedText as BasePrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Layout, Submit
from django import forms
from django.forms import inlineformset_factory
from django.forms.utils import ErrorList
from django.forms.widgets import ClearableFileInput, RadioSelect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from web.models import Pet, PetGender, PetProfilePhoto, PetQuerySet, PetStatus

_redirect_field_html = HTML("""
                  {% if redirect_field_value %}
                      <input type="hidden" name="{{ redirect_field_name }}"
                                   value="{{ redirect_field_value }}"/>
                  {% endif %}
                """)


def _remove_autofocus_and_placeholders(form: Type[BaseSignupForm]):
    for field_name in form.fields:
        form.fields[field_name].widget.attrs.pop("placeholder", None)


class PrependedText(BasePrependedText):
    def __init__(self, field, text, *args, **kwargs):
        kwargs['template'] = 'management/widget/prepended_appended_text.html'
        super().__init__(field, text, *args, **kwargs)


class AppendedText(BaseAppendedText):
    def __init__(self, field, text, *args, **kwargs):
        kwargs['template'] = 'management/widget/prepended_appended_text.html'
        super().__init__(field, text, *args, **kwargs)


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


class ShelterPetUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WebFormHelper()
        self.helper.disable_csrf = True
        self.helper.form_tag = False

        if self.instance and self.instance.photo:
            self.fields['photo'].widget.attrs['data-default-file'] = self.instance.photo.url

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML(f"""
                    <h4 class="card-title">
                        <strong>{_("Pagrindinė")}</strong> {_("informacija")}
                    </h4>
                    """),
                    Div(
                        Div(
                            Div('name', css_class='col-md-6'),
                            Div('status', css_class='col-md-6'),

                            Div('short_description', css_class='col-12'),
                            Div('description', css_class='col-12'),
                            css_class='row'
                        ),
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                css_class='col-lg-8'
            ),
            Div(
                Div(
                    HTML(f"""
                    <h4 class="card-title">
                        <strong>{_("Profilio")}</strong> {_("nuotrauka")}
                    </h4>
                    """),
                    Div(
                        Div(
                            Div('photo', css_class='col-12'),
                            css_class='row'
                        ),
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                css_class='col-lg-4'
            ),
            Div(
                Div(
                    HTML(f"""
            <h4 class="card-title">
                <strong>{_("Savybių")}</strong> {_("informacija")}
            </h4>
            """),
                    Div(
                        Div(
                            Div('gender', css_class='col-md-6'),
                            Div('desexed', css_class='col-md-6'),

                            Div('size', css_class='col-md-4'),
                            Div('age', css_class='col-md-4'),
                            Div(AppendedText('weight', 'kg'), css_class='col-md-4'),

                            Div('is_vaccinated', css_class='col-md-6'),
                            Div('is_special_care_needed', css_class='col-md-6'),

                            Div('cat_friendly', css_class='col-md-4'),
                            Div('dog_friendly', css_class='col-md-4'),
                            Div('child_friendly', css_class='col-md-4'),
                            css_class='row'
                        ),
                        css_class='card-body'
                    ),
                    css_class='card'
                ),
                css_class='col-lg-8'
            ),
        )

    class Meta:
        model = Pet
        fields = [
            'name',
            'status',
            'photo',
            'short_description',
            'description',
            'gender',
            'age',
            'size',
            'weight',
            'desexed',
            'is_vaccinated',
            'is_special_care_needed',
            'cat_friendly',
            'dog_friendly',
            'child_friendly',
        ]
        widgets = {
            'photo': ClearableFileInput(attrs={
                'class': 'photo',
                'data-show-remove': 'false',
            }),
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


PetProfilePhotoFormSet = inlineformset_factory(Pet, PetProfilePhoto, form=PetProfilePhotoForm, extra=0)


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
            'q',
            HTML("<hr>"),
            Div(
                HTML(
                    f"""<a href="{reverse("management_pets_list")}" 
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

    # noinspection PyMethodMayBeStatic
    def filter_pet_status(self, queryset: PetQuerySet, status: PetStatus) -> PetQuerySet:
        return queryset.filter(status=status)

    # noinspection PyMethodMayBeStatic
    def filter_pet_gender(self, queryset: PetQuerySet, gender: PetGender) -> PetQuerySet:
        return queryset.filter(gender=gender)

    # noinspection PyMethodMayBeStatic
    def filter_by_search_term(self, queryset: PetQuerySet, search_term: str) -> PetQuerySet:
        return queryset.filter_by_search_term(search_term)

    def filter_queryset(self, queryset: PetQuerySet) -> PetQuerySet:
        if status := self.get_selected_status():
            queryset = self.filter_pet_status(queryset, status)

        if gender := self.get_selected_gender():
            queryset = self.filter_pet_gender(queryset, gender)

        if search_term := self.get_search_term():
            queryset = self.filter_by_search_term(queryset, search_term)

        return queryset
