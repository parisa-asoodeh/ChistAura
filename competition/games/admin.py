from django.contrib import admin
from django.contrib import messages

from .services import MatchService
from .models import Match, MatchPlayerScore

from .quiz_models import (
    QuizCategory,
    QuizQuestion,
    QuizMatchQuestion,
)

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

    readonly_fields = (
        'winner',
        'score_team1',
        'score_team2',
        'played_at',
    )



@admin.register(MatchPlayerScore)
class MatchPlayerScoreAdmin(admin.ModelAdmin):

    list_display = (
        'match',
        'user',
        'team',
        'score',
        'completion_time',
    )

    list_filter = (
        'team',
        'match',
    )

    search_fields = (
        'user__username',
        'team__name',
    )


@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
    )


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):

    list_display = (
        'question',
        'category',
        'is_active',
    )

    list_filter = (
        'category',
        'is_active',
    )


@admin.register(QuizMatchQuestion)
class QuizMatchQuestionAdmin(admin.ModelAdmin):

    list_display = (
        'match',
        'question',
        'order',
    )

    list_filter = (
        'match',
    )