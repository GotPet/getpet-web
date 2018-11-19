from rest_framework.permissions import IsAuthenticated

from api.authentication import FirebaseAuthentication


class FirebaseAuthMixin:
    permission_classes = (IsAuthenticated,)
    authentication_classes = (FirebaseAuthentication,)
