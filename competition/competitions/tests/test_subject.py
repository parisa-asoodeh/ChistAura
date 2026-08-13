from django.test import TestCase

from competitions.models import (
    Subject,
    Tournament,
    GameType,
    Round,
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
            "Chemistry",
        )

        self.assertTrue(
            subject.is_active,
        )


    def test_round_can_have_subject(self):

        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="Math League",
            game_type=game_type,
        )

        tournament.status = "active"
        tournament.save()

        subject = Subject.objects.create(
            name="Mathematics",
            slug="mathematics",
        )

        round_obj = Round.objects.create(
            tournament=tournament,
            number=1,
            subject=subject,
        )

        self.assertEqual(
            round_obj.subject,
            subject,
        )