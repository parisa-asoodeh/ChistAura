from .quiz_models import QuizMatchQuestion
from .game_resume_service import GameResumeService


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

        return {
            "session": session,
            "questions": questions,
            "resume_state": resume_state,
        }