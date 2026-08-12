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
)

from games.models import (
    Match,
    GameSession,
    MatchPlayerScore,
)

from games.match_detail_service import (
    MatchDetailService,
)

class MatchDetailServiceTest(TestCase):
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

        self.subject = Subject.objects.create(
            name="General",
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            subject=self.subject,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )

        self.match = Match.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )


    def test_build_team_players(
        self,
    ):

        # Arrange
        session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
            status="completed",
        )

        score = MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=25,
        )

        # Act
        players = MatchDetailService._build_team_players(
            self.match,
            self.team1,
        )

        # Assert
        self.assertEqual(
            len(players),
            1,
        )

        self.assertEqual(
            players[0]["user"],
            self.user1,
        )

        self.assertEqual(
            players[0]["session"],
            session,
        )

        self.assertEqual(
            players[0]["score"],
            score,
        )


    def test_build(
        self,
    ):

        # Arrange
        GameSession.objects.create(
            match=self.match,
            user=self.user1,
            status="completed",
        )

        GameSession.objects.create(
            match=self.match,
            user=self.user2,
            status="pending",
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=30,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team2,
            score=20,
        )

        # Act
        result = MatchDetailService.build(
            self.match,
        )

        # Assert
        self.assertEqual(
            result["match"],
            self.match,
        )

        self.assertEqual(
            result["team1_total"],
            1,
        )

        self.assertEqual(
            result["team2_total"],
            1,
        )

        self.assertEqual(
            result["team1_completed"],
            1,
        )

        self.assertEqual(
            result["team2_completed"],
            0,
        )

        self.assertEqual(
            result["completed_players"],
            1,
        )

        self.assertEqual(
            result["total_players"],
            2,
        )

        self.assertEqual(
            result["remaining_players"],
            1,
        )

        self.assertEqual(
            len(result["team1_players"]),
            1,
        )

        self.assertEqual(
            len(result["team2_players"]),
            1,
        )