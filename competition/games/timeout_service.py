from django.core.exceptions import ValidationError
from django.utils import timezone

from games.forfeit_service import MatchForfeitService
from games.scoring import MatchScoringService


class MatchTimeoutService:

    @staticmethod
    def handle_expired_round(round_obj):

        if round_obj.ends_at is None:
            raise ValidationError(
                "این Round زمان پایان ندارد."
            )

        if timezone.now() < round_obj.ends_at:
            raise ValidationError(
                "زمان Round هنوز تمام نشده است."
            )

        unfinished_matches = round_obj.matches.filter(
            status__in=["pending", "active"],
        )

        for match in unfinished_matches:

            present_teams = set()

            sessions = match.sessions.select_related(
                "user",
            )

            for session in sessions:
                if session.status in ["started", "completed"]:
                    present_teams.add(
                        match.team1
                        if session.user_id in match.team1.members.values_list(
                            "user_id",
                            flat=True,
                        )
                        else match.team2
                    )

            if len(present_teams) == 1:
                present_team = next(
                    iter(present_teams)
                )

                MatchForfeitService.forfeit_match(
                    match=match,
                    present_team=present_team,
                )

            elif len(present_teams) == 0:
                match.status = "double_forfeit"
                match.forfeit_team = None

                match.save(
                    update_fields=[
                        "status",
                        "forfeit_team",
                        "winner",
                    ],
                )

            elif len(present_teams) == 2:
                MatchScoringService.finalize_timeout_match(
                    match,
                )