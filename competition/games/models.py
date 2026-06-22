from django.db import models
from django.core.exceptions import ValidationError
from teams.models import Team
from competitions.models import Tournament
from django.utils import timezone
from django.conf import settings



class Match(models.Model):

    tournament = models.ForeignKey(
        'competitions.Tournament',
        on_delete=models.CASCADE,
        related_name='matches',
        verbose_name='لیگ',
    )

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
        null=True,
        blank=True,
        verbose_name='امتیاز تیم اول'
    )

    score_team2 = models.IntegerField(
        null=True,
        blank=True,
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

    report = models.TextField(
    blank=True,
    verbose_name="گزارش مسابقه"
    )
    
    def clean(self):

        if self.team1 == self.team2:
            raise ValidationError(
                "یک تیم نمی‌تواند با خودش مسابقه بدهد."
            )
        
    def save(self, *args, **kwargs):

        self.full_clean()

        if self.score_team1 is None or self.score_team2 is None:
            self.winner = None

        elif self.score_team1 > self.score_team2:
            self.winner = self.team1

        elif self.score_team2 > self.score_team1:
            self.winner = self.team2

        else:
            self.winner = None

        super().save(*args, **kwargs)
        
        unfinished_matches = self.tournament.matches.filter(
            score_team1__isnull=True
        ).exists()

        if (
            not unfinished_matches and
            self.tournament.status == 'active'
        ):
            
            teams = [
                tt.team
                for tt in self.tournament.teams.select_related('team')
            ]
            teams.sort(
                key=lambda team: team.get_points_in_tournament(
                    self.tournament
                ),
                reverse=True
            )
            if teams:
                self.tournament.champion = teams[0]


            self.tournament.status = 'finished'
            self.tournament.finished_at = timezone.now()

            self.tournament.save(
                update_fields=[
                    'status',
                    'finished_at',
                    'champion'
                ]
            )


class MatchPlayerScore(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='player_scores',
        verbose_name='مسابقه'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='match_scores',
        verbose_name='بازیکن'
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='player_scores',
        verbose_name='تیم'
    )

    score = models.IntegerField(
        default=0,
        verbose_name='امتیاز'
    )

    class Meta:

        unique_together = (
            'match',
            'user',
        )

        verbose_name = 'امتیاز بازیکن'
        verbose_name_plural = 'امتیازات بازیکنان'

    def clean(self):

        from teams.models import TeamMembership

        if self.team not in (
            self.match.team1,
            self.match.team2
        ):
            raise ValidationError(
                "تیم انتخاب شده در این مسابقه حضور ندارد."
            )

        is_member = TeamMembership.objects.filter(
            team=self.team,
            user=self.user
        ).exists()

        if not is_member:
            raise ValidationError(
                "این بازیکن عضو تیم انتخاب شده نیست."
            )
        

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)



    def __str__(self):

        return (
            f"{self.user.username} | "
            f"{self.match.id} | "
            f"{self.score}"
        )