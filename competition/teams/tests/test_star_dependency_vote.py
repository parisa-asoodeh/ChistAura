from django.test import TestCase

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from teams.ai.votes.star_dependency_vote import (
    StarDependencyVote,
)


class StarDependencyVoteTest(TestCase):

    def setUp(self):

        self.user1 = CustomUser.objects.create_user(
            username="captain1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="captain2",
            password="1234",
        )

        self.team1 = Team.objects.create(
            name="Alpha",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Beta",
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


    def test_team1_gets_vote(self):

        team1_context = {
            "team": self.team1,
            "scores": [40, 45, 50],
        }

        team2_context = {
            "team": self.team2,
            "scores": [10, 90, 100],
        }

        result = StarDependencyVote.vote(
            team1_context,
            team2_context,
        )

        self.assertEqual(
            result["vote"],
            self.team1,
        )

        self.assertEqual(
            result["confidence"],
            13.0,
        )

        self.assertEqual(
            result["analyzer"],
            "StarDependencyVote",
        )

        self.assertIn(
            self.team1.name,
            result["reason"],
        )


    def test_team2_gets_vote(self):

        team1_context = {
            "team": self.team1,
            "scores": [10, 90, 100],
        }

        team2_context = {
            "team": self.team2,
            "scores": [40, 45, 50],
        }

        result = StarDependencyVote.vote(
            team1_context,
            team2_context,
        )

        self.assertEqual(
            result["vote"],
            self.team2,
        )

        self.assertEqual(
            result["confidence"],
            13.0,
        )

        self.assertEqual(
            result["analyzer"],
            "StarDependencyVote",
        )

        self.assertIn(
            self.team2.name,
            result["reason"],
        )


    def test_equal_percentage(self):

        team1_context = {
            "team": self.team1,
            "scores": [50, 50],
        }

        team2_context = {
            "team": self.team2,
            "scores": [50, 50],
        }

        result = StarDependencyVote.vote(
            team1_context,
            team2_context,
        )

        self.assertIsNone(
            result["vote"],
        )

        self.assertEqual(
            result["reason"],
            "هر دو تیم وابستگی مشابهی به بهترین بازیکن خود دارند.",
        )


    def test_output_structure(self):

        team1_context = {
            "team": self.team1,
            "scores": [80],
        }

        team2_context = {
            "team": self.team2,
            "scores": [50],
        }

        result = StarDependencyVote.vote(
            team1_context,
            team2_context,
        )

        self.assertIn(
            "analyzer",
            result,
        )

        self.assertIn(
            "vote",
            result,
        )

        self.assertIn(
            "confidence",
            result,
        )

        self.assertIn(
            "reason",
            result,
        )