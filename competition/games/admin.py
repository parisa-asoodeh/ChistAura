from django.contrib import admin
from django.contrib import messages

from .services import MatchService
from .models import Match, MatchPlayerScore

from .quiz_models import (
    QuizQuestion,
    QuizMatchQuestion,
)

from competitions.models import (
    Category,
)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):

    list_display = (
        'round',
        'team1',
        'score_team1',       
        'team2',
        'score_team2',
        'winner',
        'played_at'
    )

    list_filter = (
        'round',
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


class SubjectFilter(admin.SimpleListFilter):

    title = "موضوع"

    parameter_name = "subject"

    def lookups(self, request, model_admin):
        from competitions.models import Subject

        return [
            (subject.id, subject.name)
            for subject in Subject.objects.all()
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                category__subject_id=self.value()
            )

        return queryset


class CategoryFilter(admin.SimpleListFilter):

    title = "دسته‌بندی"

    parameter_name = "category"

    def lookups(self, request, model_admin):
        from competitions.models import Category

        return [
            (category.id, str(category))
            for category in Category.objects.all()
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                category_id=self.value()
            )

        return queryset

    
@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):

    list_display = (
        'get_subject',
        'category',
        'short_question',
        'difficulty',
        'is_active',
    )

    list_filter = (
        SubjectFilter,
        CategoryFilter,
        'difficulty',
        'is_active',
    )

    search_fields = (
        'question',
        'category__name',
        'category__subject__name',
    )

    def short_question(self, obj):
        return obj.question[:50]

    short_question.short_description = "سؤال"

    def get_subject(self, obj):
        return obj.category.subject.name

    get_subject.short_description = "موضوع"


@admin.register(QuizMatchQuestion)
class QuizMatchQuestionAdmin(admin.ModelAdmin):

    list_display = (
        'match',
        'round_question',
        'order',
    )

    list_filter = (
        'match',
    )