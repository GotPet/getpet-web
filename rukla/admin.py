from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminMixin
from django.contrib import admin
from django.contrib.admin import StackedInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, F
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

# Register your models here.
from rukla.models import Question, Answer, Rank, GameStatus, UserInfo


class AnswerInline(admin.TabularInline):
    model = Answer


@admin.register(Question)
class QuestionAdmin(VersionAdmin):
    search_fields = ['text', 'explanation', ]
    list_display = ['text', 'explanation', 'created_at', 'updated_at']

    inlines = [
        AnswerInline
    ]


@admin.register(GameStatus)
class GameStatusAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['user_info', 'answered_count', 'is_finished', 'failed_answer', 'time', 'rank', 'created_at',
                    'updated_at']
    raw_id_fields = ['user_info', 'failed_answer']
    list_select_related = ['rank', 'user_info', 'failed_answer', ]
    filter_horizontal = ['answered_questions']
    list_filter = ['is_finished', 'rank']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(answered_count=Count('answered_questions'),
                                                      time=F('updated_at') - F('created_at'))

    def answered_count(self, obj):
        return obj.answered_count

    answered_count.admin_order_field = "answered_count"
    answered_count.short_description = _("Atsakyta klausimų žaidime")

    def time(self, obj):
        return obj.time

    time.admin_order_field = "time"
    time.short_description = _("Laikas")


@admin.register(Rank)
class RankAdmin(SortableAdminMixin, VersionAdmin):
    search_fields = ['name']
    list_display = ['name', ]


@admin.register(UserInfo)
class UserInfoAdmin(VersionAdmin):
    list_display = ['user', 'rank']
    list_filter = ['rank']
    raw_id_fields = ['user']
