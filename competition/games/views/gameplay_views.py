from django.shortcuts import render

from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.contrib.auth.decorators import (
    login_required,
)
from ..models import GameSession
from django.shortcuts import redirect

from ..quiz_forms import QuizPlayForm

from ..session_service import (
    GameSessionService
)
from django.core.exceptions import ValidationError

from ..quiz_play_service import QuizPlayService

from ..quiz_submission_service import QuizSubmissionService

from django.utils import timezone

from ..models import GameSessionState


@login_required
def game_play(request, session_id):

    session = get_object_or_404(
        GameSession,
        id=session_id
    )

    if session.match.round.status != "active":
        return render(
            request,
            "games/error.html",
            {
                "message": "این راند هنوز فعال نشده است."
            }
        )

    if session.user != request.user:
        return render(
            request,
            "games/error.html",
            {
                "message": "شما به این بازی دسترسی ندارید."
            }
        )

    if session.started_at is None:

        session.started_at = timezone.now()
        session.status = "started"

        session.save(
            update_fields=[
                "started_at",
                "status",
            ]
        )


    if session.status == "completed":

        return render(
            request,
            "games/error.html",
            {
                "message": "این بازی قبلاً انجام شده است."
            }
        )

    if request.method == "POST":

        questions = QuizPlayService.build(session)["questions"]

        form = QuizPlayForm(
            questions,
            data=request.POST
        )

        if form.is_valid():

            QuizSubmissionService.submit(
                session=session,
                form=form,
            )

            return redirect(
                "game_result",
                session_id=session.id,
            )

    else:

        data = QuizPlayService.build(session)

        questions = data["questions"]

        resume_state = data["resume_state"]

        form = QuizPlayForm(
            questions,
            resume_state=resume_state,
        )

    context = {
        "session": session,
        "questions": questions,
        "form": form,
    }

    return render(
        request,
        "games/game_play.html",
        context
    )