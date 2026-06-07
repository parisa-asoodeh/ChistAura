from django import forms
from .models import Team
from django.contrib.auth import get_user_model

User = get_user_model()

class TeamCreateForm(forms.ModelForm):
    # این فیلد لیست کاربران را برای انتخاب نمایش می‌دهد
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple, # یا برای ظاهر بهتر: forms.SelectMultiple
        label="انتخاب ۲ هم‌تیمی"
    )

    class Meta:
        model = Team
        fields = ['name']

    def clean_members(self):
        members = self.cleaned_data.get('members')
        # ولیدیشن: حتماً باید ۲ نفر انتخاب شوند
        if members.count() != 2:
            raise forms.ValidationError("شما باید دقیقاً ۲ هم‌تیمی انتخاب کنید.")
        return members
