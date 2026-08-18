from django.db import transaction
from django.core.exceptions import ValidationError

from competitions.services import TournamentService
from competitions.round_service import RoundService
from competitions.pairing_service import SwissPairingService
from competitions.match_creation_service import MatchCreationService
from competitions.round_question_service import RoundQuestionService
from competitions.status_service import TournamentStatusService
from games.timeout_service import MatchTimeoutService


class TournamentExecutionService:

    # =========================================================
    # 1. شروع Tournament و ایجاد Round اول
    # =========================================================

    @staticmethod
    @transaction.atomic
    def start_tournament(tournament):

        tournament = TournamentService.start_tournament(
            tournament,
        )

        first_round = (
            tournament.rounds
            .filter(number=1)
            .first()
        )

        if not first_round:
            raise ValidationError(
                "Round اول برای این Tournament تنظیم نشده است."
            )

        # Round اول ابتدا باید آماده شود،
        # چون سرویس‌های Question / Pairing / Match
        # فقط Round زمان‌بندی‌شده را می‌پذیرند.
        TournamentExecutionService.prepare_round(
            first_round,
        )

        # شروع Tournament = شروع Round اول
        return RoundService.start_round(
            first_round,
        )

    # =========================================================
    # 2. آماده‌سازی Round
    #
    # Round
    #   ↓
    # Questions
    #   ↓
    # Pairings / Bye
    #   ↓
    # Matches
    #   ↓
    # GameSessions
    # =========================================================

    @staticmethod
    @transaction.atomic
    def prepare_round(round_obj):

        round_questions = (
            RoundQuestionService.assign_questions(
                round_obj,
            )
        )

        pairings = (
            SwissPairingService.create_pairings(
                round_obj,
            )
        )

        matches = []

        for pairing in pairings:

            match = (
                MatchCreationService
                .create_match_from_pairing(
                    pairing,
                )
            )

            matches.append(match)

        return {
            "questions": round_questions,
            "pairings": pairings,
            "matches": matches,
        }

    # =========================================================
    # 3. انقضای Round و تعیین‌تکلیف Matchها
    # =========================================================

    @staticmethod
    @transaction.atomic
    def expire_round(round_obj):

        MatchTimeoutService.handle_expired_round(
            round_obj,
        )

        return TournamentExecutionService.finish_round(
            round_obj,
        )

    # =========================================================
    # 4. پایان Round
    # =========================================================

    @staticmethod
    @transaction.atomic
    def finish_round(round_obj):

        finished_round = RoundService.finish_round(
            round_obj,
        )

        tournament = finished_round.tournament

        # ---------------------------------------------------------
        # اگر هنوز Round دیگری باقی مانده است،
        # Round بعدی را ایجاد و آماده می‌کنیم.
        # ---------------------------------------------------------

        if finished_round.number < tournament.total_rounds:

            next_round = (
                tournament.rounds
                .filter(
                    number=finished_round.number + 1,
                )
                .first()
            )

            if next_round:
                TournamentExecutionService.prepare_round(
                    next_round,
                )

                RoundService.start_round(
                    next_round,
                )

        # ---------------------------------------------------------
        # اگر این آخرین Round بود،
        # Tournament را نهایی می‌کنیم.
        # ---------------------------------------------------------

        else:

            TournamentStatusService.refresh_tournament(
                tournament,
            )

        return finished_round

    # =========================================================
    # 5. پایان Round در صورت آماده بودن
    # =========================================================

    @staticmethod
    @transaction.atomic
    def finish_round_if_ready(round_obj):

        unfinished_matches = (
            round_obj.matches
            .filter(
                status__in=[
                    "pending",
                    "active",
                ],
            )
            .exists()
        )

        if unfinished_matches:
            return round_obj

        return TournamentExecutionService.finish_round(
            round_obj
        )

    # =========================================================
    # 6. ایجاد Round بعدی
    # =========================================================

    @staticmethod
    @transaction.atomic
    def create_next_round(
        tournament,
        subject,
    ):

        return RoundService.create_round(
            tournament=tournament,
            subject=subject,
        )

    # =========================================================
    # 7. نهایی کردن Tournament
    #
    # Ranking
    #   ↓
    # Champion
    #   ↓
    # Tournament = finished
    # =========================================================

    @staticmethod
    @transaction.atomic
    def finalize_tournament(
        tournament,
    ):

        return TournamentStatusService.refresh_tournament(
            tournament,
        )