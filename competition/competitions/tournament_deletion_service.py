from django.db import transaction

from .models import (
    Tournament,
    TournamentTeam,
    Round,
    RoundQuestion,
    Pairing,
    RoundBye,
)

from games.models import Match
from games.quiz_models import QuizMatchQuestion


class TournamentDeletionService:

    @staticmethod
    @transaction.atomic
    def delete_tournament(tournament: Tournament):

        # تمام Roundهای این Tournament
        rounds = Round.objects.filter(
            tournament=tournament
        )

        # ابتدا QuizMatchQuestionها را حذف می‌کنیم
        # چون به RoundQuestion با PROTECT متصل هستند.
        QuizMatchQuestion.objects.filter(
            match__round__in=rounds
        ).delete()

        # سپس Matchها را حذف می‌کنیم.
        # GameSession و MatchPlayerScore و QuizAnswer
        # طبق CASCADE همراه آن‌ها حذف می‌شوند.
        Match.objects.filter(
            round__in=rounds
        ).delete()

        # حالا Pairingها را حذف می‌کنیم.
        # چون Match دیگر به آن‌ها متصل نیست.
        Pairing.objects.filter(
            round__in=rounds
        ).delete()

        # RoundQuestionها را حذف می‌کنیم.
        # QuizMatchQuestionهای وابسته قبلاً حذف شده‌اند.
        RoundQuestion.objects.filter(
            round__in=rounds
        ).delete()

        # Byeها را حذف می‌کنیم.
        RoundBye.objects.filter(
            round__in=rounds
        ).delete()

        # Roundها را حذف می‌کنیم.
        Round.objects.filter(
            pk__in=rounds.values("pk")
        ).delete()

        # اعضای Tournament را حذف می‌کنیم.
        TournamentTeam.objects.filter(
            tournament=tournament
        ).delete()

        # در نهایت خود Tournament حذف می‌شود.
        tournament.delete()