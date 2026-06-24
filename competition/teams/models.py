from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام تیم")

    captain = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='captained_teams',
        verbose_name="کاپیتان"
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    def __str__(self):
        return self.name

    # -----------------------------
    # RELATION HELPERS (CORE LOGIC)
    # -----------------------------

    def matches(self):
        """
        همه مسابقات تیم (چه تیم اول چه تیم دوم)
        """
        return self.home_matches.all() | self.away_matches.all()

    def get_wins(self):
        return sum(
            1
            for match in self.won_matches.all()
            if match.is_complete
        )

    def get_draws(self):
        return sum(
            1
            for match in self.matches()
            if (
                match.is_complete
                and
                match.winner is None
            )
        )

    def get_played(self):
        return sum(
            1
            for match in self.matches()
            if match.is_complete
        )

    def get_losses(self):
        return self.get_played() - self.get_wins() - self.get_draws()

    def get_points(self):
        return (self.get_wins() * 3) + self.get_draws()
    
    #برای جدا کردن امتیازهای تورنمنت ها در جدول های جدا
    def matches_in_tournament(self, tournament):
        return self.matches().filter(
            tournament=tournament
        )
    
    def get_wins_in_tournament(
        self,
        tournament
    ):
        return sum(
            1
            for match in self.won_matches.filter(
                tournament=tournament
            )
            if match.is_complete
        )
    
    def get_draws_in_tournament(
        self,
        tournament
    ):
        return sum(
            1
            for match in self.matches_in_tournament(
                tournament
            )
            if (
                match.is_complete
                and
                match.winner is None
            )
        )
    
    def get_played_in_tournament(
        self,
        tournament
    ):
        return sum(
            1
            for match in self.matches_in_tournament(
                tournament
            )
            if match.is_complete
        )
    
    def get_losses_in_tournament(self, tournament):
        return (
            self.get_played_in_tournament(
                tournament
            )
            -
            self.get_wins_in_tournament(
                tournament
            )
            -
            self.get_draws_in_tournament(
                tournament
            )
        )
    
    def get_points_in_tournament(self, tournament):
        return (
            self.get_wins_in_tournament(
                tournament
            ) * 3
            +
            self.get_draws_in_tournament(
                tournament
            )
        )
    
    def get_score_difference_in_tournament(
        self,
        tournament
    ):
        difference = 0
        matches = self.matches_in_tournament(
            tournament
        )
        for match in matches:
            if not match.is_complete:
                continue
            if match.team1 == self:
                difference += (
                    match.score_team1
                    -
                    match.score_team2
                )
            else:
                difference += (
                    match.score_team2
                    -
                    match.score_team1
                )
        return difference
    

    def get_total_time_in_tournament(
        self,
        tournament
    ):

        from django.db.models import Sum
        from games.models import MatchPlayerScore

        total_time = (
            MatchPlayerScore.objects.filter(
                match__tournament=tournament,
                team=self,
                completion_time__isnull=False,
            )
            .aggregate(
                total=Sum(
                    'completion_time'
                )
            )['total']
        )
        return total_time or 0


class TeamMembership(models.Model):
    # ارتباط بین تیم و کاربر
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        related_name='members',
        verbose_name="تیم"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name="عضو"
    )
    individual_score = models.IntegerField(default=0, verbose_name="امتیاز فردی")

    class Meta:
        # جلوگیری از اینکه یک نفر در یک تیم دو بار عضو شود
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} در {self.team.name}"
