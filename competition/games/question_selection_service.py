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
        round,
        categories,
        difficulty,
        count,
    ):
        questions = cls._filter_questions(
            round=round,
            categories=categories,
            difficulty=difficulty,
        )

        return cls._randomize_questions(
            questions=questions,
            count=count,
        )

    @staticmethod
    def _filter_questions(
        *,
        round,
        categories,
        difficulty,
    ):
        used_question_ids = (
            QuizMatchQuestion.objects.filter(
                match__round__tournament=round.tournament,
            )
            .values_list(
                "round_question__question_id",
                flat=True,
            )
        )

        return QuizQuestion.objects.filter(
            category__in=categories,
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
        round,
        categories,
        difficulty_distribution,
    ):
        selected_questions = []

        for difficulty, count in (
            difficulty_distribution.items()
        ):
            questions = cls.select_questions(
                round=round,
                categories=categories,
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