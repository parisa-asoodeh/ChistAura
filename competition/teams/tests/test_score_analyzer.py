from django.test import TestCase

from accounts.models import CustomUser

from teams.models import Team

from competitions.models import (
    Tournament,
    GameType,
    Round,
    Subject,
)

from games.models import Match

from teams.ai.analyzers.score_analyzer import (
    ScoreAnalyzer,
)


class ScoreAnalyzerTest(TestCase):

    def setUp(self):

        # -------------------------
        # Users
        # -------------------------

        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        # -------------------------
        # Teams
        # -------------------------

        self.team1 = Team.objects.create(
            name="Team 1",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Team 2",
            captain=self.user2,
        )

        # -------------------------
        # Game Type
        # -------------------------

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        # -------------------------
        # Tournament
        # -------------------------

        self.tournament = Tournament.objects.create(
            name="League",
            game_type=self.game_type,
        )

        # -------------------------
        # Subject
        # -------------------------

        self.subject = Subject.objects.create(
            name="Math",
            slug="math",
        )

        # -------------------------
        # Round
        # -------------------------

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            subject=self.subject,
        )

        # -------------------------
        # Match
        # -------------------------

        self.match = Match.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )

    def test_analyze_when_match_is_draw(
        self,
    ):

        self.match.score_team1 = 50
        self.match.score_team2 = 50
        self.match.winner = None

        result = ScoreAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "این مسابقه کاملاً نزدیک بود و "
            "هیچ تیمی برتری محسوسی نداشت.",
        )

    def test_analyze_when_difference_is_50_or_more(
        self,
    ):

        self.match.score_team1 = 100
        self.match.score_team2 = 40
        self.match.winner = self.team1

        result = ScoreAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "اختلاف امتیاز بسیار زیاد بود و "
            "تیم برنده عملکردی کاملاً برتر داشت.",
        )

    def test_analyze_when_difference_is_between_20_and_49(
        self,
    ):

        self.match.score_team1 = 60
        self.match.score_team2 = 35
        self.match.winner = self.team1

        result = ScoreAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "تیم برنده در طول مسابقه "
            "برتری محسوسی نسبت به حریف داشت.",
        )

    def test_analyze_when_difference_is_less_than_20(
        self,
    ):

        self.match.score_team1 = 40
        self.match.score_team2 = 30
        self.match.winner = self.team1

        result = ScoreAnalyzer.analyze(
            self.match,
        )

        self.assertEqual(
            result,
            "مسابقه نزدیک و رقابتی بود و "
            "تیم برنده با اختلاف کمی پیروز شد.",
        )