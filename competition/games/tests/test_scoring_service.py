from unittest.mock import Mock, patch

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

from games.scoring import MatchScoringService

from unittest.mock import patch

from django.db.models.signals import post_save

from games.signals import (
    recalculate_after_save,
)

from games.models import MatchPlayerScore


class MatchScoringServiceTest(TestCase):
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

    
    def test_is_match_complete_when_all_players_have_score(
        self,
    ):

        # Arrange
        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=10,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team2,
            score=20,
        )

        # Act
        result = MatchScoringService.is_match_complete(
            self.match,
        )

        # Assert
        self.assertTrue(
            result,
        )


    def test_is_match_complete_when_some_players_have_no_score(
        self,
    ):

        # Arrange
        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=10,
        )

        # Act
        result = MatchScoringService.is_match_complete(
            self.match,
        )

        # Assert
        self.assertFalse(
            result,
        )


    def test_recalculate_match_when_team_has_no_scores(
        self,
    ):

        # Arrange
        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=10,
        )

        # Act
        MatchScoringService.recalculate_match(
            self.match,
        )

        self.match.refresh_from_db()

        # Assert
        self.assertIsNone(
            self.match.score_team1,
        )

        self.assertIsNone(
            self.match.score_team2,
        )

        self.assertIsNone(
            self.match.winner,
        )

    
    @patch(
        "games.scoring.PlayerScoreService.update_player_scores"
    )
    def test_recalculate_match_when_match_is_not_complete(
        self,
        mock_update_scores,
    ):

        post_save.disconnect(
            receiver=recalculate_after_save,
            sender=MatchPlayerScore,
        )

        try:

            # Arrange
            user3 = CustomUser.objects.create_user(
                username="user3",
                password="1234",
            )

            TeamMembership.objects.create(
                team=self.team1,
                user=user3,
            )

            MatchPlayerScore.objects.create(
                match=self.match,
                user=self.user1,
                team=self.team1,
                score=10,
            )

            MatchPlayerScore.objects.create(
                match=self.match,
                user=self.user2,
                team=self.team2,
                score=20,
            )

            # Act
            MatchScoringService.recalculate_match(
                self.match,
            )

            self.match.refresh_from_db()

            # Assert
            self.assertIsNone(
                self.match.score_team1,
            )

            self.assertIsNone(
                self.match.score_team2,
            )

            self.assertIsNone(
                self.match.winner,
            )

            mock_update_scores.assert_called_once_with(
                self.match,
            )

        finally:

            post_save.connect(
                receiver=recalculate_after_save,
                sender=MatchPlayerScore,
            )


    @patch(
        "games.scoring.get_game_type"
    )
    def test_recalculate_match_when_match_is_complete(
        self,
        mock_get_game_type,
    ):

        post_save.disconnect(
            receiver=recalculate_after_save,
            sender=MatchPlayerScore,
        )

        try:

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
                score=10,
            )

            fake_game_type = Mock()

            fake_game_type.determine_winner.return_value = (
                self.team1
            )

            mock_get_game_type.return_value = (
                fake_game_type
            )

            # Act
            MatchScoringService.recalculate_match(
                self.match,
            )

            self.match.refresh_from_db()

            # Assert
            self.assertEqual(
                self.match.score_team1,
                15,
            )

            self.assertEqual(
                self.match.score_team2,
                10,
            )

            self.assertEqual(
                self.match.winner,
                self.team1,
            )

            mock_get_game_type.assert_called_once_with(
                self.game_type,
            )

            fake_game_type.determine_winner.assert_called_once_with(
                self.match,
                15,
                10,
            )

        finally:

            post_save.connect(
                receiver=recalculate_after_save,
                sender=MatchPlayerScore,
            )