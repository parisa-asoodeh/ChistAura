from unittest.mock import (
    Mock,
    patch,
)

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
    Category,
    RoundQuestion,
)

from games.models import (
    Match,
    GameSession,
)

from games.quiz_models import (
    QuizQuestion,
    QuizMatchQuestion,
    QuizAnswer,
)

from games.quiz_submission_service import (
    QuizSubmissionService,
)

from django.core.exceptions import ValidationError


User = get_user_model()


class QuizSubmissionServiceTest(TestCase):

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
            status="active",
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

        self.category = Category.objects.create(
            name="Chemistry",
            slug="chemistry",
            subject=self.subject,
        )

        self.questions = []

        for index, correct_answer in enumerate(
            ["A", "B", "C"],
            start=1,
        ):

            question = QuizQuestion.objects.create(
                category=self.category,
                question=f"Question {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer=correct_answer,
                difficulty="easy",
            )

            round_question = RoundQuestion.objects.create(
                round=self.round,
                question=question,
                order=index,
            )

            match_question = QuizMatchQuestion.objects.create(
                match=self.match,
                round_question=round_question,
                order=index,
            )

            self.questions.append(
                match_question
            )

        self.session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
            status="started",
        )

        self.form = Mock()

        self.form.cleaned_data = {
            "question_1": "A",
            "question_2": "B",
            "question_3": "D",
        }

    @patch(
        "games.quiz_submission_service.GameSessionService.complete_session"
    )
    @patch(
        "games.quiz_submission_service.SessionTimeService.calculate_completion_time"
    )
    @patch(
        "games.quiz_submission_service.QuizCorrectionService.calculate_raw_score"
    )
    def test_submit_success(
        self,
        mock_raw_score,
        mock_completion_time,
        mock_complete_session,
    ):

        mock_raw_score.return_value = 2
        mock_completion_time.return_value = 15

        mock_completed_session = Mock()
        mock_completed_session.match.round = self.round

        mock_complete_session.return_value = (
            mock_completed_session
        )

        with patch(
            "competitions.tournament_execution_service.TournamentExecutionService.finish_round_if_ready"
        ) as mock_finish_round:

            QuizSubmissionService.submit(
                session=self.session,
                form=self.form,
            )

        self.assertEqual(
            QuizAnswer.objects.filter(
                session=self.session,
            ).count(),
            3,
        )

        mock_raw_score.assert_called_once_with(
            self.session,
        )

        mock_completion_time.assert_called_once_with(
            self.session,
        )

        mock_complete_session.assert_called_once_with(
            session=self.session,
            raw_score=2,
            completion_time=15,
        )

        mock_finish_round.assert_called_once_with(
            self.round,
        )


    def test_submit_fails_when_round_is_not_active(self):

        self.round.status = "scheduled"
        self.round.save(
            update_fields=["status"]
        )

        with self.assertRaisesMessage(
            ValidationError,
            "این راند هنوز فعال نشده است.",
        ):
            QuizSubmissionService.submit(
                session=self.session,
                form=self.form,
            )

        self.assertEqual(
            QuizAnswer.objects.filter(
                session=self.session,
            ).count(),
            0,
        )


    @patch(
        "games.quiz_submission_service.GameSessionService.complete_session"
    )
    def test_submit_creates_correct_answers(
        self,
        mock_complete_session,
    ):

        mock_completed_session = Mock()
        mock_completed_session.match.round = self.round

        mock_complete_session.return_value = (
            mock_completed_session
        )

        with patch(
            "games.quiz_submission_service.QuizCorrectionService.calculate_raw_score",
            return_value=2,
        ), patch(
            "games.quiz_submission_service.SessionTimeService.calculate_completion_time",
            return_value=10,
        ), patch(
            "competitions.tournament_execution_service.TournamentExecutionService.finish_round_if_ready"
        ):

            QuizSubmissionService.submit(
                session=self.session,
                form=self.form,
            )

        answers = (
            QuizAnswer.objects
            .filter(session=self.session)
            .order_by("match_question__order")
        )

        self.assertEqual(
            answers.count(),
            3,
        )

        self.assertEqual(
            answers[0].selected_answer,
            "A",
        )

        self.assertTrue(
            answers[0].is_correct,
        )

        self.assertEqual(
            answers[1].selected_answer,
            "B",
        )

        self.assertTrue(
            answers[1].is_correct,
        )

        self.assertEqual(
            answers[2].selected_answer,
            "D",
        )

        self.assertFalse(
            answers[2].is_correct,
        )

    @patch(
        "games.quiz_submission_service.GameSessionService.complete_session"
    )
    def test_submit_rolls_back_answers_when_completion_fails(
        self,
        mock_complete_session,
    ):

        mock_complete_session.side_effect = RuntimeError(
            "completion failed"
        )

        with patch(
            "games.quiz_submission_service.QuizCorrectionService.calculate_raw_score",
            return_value=2,
        ), patch(
            "games.quiz_submission_service.SessionTimeService.calculate_completion_time",
            return_value=10,
        ):

            with self.assertRaises(
                RuntimeError
            ):

                QuizSubmissionService.submit(
                    session=self.session,
                    form=self.form,
                )

        self.assertEqual(
            QuizAnswer.objects.filter(
                session=self.session,
            ).count(),
            0,
        )

    @patch(
        "games.quiz_submission_service.GameSessionService.complete_session"
    )
    def test_submit_returns_completed_session(
        self,
        mock_complete_session,
    ):

        mock_completed_session = Mock()
        mock_completed_session.match.round = self.round

        mock_complete_session.return_value = (
            mock_completed_session
        )

        with patch(
            "games.quiz_submission_service.QuizCorrectionService.calculate_raw_score",
            return_value=3,
        ), patch(
            "games.quiz_submission_service.SessionTimeService.calculate_completion_time",
            return_value=20,
        ), patch(
            "competitions.tournament_execution_service.TournamentExecutionService.finish_round_if_ready"
        ):

            result = QuizSubmissionService.submit(
                session=self.session,
                form=self.form,
            )

        self.assertIs(
            result,
            mock_completed_session,
        )