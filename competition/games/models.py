from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام تیم")
    # کاپیتان همان کاربری است که تیم را ساخته
    captain = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='captained_teams',
        verbose_name="کاپیتان"
    )
    total_score = models.IntegerField(default=0, verbose_name="امتیاز کلی تیم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def __str__(self):
        return self.name

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


class Match(models.Model):

    team1 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_matches',
        verbose_name='تیم اول'
    )

    team2 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_matches',
        verbose_name='تیم دوم'
    )

    score_team1 = models.IntegerField(
        default=0,
        verbose_name='امتیاز تیم اول'
    )

    score_team2 = models.IntegerField(
        default=0,
        verbose_name='امتیاز تیم دوم'
    )

    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_matches',
        verbose_name='برنده'
    )

    played_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ مسابقه'
    )

    def clean(self):

        if self.team1 == self.team2:
            raise ValidationError(
                "یک تیم نمی‌تواند با خودش مسابقه بدهد."
            )
        
    def save(self, *args, **kwargs):

        if self.score_team1 > self.score_team2:
            self.winner = self.team1

        elif self.score_team2 > self.score_team1:
            self.winner = self.team2

        else:
            self.winner = None

        super().save(*args, **kwargs)    
    
    
    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name}"
    