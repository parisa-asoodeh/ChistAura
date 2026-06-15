from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام تیم")

    captain = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='captained_teams',
        verbose_name="کاپیتان"
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    def __str__(self):
        return self.name

    # -----------------------------
    # RELATION HELPERS (CORE LOGIC)
    # -----------------------------

    def matches(self):
        """
        همه مسابقات تیم (چه تیم اول چه تیم دوم)
        """
        return self.home_matches.all() | self.away_matches.all()

    def get_wins(self):
        return self.won_matches.count()

    def get_draws(self):
        return self.matches().filter(winner__isnull=True).count()

    def get_played(self):
        return self.matches().count()

    def get_losses(self):
        return self.get_played() - self.get_wins() - self.get_draws()

    def get_points(self):
        return (self.get_wins() * 3) + self.get_draws()
    
    

class TeamMembership(models.Model):
    # ارتباط بین تیم و کاربر
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        related_name='members',
        verbose_name="تیم"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name="عضو"
    )
    individual_score = models.IntegerField(default=0, verbose_name="امتیاز فردی")

    class Meta:
        # جلوگیری از اینکه یک نفر در یک تیم دو بار عضو شود
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} در {self.team.name}"
