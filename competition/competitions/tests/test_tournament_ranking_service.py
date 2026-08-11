from unittest.mock import Mock

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
    Subject,
    Round,
)

from competitions.ranking_service import (
    TournamentRankingService,
)

from games.models import Match


class TournamentRankingServiceTest(TestCase):
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
            name="Chemistry",
            slug="chemistry",
            is_active=True,
        )

        self.tournament.status = "active"
        self.tournament.save()

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


    def test_rank_teams_returns_empty_list_when_no_teams(
        self,
    ):

        # Arrange
        self.tournament.teams.all().delete()

        # Act
        teams = TournamentRankingService.rank_teams(
            self.tournament,
        )

        # Assert
        self.assertEqual(
            teams,
            [],
        )


    def test_rank_teams_orders_by_points(
        self,
    ):

        # Arrange
        self.team1.get_points_in_tournament = Mock(
            return_value=9,
        )

        self.team2.get_points_in_tournament = Mock(
            return_value=6,
        )

        self.team1.get_score_difference_in_tournament = Mock(
            return_value=0,
        )

        self.team2.get_score_difference_in_tournament = Mock(
            return_value=0,
        )

        self.team1.get_total_time_in_tournament = Mock(
            return_value=100,
        )

        self.team2.get_total_time_in_tournament = Mock(
            return_value=100,
        )

        # Act
        teams = TournamentRankingService.rank_teams(
            self.tournament,
        )

        # Assert
        self.assertEqual(
            teams,
            [
                self.team1,
                self.team2,
            ],
        )


    def test_rank_teams_orders_by_score_difference_when_points_are_equal(
        self,
    ):

        # Arrange
        self.team1.get_points_in_tournament = Mock(
            return_value=9,
        )

        self.team2.get_points_in_tournament = Mock(
            return_value=9,
        )

        self.team1.get_score_difference_in_tournament = Mock(
            return_value=12,
        )

        self.team2.get_score_difference_in_tournament = Mock(
            return_value=5,
        )

        self.team1.get_total_time_in_tournament = Mock(
            return_value=100,
        )

        self.team2.get_total_time_in_tournament = Mock(
            return_value=100,
        )

        # Act
        teams = TournamentRankingService.rank_teams(
            self.tournament,
        )

        # Assert
        self.assertEqual(
            teams,
            [
                self.team1,
                self.team2,
            ],
        )


    def test_rank_teams_orders_by_total_time_when_points_and_difference_are_equal(
        self,
    ):

        # Arrange
        self.team1.get_points_in_tournament = Mock(
            return_value=9,
        )

        self.team2.get_points_in_tournament = Mock(
            return_value=9,
        )

        self.team1.get_score_difference_in_tournament = Mock(
            return_value=5,
        )

        self.team2.get_score_difference_in_tournament = Mock(
            return_value=5,
        )

        self.team1.get_total_time_in_tournament = Mock(
            return_value=90,
        )

        self.team2.get_total_time_in_tournament = Mock(
            return_value=120,
        )

        # Act
        teams = TournamentRankingService.rank_teams(
            self.tournament,
        )

        # Assert
        self.assertEqual(
            teams,
            [
                self.team1,
                self.team2,
            ],
        )


    def test_ranking_key_returns_expected_tuple(
        self,
    ):

        # Arrange
        self.team1.get_points_in_tournament = Mock(
            return_value=9,
        )

        self.team1.get_score_difference_in_tournament = Mock(
            return_value=12,
        )

        self.team1.get_total_time_in_tournament = Mock(
            return_value=95,
        )

        # Act
        key = TournamentRankingService.ranking_key(
            self.team1,
            self.tournament,
        )

        # Assert
        self.assertEqual(
            key,
            (
                9,
                12,
                -95,
            ),
        )