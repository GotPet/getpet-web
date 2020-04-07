from typing import Type

from allauth.account.forms import LoginForm as AllAuthLoginForm, ResetPasswordForm as AllAuthResetPasswordForm, \
    SignupForm as AllAuthSignupForm, BaseSignupForm
from allauth.socialaccount.forms import SignupForm as AllAuthSocialSignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Layout, Submit
from django.utils.translation import gettext_lazy as _

_redirect_field_html = HTML("""
                  {% if redirect_field_value %}
                      <input type="hidden" name="{{ redirect_field_name }}"
                                   value="{{ redirect_field_value }}"/>
                  {% endif %}
                """)


def _remove_autofocus_and_placeholders(form: Type[BaseSignupForm]):
    for field_name in form.fields:
        form.fields[field_name].widget.attrs.pop("autofocus", None)
        form.fields[field_name].widget.attrs.pop("placeholder", None)


class WebFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label_class = 'text-uppercase text-fader fw-500 fs-11'
        self.field_template = 'management/widget/bootstrap-field.html'


class AccountFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form_method = 'POST'
        self.form_class = "form-type-material"
        self.label_class = ''
        self.field_template = 'management/widget/bootstrap-field.html'


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
        _remove_autofocus_and_placeholders(self)


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
