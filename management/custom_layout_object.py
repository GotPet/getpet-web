from crispy_forms.layout import LayoutObject
from crispy_forms.utils import TEMPLATE_PACK
from django.template.loader import render_to_string
from crispy_forms.bootstrap import AppendedText as BaseAppendedText, PrependedText as BasePrependedText


class Formset(LayoutObject):
    template = "crispy/formset.html"

    def __init__(self, formset_name_in_context):
        self.formset_name_in_context = formset_name_in_context
        self.fields = []

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]
        return render_to_string(self.template, {'formset': formset})


class CardTitle(LayoutObject):
    template = "crispy/card-title.html"

    def __init__(self, strong_text=None, light_text=None):
        self.strong_text = strong_text
        self.light_text = light_text
        self.fields = []

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        return render_to_string(self.template, {
            'strong_text': self.strong_text,
            'light_text': self.light_text,

        })


class PrependedText(BasePrependedText):
    def __init__(self, field, text, *args, **kwargs):
        kwargs['template'] = 'management/widget/prepended_appended_text.html'
        super().__init__(field, text, *args, **kwargs)


class AppendedText(BaseAppendedText):
    def __init__(self, field, text, *args, **kwargs):
        kwargs['template'] = 'management/widget/prepended_appended_text.html'
        super().__init__(field, text, *args, **kwargs)
