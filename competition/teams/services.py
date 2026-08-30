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
        if len(members) != 2:
            raise ValidationError(
                "تعداد اعضای تیم باید دقیقاً ۳ نفر باشد."
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

        # RULE: team must have exactly 3 members
        if team.members.count() >= 3:
            raise ValidationError(
                "تعداد اعضای تیم نمی‌تواند بیشتر از ۳ نفر باشد."
            )

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

        # RULE: team must remain exactly 3 members
        if team.members.count() <= 3:
            raise ValidationError(
                "تعداد اعضای تیم باید دقیقاً ۳ نفر باشد. "
                "برای تغییر عضو، از گزینه تعویض عضو استفاده کنید."
            )

        membership.delete()


    @staticmethod
    @transaction.atomic
    def replace_member(*, team, old_user, new_user):

        # RULE: captain cannot be replaced
        if team.captain == old_user:
            raise ValidationError(
                "کاپیتان قابل تعویض نیست."
            )

        # RULE: team must have exactly 3 members
        if team.members.count() != 3:
            raise ValidationError(
                "تعداد اعضای تیم باید دقیقاً ۳ نفر باشد."
            )

        # RULE: team cannot be modified during active tournament
        active_team = TournamentTeam.objects.filter(
            team=team,
            tournament__status='active'
        ).exists()

        if active_team:
            raise ValidationError(
                "در زمان برگزاری لیگ امکان تغییر اعضای تیم وجود ندارد."
            )

        # RULE: old user must actually be a member of this team
        old_membership = TeamMembership.objects.filter(
            team=team,
            user=old_user
        ).first()

        if not old_membership:
            raise ValidationError(
                "عضو موردنظر عضو این تیم نیست."
            )

        # RULE: new user must not already be a member of this team
        if team.members.filter(
            user=new_user
        ).exists():
            raise ValidationError(
                "کاربر جدید قبلاً عضو این تیم است."
            )

        # RULE: new user must not belong to another team
        if TeamMembership.objects.filter(
            user=new_user
        ).exists():
            raise ValidationError(
                "این کاربر قبلاً عضو تیم دیگری است."
            )

        # Replace the member atomically
        old_membership.delete()

        TeamMembership.objects.create(
            team=team,
            user=new_user
        )

