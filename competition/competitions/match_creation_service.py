from django.core.exceptions import ValidationError
from django.db import transaction

from games.models import Match
from games.session_creation_service import (
    GameSessionCreationService,
)
from games.quiz_match_question_service import (
    QuizMatchQuestionService,
)


class MatchCreationService:

    @staticmethod
    @transaction.atomic
    def create_match_from_pairing(pairing):

        round_obj = pairing.round
        tournament = round_obj.tournament

        # -----------------------------
        # 1. بررسی وضعیت Round
        # -----------------------------
        if round_obj.status != "scheduled":
            raise ValidationError(
                "فقط برای Round زمان‌بندی‌شده می‌توان Match ایجاد کرد."
            )

        # -----------------------------
        # 2. بررسی وضعیت Tournament
        # -----------------------------
        if tournament.status != "active":
            raise ValidationError(
                "Tournament باید فعال باشد."
            )

        # -----------------------------
        # 3. جلوگیری از ایجاد Match تکراری
        # -----------------------------
        if hasattr(pairing, "match"):
            raise ValidationError(
                "برای این Pairing قبلاً Match ایجاد شده است."
            )

        # -----------------------------
        # 4. ایجاد Match
        # -----------------------------
        match = Match.objects.create(
            round=round_obj,
            pairing=pairing,
            team1=pairing.team1,
            team2=pairing.team2,
        )

        # -----------------------------
        # 5. اتصال سؤال‌های Round به Match
        # -----------------------------
        if tournament.game_type.key == "quiz":

            QuizMatchQuestionService.create_questions_for_match(
                match=match,
            )

        # -----------------------------
        # 6. ایجاد GameSession برای
        #    اعضای دو تیم
        # -----------------------------
        GameSessionCreationService.create_sessions(
            match
        )

        return match