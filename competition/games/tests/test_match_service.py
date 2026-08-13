from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Round,
)

from games.models import Match

from games.services import MatchService

class MatchServiceTest(TestCase):
    def setUp(self):

        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        self.team1 = Team.objects.create(
            name="Team 1",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Team 2",
            captain=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.tournament = Tournament.objects.create(
            name="League",
            game_type=self.game_type,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )

        self.subject = Subject.objects.create(
            name="General",
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            subject=self.subject,
        )

        self.match = Match.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )


    def test_set_result_team1_wins(self):
        MatchService.set_result(
            self.match,
            score_team1=20,
            score_team2=10,
        )

        self.match.refresh_from_db()

        self.assertEqual(self.match.score_team1, 20)
        self.assertEqual(self.match.score_team2, 10)
        self.assertEqual(self.match.winner, self.team1)


    def test_set_result_team2_wins(self):
        MatchService.set_result(
            self.match,
            score_team1=10,
            score_team2=20,
        )

        self.match.refresh_from_db()

        self.assertEqual(self.match.score_team1, 10)
        self.assertEqual(self.match.score_team2, 20)
        self.assertEqual(self.match.winner, self.team2)


    def test_set_result_draw(self):
        MatchService.set_result(
            self.match,
            score_team1=15,
            score_team2=15,
        )

        self.match.refresh_from_db()

        self.assertEqual(self.match.score_team1, 15)
        self.assertEqual(self.match.score_team2, 15)
        self.assertIsNone(self.match.winner)


    def test_set_result_rejects_negative_score_for_team1(self):
        with self.assertRaises(ValidationError):
            MatchService.set_result(
                self.match,
                score_team1=-1,
                score_team2=10,
            )


    def test_set_result_rejects_negative_score_for_team2(self):
        with self.assertRaises(ValidationError):
            MatchService.set_result(
                self.match,
                score_team1=10,
                score_team2=-1,
            )


    def test_set_result_sets_played_at(self):
        self.assertIsNotNone(self.match.played_at)

        MatchService.set_result(
            self.match,
            score_team1=20,
            score_team2=10,
        )

        self.match.refresh_from_db()

        self.assertIsNotNone(self.match.played_at)