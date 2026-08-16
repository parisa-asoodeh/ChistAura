from django.contrib import admin
from django.contrib import messages

from .models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Category,
    Round,
)

from .tournament_execution_service import TournamentExecutionService


class RoundInline(admin.TabularInline):
    model = Round
    extra = 0

    fields = (
        'number',
        'status',
        'subject',
        'question_difficulty',
        'question_count',
        'starts_at',
        'ends_at',
    )

    readonly_fields = (
        'status',
        'starts_at',
        'ends_at',
    )

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):

    inlines = [
        RoundInline,
    ]

    list_display = (
        'name',
        'status',
        'created_at',
        'started_at',
        'finished_at',
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'name',
    )


    actions = [
        'start_selected_tournaments',
    ]


    @admin.action(
        description="شروع لیگ‌های انتخاب شده"
    )
    def start_selected_tournaments(self, request, queryset):

        success_count = 0

        for tournament in queryset:

            try:
                TournamentExecutionService.start_tournament(
                    tournament
                )

                success_count += 1

            except Exception as e:

                self.message_user(
                    request,
                    f"{tournament.name}: {str(e)}",
                    level=messages.ERROR
                )


        if success_count:

            self.message_user(
                request,
                f"{success_count} لیگ با موفقیت شروع شد.",
                level=messages.SUCCESS
            )

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)

        if obj is None:
            return inline_instances
        return inline_instances


    def save_related(self, request, form, formsets, change):
        super().save_related(
            request,
            form,
            formsets,
            change,
        )

        tournament = form.instance

        if tournament.status != "draft":
            return

        round_count = tournament.rounds.count()

        if round_count != tournament.total_rounds:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                f"تعداد Roundهای تنظیم‌شده باید دقیقاً "
                f"{tournament.total_rounds} عدد باشد."
            )


@admin.register(TournamentTeam)
class TournamentTeamAdmin(admin.ModelAdmin):

    list_display = (
        'tournament',
        'team',
        'joined_at',
    )

    list_filter = (
        'tournament',
    )

    search_fields = (
        'team__name',
        'tournament__name',
    )

    def has_add_permission(self, request):
        return True
    


@admin.register(GameType)
class GameTypeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "subject",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "subject__name",
    )

    list_filter = (
        "subject",
        "is_active",
    )


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):

    list_display = (
        'tournament',
        'number',
        'status',
        'subject',
        'question_difficulty',
        'question_count',
        'starts_at',
        'ends_at',
    )

    list_filter = (
        'status',
        'question_difficulty',
        'tournament',
        'subject',
    )

    search_fields = (
        'tournament__name',
        'subject__name',
    )

    ordering = (
        'tournament',
        'number',
    )


    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.tournament.status != 'draft':
            return False

        return super().has_change_permission(request, obj)


    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.tournament.status != 'draft':
            return False

        return super().has_delete_permission(request, obj)