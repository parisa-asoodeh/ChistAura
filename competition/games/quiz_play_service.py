from .quiz_models import QuizMatchQuestion
from .game_resume_service import GameResumeService
from .state_serializers.quiz import QuizStateSerializer


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

        resume_state = GameResumeService.load(
            session
        )

        answers = QuizStateSerializer().deserialize(
            resume_state
        )

        return {
            "session": session,
            "questions": questions,
            "resume_state": answers,
        }