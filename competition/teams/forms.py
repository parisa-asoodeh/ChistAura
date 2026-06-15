from django import forms
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership

User = get_user_model()


class TeamCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="انتخاب ۲ هم‌تیمی"
    )

    class Meta:
        model = Team
        fields = ['name']

    def clean_members(self):
        members = self.cleaned_data.get('members')

        if members.count() != 2:
            raise forms.ValidationError("شما باید دقیقاً ۲ هم‌تیمی انتخاب کنید.")

        for member in members:
            if TeamMembership.objects.filter(user=member).exists():
                raise forms.ValidationError(
                    f"{member.username} قبلاً عضو یک تیم است."
                )

        return members