from .quiz_models import QuizAnswer


class QuizAnswerService:

    @staticmethod
    def save_answers(
        session,
        form,
        questions,
    ):

        for item in questions:

            QuizAnswer.objects.create(

                session=session,

                match_question=item,

                selected_answer=form.cleaned_data[
                    f"question_{item.id}"
                ]

            )