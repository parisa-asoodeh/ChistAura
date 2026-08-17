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
    Category,
)

from games.models import (
    Match,
    GameSession,
)

from games.quiz_models import QuizQuestion


class TournamentExecutionServiceTest(TestCase):

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

        self.user3 = CustomUser.objects.create_user(
            username="user3",
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

        self.team3 = Team.objects.create(
            name="Team 3",
            captain=self.user3,
        )

        self.team4 = Team.objects.create(
            name="Team 4",
            captain=self.user1,
        )

        # -------------------------
        # Memberships
        # -------------------------

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team3,
            user=self.user3,
        )

        TeamMembership.objects.create(
            team=self.team4,
            user=self.user1,
        )

        # -------------------------
        # Game Type
        # -------------------------

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        # -------------------------
        # Subject
        # -------------------------

        self.subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
            is_active=True,
        )

        # -------------------------
        # Category
        # -------------------------

        self.category = Category.objects.create(
            subject=self.subject,
            name="General Chemistry",
            slug="general-chemistry",
        )

        for index in range(20):
            QuizQuestion.objects.create(
                category=self.category,
                question=f"Question {index + 1}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="easy",
                is_active=True,
            )

        # -------------------------
        # Tournament
        # -------------------------

        self.tournament = Tournament.objects.create(
            name="Swiss Tournament",
            game_type=self.game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team3,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team4,
        )

        self.round1 = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
        )

    # =========================================================
    # 1. Start Tournament → Round 1
    # =========================================================

    def test_start_tournament_creates_first_round(self):

        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )

        TournamentExecutionService.start_tournament(
            tournament=self.tournament,
        )

        self.tournament.refresh_from_db()

        round_obj = Round.objects.get(
            tournament=self.tournament,
            number=1,
        )

        self.assertEqual(
            self.tournament.status,
            "active",
        )

        self.assertIsNotNone(
            self.tournament.started_at,
        )

        self.assertIsNotNone(
            round_obj,
        )

        self.assertEqual(
            round_obj.number,
            1,
        )

        self.assertEqual(
            round_obj.status,
            "active",
        )

        self.assertEqual(
            Round.objects.filter(
                tournament=self.tournament,
            ).count(),
            1,
        )

    # =========================================================
    # 2. Finish Round 1 → Create Round 2
    # =========================================================

    def test_finish_round_creates_next_round(self):

        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )

        TournamentExecutionService.start_tournament(
            tournament=self.tournament,
        )

        round1 = Round.objects.get(
            tournament=self.tournament,
            number=1,
        )

        matches = Match.objects.filter(
            round=round1,
        )

        for match in matches:
            match.score_team1 = 20
            match.score_team2 = 10
            match.status = "completed"
            match.save(
                update_fields=[
                    "score_team1",
                    "score_team2",
                    "status",
                ]
            )

        TournamentExecutionService.finish_round(
            round1,
        )

        round2 = Round.objects.get(
            tournament=self.tournament,
            number=2,
        )

        self.assertEqual(
            round2.number,
            2,
        )

        self.assertEqual(
            round2.status,
            "scheduled",
        )

        self.assertEqual(
            Round.objects.filter(
                tournament=self.tournament,
            ).count(),
            2,
        )

    # =========================================================
    # 3. Pairing / Bye / Match / GameSession
    # =========================================================

    def test_prepare_round_creates_pairings_matches_and_sessions(
        self,
    ):

        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )

        result = (
            TournamentExecutionService.start_tournament(
                tournament=self.tournament,
            )
        )

        round_obj = Round.objects.get(
            tournament=self.tournament,
            number=1,
        )

        self.assertIsNotNone(
            result,
        )

        self.assertTrue(
            Pairing.objects.filter(
                round=round_obj,
            ).exists()
        )

        self.assertTrue(
            Match.objects.filter(
                round=round_obj,
            ).exists()
        )

        self.assertTrue(
            GameSession.objects.filter(
                match__round=round_obj,
            ).exists()
        )

    # =========================================================
    # 4. Finish Matches → Finish Round
    # =========================================================

    def test_finish_matches_finishes_round(
        self,
    ):

        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )

        TournamentExecutionService.start_tournament(
            tournament=self.tournament,
        )

        round_obj = Round.objects.get(
            tournament=self.tournament,
            number=1,
        )

        matches = Match.objects.filter(
            round=round_obj,
        )

        for match in matches:
            match.score_team1 = 20
            match.score_team2 = 10
            match.status = "completed"
            match.save(
                update_fields=[
                    "score_team1",
                    "score_team2",
                    "status",
                ]
            )

        TournamentExecutionService.finish_round(
            round_obj,
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "finished",
        )

        self.assertIsNotNone(
            round_obj.ends_at,
        )

    # =========================================================
    # 5. Final Round → Ranking / Champion
    # =========================================================

    def test_final_round_produces_final_ranking_and_champion(
        self,
    ):

        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )

        self.tournament.total_rounds = 1
        self.tournament.save(
            update_fields=["total_rounds"],
        )

        TournamentExecutionService.start_tournament(
            tournament=self.tournament,
        )

        round_obj = Round.objects.get(
            tournament=self.tournament,
            number=1,
        )

        matches = Match.objects.filter(
            round=round_obj,
        )

        for match in matches:
            match.score_team1 = 30
            match.score_team2 = 10
            match.status = "completed"
            match.save(
                update_fields=[
                    "score_team1",
                    "score_team2",
                    "status",
                ]
            )

        TournamentExecutionService.finish_round(
            round_obj,
        )

        result = (
            TournamentExecutionService.finalize_tournament(
                tournament=self.tournament,
            )
        )

        self.assertIsNotNone(
            result,
        )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "finished",
        )

        self.assertIsNotNone(
            self.tournament.champion,
        )

    # =========================================================
    # 6. Complete Tournament Flow
    # =========================================================

    def test_complete_tournament_flow(
        self,
    ):

        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )
        from competitions.round_service import RoundService

        # -------------------------
        # Round 1
        # -------------------------

        TournamentExecutionService.start_tournament(
            tournament=self.tournament,
        )

        round1 = Round.objects.get(
            tournament=self.tournament,
            number=1,
        )

        matches_round1 = Match.objects.filter(
            round=round1,
        )

        for match in matches_round1:
            match.score_team1 = 20
            match.score_team2 = 10
            match.status = "completed"
            match.save(
                update_fields=[
                    "score_team1",
                    "score_team2",
                    "status",
                ]
            )

        self.assertFalse(
            Match.objects.filter(
                round=round1,
                status__in=["pending", "active"],
            ).exists()
        )

        TournamentExecutionService.finish_round(
            round1,
        )

        # -------------------------
        # Round 2
        # -------------------------

        round2 = Round.objects.get(
            tournament=self.tournament,
            number=2,
        )

        RoundService.start_round(
            round2,
        )

        matches_round2 = Match.objects.filter(
            round=round2,
        )

        for match in matches_round2:
            match.score_team1 = 30
            match.score_team2 = 10
            match.status = "completed"
            match.save(
                update_fields=[
                    "score_team1",
                    "score_team2",
                    "status",
                ]
            )

        self.assertFalse(
            Match.objects.filter(
                round=round2,
                status__in=["pending", "active"],
            ).exists()
        )

        TournamentExecutionService.finish_round(
            round2,
        )

        # -------------------------
        # Finalize Tournament
        # -------------------------

        TournamentExecutionService.finalize_tournament(
            tournament=self.tournament,
        )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "finished",
        )

        self.assertIsNotNone(
            self.tournament.finished_at,
        )

        self.assertIsNotNone(
            self.tournament.champion,
        )

    # =========================================================
    # 7. Expire Round
    # =========================================================

    def test_expire_round_handles_timeout_and_finishes_round(
        self,
    ):

        from datetime import timedelta

        from django.utils import timezone

        from competitions.tournament_execution_service import (
            TournamentExecutionService,
        )

        TournamentExecutionService.start_tournament(
            tournament=self.tournament,
        )

        round_obj = Round.objects.get(
            tournament=self.tournament,
            number=1,
        )

        match = Match.objects.filter(
            round=round_obj,
        ).first()

        sessions = list(
            match.sessions.order_by("id")
        )

        sessions[0].status = "started"
        sessions[0].started_at = timezone.now()
        sessions[0].save(
            update_fields=[
                "status",
                "started_at",
            ],
        )

        sessions[1].status = "pending"
        sessions[1].started_at = None
        sessions[1].save(
            update_fields=[
                "status",
                "started_at",
            ],
        )

        round_obj.ends_at = timezone.now() - timedelta(
            minutes=5,
        )

        round_obj.save(
            update_fields=["ends_at"],
        )

        TournamentExecutionService.expire_round(
            round_obj,
        )

        match.refresh_from_db()
        round_obj.refresh_from_db()

        self.assertEqual(
            match.status,
            "forfeit",
        )

        self.assertEqual(
            match.forfeit_team,
            match.team1,
        )

        self.assertEqual(
            round_obj.status,
            "finished",
        )
