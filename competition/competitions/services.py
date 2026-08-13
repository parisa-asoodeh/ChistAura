from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import TournamentTeam


class TournamentService:

    # =========================================================
    # 1. اضافه کردن تیم به Tournament
    # =========================================================
    #
    # این متد فقط زمانی اجازه اضافه کردن تیم را می‌دهد
    # که Tournament هنوز در وضعیت draft باشد.
    #
    # مسئولیت این متد:
    #   Tournament → اضافه کردن Team
    #
    # این متد مسئول ساخت Round، Pairing یا Match نیست.
    #
    @staticmethod
    def add_team(tournament, team):

        # بعد از شروع Tournament دیگر اجازه تغییر تیم‌ها وجود ندارد.
        if tournament.status != "draft":
            raise ValidationError(
                "بعد از شروع لیگ امکان اضافه کردن تیم وجود ندارد."
            )

        # ثبت رابطه Tournament و Team
        return TournamentTeam.objects.create(
            tournament=tournament,
            team=team,
        )


    # =========================================================
    # 2. حذف کردن تیم از Tournament
    # =========================================================
    #
    # این متد فقط زمانی اجازه حذف تیم را می‌دهد
    # که Tournament هنوز در وضعیت draft باشد.
    #
    # مسئولیت این متد:
    #   Tournament → حذف Team
    #
    @staticmethod
    def remove_team(tournament, team):

        # بعد از شروع Tournament دیگر اجازه حذف تیم وجود ندارد.
        if tournament.status != "draft":
            raise ValidationError(
                "بعد از شروع لیگ امکان حذف تیم وجود ندارد."
            )

        # حذف رابطه Tournament و Team
        TournamentTeam.objects.filter(
            tournament=tournament,
            team=team,
        ).delete()


    # =========================================================
    # 3. شروع Tournament
    # =========================================================
    #
    # این متد فقط Tournament را از حالت draft
    # به حالت active منتقل می‌کند.
    #
    # نکته بسیار مهم:
    #
    # این متد دیگر:
    #   ❌ Round نمی‌سازد
    #   ❌ سؤال انتخاب نمی‌کند
    #   ❌ Pairing نمی‌سازد
    #   ❌ Bye ایجاد نمی‌کند
    #   ❌ Match نمی‌سازد
    #   ❌ GameSession نمی‌سازد
    #
    # هرکدام از این مسئولیت‌ها Service مخصوص خودشان را دارند.
    #
    # جریان بعد از این متد توسط Serviceهای دیگر ادامه پیدا می‌کند:
    #
    #   TournamentService.start_tournament()
    #          ↓
    #   RoundService.create_round()
    #          ↓
    #   RoundQuestionService.assign_questions()
    #          ↓
    #   SwissPairingService.create_pairings()
    #          ↓
    #   MatchCreationService.create_match_from_pairing()
    #
    @staticmethod
    @transaction.atomic
    def start_tournament(tournament):

        # -----------------------------------------------------
        # بررسی وضعیت Tournament
        # -----------------------------------------------------
        #
        # فقط Tournament در حالت draft می‌تواند شروع شود.
        #
        if tournament.status != "draft":
            raise ValidationError(
                "این Tournament قبلاً شروع شده یا به پایان رسیده است."
            )


        # -----------------------------------------------------
        # بررسی حداقل تعداد تیم
        # -----------------------------------------------------
        #
        # برای شروع مسابقات حداقل دو تیم لازم است.
        #
        team_count = TournamentTeam.objects.filter(
            tournament=tournament,
        ).count()

        if team_count < 2:
            raise ValidationError(
                "برای شروع Tournament حداقل ۲ تیم نیاز است."
            )


        # -----------------------------------------------------
        # تغییر وضعیت Tournament
        # -----------------------------------------------------
        #
        # Tournament از draft به active منتقل می‌شود.
        #
        tournament.status = "active"

        # زمان شروع Tournament ثبت می‌شود.
        tournament.started_at = timezone.now()


        # -----------------------------------------------------
        # ذخیره تغییرات
        # -----------------------------------------------------
        #
        # فقط فیلدهایی که تغییر کرده‌اند ذخیره می‌شوند.
        #
        tournament.save(
            update_fields=[
                "status",
                "started_at",
            ]
        )


        # -----------------------------------------------------
        # پایان عملیات
        # -----------------------------------------------------
        #
        # خود Tournament فعال‌شده را برمی‌گردانیم.
        #
        return tournament