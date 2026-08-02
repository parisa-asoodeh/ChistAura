from django import forms


class QuizPlayForm(forms.Form):


    def __init__(
        self,
        questions,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        for item in questions:

            self.fields[
                f"question_{item.id}"
            ] = forms.ChoiceField(
                label=item.question.question,
                choices=[
                    ("A", item.question.option_a),
                    ("B", item.question.option_b),
                    ("C", item.question.option_c),
                    ("D", item.question.option_d),
                ],
                widget=forms.RadioSelect,
                required=True,
            )