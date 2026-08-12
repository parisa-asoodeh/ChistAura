from .quiz_models import QuizAnswer


class QuizCorrectionService:

    @staticmethod
    def calculate_raw_score(session):

        raw_score = 0

        answers = (
            QuizAnswer.objects
            .filter(session=session)
            .select_related(
                "match_question__round_question__question"
            )
        )

        for answer in answers:

            if (
                answer.selected_answer
                == answer.match_question.round_question.question.correct_answer
            ):
                raw_score += 1

        return raw_score