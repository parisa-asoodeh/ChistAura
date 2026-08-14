from django.db import models
from django.core.exceptions import ValidationError
from teams.models import Team
from competitions.models import Tournament
from django.utils import timezone
from django.conf import settings



class Match(models.Model):

    round = models.ForeignKey(
        'competitions.Round',
        on_delete=models.CASCADE,
        related_name='matches',
        verbose_name='دور',
        null=True,
        blank=True,
    )

    pairing = models.OneToOneField(
        'competitions.Pairing',
        on_delete=models.PROTECT,
        related_name='match',
        null=True,
        blank=True,
        verbose_name='Pairing',
    )

    STATUS_CHOICES = [
        ("pending", "در انتظار"),
        ("active", "در حال بازی"),
        ("completed", "تکمیل شده"),
        ("forfeit", "فورفیت شده"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="وضعیت",
    )

    forfeit_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forfeited_matches",
        verbose_name="تیم حاضر در فورفیت",
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

        if self.pairing_id:
            if (
                self.team1_id != self.pairing.team1_id
                or
                self.team2_id != self.pairing.team2_id
            ):
                raise ValidationError(
                    "تیم‌های Match باید با Pairing یکسان باشند."
                )

            if self.round_id != self.pairing.round_id:
                raise ValidationError(
                    "Round مربوط به Match باید با Pairing یکسان باشد."
                )
            
        
    def save(self, *args, **kwargs):

        self.full_clean()

        if self.status == "forfeit":
            self.winner = self.forfeit_team

        elif self.score_team1 is None or self.score_team2 is None:
            self.winner = None

        elif self.score_team1 > self.score_team2:
            self.winner = self.team1

        elif self.score_team2 > self.score_team1:
            self.winner = self.team2

        else:
            self.winner = None

        super().save(*args, **kwargs)
        
        
    @property
    def is_complete(self):

        return (
            (
                self.score_team1 is not None
                and
                self.score_team2 is not None
            )
            or
            self.status == "forfeit"
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

    completion_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='زمان (ثانیه)'
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
    

class GameSession(models.Model):

    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('started', 'شروع شده'),
        ('completed', 'تکمیل شده'),
        ('abandoned', 'رها شده'),
    ]

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_sessions'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    raw_score = models.IntegerField(
        null=True,
        blank=True
    )

    completion_time = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
    auto_now_add=True
    )


    class Meta:

        unique_together = (
            'match',
            'user',
        )

    def __str__(self):

        return (
            f"{self.user.username}"
            f" - Match {self.match_id}"
        )
    

class GameSessionState(models.Model):

    session = models.OneToOneField(
        GameSession,
        on_delete=models.CASCADE,
        related_name="resume_state",
        verbose_name="جلسه بازی",
    )

    state = models.JSONField(
        default=dict,
        verbose_name="وضعیت بازی",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    def __str__(self):

        return (
            f"Resume State - Session {self.session.id}"
        )
    
from .quiz_models import *