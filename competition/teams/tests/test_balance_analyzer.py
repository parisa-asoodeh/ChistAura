from django.test import TestCase

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Round,
    Pairing,
)

from games.models import (
    Match,
    MatchPlayerScore,
)

from teams.ai.analyzers.balance_analyzer import (
    BalanceAnalyzer,
)


class BalanceAnalyzerTest(TestCase):

    def setUp(self):

        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        self.user3 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        self.user4 = CustomUser.objects.create_user(
            username="user4",
            password="1234",
        )

        self.team1 = Team.objects.create(
            name="Team 1",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Team 2",
            captain=self.user3,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user3,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user4,
        )

        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="League",
            game_type=game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=self.team2,
        )

        self.subject = Subject.objects.create(
            name="General",
            slug="general",
        )

        self.round = Round.objects.create(
            tournament=tournament,
            number=1,
            subject=self.subject,
        )

        self.pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )

        self.match = Match.objects.create(
            round=self.round,
            pairing=self.pairing,
            team1=self.team1,
            team2=self.team2,
        )
        
    # بقیه تست‌ها بدون تغییر
    def test_is_balanced_when_difference_is_small(
        self,
    ):

        self.assertTrue(
            BalanceAnalyzer.is_balanced(
                [40, 50],
            )
        )

    def test_is_balanced_when_difference_is_large(
        self,
    ):

        self.assertFalse(
            BalanceAnalyzer.is_balanced(
                [20, 60],
            )
        )

    def test_analyze_when_both_teams_are_balanced(
        self,
    ):

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=40,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team1,
            score=50,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user3,
            team=self.team2,
            score=60,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user4,
            team=self.team2,
            score=70,
        )

        result = BalanceAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "هر دو تیم عملکردی هماهنگ و گروهی داشتند.",
        )

    def test_analyze_when_only_team1_is_balanced(
        self,
    ):

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=40,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team1,
            score=50,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user3,
            team=self.team2,
            score=10,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user4,
            team=self.team2,
            score=80,
        )

        result = BalanceAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "Team 1 عملکرد گروهی‌تری داشت.",
        )

    def test_analyze_when_no_team_is_balanced(
        self,
    ):

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=10,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team1,
            score=90,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user3,
            team=self.team2,
            score=20,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user4,
            team=self.team2,
            score=80,
        )

        result = BalanceAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "هر دو تیم بیش از حد به عملکرد چند بازیکن متکی بودند.",
        )

    def test_analyze_when_only_team2_is_balanced(
        self,
    ):

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=10,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team1,
            score=80,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user3,
            team=self.team2,
            score=40,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user4,
            team=self.team2,
            score=50,
        )

        result = BalanceAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "Team 2 عملکرد گروهی‌تری داشت.",
        )