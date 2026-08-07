from django.test import TestCase

from competitions.models import Subject, Category
from games.models import Match
from games.quiz_models import QuizQuestion, QuizMatchQuestion
from games.quiz_match_question_service import QuizMatchQuestionService
from competitions.models import GameType
from competitions.models import Tournament
from teams.models import Team
from accounts.models import CustomUser

class QuizMatchQuestionServiceTest(TestCase):

    def test_create_questions_for_match_creates_questions(self):

        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
        )

        category = Category.objects.create(
            subject=subject,
            name="Periodic Table",
            slug="periodic-table",
        )

        for index in range(5):
            QuizQuestion.objects.create(
                category=category,
                question=f"Question {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="easy",
                is_active=True,
            )

        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="Chemistry Tournament",
            game_type=game_type,
            subject=subject,
        )

        captain1 = CustomUser.objects.create_user(
            username="captain1",
            password="testpass123",
        )

        captain2 = CustomUser.objects.create_user(
            username="captain2",
            password="testpass123",
        )

        team1 = Team.objects.create(
            name="Team 1",
            captain=captain1,
        )

        team2 = Team.objects.create(
            name="Team 2",
            captain=captain2,
        )

        match = Match.objects.create(
            tournament=tournament,
            team1=team1,
            team2=team2,
        )

        QuizMatchQuestionService.create_questions_for_match(
            match=match,
            category=category,
            difficulty="easy",
            count=3,
        )

        quiz_questions = QuizMatchQuestion.objects.filter(
            match=match
        )

        self.assertEqual(
            quiz_questions.count(),
            3,
        )

        self.assertEqual(
            quiz_questions.first().order,
            1,
        )

        orders = list(
            quiz_questions.values_list(
                "order",
                flat=True,
            )
        )

        self.assertEqual(
            orders,
            [1, 2, 3],
        )


    def test_create_questions_for_match_does_not_repeat_questions_in_tournament(self):

        subject = Subject.objects.create(
            name="Physics",
            slug="physics",
        )

        category = Category.objects.create(
            subject=subject,
            name="Mechanics",
            slug="mechanics",
        )


        questions = []

        for index in range(6):
            questions.append(
                QuizQuestion.objects.create(
                    category=category,
                    question=f"Physics Question {index}",
                    option_a="A",
                    option_b="B",
                    option_c="C",
                    option_d="D",
                    correct_answer="A",
                    difficulty="easy",
                    is_active=True,
                )
            )


        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )


        tournament = Tournament.objects.create(
            name="Physics Tournament",
            game_type=game_type,
            subject=subject,
        )


        captain1 = CustomUser.objects.create_user(
            username="captain3",
            password="testpass123",
        )

        captain2 = CustomUser.objects.create_user(
            username="captain4",
            password="testpass123",
        )


        team1 = Team.objects.create(
            name="Team A",
            captain=captain1,
        )

        team2 = Team.objects.create(
            name="Team B",
            captain=captain2,
        )


        match1 = Match.objects.create(
            tournament=tournament,
            team1=team1,
            team2=team2,
        )


        match2 = Match.objects.create(
            tournament=tournament,
            team1=team2,
            team2=team1,
        )


        QuizMatchQuestionService.create_questions_for_match(
            match=match1,
            category=category,
            difficulty="easy",
            count=3,
        )


        QuizMatchQuestionService.create_questions_for_match(
            match=match2,
            category=category,
            difficulty="easy",
            count=3,
        )


        first_match_questions = set(
            QuizMatchQuestion.objects.filter(
                match=match1
            ).values_list(
                "question_id",
                flat=True,
            )
        )


        second_match_questions = set(
            QuizMatchQuestion.objects.filter(
                match=match2
            ).values_list(
                "question_id",
                flat=True,
            )
        )


        self.assertEqual(
            first_match_questions.intersection(
                second_match_questions
            ),
            set(),
        )