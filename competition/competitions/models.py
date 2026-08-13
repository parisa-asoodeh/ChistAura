from django.db import models
from teams.models import Team
from django.core.exceptions import ValidationError


class GameType(models.Model):

    key = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name='کلید فنی'
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='نوع بازی'
    )

    def __str__(self):
        return self.name
    

class Subject(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    name = models.CharField(
        max_length=100,
    )

    slug = models.SlugField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["subject", "name"]
        unique_together = (
            "subject",
            "name",
        )

    def __str__(self):
        return f"{self.subject.name} - {self.name}"
        

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

    total_rounds = models.PositiveIntegerField(
        verbose_name="تعداد کل دورها"
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

    game_type = models.ForeignKey(
    'GameType',
    on_delete=models.PROTECT,
    related_name='tournaments',
    verbose_name='نوع بازی'
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


class Round(models.Model):

    STATUS_CHOICES = [
        ('scheduled', 'زمان‌بندی شده'),
        ('active', 'در حال برگزاری'),
        ('finished', 'تمام شده'),
    ]

    QUESTION_DIFFICULTY_CHOICES = [
        ('easy', 'آسان'),
        ('medium', 'متوسط'),
        ('hard', 'سخت'),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='rounds',
        verbose_name='مسابقات'
    )

    number = models.PositiveIntegerField(
        verbose_name='شماره دور'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='وضعیت'
    )

    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='زمان شروع'
    )

    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='زمان پایان'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='rounds',
        verbose_name='موضوع'
    )

    question_difficulty = models.CharField(
        max_length=10,
        choices=QUESTION_DIFFICULTY_CHOICES,
        default='easy',
        verbose_name='درجه سختی سوالات'
    )

    question_count = models.PositiveIntegerField(
        default=10,
        verbose_name='تعداد سوالات'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        ordering = ['tournament', 'number']
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'number'],
                name='unique_round_number_per_tournament'
            )
        ]

    def __str__(self):
        return f"{self.tournament.name} - Round {self.number}"



class RoundQuestion(models.Model):

    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='دور'
    )

    question = models.ForeignKey(
        'games.QuizQuestion',
        on_delete=models.PROTECT,
        related_name='round_questions',
        verbose_name='سؤال'
    )

    order = models.PositiveIntegerField(
        verbose_name='ترتیب سؤال'
    )

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['round', 'question'],
                name='unique_question_per_round'
            ),
            models.UniqueConstraint(
                fields=['round', 'order'],
                name='unique_question_order_per_round'
            ),
        ]

    def __str__(self):
        return f"Round {self.round.number} - Question {self.order}"


class Pairing(models.Model):

    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name='pairings',
        verbose_name='دور'
    )

    team1 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='pairings_as_team1',
        verbose_name='تیم اول'
    )

    team2 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='pairings_as_team2',
        verbose_name='تیم دوم'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['round', 'team1'],
                name='unique_team1_pairing_per_round'
            ),
            models.UniqueConstraint(
                fields=['round', 'team2'],
                name='unique_team2_pairing_per_round'
            ),
        ]

    def clean(self):
        if self.team1 == self.team2:
            raise ValidationError(
                "یک تیم نمی‌تواند با خودش Pair شود."
            )

        tournament = self.round.tournament

        if not TournamentTeam.objects.filter(
            tournament=tournament,
            team=self.team1
        ).exists():
            raise ValidationError(
                "تیم اول عضو این Tournament نیست."
            )

        if not TournamentTeam.objects.filter(
            tournament=tournament,
            team=self.team2
        ).exists():
            raise ValidationError(
                "تیم دوم عضو این Tournament نیست."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Round {self.round.number}: "
            f"{self.team1.name} vs {self.team2.name}"
        )


class RoundBye(models.Model):

    round = models.OneToOneField(
        Round,
        on_delete=models.CASCADE,
        related_name='bye',
        verbose_name='دور'
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='round_byes',
        verbose_name='تیم'
    )

    points = models.PositiveIntegerField(
        default=3,
        verbose_name='امتیاز'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['round', 'team'],
                name='unique_bye_team_per_round'
            )
        ]

    def clean(self):
        if not TournamentTeam.objects.filter(
            tournament=self.round.tournament,
            team=self.team
        ).exists():
            raise ValidationError(
                "تیم دریافت‌کننده Bye عضو این Tournament نیست."
            )

        if self.points != 3:
            raise ValidationError(
                "امتیاز Bye باید ۳ باشد."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Round {self.round.number} - "
            f"Bye: {self.team.name}"
        )