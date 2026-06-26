from django.db import transaction

from teams.models import TeamMembership

from .models import GameSession


class GameSessionCreationService:

    @staticmethod
    @transaction.atomic
    def create_sessions(match):

        team1_members = TeamMembership.objects.filter(
            team=match.team1
        )

        team2_members = TeamMembership.objects.filter(
            team=match.team2
        )

        for membership in team1_members:

            GameSession.objects.create(
                match=match,
                user=membership.user,
            )

        for membership in team2_members:

            GameSession.objects.create(
                match=match,
                user=membership.user,
            )