from django.db import transaction

from competitions.services import TournamentService
from competitions.round_service import RoundService
from competitions.pairing_service import SwissPairingService
from competitions.match_creation_service import MatchCreationService
from competitions.round_question_service import RoundQuestionService
from competitions.status_service import TournamentStatusService


class TournamentExecutionService:

    # =========================================================
    # 1. شروع Tournament و ایجاد Round اول
    # =========================================================

    @staticmethod
    @transaction.atomic
    def start_tournament(
        tournament,
        subject,
    ):

        tournament = TournamentService.start_tournament(
            tournament,
        )

        return RoundService.create_round(
            tournament=tournament,
            subject=subject,
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
    # 3. پایان Round
    # =========================================================

    @staticmethod
    @transaction.atomic
    def finish_round(round_obj):

        return RoundService.finish_round(
            round_obj,
        )

    # =========================================================
    # 4. ایجاد Round بعدی
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
    # 5. نهایی کردن Tournament
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