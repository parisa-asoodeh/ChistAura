from django.core.exceptions import ValidationError
from .models import Team, TeamMembership
from django.db import transaction


class TeamService:

    @staticmethod
    @transaction.atomic
    def create_team(*, captain, team_name, members):

        # -------------------------
        # 1. RULE: unique team name
        # -------------------------
        if Team.objects.filter(name=team_name).exists():
            raise ValidationError("نام تیم تکراری است")

        # -------------------------
        # 2. RULE: captain already in team?
        # -------------------------
        if Team.objects.filter(captain=captain).exists():
            raise ValidationError("این کاربر قبلاً کاپیتان یک تیم است")

        # -------------------------
        # 3. RULE: prevent duplicate members
        # -------------------------
        members = set(members)

        # captain should not be in members list
        members.discard(captain)

        # -------------------------
        # 4. RULE: user cannot already be in another team
        # -------------------------
        existing_users = TeamMembership.objects.filter(
            user__in=members
        ).values_list('user_id', flat=True)

        if existing_users:
            raise ValidationError("بعضی از اعضا قبلاً در تیم دیگری هستند")

        # -------------------------
        # CREATE TEAM
        # -------------------------
        if len(members) < 2:
            raise ValidationError(
                "حداقل ۲ عضو باید انتخاب شود."
            )
        team = Team.objects.create(
            name=team_name,
            captain=captain
        )

        # captain membership
        TeamMembership.objects.create(
            team=team,
            user=captain
        )

        # members
        TeamMembership.objects.bulk_create([
            TeamMembership(team=team, user=user)
            for user in members
        ])

        return team