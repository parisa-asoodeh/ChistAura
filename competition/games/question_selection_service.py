import random

from games.quiz_models import (
    QuizQuestion,
    QuizMatchQuestion,
)


class QuestionSelectionService:

    @classmethod
    def select_questions(
        cls,
        *,
        tournament,
        category,
        difficulty,
        count,
    ):
        questions = cls._filter_questions(
            tournament=tournament,
            category=category,
            difficulty=difficulty,
        )

        return cls._randomize_questions(
            questions=questions,
            count=count,
        )

    @staticmethod
    def _filter_questions(
        *,
        tournament,
        category,
        difficulty,
    ):
        used_question_ids = QuizMatchQuestion.objects.filter(
            match__tournament=tournament,
        ).values_list(
            "question_id",
            flat=True,
        )


        return QuizQuestion.objects.filter(
            category=category,
            difficulty=difficulty,
            is_active=True,
        ).exclude(
            id__in=used_question_ids,
        )

    @staticmethod
    def _randomize_questions(
        *,
        questions,
        count,
    ):
        question_ids = list(
            questions.values_list(
                "id",
                flat=True,
            )
        )

        selected_ids = random.sample(
            question_ids,
            min(count, len(question_ids)),
        )

        return QuizQuestion.objects.filter(
            id__in=selected_ids,
        )


    @classmethod
    def select_questions_by_difficulty(
        cls,
        *,
        tournament,
        category,
        difficulty_distribution,
    ):

        selected_questions = []

        for difficulty, count in difficulty_distribution.items():

            questions = cls.select_questions(
                tournament=tournament,
                category=category,
                difficulty=difficulty,
                count=count,
            )

            selected_questions.extend(
                questions
            )

        random.shuffle(
            selected_questions
        )

        return selected_questions