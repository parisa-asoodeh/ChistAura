from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Pairing, RoundBye
from .ranking_service import TournamentRankingService


class SwissPairingService:

    MAX_ATTEMPTS = 20

    @staticmethod
    @transaction.atomic
    def create_pairings(round_obj):

        if round_obj.status != "scheduled":
            raise ValidationError(
                "فقط برای Round زمان‌بندی‌شده می‌توان Pairing ایجاد کرد."
            )

        tournament = round_obj.tournament

        if tournament.status != "active":
            raise ValidationError(
                "Tournament باید فعال باشد."
            )

        if Pairing.objects.filter(
            round=round_obj,
        ).exists():
            raise ValidationError(
                "برای این Round قبلاً Pairing ایجاد شده است."
            )

        if RoundBye.objects.filter(
            round=round_obj,
        ).exists():
            raise ValidationError(
                "برای این Round قبلاً Bye ایجاد شده است."
            )

        ranked_teams = list(
            TournamentRankingService.rank_teams(
                tournament,
            )
        )

        if not ranked_teams:
            raise ValidationError(
                "برای ایجاد Pairing حداقل یک تیم لازم است."
            )

        # ---------------------------------------------------------
        # Bye
        # ---------------------------------------------------------

        teams = ranked_teams.copy()

        if len(teams) % 2 != 0:

            bye_team = teams.pop()

            RoundBye.objects.create(
                round=round_obj,
                team=bye_team,
                points=3,
            )

        # ---------------------------------------------------------
        # سابقه Pairingها
        # ---------------------------------------------------------

        previous_pairings = Pairing.objects.filter(
            round__tournament=tournament,
        ).values_list(
            "team1_id",
            "team2_id",
        )

        previous_pairs = {
            frozenset(
                (team1_id, team2_id)
            )
            for team1_id, team2_id in previous_pairings
        }

        # ---------------------------------------------------------
        # امتیازها را فقط یک بار محاسبه می‌کنیم.
        # ---------------------------------------------------------

        points = {
            team.id: team.get_points_in_tournament(
                tournament,
            )
            for team in teams
        }

        # ---------------------------------------------------------
        # حریف‌های مجاز
        # ---------------------------------------------------------

        allowed = {}

        for team in teams:

            allowed[team.id] = {
                opponent.id
                for opponent in teams
                if (
                    opponent.id != team.id
                    and frozenset(
                        (
                            team.id,
                            opponent.id,
                        )
                    ) not in previous_pairs
                )
            }

        # ---------------------------------------------------------
        # چند ترتیب مختلف، بدون recursion
        # ---------------------------------------------------------

        orders = []

        base = list(teams)

        orders.append(base)
        orders.append(list(reversed(base)))

        # زوج/فرد
        orders.append(
            base[::2] + base[1::2]
        )

        orders.append(
            base[1::2] + base[::2]
        )

        # چرخش محدود لیست
        for shift in range(
            1,
            min(SwissPairingService.MAX_ATTEMPTS, len(base)),
        ):
            orders.append(
                base[shift:] + base[:shift]
            )

        # ---------------------------------------------------------
        # تلاش برای ساخت یک Matching کامل
        # ---------------------------------------------------------

        for order in orders:

            remaining = order.copy()
            result = []

            while remaining:

                # -------------------------------------------------
                # تیمی که کمترین گزینه را دارد انتخاب می‌شود.
                # -------------------------------------------------

                team1_index = min(
                    range(len(remaining)),
                    key=lambda index: (
                        sum(
                            1
                            for opponent_id
                            in allowed[remaining[index].id]
                            if any(
                                team.id == opponent_id
                                for team in remaining
                            )
                        ),
                        -points[remaining[index].id],
                        remaining[index].id,
                    ),
                )

                team1 = remaining.pop(team1_index)

                candidates = [
                    team
                    for team in remaining
                    if team.id in allowed[team1.id]
                ]

                if not candidates:
                    result = None
                    break

                # -------------------------------------------------
                # اول حریف با نزدیک‌ترین امتیاز انتخاب می‌شود.
                # -------------------------------------------------

                candidates.sort(
                    key=lambda team: (
                        abs(
                            points[team1.id]
                            - points[team.id]
                        ),
                        team.id,
                    )
                )

                # -------------------------------------------------
                # چند حریف اول را بررسی می‌کنیم.
                # ارزان است و از بن‌بست‌های ساده جلوگیری می‌کند.
                # -------------------------------------------------

                selected_opponent = None

                for candidate in candidates[:5]:

                    candidate_id = candidate.id

                    remaining_ids = {
                        team.id
                        for team in remaining
                        if team.id != candidate_id
                    }

                    can_continue = True

                    for team in remaining:

                        if team.id == candidate_id:
                            continue

                        has_opponent = any(
                            opponent_id in remaining_ids
                            for opponent_id
                            in allowed[team.id]
                        )

                        if not has_opponent:
                            can_continue = False
                            break

                    if can_continue:
                        selected_opponent = candidate
                        break

                if selected_opponent is None:
                    selected_opponent = candidates[0]

                remaining.remove(
                    selected_opponent
                )

                result.append(
                    (
                        team1,
                        selected_opponent,
                    )
                )

            # -----------------------------------------------------
            # اگر کل تیم‌ها Pair شدند، ذخیره می‌کنیم.
            # -----------------------------------------------------

            if result is not None:

                pairings = []

                for team1, team2 in result:

                    pairing = Pairing.objects.create(
                        round=round_obj,
                        team1=team1,
                        team2=team2,
                    )

                    pairings.append(pairing)

                return pairings

        raise ValidationError(
            "امکان ایجاد Pairing معتبر بدون تکرار حریف وجود ندارد."
        )