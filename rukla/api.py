from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from rukla.models import GameStatus, UserInfo, Rank


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameStatus
        fields = ['id', 'game_id', 'answered', 'failed']


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_description="Starts game and updates game status",
))
class GameView(LoggingMixin, UpdateAPIView, CreateAPIView):
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    serializer_class = GameSerializer
    permission_classes = (IsAuthenticated,)

    def user_info(self):
        info, _ = UserInfo.objects.get_or_create(
            user=self.request.user,
            defaults={
                'rank': Rank.default_rank()
            }
        )

        return info

    def perform_create(self, serializer):
        serializer.save(user_info=self.user_info())

    def perform_update(self, serializer):
        serializer.save(user_info=self.user_info())

    # def get_object(self):
    #     return GameStatus.objects.filter(
    #         id=self.request.data.get('id')
    #     ).first()
