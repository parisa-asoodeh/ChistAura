from django.contrib import admin
from .models import Team, TeamMembership


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'captain',
        'created_at',
        'get_points',
        'get_wins',
        'get_draws',
        'get_losses',
        'get_played',
    )

    search_fields = ('name', 'captain__username')
    list_filter = ('created_at',)

    def get_points(self, obj):
        return obj.get_points()
    get_points.short_description = "امتیاز"

    def get_wins(self, obj):
        return obj.get_wins()
    get_wins.short_description = "برد"

    def get_draws(self, obj):
        return obj.get_draws()
    get_draws.short_description = "مساوی"

    def get_losses(self, obj):
        return obj.get_losses()
    get_losses.short_description = "باخت"

    def get_played(self, obj):
        return obj.get_played()
    get_played.short_description = "بازی‌ها"


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'individual_score')
    search_fields = ('user__username', 'team__name')
    list_filter = ('team',)