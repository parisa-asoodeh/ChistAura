from django.test import TestCase

from competitions.models import (
    Category,
    Subject,
)


class CategoryModelTest(TestCase):

    def test_create_category_for_subject(self):

        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
        )

        category = Category.objects.create(
            subject=subject,
            name="Periodic Table",
            slug="periodic-table",
            description="Questions about elements and periodic table.",
        )

        self.assertEqual(
            category.subject,
            subject
        )

        self.assertEqual(
            category.name,
            "Periodic Table"
        )