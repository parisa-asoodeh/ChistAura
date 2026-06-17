from django.db import models
from teams.models import Team
from django.core.exceptions import ValidationError


class Tournament(models.Model):

    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('active', 'در حال برگزاری'),
        ('finished', 'تمام شده'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="نام لیگ"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="وضعیت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ شروع"
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان"
    )

    champion = models.ForeignKey(
    'teams.Team',
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='won_tournaments',
    verbose_name='قهرمان'
    )

    def __str__(self):
        return self.name



class TournamentTeam(models.Model):

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name="لیگ"
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='tournaments',
        verbose_name="تیم"
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )


    class Meta:
        unique_together = (
            'tournament',
            'team',
        )

    def clean(self):
        if self.tournament.status != 'draft':
            raise ValidationError(
                "بعد از شروع لیگ امکان تغییر تیم‌ها وجود ندارد."
            )
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name}"