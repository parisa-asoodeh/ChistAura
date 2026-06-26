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

from ..forms import GameResultForm

from ..session_service import (
    GameSessionService
)
from django.core.exceptions import ValidationError


@login_required
def game_play(request, session_id):

    session = get_object_or_404(
        GameSession,
        id=session_id
    )

    if session.user != request.user:
        return render(
            request,
            "games/error.html",
            {
                "message": "شما به این بازی دسترسی ندارید."
            }
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

        form = GameResultForm(request.POST)

        if form.is_valid():

            try:
                GameSessionService.complete_session(
                    session=session,
                    raw_score=form.cleaned_data["raw_score"],
                    completion_time=form.cleaned_data["completion_time"],
                )

                return redirect(
                    "match_detail",
                    match_id=session.match.id
                )

            except ValidationError as e:
                form.add_error(
                    None,
                    e.message
                )

    else:

        form = GameResultForm()

    return render(
        request,
        "games/game_play.html",
        {
            "session": session,
            "form": form,
        }
    )