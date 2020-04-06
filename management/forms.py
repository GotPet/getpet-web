from allauth.account.forms import LoginForm as AllAuthLoginForm, SignupForm as AllAuthSignupForm, \
    ResetPasswordForm as AllAuthResetPasswordForm
from allauth.socialaccount.forms import SignupForm as AllAuthSocialSignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Submit
from django.utils.translation import gettext_lazy as _


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

        login_fields = ['login', 'password']

        self.helper.layout = Layout(
            HTML(
                """
                  {% if redirect_field_value %}
                      <input type="hidden" name="{{ redirect_field_name }}"
                                   value="{{ redirect_field_value }}"/>
                  {% endif %}
                """
            ),
            *login_fields,
            Submit('submit', _("Prisijungti"), css_class='btn btn-bold btn-block btn-primary')
        )

        for field in login_fields:
            self.fields[field].widget.attrs.pop("autofocus", None)
            self.fields[field].widget.attrs.pop("placeholder", None)


# TODO add recaptcha
class SignupForm(AllAuthSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WebFormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-12'),
                Div('password1', css_class='col-12'),
                Div('password2', css_class='col-12'),
                Div('captcha', css_class='col-12'),
                css_class='row'
            ),
        )


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
        self.helper = WebFormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-12'),
                css_class='row'
            ),
        )
