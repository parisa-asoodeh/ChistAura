from django import forms


class GameResultForm(forms.Form):

    raw_score = forms.IntegerField(
        min_value=0,
        label="امتیاز"
    )

    completion_time = forms.IntegerField(
        min_value=1,
        label="زمان (ثانیه)"
    )