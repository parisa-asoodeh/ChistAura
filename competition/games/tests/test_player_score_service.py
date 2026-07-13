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

from games.player_score_service import (
    PlayerScoreService,
)

class PlayerScoreServiceTest(TestCase):

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

        self.membership1 = TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        self.membership2 = TeamMembership.objects.create(
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


    def test_update_player_scores(
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
            match=self.match,
            user=self.user2,
            team=self.team2,
            score=25,
        )

        # Act
        PlayerScoreService.update_player_scores(
            self.match,
        )

        self.membership1.refresh_from_db()
        self.membership2.refresh_from_db()

        # Assert
        self.assertEqual(
            self.membership1.individual_score,
            15,
        )

        self.assertEqual(
            self.membership2.individual_score,
            25,
        )