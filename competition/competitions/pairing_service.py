from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Pairing, RoundBye
from .ranking_service import TournamentRankingService


class SwissPairingService:

    @staticmethod
    @transaction.atomic
    def create_pairings(round_obj):

        if round_obj.status != "scheduled":
            raise ValidationError(
                "فقط برای Round زمان‌بندی‌شده می‌توان Pairing ایجاد کرد."
            )

        tournament = round_obj.tournament

        if tournament.status != "active":
            raise ValidationError(
                "Tournament باید فعال باشد."
            )

        if Pairing.objects.filter(
            round=round_obj,
        ).exists():

            raise ValidationError(
                "برای این Round قبلاً Pairing ایجاد شده است."
            )

        if RoundBye.objects.filter(
            round=round_obj,
        ).exists():

            raise ValidationError(
                "برای این Round قبلاً Bye ایجاد شده است."
            )

        teams = TournamentRankingService.rank_teams(
            tournament,
        )

        if not teams:
            raise ValidationError(
                "برای ایجاد Pairing حداقل یک تیم لازم است."
            )

        bye_team = None

        if len(teams) % 2 != 0:

            bye_team = teams.pop()

            RoundBye.objects.create(
                round=round_obj,
                team=bye_team,
                points=3,
            )

        existing_pairings = set()

        previous_pairings = Pairing.objects.filter(
            round__tournament=tournament,
        ).values_list(
            "team1_id",
            "team2_id",
        )

        for team1_id, team2_id in previous_pairings:
            existing_pairings.add(
                frozenset(
                    (team1_id, team2_id)
                )
            )

        pairings = []

        remaining_teams = teams.copy()

        while remaining_teams:

            team1 = remaining_teams.pop(0)

            opponent_index = None

            for index, team2 in enumerate(
                remaining_teams
            ):
                pair_key = frozenset(
                    (
                        team1.id,
                        team2.id,
                    )
                )

                if pair_key not in existing_pairings:
                    opponent_index = index
                    break

            if opponent_index is None:
                raise ValidationError(
                    "امکان ایجاد Pairing معتبر بدون تکرار حریف وجود ندارد."
                )

            team2 = remaining_teams.pop(
                opponent_index
            )

            pairing = Pairing.objects.create(
                round=round_obj,
                team1=team1,
                team2=team2,
            )

            pairings.append(pairing)

            existing_pairings.add(
                frozenset(
                    (
                        team1.id,
                        team2.id,
                    )
                )
            )

        return pairings