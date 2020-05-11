from ipware import get_client_ip
from rest_framework_tracking.mixins import LoggingMixin


class ApiLoggingMixin(LoggingMixin):
    def handle_log(self):
        self.log['response'] = None

        super().handle_log()

    def _get_ip_address(self, request):
        client_ip, _ = get_client_ip(request)

        return client_ip
