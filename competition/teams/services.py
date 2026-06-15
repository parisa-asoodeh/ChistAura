from .models import Team, TeamMembership


class TeamService:

    @staticmethod
    def create_team(*, captain, team_name, members):

        team = Team.objects.create(
            name=team_name,
            captain=captain
        )

        TeamMembership.objects.create(
            team=team,
            user=captain
        )

        for member in members:
            TeamMembership.objects.create(
                team=team,
                user=member
            )

        return team