from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.views import View


class UserWithAssociatedShelterMixin(UserPassesTestMixin, View):
    def test_func(self):
        # noinspection PyUnresolvedReferences
        return self.request.user_selected_shelter is not None

    def handle_no_permission(self):
        return redirect('management:shelters_no_associated_shelter')
