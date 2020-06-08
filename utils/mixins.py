from abc import ABCMeta

from django.views.generic.list import BaseListView

from utils.utils import PaginatorWithPageLink, add_url_params


class ViewPaginatorMixin(BaseListView, metaclass=ABCMeta):

    def _page_link(self, page) -> str:
        return add_url_params(
            self.request.get_full_path_info(),
            {self.page_kwarg: page if page != 1 else None}
        )

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        return PaginatorWithPageLink(queryset, per_page,
                                     page_link_function=self._page_link,
                                     orphans=orphans,
                                     allow_empty_first_page=allow_empty_first_page)
