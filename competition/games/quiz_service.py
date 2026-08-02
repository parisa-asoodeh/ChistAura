from .quiz_models import QuizQuestion


class QuizService:

    @staticmethod
    def get_questions_for_session(session):

        return QuizQuestion.objects.filter(
            is_active=True
        )