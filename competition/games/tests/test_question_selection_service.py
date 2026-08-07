from django.test import TestCase

from competitions.models import (
    Subject,
    Category,
    Tournament,
    GameType,
)
from games.models import Match
from games.question_selection_service import QuestionSelectionService
from games.quiz_models import (
    QuizQuestion,
    QuizMatchQuestion,
)
from teams.models import Team
from accounts.models import CustomUser



class QuestionSelectionServiceTest(TestCase):

    def test_select_questions_returns_only_matching_questions(self):

        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
        )

        category = Category.objects.create(
            subject=subject,
            name="Periodic Table",
            slug="periodic-table",
        )

        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="Chemistry Tournament",
            subject=subject,
            game_type=game_type,
        )

        matching_question = QuizQuestion.objects.create(
            category=category,
            question="Hydrogen symbol?",
            option_a="H",
            option_b="He",
            option_c="Li",
            option_d="O",
            correct_answer="A",
            difficulty="easy",
            is_active=True,
        )

        wrong_difficulty_question = QuizQuestion.objects.create(
            category=category,
            question="Hard question",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            difficulty="hard",
            is_active=True,
        )

        questions = QuestionSelectionService.select_questions(
            tournament=tournament,
            category=category,
            difficulty="easy",
            count=10,
        )

        self.assertEqual(
            questions.count(),
            1,
        )

        self.assertIn(
            matching_question,
            questions,
        )

        self.assertNotIn(
            wrong_difficulty_question,
            questions,
        )


    def test_select_questions_returns_requested_count_randomly(self):

        subject = Subject.objects.create(
            name="Math",
            slug="math",
        )

        category = Category.objects.create(
            subject=subject,
            name="Algebra",
            slug="algebra",
        )

        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="Math Tournament",
            subject=subject,
            game_type=game_type,
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

        questions = QuestionSelectionService.select_questions(
            tournament=tournament,
            category=category,
            difficulty="easy",
            count=3,
        )

        self.assertEqual(
            questions.count(),
            3,
        )

        for question in questions:
            self.assertEqual(
                question.category,
                category,
            )

            self.assertEqual(
                question.difficulty,
                "easy",
            )


    def test_used_questions_are_excluded_for_same_tournament(self):

        subject = Subject.objects.create(
            name="Physics",
            slug="physics",
        )

        category = Category.objects.create(
            subject=subject,
            name="Mechanics",
            slug="mechanics",
        )

        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="Physics Tournament",
            subject=subject,
            game_type=game_type,
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


        questions = []

        for index in range(5):
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


        QuizMatchQuestion.objects.create(
            match=match,
            question=questions[0],
            order=1,
        )


        selected_questions = QuestionSelectionService.select_questions(
            tournament=tournament,
            category=category,
            difficulty="easy",
            count=4,
        )


        self.assertNotIn(
            questions[0],
            selected_questions,
        )


    def test_select_questions_by_difficulty_distribution(self):

        subject = Subject.objects.create(
            name="Biology",
            slug="biology",
        )

        category = Category.objects.create(
            subject=subject,
            name="Cells",
            slug="cells",
        )


        for index in range(3):

            QuizQuestion.objects.create(
                category=category,
                question=f"Easy {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="easy",
                is_active=True,
            )


        for index in range(3):

            QuizQuestion.objects.create(
                category=category,
                question=f"Hard {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="hard",
                is_active=True,
            )


        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="Biology Tournament",
            game_type=game_type,
            subject=subject,
        )
        
        questions = QuestionSelectionService.select_questions_by_difficulty(
            tournament=tournament,
            category=category,
            difficulty_distribution={
                "easy": 2,
                "hard": 1,
            },
        )


        self.assertEqual(
            len(questions),
            3,
        )


        difficulties = [
            question.difficulty
            for question in questions
        ]


        self.assertEqual(
            difficulties.count("easy"),
            2,
        )


        self.assertEqual(
            difficulties.count("hard"),
            1,
        )