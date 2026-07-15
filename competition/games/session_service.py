from django.db import transaction
from django.core.exceptions import ValidationError
from teams.models import TeamMembership
from django.utils import timezone

from .models import MatchPlayerScore

from .game_types.registry import (
    get_game_type,
)
from .scoring import (
    MatchScoringService,
)


class GameSessionService:

    @staticmethod
    @transaction.atomic
    def complete_session(
        session,
        raw_score,
        completion_time
    ):

        if session.status == 'completed':
            raise ValidationError(
                "این Session قبلاً تکمیل شده است."
            )
        

        existing_score = MatchPlayerScore.objects.filter(
            match=session.match,
            user=session.user,
        ).exists()

        if existing_score:
            raise ValidationError(
                "امتیاز این بازیکن قبلاً ثبت شده است."
            )
        
        if not session.match.tournament.game_type:
            raise ValidationError(
                "نوع بازی برای این لیگ تعریف نشده است."
            )
        game_type = get_game_type(
            session.match.tournament.game_type
        )

        official_score = (
            game_type.calculate_score(
                raw_score,
                completion_time
            )
        )

        membership = TeamMembership.objects.filter(
            user=session.user,
            team__in=[
                session.match.team1,
                session.match.team2,
            ]
        ).first()

        if not membership:
            raise ValidationError(
                "بازیکن عضو هیچ‌یک از تیم‌های این مسابقه نیست."
            )
        team = membership.team


        MatchPlayerScore.objects.create(
            match=session.match,
            user=session.user,
            team=team,
            score=official_score,
            completion_time=completion_time,
        )


        session.raw_score = raw_score
        session.completion_time = completion_time

        session.status = 'completed'
        session.finished_at = timezone.now()

        session.save(
            update_fields=[
                'raw_score',
                'completion_time',
                'status',
                'finished_at',
            ]
        )
        if MatchScoringService.can_finalize(
            session.match
        ):
            MatchScoringService.finalize_match(
                session.match
            )
        return session