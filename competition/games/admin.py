from django.contrib import admin
from django.contrib import messages

from .models import Match
from .services import MatchService
from .models import Match, MatchPlayerScore


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):

    list_display = (
        'tournament',
        'team1',
        'score_team1',       
        'team2',
        'score_team2',
        'winner',
        'played_at'
    )

    list_filter = (
        'tournament',
        'played_at',
    )


    actions = [
        'finish_match',
    ]


    @admin.action(description="ثبت نتیجه مسابقه")
    def finish_match(self, request, queryset):

        for match in queryset:

            MatchService.set_result(
                match,
                match.score_team1,
                match.score_team2
            )

        self.message_user(
            request,
            "نتیجه مسابقات ثبت شد.",
            messages.SUCCESS
        )


@admin.register(MatchPlayerScore)
class MatchPlayerScoreAdmin(admin.ModelAdmin):

    list_display = (
        'match',
        'user',
        'team',
        'score',
    )

    list_filter = (
        'team',
        'match',
    )

    search_fields = (
        'user__username',
        'team__name',
    )