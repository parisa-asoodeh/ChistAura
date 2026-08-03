from django.utils import timezone
from django.core.exceptions import ValidationError


class SessionTimeService:

    @staticmethod
    def calculate_completion_time(session):

        if not session.started_at:
            raise ValidationError(
                "زمان شروع بازی ثبت نشده است."
            )

        finished_at = timezone.now()

        completion_time = (
            finished_at - session.started_at
        ).total_seconds()

        return int(completion_time)