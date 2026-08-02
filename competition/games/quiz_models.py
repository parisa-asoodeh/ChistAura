from django.db import models

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