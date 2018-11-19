from logging import getLogger

from rest_framework import authentication

from api.firebase import Firebase
from web.models import User

logger = getLogger()


class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        firebase = Firebase()
        id_token = request.GET.get('Authorization')

        decoded_token = None
        try:
            decoded_token = firebase.verify_id_token(id_token)
        except Exception as e:
            logger.warning(e)
            pass

        if not id_token or not decoded_token:
            return None

        uid = decoded_token.get('uid')
        try:
            firebase_user = firebase.get_user(uid)
        except Exception as e:
            logger.warning(e)
            return None
        email = firebase_user.email.lower() if firebase_user.email else None

        user, is_created = User.objects.update_or_create(username=uid, defaults={
            'email': email,
            'first_name': firebase_user.display_name
        })

        return user, None
