from django.contrib import admin
from django.contrib import messages

from .models import Tournament, TournamentTeam, GameType, Subject
from .services import TournamentService


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):

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
                TournamentService.start_tournament(
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