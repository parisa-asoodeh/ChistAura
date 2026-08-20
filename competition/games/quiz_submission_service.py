from django.db import transaction

from .quiz_answer_service import (
    QuizAnswerService,
)

from .quiz_correction_service import (
    QuizCorrectionService,
)

from .quiz_play_service import (
    QuizPlayService,
)

from .session_time_service import (
    SessionTimeService,
)

from .session_service import (
    GameSessionService,
)

from django.db import transaction
from django.core.exceptions import ValidationError


class QuizSubmissionService:

    @staticmethod
    @transaction.atomic
    def submit(
        session,
        form,
    ):

        if session.match.round.status != "active":
            raise ValidationError(
                "این راند هنوز فعال نشده است."
            )

        questions = (
            QuizPlayService.build(session)[
                "questions"
            ]
        )

        # 1) ذخیره پاسخ‌ها
        QuizAnswerService.save_answers(
            session=session,
            form=form,
            questions=questions,
        )

        # 2) محاسبه Raw Score
        raw_score = (
            QuizCorrectionService.calculate_raw_score(
                session
            )
        )

        # 3) محاسبه Completion Time
        completion_time = (
            SessionTimeService.calculate_completion_time(
                session
            )
        )

        # 4) Complete Session
        completed_session = (
            GameSessionService.complete_session(
                session=session,
                raw_score=raw_score,
                completion_time=completion_time,
            )
        )

        # 5) بررسی پایان Round
        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )

        TournamentExecutionService.finish_round_if_ready(
            completed_session.match.round
        )

        return completed_session