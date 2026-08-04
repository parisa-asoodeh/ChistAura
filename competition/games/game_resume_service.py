from .models import (
    GameSession,
    GameSessionState,
)


class GameResumeService:

    @staticmethod
    def save(
        session: GameSession,
        state: dict,
    ):

        GameSessionState.objects.update_or_create(
            session=session,
            defaults={
                "state": state,
            },
        )

    @staticmethod
    def load(
        session: GameSession,
    ):

        try:

            return session.resume_state.state

        except GameSessionState.DoesNotExist:

            return {}

    @staticmethod
    def clear(
        session: GameSession,
    ):

        GameSessionState.objects.filter(
            session=session
        ).delete()