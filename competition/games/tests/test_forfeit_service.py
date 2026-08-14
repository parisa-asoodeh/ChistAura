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

from games.models import Match

from games.forfeit_service import (
    MatchForfeitService,
)

from django.core.exceptions import ValidationError
from competitions.round_service import RoundService


class MatchForfeitServiceTest(TestCase):

    def setUp(self):

        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        self.team1 = Team.objects.create(
            name="Team 1",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Team 2",
            captain=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
            is_active=True,
        )

        self.tournament = Tournament.objects.create(
            name="Swiss Tournament",
            game_type=self.game_type,
            total_rounds=1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )

        self.tournament.status = "active"
        self.tournament.save(
            update_fields=["status"],
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="active",
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


    def test_forfeit_match_awards_win_to_present_team(
        self,
    ):

        original_score_team1 = self.match.score_team1
        original_score_team2 = self.match.score_team2

        result = MatchForfeitService.forfeit_match(
            match=self.match,
            present_team=self.team1,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            result,
            self.match,
        )

        self.assertEqual(
            self.match.winner,
            self.team1,
        )

        self.assertEqual(
            self.match.status,
            "forfeit",
        )

        self.assertEqual(
            self.match.forfeit_team,
            self.team1,
        )

        self.assertEqual(
            self.match.score_team1,
            original_score_team1,
        )

        self.assertEqual(
            self.match.score_team2,
            original_score_team2,
        )


    def test_forfeit_match_awards_three_tournament_points(
        self,
    ):

        MatchForfeitService.forfeit_match(
            match=self.match,
            present_team=self.team1,
        )

        self.assertEqual(
            self.team1.get_points_in_tournament(
                self.tournament
            ),
            3,
        )

        self.assertEqual(
            self.team2.get_points_in_tournament(
                self.tournament
            ),
            0,
        )


    def test_forfeit_does_not_change_score_difference(
        self,
    ):

        team1_difference_before = (
            self.team1.get_score_difference_in_tournament(
                self.tournament,
            )
        )

        team2_difference_before = (
            self.team2.get_score_difference_in_tournament(
                self.tournament,
            )
        )

        MatchForfeitService.forfeit_match(
            match=self.match,
            present_team=self.team1,
        )

        team1_difference_after = (
            self.team1.get_score_difference_in_tournament(
                self.tournament,
            )
        )

        team2_difference_after = (
            self.team2.get_score_difference_in_tournament(
                self.tournament,
            )
        )

        self.assertEqual(
            team1_difference_after,
            team1_difference_before,
        )

        self.assertEqual(
            team2_difference_after,
            team2_difference_before,
        )


    def test_forfeit_does_not_change_time(
        self,
    ):

        from games.models import MatchPlayerScore

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=10,
            completion_time=120,
        )

        time_before = (
            self.team1.get_total_time_in_tournament(
                self.tournament,
            )
        )

        MatchForfeitService.forfeit_match(
            match=self.match,
            present_team=self.team1,
        )

        time_after = (
            self.team1.get_total_time_in_tournament(
                self.tournament,
            )
        )

        self.assertEqual(
            time_after,
            time_before,
        )


    def test_forfeit_match_awards_zero_points_to_absent_team(
        self,
    ):

        MatchForfeitService.forfeit_match(
            match=self.match,
            present_team=self.team1,
        )

        self.assertEqual(
            self.team1.get_points_in_tournament(
                self.tournament,
            ),
            3,
        )

        self.assertEqual(
            self.team2.get_points_in_tournament(
                self.tournament,
            ),
            0,
        )


    def test_forfeit_does_not_remove_team_from_tournament(
        self,
    ):

        MatchForfeitService.forfeit_match(
            match=self.match,
            present_team=self.team1,
        )

        self.assertTrue(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team2,
            ).exists()
        )


    def test_forfeit_match_can_only_be_applied_once(
        self,
    ):

        MatchForfeitService.forfeit_match(
            match=self.match,
            present_team=self.team1,
        )

        with self.assertRaises(
            ValidationError,
        ):
            MatchForfeitService.forfeit_match(
                match=self.match,
                present_team=self.team2,
            )


    def test_expired_round_forfeits_unfinished_match(
        self,
    ):

        from django.utils import timezone
        from datetime import timedelta

        self.round.ends_at = timezone.now() - timedelta(
            minutes=5,
        )
        self.round.save(
            update_fields=["ends_at"],
        )

        MatchForfeitService.handle_expired_round(
            round_obj=self.round,
            present_teams={
                self.match.id: self.team1,
            },
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "forfeit",
        )

        self.assertEqual(
            self.match.forfeit_team,
            self.team1,
        )

        self.assertEqual(
            self.match.winner,
            self.team1,
        )


    def test_expired_round_can_be_finished_after_forfeits(
        self,
    ):

        from datetime import timedelta
        from django.utils import timezone

        self.round.ends_at = timezone.now() - timedelta(
            minutes=5,
        )
        self.round.save(
            update_fields=["ends_at"],
        )

        MatchForfeitService.handle_expired_round(
            round_obj=self.round,
            present_teams={
                self.match.id: self.team1,
            },
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "forfeit",
        )

        RoundService.finish_round(
            self.round,
        )

        self.round.refresh_from_db()

        self.assertEqual(
            self.round.status,
            "finished",
        )

        self.assertIsNotNone(
            self.round.ends_at,
        )