import json

from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404

from games.models import GameSession
from games.game_resume_service import GameResumeService


class GameStateUpdateView(View):

    def post(
        self,
        request,
        session_id,
    ):

        session = get_object_or_404(
            GameSession,
            id=session_id,
        )

        if session.user != request.user:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Permission denied.",
                },
                status=403,
            )

        try:

            payload = json.loads(
                request.body
            )

        except json.JSONDecodeError:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid JSON.",
                },
                status=400,
            )


        GameResumeService.save(
            session=session,
            state=payload.get(
                "state",
                {},
            ),
        )

        return JsonResponse(
            {
                "success": True,
            }
        )