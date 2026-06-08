from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import TeamCreateForm
from .models import Team, TeamMembership
from django.shortcuts import get_object_or_404

@login_required
def create_team(request):

    # ==========================
    # تغییر شماره 1
    # اگر کاربر قبلاً عضو یک تیم باشد
    # اجازه ساخت تیم جدید ندارد
    # ==========================
    if TeamMembership.objects.filter(user=request.user).exists():
        return render(
            request,
            'games/error.html',
            {
                'message': 'شما قبلاً عضو یک تیم شده‌اید.'
            }
        )

    if request.method == 'POST':

        form = TeamCreateForm(request.POST)

        # ==========================
        # تغییر شماره 2
        # جلوگیری از نمایش اعضای دارای تیم
        # هنگام ارسال فرم نیز دوباره اعمال می‌شود
        # ==========================
        used_users = TeamMembership.objects.values_list(
            'user_id',
            flat=True
        )

        form.fields['members'].queryset = (
            form.fields['members']
            .queryset
            .exclude(id=request.user.id)
            .exclude(id__in=used_users)
        )

        if form.is_valid():

            # ایجاد تیم
            team = form.save(commit=False)
            team.captain = request.user
            team.save()

            # ثبت کاپیتان به عنوان عضو تیم
            TeamMembership.objects.create(
                team=team,
                user=request.user
            )

            # ثبت دو عضو انتخاب‌شده
            for member in form.cleaned_data['members']:
                TeamMembership.objects.create(
                    team=team,
                    user=member
                )

            return redirect('home')

    else:

        form = TeamCreateForm()

        # ==========================
        # تغییر شماره 3
        # کاپیتان خودش را نبیند
        # اعضای تیم‌های دیگر نیز دیده نشوند
        # ==========================
        used_users = TeamMembership.objects.values_list(
            'user_id',
            flat=True
        )

        form.fields['members'].queryset = (
            form.fields['members']
            .queryset
            .exclude(id=request.user.id)
            .exclude(id__in=used_users)
        )

    return render(
        request,
        'games/create_team.html',
        {
            'form': form
        }
    )

def team_list(request):
    teams = Team.objects.all().order_by('-total_score')

    return render(
        request,
        'games/team_list.html',
        {
            'teams': teams
        }
    )


def team_detail(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    members = TeamMembership.objects.filter(
        team=team
    )

    return render(
        request,
        'games/team_detail.html',
        {
            'team': team,
            'members': members
        }
    )