from django.core.exceptions import ValidationError
from .models import Team, TeamMembership
from django.db import transaction
from competitions.models import TournamentTeam


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
    
class TeamMemberService:
    
    @staticmethod
    def add_member(*, team, user):

        if team.members.filter(user=user).exists():
            raise ValidationError(
                "این کاربر قبلاً عضو تیم است."
            )
        if TeamMembership.objects.filter(
            user=user
        ).exists():
            raise ValidationError(
                "این کاربر قبلاً عضو تیم دیگری است."
            )

        active_team = TournamentTeam.objects.filter(
            team=team,
            tournament__status='active'
        ).exists()

        if active_team:
            raise ValidationError(
                "در زمان برگزاری لیگ امکان تغییر اعضای تیم وجود ندارد."
            )

        TeamMembership.objects.create(
            team=team,
            user=user
        )


    @staticmethod
    def remove_member(*, team, user):

        if team.captain == user:
            raise ValidationError(
                "کاپیتان قابل حذف نیست."
            )

        active_team = TournamentTeam.objects.filter(
            team=team,
            tournament__status='active'
        ).exists()

        if active_team:
            raise ValidationError(
                "در زمان برگزاری لیگ امکان تغییر اعضای تیم وجود ندارد."
            )

        membership = TeamMembership.objects.filter(
            team=team,
            user=user
        ).first()

        if not membership:
            raise ValidationError(
                "این کاربر عضو این تیم نیست."
            )

        membership.delete()