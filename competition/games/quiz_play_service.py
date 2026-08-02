from .quiz_models import QuizMatchQuestion


class QuizPlayService:

    @staticmethod
    def build(session):

        questions = (
            QuizMatchQuestion.objects
            .filter(
                match=session.match
            )
            .select_related(
                "question"
            )
            .order_by(
                "order"
            )
        )

        return {
            "session": session,
            "questions": questions,
        }