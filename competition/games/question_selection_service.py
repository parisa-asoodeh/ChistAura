from games.quiz_models import QuizQuestion


class QuestionSelectionService:

    @staticmethod
    def select_questions(
        *,
        category,
        difficulty,
        count,
    ):
        """
        Return active questions for the given category and difficulty.

        Version 1:
        - No random selection
        - No duplicate prevention
        - No persistence
        """

        return QuizQuestion.objects.filter(
            category=category,
            difficulty=difficulty,
            is_active=True,
        )[:count]