from abc import ABCMeta, abstractmethod
from functools import partial

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic.list import BaseListView

from utils.utils import PaginatorWithPageLink


class UserWithAssociatedShelterMixin(UserPassesTestMixin, View):
    def test_func(self):
        # noinspection PyUnresolvedReferences
        return self.request.user_selected_shelter is not None

    def handle_no_permission(self):
        return redirect('management:shelters_no_associated_shelter')


class ViewPaginatorMixin(BaseListView, metaclass=ABCMeta):

    @abstractmethod
    def page_link(self, query_params, page):
        raise NotImplementedError("ViewPaginatorMixin page_link should be implemented")

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        query_params = self.request.GET.urlencode()
        query_params = '?' + query_params if query_params else ''

        page_link_function = partial(self.page_link, query_params)

        return PaginatorWithPageLink(queryset, per_page,
                                     page_link_function=page_link_function,
                                     orphans=orphans,
                                     allow_empty_first_page=allow_empty_first_page)
