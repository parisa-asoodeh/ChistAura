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
    Round,
    Subject,
    Pairing,
)

from games.models import (
    Match,
    MatchPlayerScore,
)

from teams.statistics.team_statistics_service import (
    TeamStatisticsService,
)


class TeamStatisticsServiceTest(TestCase):

    def setUp(self):

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.tournament1 = Tournament.objects.create(
            name="League 1",
            game_type=self.game_type,
            total_rounds=2,
        )

        self.tournament2 = Tournament.objects.create(
            name="League 2",
            game_type=self.game_type,
            total_rounds=2,
        )

        self.captain1 = CustomUser.objects.create_user(
            username="captain1",
            password="1234",
        )

        self.member1 = CustomUser.objects.create_user(
            username="member1",
            password="1234",
        )

        self.captain2 = CustomUser.objects.create_user(
            username="captain2",
            password="1234",
        )

        self.member2 = CustomUser.objects.create_user(
            username="member2",
            password="1234",
        )

        self.team1 = Team.objects.create(
            name="Alpha",
            captain=self.captain1,
        )

        self.team2 = Team.objects.create(
            name="Beta",
            captain=self.captain2,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.captain1,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.member1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.captain2,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.member2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament1,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament1,
            team=self.team2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament2,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament2,
            team=self.team2,
        )

        self.subject = Subject.objects.create(
            name="Math",
            slug="math",
        )

        self.match1 = self.create_match(
            tournament=self.tournament1,
            score_team1=100,
            score_team2=80,
            winner=self.team1,
        )

        self.match2 = self.create_match(
            tournament=self.tournament1,
            score_team1=90,
            score_team2=90,
            winner=None,
        )

        self.match3 = self.create_match(
            tournament=self.tournament1,
            score_team1=70,
            score_team2=95,
            winner=self.team2,
        )

        self.match4 = self.create_match(
            tournament=self.tournament1,
        )

        self.match5 = self.create_match(
            tournament=self.tournament2,
            score_team1=110,
            score_team2=60,
            winner=self.team1,
        )

        self.create_player_scores()

    def create_match(
        self,
        tournament,
        score_team1=None,
        score_team2=None,
        winner=None,
    ):

        round_number = (
            Round.objects.filter(
                tournament=tournament,
            ).count()
            + 1
        )

        round = Round.objects.create(
            tournament=tournament,
            number=round_number,
            subject=self.subject,
        )

        pairing = Pairing.objects.create(
            round=round,
            team1=self.team1,
            team2=self.team2,
        )

        return Match.objects.create(
            round=round,
            pairing=pairing,
            team1=self.team1,
            team2=self.team2,
            winner=winner,
            score_team1=score_team1,
            score_team2=score_team2,
        )

    def create_player_scores(self):

        MatchPlayerScore.objects.create(
            match=self.match1,
            user=self.captain1,
            team=self.team1,
            score=60,
            completion_time=120,
        )

        MatchPlayerScore.objects.create(
            match=self.match1,
            user=self.member1,
            team=self.team1,
            score=40,
            completion_time=180,
        )

        MatchPlayerScore.objects.create(
            match=self.match1,
            user=self.captain2,
            team=self.team2,
            score=50,
            completion_time=200,
        )

        MatchPlayerScore.objects.create(
            match=self.match1,
            user=self.member2,
            team=self.team2,
            score=30,
            completion_time=220,
        )

        MatchPlayerScore.objects.create(
            match=self.match5,
            user=self.captain1,
            team=self.team1,
            score=70,
            completion_time=100,
        )

        MatchPlayerScore.objects.create(
            match=self.match5,
            user=self.member1,
            team=self.team1,
            score=40,
            completion_time=150,
        )

        MatchPlayerScore.objects.create(
            match=self.match5,
            user=self.captain2,
            team=self.team2,
            score=35,
            completion_time=130,
        )

        MatchPlayerScore.objects.create(
            match=self.match5,
            user=self.member2,
            team=self.team2,
            score=25,
            completion_time=170,
        )

    def test_get_matches(self):

        matches = TeamStatisticsService.get_matches(
            self.team1,
        )

        self.assertEqual(
            matches.count(),
            5,
        )

    def test_get_matches_in_tournament(self):

        matches = (
            TeamStatisticsService.get_matches_in_tournament(
                self.team1,
                self.tournament1,
            )
        )

        self.assertEqual(
            matches.count(),
            4,
        )

    def test_get_wins(self):

        self.assertEqual(
            TeamStatisticsService.get_wins(
                self.team1,
            ),
            2,
        )

    def test_get_draws(self):

        self.assertEqual(
            TeamStatisticsService.get_draws(
                self.team1,
            ),
            1,
        )

    def test_get_played(self):

        self.assertEqual(
            TeamStatisticsService.get_played(
                self.team1,
            ),
            4,
        )

    def test_get_losses(self):

        self.assertEqual(
            TeamStatisticsService.get_losses(
                self.team1,
            ),
            1,
        )

    def test_get_points(self):

        self.assertEqual(
            TeamStatisticsService.get_points(
                self.team1,
            ),
            7,
        )

    def test_tournament1_statistics(self):

        self.assertEqual(
            TeamStatisticsService.get_wins_in_tournament(
                self.team1,
                self.tournament1,
            ),
            1,
        )

        self.assertEqual(
            TeamStatisticsService.get_draws_in_tournament(
                self.team1,
                self.tournament1,
            ),
            1,
        )

        self.assertEqual(
            TeamStatisticsService.get_played_in_tournament(
                self.team1,
                self.tournament1,
            ),
            3,
        )

        self.assertEqual(
            TeamStatisticsService.get_losses_in_tournament(
                self.team1,
                self.tournament1,
            ),
            1,
        )

        self.assertEqual(
            TeamStatisticsService.get_points_in_tournament(
                self.team1,
                self.tournament1,
            ),
            4,
        )

    def test_tournament2_statistics(self):

        self.assertEqual(
            TeamStatisticsService.get_wins_in_tournament(
                self.team1,
                self.tournament2,
            ),
            1,
        )

        self.assertEqual(
            TeamStatisticsService.get_draws_in_tournament(
                self.team1,
                self.tournament2,
            ),
            0,
        )

        self.assertEqual(
            TeamStatisticsService.get_played_in_tournament(
                self.team1,
                self.tournament2,
            ),
            1,
        )

        self.assertEqual(
            TeamStatisticsService.get_losses_in_tournament(
                self.team1,
                self.tournament2,
            ),
            0,
        )

        self.assertEqual(
            TeamStatisticsService.get_points_in_tournament(
                self.team1,
                self.tournament2,
            ),
            3,
        )

    def test_empty_tournament_statistics(self):

        tournament = Tournament.objects.create(
            name="Empty",
            game_type=self.game_type,
            total_rounds=1,
        )

        self.assertEqual(
            TeamStatisticsService.get_wins_in_tournament(
                self.team1,
                tournament,
            ),
            0,
        )

        self.assertEqual(
            TeamStatisticsService.get_draws_in_tournament(
                self.team1,
                tournament,
            ),
            0,
        )

        self.assertEqual(
            TeamStatisticsService.get_played_in_tournament(
                self.team1,
                tournament,
            ),
            0,
        )

        self.assertEqual(
            TeamStatisticsService.get_losses_in_tournament(
                self.team1,
                tournament,
            ),
            0,
        )

        self.assertEqual(
            TeamStatisticsService.get_points_in_tournament(
                self.team1,
                tournament,
            ),
            0,
        )

    def test_get_score_difference_in_tournament(self):

        self.assertEqual(
            TeamStatisticsService.get_score_difference_in_tournament(
                self.team1,
                self.tournament1,
            ),
            -5,
        )

    def test_get_score_difference_in_empty_tournament(self):

        tournament = Tournament.objects.create(
            name="Empty",
            game_type=self.game_type,
            total_rounds=1,
        )

        self.assertEqual(
            TeamStatisticsService.get_score_difference_in_tournament(
                self.team1,
                tournament,
            ),
            0,
        )

    def test_get_total_time_in_tournament(self):

        self.assertEqual(
            TeamStatisticsService.get_total_time_in_tournament(
                self.team1,
                self.tournament1,
            ),
            300,
        )

    def test_get_total_time_in_empty_tournament(self):

        tournament = Tournament.objects.create(
            name="Empty",
            game_type=self.game_type,
            total_rounds=1,
        )

        self.assertEqual(
            TeamStatisticsService.get_total_time_in_tournament(
                self.team1,
                tournament,
            ),
            0,
        )