from teams.models import TeamMembership

from .models import (
    GameSession,
    MatchPlayerScore,
)


class MatchDetailService:

    @staticmethod
    def build(match):

        team1_players = MatchDetailService._build_team_players(
            match,
            match.team1
        )

        team2_players = MatchDetailService._build_team_players(
            match,
            match.team2
        )


        team1_completed = sum(
            1
            for player in team1_players
            if player["session"] and player["session"].status == "completed"
        )

        team2_completed = sum(
            1
            for player in team2_players
            if player["session"] and player["session"].status == "completed"
        )

        team1_total = len(team1_players)
        team2_total = len(team2_players)

        completed_players = (
            team1_completed +
            team2_completed
        )

        total_players = (
            team1_total +
            team2_total
        )

        remaining_players = (
            total_players -
            completed_players
        )

        return {
            "match": match,

            "team1_players": team1_players,
            "team2_players": team2_players,

            "team1_completed": team1_completed,
            "team2_completed": team2_completed,

            "team1_total": team1_total,
            "team2_total": team2_total,

            "completed_players": completed_players,
            "total_players": total_players,
            "remaining_players": remaining_players,
        }
    

    @staticmethod
    def _build_team_players(match, team):

        players = []

        members = TeamMembership.objects.filter(
            team=team
        ).select_related("user")

        for member in members:

            session = GameSession.objects.filter(
                match=match,
                user=member.user
            ).first()

            score = MatchPlayerScore.objects.filter(
                match=match,
                user=member.user
            ).first()

            players.append({
                "user": member.user,
                "session": session,
                "score": score,
            })

        return players