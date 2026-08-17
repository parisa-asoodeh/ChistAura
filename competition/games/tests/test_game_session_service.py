from django.test import TestCase
from django.contrib.auth import get_user_model

from teams.models import (
    Team,
    TeamMembership,
)

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Round,
    Pairing,
    Subject,
)

from games.models import (
    Match,
    GameSession,
    MatchPlayerScore,
)

from games.session_service import (
    GameSessionService,
)

from django.core.exceptions import ValidationError

from unittest.mock import (
    Mock,
    patch,
)


User = get_user_model()


class GameSessionServiceTest(TestCase):

    def setUp(self):

        self.user1 = User.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = User.objects.create_user(
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
            total_rounds=2,
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

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=3,
        )

        self.pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )

        self.match = Match.objects.create(
            round=self.round,
            pairing=self.pairing,
            team1=self.team1,
            team2=self.team2,
        )

    def test_complete_session_success(self):

        # Arrange
        session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        # Act
        GameSessionService.complete_session(
            session=session,
            raw_score=80,
            completion_time=120,
        )

        # Assert

        session.refresh_from_db()

        self.assertEqual(
            session.status,
            "completed",
        )

        self.assertEqual(
            session.raw_score,
            80,
        )

        self.assertEqual(
            session.completion_time,
            120,
        )

        self.assertIsNotNone(
            session.finished_at,
        )

        score = MatchPlayerScore.objects.get(
            match=self.match,
            user=self.user1,
        )

        self.assertEqual(
            score.score,
            80,
        )

        self.assertEqual(
            score.team,
            self.team1,
        )


    def test_complete_session_when_session_is_completed(self):

        # Arrange
        session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
            status="completed",
        )

        # Act + Assert
        with self.assertRaises(
            ValidationError
        ) as context:

            GameSessionService.complete_session(
                session=session,
                raw_score=80,
                completion_time=120,
            )

        self.assertEqual(
            context.exception.messages,
            [
                "این Session قبلاً تکمیل شده است."
            ],
        )


    def test_complete_session_when_player_score_already_exists(self):

        session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=50,
            completion_time=30,
        )

        with self.assertRaises(ValidationError):
            GameSessionService.complete_session(
                session=session,
                raw_score=100,
                completion_time=40,
            )

        self.assertEqual(
            MatchPlayerScore.objects.filter(
                match=self.match,
                user=self.user1,
            ).count(),
            1,
        )


    def test_complete_session_when_user_is_not_team_member(self):

        session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        TeamMembership.objects.filter(
            team=self.team1,
            user=self.user1,
        ).delete()

        with self.assertRaises(ValidationError):

            GameSessionService.complete_session(
                session=session,
                raw_score=80,
                completion_time=50,
            )


    @patch(
        "games.session_service.get_game_type"
    )
    def test_complete_session_uses_official_score(
        self,
        mock_get_game_type,
    ):

        # Arrange
        session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        mock_game_type = Mock()
        mock_game_type.calculate_score.return_value = 95

        mock_get_game_type.return_value = mock_game_type

        # Act
        GameSessionService.complete_session(
            session=session,
            raw_score=80,
            completion_time=20,
        )

        # Assert
        player_score = MatchPlayerScore.objects.get(
            match=self.match,
            user=self.user1,
        )

        self.assertEqual(
            player_score.score,
            95,
        )

        mock_game_type.calculate_score.assert_called_once_with(
            80,
            20,
        )


    def test_complete_session_updates_session_information(
        self,
    ):

        # Arrange
        session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        # Act
        GameSessionService.complete_session(
            session=session,
            raw_score=80,
            completion_time=20,
        )

        session.refresh_from_db()

        # Assert
        self.assertEqual(
            session.status,
            "completed",
        )

        self.assertEqual(
            session.raw_score,
            80,
        )

        self.assertEqual(
            session.completion_time,
            20,
        )

        self.assertIsNotNone(
            session.finished_at,
        )


    @patch(
        "games.session_service.MatchScoringService.finalize_match"
    )
    def test_complete_session_finalizes_match_when_ready(
        self,
        mock_finalize,
    ):

        # Arrange
        self.round.status = "active"
        self.round.save(update_fields=["status"])

        session1 = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        session2 = GameSession.objects.create(
            match=self.match,
            user=self.user2,
        )

        # بازیکن اول بازی را تمام می‌کند.
        GameSessionService.complete_session(
            session=session1,
            raw_score=80,
            completion_time=20,
        )

        # اثر فراخوانی‌های قبلی Mock را پاک می‌کنیم.
        mock_finalize.reset_mock()

        # Act
        GameSessionService.complete_session(
            session=session2,
            raw_score=70,
            completion_time=25,
        )

        # Assert
        mock_finalize.assert_called_once_with(
            self.match,
        )



    @patch(
        "games.session_service.MatchScoringService.finalize_match"
    )
    def test_complete_session_does_not_finalize_match_when_not_ready(
        self,
        mock_finalize,
    ):

        # Arrange
        session1 = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        GameSession.objects.create(
            match=self.match,
            user=self.user2,
        )

        # Act
        GameSessionService.complete_session(
            session=session1,
            raw_score=80,
            completion_time=20,
        )

        # Assert
        mock_finalize.assert_not_called()