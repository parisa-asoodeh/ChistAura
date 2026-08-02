from django.db import models
from .models import Match

class QuizCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="دسته‌بندی"
    )

    def __str__(self):
        return self.name


class QuizQuestion(models.Model):

    DIFFICULTY_CHOICES = [
        ("easy", "آسان"),
        ("medium", "متوسط"),
        ("hard", "سخت"),
    ]

    category = models.ForeignKey(
        QuizCategory,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="دسته‌بندی",
    )

    question = models.TextField(
        verbose_name="متن سؤال"
    )

    option_a = models.CharField(
        max_length=255
    )

    option_b = models.CharField(
        max_length=255
    )

    option_c = models.CharField(
        max_length=255
    )

    option_d = models.CharField(
        max_length=255
    )

    correct_answer = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
    )

    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default="easy",
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.question
    


class QuizMatchQuestion(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="quiz_questions",
        verbose_name="مسابقه"
    )

    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name="سؤال"
    )

    order = models.PositiveIntegerField(
        verbose_name="ترتیب سؤال"
    )


    class Meta:

        ordering = [
            "order"
        ]

        unique_together = (
            "match",
            "question",
        )


    def __str__(self):

        return (
            f"{self.match.id} - "
            f"{self.question.question[:30]}"
        )


class QuizAnswer(models.Model):

    session = models.ForeignKey(
        "GameSession",
        on_delete=models.CASCADE,
        related_name="quiz_answers",
        verbose_name="جلسه بازی",
    )

    match_question = models.ForeignKey(
        QuizMatchQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="سؤال مسابقه",
    )

    selected_answer = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
        verbose_name="پاسخ انتخاب‌شده",
    )

    is_correct = models.BooleanField(
        default=False,
        verbose_name="درست است؟",
    )

    answered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان پاسخ",
    )

    class Meta:

        unique_together = (
            "session",
            "match_question",
        )

    def save(self, *args, **kwargs):

        self.is_correct = (
            self.selected_answer ==
            self.match_question.question.correct_answer
        )

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.session.user.username} - "
            f"{self.match_question.order}"
        )