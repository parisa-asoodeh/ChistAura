from django import forms


class QuizPlayForm(forms.Form):

    def __init__(
        self,
        questions,
        resume_state=None,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        answers = resume_state or {}

        for item in questions:

            question = item.round_question.question

            self.fields[
                f"question_{item.id}"
            ] = forms.ChoiceField(
                label=question.question,
                choices=[
                    ("A", question.option_a),
                    ("B", question.option_b),
                    ("C", question.option_c),
                    ("D", question.option_d),
                ],
                widget=forms.RadioSelect,
                required=True,
                initial=answers.get(
                    str(item.id)
                ),
            )