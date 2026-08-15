from django.test import TestCase

from accounts.models import CustomUser
from teams.models import Team

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Round,
    Pairing,
    RoundBye,
)

from competitions.pairing_service import SwissPairingService


class PairingStressTest(TestCase):

    TEAM_COUNT = 100
    ROUND_COUNT = 10

    def setUp(self):

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
            is_active=True,
        )

        self.tournament = Tournament.objects.create(
            name="Pairing Stress Tournament",
            game_type=self.game_type,
            total_rounds=self.ROUND_COUNT,
            status="active",
        )

        users = [
            CustomUser(
                username=f"stress_user_{index}",
            )
            for index in range(1, self.TEAM_COUNT + 1)
        ]

        CustomUser.objects.bulk_create(users)

        users = list(
            CustomUser.objects.filter(
                username__startswith="stress_user_",
            ).order_by("id")
        )

        teams = [
            Team(
                name=f"Stress Team {index}",
                captain=user,
            )
            for index, user in enumerate(
                users,
                start=1,
            )
        ]

        Team.objects.bulk_create(teams)

        teams = list(
            Team.objects.filter(
                name__startswith="Stress Team ",
            ).order_by("id")
        )

        TournamentTeam.objects.bulk_create(
            [
                TournamentTeam(
                    tournament=self.tournament,
                    team=team,
                )
                for team in teams
            ]
        )

        self.teams = teams

    def test_pairing_engine_handles_100_teams_for_multiple_rounds(self):

        played_pairs = set()

        for round_number in range(
            1,
            self.ROUND_COUNT + 1,
        ):

            round_obj = Round.objects.create(
                tournament=self.tournament,
                number=round_number,
                status="scheduled",
                subject=self.subject,
                question_difficulty="easy",
                question_count=10,
            )

            try:
                pairings = SwissPairingService.create_pairings(
                    round_obj,
                )
            except Exception as exc:
                self.fail(
                    f"Pairing در Round {round_number} شکست خورد: {exc}"
                )

            # ---------------------------------------------
            # 1. هر Round نباید بیشتر از یک Bye داشته باشد
            # ---------------------------------------------

            bye_count = RoundBye.objects.filter(
                round=round_obj,
            ).count()

            self.assertLessEqual(
                bye_count,
                1,
            )

            # ---------------------------------------------
            # 2. تعداد Pairingها برای 100 تیم باید 50 باشد
            # ---------------------------------------------

            self.assertEqual(
                len(pairings),
                self.TEAM_COUNT // 2,
            )

            self.assertEqual(
                Pairing.objects.filter(
                    round=round_obj,
                ).count(),
                self.TEAM_COUNT // 2,
            )

            # ---------------------------------------------
            # 3. هر تیم فقط یک بار در Round ظاهر شود
            # ---------------------------------------------

            paired_team_ids = []

            for pairing in pairings:

                self.assertNotEqual(
                    pairing.team1_id,
                    pairing.team2_id,
                )

                paired_team_ids.extend(
                    [
                        pairing.team1_id,
                        pairing.team2_id,
                    ]
                )

            self.assertEqual(
                len(paired_team_ids),
                self.TEAM_COUNT,
            )

            self.assertEqual(
                len(set(paired_team_ids)),
                self.TEAM_COUNT,
            )

            # ---------------------------------------------
            # 4. همه تیم‌های Tournament تعیین تکلیف شده‌اند
            # ---------------------------------------------

            bye_team_ids = set(
                RoundBye.objects.filter(
                    round=round_obj,
                ).values_list(
                    "team_id",
                    flat=True,
                )
            )

            resolved_team_ids = (
                set(paired_team_ids)
                | bye_team_ids
            )

            tournament_team_ids = set(
                TournamentTeam.objects.filter(
                    tournament=self.tournament,
                ).values_list(
                    "team_id",
                    flat=True,
                )
            )

            self.assertEqual(
                resolved_team_ids,
                tournament_team_ids,
            )

            # ---------------------------------------------
            # 5. Rematch نباید در این سناریو اتفاق بیفتد
            # ---------------------------------------------

            current_pairs = set()

            for pairing in pairings:

                pair_key = frozenset(
                    (
                        pairing.team1_id,
                        pairing.team2_id,
                    )
                )

                self.assertNotIn(
                    pair_key,
                    played_pairs,
                )

                self.assertNotIn(
                    pair_key,
                    current_pairs,
                )

                current_pairs.add(pair_key)

            played_pairs.update(
                current_pairs,
            )

            # ---------------------------------------------
            # Round را برای ساخت Round بعدی تمام می‌کنیم.
            # در این Stress Test تمرکز فقط روی Pairing Engine است.
            # ---------------------------------------------

            round_obj.status = "finished"
            round_obj.save(
                update_fields=["status"],
            )

        # ---------------------------------------------
        # 6. در پایان همه Roundها دقیقاً 50 Pairing داشته‌ایم
        # ---------------------------------------------

        self.assertEqual(
            Pairing.objects.filter(
                round__tournament=self.tournament,
            ).count(),
            self.ROUND_COUNT * (self.TEAM_COUNT // 2),
        )

        # ---------------------------------------------
        # 7. هیچ Roundای بیش از یک Bye نداشته است
        # ---------------------------------------------

        for round_obj in Round.objects.filter(
            tournament=self.tournament,
        ):
            self.assertLessEqual(
                RoundBye.objects.filter(
                    round=round_obj,
                ).count(),
                1,
            )