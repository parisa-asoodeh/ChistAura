from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)

from ..models import (
    GameSession,
    MatchPlayerScore,
)


@login_required
def game_result(
    request,
    session_id,
):

    session = get_object_or_404(
        GameSession,
        id=session_id,
    )

    if session.user != request.user:

        return render(
            request,
            "games/error.html",
            {
                "message": "شما به نتیجه این بازی دسترسی ندارید."
            },
        )

    player_score = get_object_or_404(
        MatchPlayerScore,
        match=session.match,
        user=session.user,
    )

    context = {
        "session": session,
        "player_score": player_score,
        "question_count": session.match.quiz_questions.count()
    }

    return render(
        request,
        "games/game_result.html",
        context,
    )