from django.template import Library

register = Library()


@register.simple_tag
def get_page_link(paginator_page, page):
    return paginator_page.page_link(page)
