import firebase_admin
from django.utils.functional import SimpleLazyObject
from firebase_admin import credentials

from getpet import settings
from firebase_admin import auth


# noinspection PyMethodMayBeStatic
class Firebase:
    app = SimpleLazyObject(
        lambda: firebase_admin.initialize_app(credentials.Certificate(settings.FIREBASE_KEY))
    )

    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)

        return cls.instance

    def verify_id_token(self, id_token, check_revoked=False):
        return auth.verify_id_token(id_token, app=self.app, check_revoked=check_revoked)

    def get_user(self, uid):
        return auth.get_user(uid, app=self.app)
