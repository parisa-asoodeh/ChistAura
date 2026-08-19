from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
)


class TournamentDetailViewTest(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.team = Team.objects.create(
            name="Team 1",
            captain=self.user,
        )

        TeamMembership.objects.create(
            team=self.team,
            user=self.user,
        )

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.tournament = Tournament.objects.create(
            name="League",
            game_type=self.game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team,
        )

        self.tournament.status = "active"
        self.tournament.save(update_fields=["status"])


    @patch(
        "competitions.views.ChampionPredictor.predict"
    )
    def test_tournament_detail_contains_ai_prediction(
        self,
        mock_predict,
    ):

        mock_prediction = {
            "champion": self.team,
            "ranking": [
                {
                    "team": self.team,
                    "score": 80.0,
                    "games": 2,
                    "power_rating": 100,
                },
            ],
            "summary": "تیم Team 1 محتمل‌ترین قهرمان لیگ است.",
            "top_reasons": [
                "عملکرد بهتر",
            ],
            "matchups": [],
        }

        mock_predict.return_value = mock_prediction

        response = self.client.get(
            reverse(
                "tournament_detail",
                args=[self.tournament.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["ai_prediction"],
            mock_prediction,
        )

        mock_predict.assert_called_once()


    @patch(
    "competitions.views.ChampionPredictor.predict"
    )
    def test_tournament_detail_does_not_predict_in_draft(
        self,
        mock_predict,
    ):

        self.tournament.status = "draft"
        self.tournament.save(update_fields=["status"])

        response = self.client.get(
            reverse(
                "tournament_detail",
                args=[self.tournament.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNone(
            response.context["ai_prediction"],
        )

        mock_predict.assert_not_called()


    @patch(
        "competitions.views.ChampionPredictor.predict"
    )
    def test_tournament_detail_does_not_predict_in_finished(
        self,
        mock_predict,
    ):

        self.tournament.status = "finished"
        self.tournament.save(update_fields=["status"])

        response = self.client.get(
            reverse(
                "tournament_detail",
                args=[self.tournament.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNone(
            response.context["ai_prediction"],
        )

        mock_predict.assert_not_called()