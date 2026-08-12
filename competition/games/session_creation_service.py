from django.db import transaction

from teams.models import TeamMembership

from .models import GameSession


class GameSessionCreationService:

    @staticmethod
    @transaction.atomic
    def create_sessions(match):

        team_memberships = TeamMembership.objects.filter(
            team__in=[
                match.team1,
                match.team2,
            ]
        )

        sessions = []

        for membership in team_memberships:

            session, created = GameSession.objects.get_or_create(
                match=match,
                user=membership.user,
            )

            sessions.append(session)

        return sessions