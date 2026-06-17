from django import forms
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership

User = get_user_model()


class TeamCreateForm(forms.ModelForm):

    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="انتخاب هم‌تیمی‌ها"
    )

    class Meta:
        model = Team
        fields = ['name']

    def __init__(self, *args, **kwargs):
        # -----------------------------
        # گرفتن کاربر لاگین کرده از view
        # اگر ارسال نشود None می‌ماند (برای جلوگیری از crash)
        # -----------------------------
        self.request_user = kwargs.pop('request_user', None)

        super().__init__(*args, **kwargs)

        # -----------------------------
        # گرفتن لیست تمام userهایی که قبلاً عضو تیم شده‌اند
        # (برای جلوگیری از عضویت چندباره)
        # -----------------------------
        used_user_ids = TeamMembership.objects.values_list(
            'user_id',
            flat=True
        )

        # -----------------------------
        # ساخت queryset اولیه کاربران
        # -----------------------------
        qs = User.objects.exclude(
            id__in=list(used_user_ids)
        )

        # -----------------------------
        # حذف کاربر فعلی (کاپیتان نباید در لیست اعضا باشد)
        # -----------------------------
        if self.request_user:
            qs = qs.exclude(id=self.request_user.id)

        # -----------------------------
        # اعمال queryset نهایی به فیلد members
        # -----------------------------
        self.fields['members'].queryset = qs

    def clean_members(self):
        # -----------------------------
        # اعتبارسنجی تعداد اعضا
        # باید حداقل ۲ نفر انتخاب شود
        # -----------------------------
        members = self.cleaned_data.get('members')

        if members.count() < 2:
            raise forms.ValidationError(
                "حداقل ۲ هم‌تیمی انتخاب کنید."
            )

        # -----------------------------
        # امنیت اضافه:
        # جلوگیری از ارسال دستی userهای نامعتبر (tampering)
        # -----------------------------
        if self.request_user in members:
            raise forms.ValidationError(
                "کاپیتان نمی‌تواند در لیست اعضا باشد."
            )

        return members

    def clean_name(self):
        # -----------------------------
        # جلوگیری از ساخت تیم با نام تکراری
        # -----------------------------
        name = self.cleaned_data.get('name')

        if Team.objects.filter(name=name).exists():
            raise forms.ValidationError(
                "نام تیم تکراری است."
            )

        return name