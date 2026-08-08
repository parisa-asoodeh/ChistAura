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
)

from competitions.services import (
    TournamentService,
)

from unittest.mock import patch

from games.models import (
    Match,
    GameSession,
)

from competitions.models import Subject, Category
from games.quiz_models import QuizQuestion, QuizMatchQuestion


class TournamentServiceTest(TestCase):

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


    def test_add_team_success(
        self,
    ):

        # Arrange
        user3 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        team3 = Team.objects.create(
            name="Team 3",
            captain=user3,
        )

        TeamMembership.objects.create(
            team=team3,
            user=user3,
        )

        # Act
        tournament_team = TournamentService.add_team(
            self.tournament,
            team3,
        )

        # Assert
        self.assertEqual(
            tournament_team.tournament,
            self.tournament,
        )

        self.assertEqual(
            tournament_team.team,
            team3,
        )

        self.assertTrue(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=team3,
            ).exists()
        )


    def test_add_team_when_tournament_is_not_draft(
        self,
    ):

        # Arrange
        self.tournament.status = "active"
        self.tournament.save()

        user3 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        team3 = Team.objects.create(
            name="Team 3",
            captain=user3,
        )

        TeamMembership.objects.create(
            team=team3,
            user=user3,
        )

        # Act & Assert
        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.add_team(
                self.tournament,
                team3,
            )


    def test_remove_team_success(
        self,
    ):

        # Arrange
        self.assertTrue(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team1,
            ).exists()
        )

        # Act
        TournamentService.remove_team(
            self.tournament,
            self.team1,
        )

        # Assert
        self.assertFalse(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team1,
            ).exists()
        )


    def test_remove_team_when_tournament_is_not_draft(
        self,
    ):

        # Arrange
        self.tournament.status = "active"
        self.tournament.save()

        # Act & Assert
        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.remove_team(
                self.tournament,
                self.team1,
            )

        self.assertTrue(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team1,
            ).exists()
        )


    def test_start_tournament_when_status_is_not_draft(
        self,
    ):

        # Arrange
        self.tournament.status = "active"
        self.tournament.save()

        # Act & Assert
        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.start_tournament(
                self.tournament,
            )


    def test_start_tournament_when_has_less_than_two_teams(
        self,
    ):

        # Arrange
        TournamentTeam.objects.filter(
            tournament=self.tournament,
            team=self.team2,
        ).delete()

        # Act & Assert
        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.start_tournament(
                self.tournament,
            )


    def test_start_tournament_when_matches_already_exist(
        self,
    ):

        # Arrange
        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
        )

        # Act & Assert
        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.start_tournament(
                self.tournament,
            )


    def test_start_tournament_success(
        self,
    ):

        # Act
        TournamentService.start_tournament(
            self.tournament,
        )

        self.tournament.refresh_from_db()

        # Assert
        self.assertEqual(
            self.tournament.status,
            "active",
        )

        self.assertIsNotNone(
            self.tournament.started_at,
        )

        matches = Match.objects.filter(
            tournament=self.tournament,
        )

        self.assertEqual(
            matches.count(),
            1,
        )

        sessions = GameSession.objects.filter(
            match=matches.first(),
        )

        self.assertEqual(
            sessions.count(),
            2,
        )


    def test_start_tournament_creates_round_robin_matches(
        self,
    ):

        # Arrange
        user3 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        team3 = Team.objects.create(
            name="Team 3",
            captain=user3,
        )

        TeamMembership.objects.create(
            team=team3,
            user=user3,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=team3,
        )

        # Act
        TournamentService.start_tournament(
            self.tournament,
        )

        # Assert
        self.assertEqual(
            Match.objects.filter(
                tournament=self.tournament,
            ).count(),
            3,
        )

        self.assertEqual(
            GameSession.objects.filter(
                match__tournament=self.tournament,
            ).count(),
            6,
        )


    def test_start_tournament_creates_quiz_questions_for_matches(self):

        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
        )

        Category.objects.create(
            subject=subject,
            name="Periodic Table",
            slug="periodic-table",
            is_active=True,
        )

        self.tournament.subject = subject
        self.tournament.save()

        for index in range(10):
            QuizQuestion.objects.create(
                category=subject.categories.first(),
                question=f"Question {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="easy",
                is_active=True,
            )

        TournamentService.start_tournament(
            self.tournament,
        )

        matches = Match.objects.filter(
            tournament=self.tournament
        )

        self.assertTrue(
            matches.exists()
        )

        self.assertEqual(
            QuizMatchQuestion.objects.filter(
                match__tournament=self.tournament
            ).count(),
            matches.count() * 10,
        )


    def test_start_tournament_uses_tournament_question_settings(
        self,
    ):
        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
        )

        category = Category.objects.create(
            subject=subject,
            name="Periodic Table",
            slug="periodic-table",
        )

        for index in range(3):
            QuizQuestion.objects.create(
                category=category,
                question=f"Medium Question {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="medium",
                is_active=True,
            )

        tournament = Tournament.objects.create(
            name="Medium Quiz Tournament",
            game_type=self.game_type,
            subject=subject,
            question_difficulty="medium",
            question_count=3,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=self.team2,
        )

        # Act
        TournamentService.start_tournament(
            tournament,
        )

        match = Match.objects.get(
            tournament=tournament,
        )

        quiz_questions = QuizMatchQuestion.objects.filter(
            match=match,
        )

        # Assert
        self.assertEqual(
            quiz_questions.count(),
            3,
        )

        for quiz_match_question in quiz_questions:
            self.assertEqual(
                quiz_match_question.question.difficulty,
                "medium",
            )