from django.contrib import admin
from .models import Team, TeamMembership, Match

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'captain', 'total_score')

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'individual_score')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'team1',
        'team2',
        'score_team1',
        'score_team2',
        'winner',
        'played_at'
    )