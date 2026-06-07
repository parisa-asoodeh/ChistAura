from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TeamCreateForm
from .models import Team, TeamMembership

@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            # ۱. ایجاد خودِ تیم
            team = form.save(commit=False)
            team.captain = request.user
            team.save()

            # ۲. اضافه کردن کاپیتان به عنوان اولین عضو در TeamMembership
            TeamMembership.objects.create(team=team, user=request.user)

            # ۳. اضافه کردن ۲ عضو انتخابی
            for member in form.cleaned_data['members']:
                TeamMembership.objects.create(team=team, user=member)

            return redirect('home') # یا هر صفحه‌ای که دوست دارید
    else:
        form = TeamCreateForm()
    
    return render(request, 'games/create_team.html', {'form': form})
