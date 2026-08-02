from .quiz_models import (
    QuizMatchQuestion,
    QuizQuestion,
)


class QuizMatchQuestionService:

    @staticmethod
    def create_questions_for_match(match):

        questions = QuizQuestion.objects.filter(
            is_active=True
        )[:10]


        for index, question in enumerate(
            questions,
            start=1
        ):

            QuizMatchQuestion.objects.create(
                match=match,
                question=question,
                order=index
            )