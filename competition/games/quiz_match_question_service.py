from .quiz_models import QuizMatchQuestion
from .question_selection_service import QuestionSelectionService


class QuizMatchQuestionService:

    @classmethod
    def create_questions_for_match(
        cls,
        *,
        match,
        category,
        difficulty,
        count,
    ):

        questions = QuestionSelectionService.select_questions(
            tournament=match.tournament,
            category=category,
            difficulty=difficulty,
            count=count,
        )

        quiz_match_questions = []

        for index, question in enumerate(
            questions,
            start=1,
        ):

            quiz_match_questions.append(
                QuizMatchQuestion(
                    match=match,
                    question=question,
                    order=index,
                )
            )

        return QuizMatchQuestion.objects.bulk_create(
            quiz_match_questions
        )