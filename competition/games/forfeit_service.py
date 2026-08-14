from django.core.exceptions import ValidationError


class MatchForfeitService:

    @staticmethod
    def forfeit_match(
        match,
        present_team,
    ):
        if match.status == "forfeit":
            raise ValidationError(
                "این Match قبلاً Forfeit شده است."
            )

        match.status = "forfeit"
        match.forfeit_team = present_team

        match.save(
            update_fields=[
                "status",
                "forfeit_team",
                "winner",
            ],
        )

        return match

    @staticmethod
    def handle_expired_round(
        round_obj,
        present_teams,
    ):
        unfinished_matches = round_obj.matches.filter(
            status__in=["pending", "active"],
        )

        for match in unfinished_matches:
            present_team = present_teams.get(match.id)

            if present_team is None:
                raise ValidationError(
                    "برای Match ناتمام تیم حاضر مشخص نشده است."
                )

            MatchForfeitService.forfeit_match(
                match=match,
                present_team=present_team,
            )