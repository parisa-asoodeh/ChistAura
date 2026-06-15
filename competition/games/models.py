from django.db import models
from django.core.exceptions import ValidationError
from teams.models import Team


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
