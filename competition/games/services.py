from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Match



class MatchService:

    @staticmethod
    @transaction.atomic
    def set_result(match, score_team1, score_team2):

        if score_team1 < 0 or score_team2 < 0:
            raise ValidationError(
                "امتیاز نمی‌تواند منفی باشد."
            )

        match.score_team1 = score_team1
        match.score_team2 = score_team2
        match.played_at = timezone.now()

        if score_team1 > score_team2:
            match.winner = match.team1

        elif score_team2 > score_team1:
            match.winner = match.team2

        else:
            match.winner = None

        match.save()

        return match