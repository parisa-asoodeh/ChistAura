from django.test import TestCase

from competitions.models import (
    Subject,
    Tournament,
    GameType,
)


class SubjectModelTest(TestCase):

    def test_create_subject(self):

        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
            description="Chemistry competitions",
        )

        self.assertEqual(
            subject.name,
            "Chemistry"
        )

        self.assertTrue(
            subject.is_active
        )


    def test_tournament_can_have_subject(self):


        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        subject = Subject.objects.create(
            name="Mathematics",
            slug="mathematics",
        )

        tournament = Tournament.objects.create(
            name="Math League",
            subject=subject,
            game_type=game_type,
        )

        self.assertEqual(
            tournament.subject,
            subject
        )