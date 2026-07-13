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
)

from games.models import (
    Match,
    MatchPlayerScore,
)

from games.player_ranking_service import (
    PlayerRankingService,
)

class PlayerRankingServiceTest(TestCase):

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

        self.match = Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
        )

        self.match2 = Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
        )


    def test_get_total_score(
        self,
    ):

        # Arrange
        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=15,
        )

        MatchPlayerScore.objects.create(
            match=self.match2,
            user=self.user1,
            team=self.team1,
            score=25,
        )

        # Act
        total = PlayerRankingService.get_total_score(
            self.user1,
        )

        # Assert
        self.assertEqual(
            total,
            40,
        )


    def test_build_leaderboard(
        self,
    ):

        # Arrange
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
            score=10,
        )

        leaderboard = (
            PlayerRankingService.build_leaderboard()
        )

        # Assert
        self.assertEqual(
            leaderboard[0]["user"],
            self.user1,
        )

        self.assertEqual(
            leaderboard[0]["total_score"],
            30,
        )

        self.assertEqual(
            leaderboard[0]["matches_played"],
            1,
        )

        self.assertEqual(
            leaderboard[0]["average_score"],
            30,
        )

        self.assertEqual(
            leaderboard[1]["user"],
            self.user2,
        )

        self.assertEqual(
            leaderboard[1]["total_score"],
            10,
        )

        self.assertEqual(
            leaderboard[1]["matches_played"],
            1,
        )

        self.assertEqual(
            leaderboard[1]["average_score"],
            10,
        )


    def test_ranking_key(
        self,
    ):

        row = {
            "total_score": 120,
            "average_score": 40,
        }

        result = PlayerRankingService.ranking_key(
            row,
        )

        self.assertEqual(
            result,
            (
                120,
                40,
            ),
        )