import firebase_admin
from firebase_admin import auth, credentials

from getpet import settings


# noinspection PyMethodMayBeStatic
class Firebase:
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)

            cred = credentials.Certificate(settings.FIREBASE_KEY)
            firebase_admin.initialize_app(cred)

        return cls.instance

    def verify_id_token(self, id_token, check_revoked=False):
        return auth.verify_id_token(id_token, check_revoked=check_revoked)

    def get_user(self, uid):
        return auth.get_user(uid)
