from django.test import TestCase

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Round,
    Subject,
    Pairing,
)

from games.models import (
    Match,
    MatchPlayerScore,
)

from teams.ai.best_player_service import (
    BestPlayerService,
)


class BestPlayerServiceTest(TestCase):

    def setUp(self):

        # -------------------------
        # Game Type
        # -------------------------
        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        # -------------------------
        # Tournament
        # -------------------------
        self.tournament = Tournament.objects.create(
            name="League",
            game_type=self.game_type,
        )

        # -------------------------
        # Subject
        # -------------------------
        self.subject = Subject.objects.create(
            name="Math",
            slug="math",
        )

        # -------------------------
        # Round
        # -------------------------
        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            subject=self.subject,
        )

        # -------------------------
        # Users
        # -------------------------
        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        self.user3 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        # -------------------------
        # Teams
        # -------------------------
        self.team1 = Team.objects.create(
            name="Alpha",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Beta",
            captain=self.user2,
        )

        # -------------------------
        # Memberships
        # -------------------------
        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user3,
        )

        # -------------------------
        # Tournament Teams
        # -------------------------
        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )

        # -------------------------
        # Pairing
        # -------------------------
        self.pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )

        # -------------------------
        # Match
        # -------------------------
        self.match = Match.objects.create(
            round=self.round,
            pairing=self.pairing,
            team1=self.team1,
            team2=self.team2,
            score_team1=100,
            score_team2=90,
        )

    def test_returns_highest_score(self):

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=60,
            completion_time=120,
        )

        best = MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team2,
            score=90,
            completion_time=200,
        )

        self.assertEqual(
            BestPlayerService.get_best_player(
                self.match,
            ),
            best,
        )

    def test_breaks_tie_by_completion_time(self):

        best = MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team2,
            score=80,
            completion_time=100,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user3,
            team=self.team2,
            score=80,
            completion_time=150,
        )

        self.assertEqual(
            BestPlayerService.get_best_player(
                self.match,
            ),
            best,
        )

    def test_returns_none_when_no_scores_exist(self):

        self.assertIsNone(
            BestPlayerService.get_best_player(
                self.match,
            )
        )