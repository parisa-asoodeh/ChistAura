from django.db import transaction
from django.core.exceptions import ValidationError

from .models import TournamentTeam
from games.models import Match
from django.utils import timezone


class TournamentService:

    @staticmethod
    def add_team(tournament, team):

        if tournament.status != 'draft':
            raise ValidationError(
                "بعد از شروع لیگ امکان اضافه کردن تیم وجود ندارد."
            )


        return TournamentTeam.objects.create(
            tournament=tournament,
            team=team
        )


    @staticmethod
    def remove_team(tournament, team):

        if tournament.status != 'draft':
            raise ValidationError(
                "بعد از شروع لیگ امکان حذف تیم وجود ندارد."
            )


        TournamentTeam.objects.filter(
            tournament=tournament,
            team=team
        ).delete()

    @staticmethod
    @transaction.atomic
    def start_tournament(tournament):

        # -----------------------------
        # 1. بررسی وضعیت لیگ
        # -----------------------------
        if tournament.status != 'draft':
            raise ValidationError(
                "این لیگ قبلاً شروع شده یا به پایان رسیده است."
            )


        # -----------------------------
        # 2. گرفتن تیم‌های لیگ
        # -----------------------------
        teams = list(
            TournamentTeam.objects.filter(
                tournament=tournament
            ).select_related('team')
        )


        # -----------------------------
        # 3. حداقل تعداد تیم
        # -----------------------------
        if len(teams) < 2:
            raise ValidationError(
                "برای شروع لیگ حداقل ۲ تیم نیاز است."
            )


        # -----------------------------
        # 4. جلوگیری از تولید دوباره مسابقات
        # -----------------------------
        if Match.objects.filter(
            tournament=tournament
        ).exists():
            raise ValidationError(
                "برای این لیگ قبلاً مسابقه ساخته شده است."
            )


        # -----------------------------
        # 5. تولید مسابقات Round Robin
        # -----------------------------
        matches = []

        for i in range(len(teams)):

            for j in range(i + 1, len(teams)):

                matches.append(
                    Match(
                        tournament=tournament,
                        team1=teams[i].team,
                        team2=teams[j].team
                    )
                )


        # -----------------------------
        # 6. ذخیره یکجای مسابقات
        # -----------------------------
        from games.session_creation_service import (
            GameSessionCreationService,
        )

        for match in matches:

            match.save()

            GameSessionCreationService.create_sessions(
                match
            )

        # -----------------------------
        # 7. فعال کردن لیگ
        # -----------------------------
        tournament.status = 'active'
        tournament.started_at = timezone.now()

        tournament.save(
            update_fields=[
                'status',
                'started_at'
            ]
        )


        return tournament