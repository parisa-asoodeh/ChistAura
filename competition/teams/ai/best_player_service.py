from games.models import MatchPlayerScore


class BestPlayerService:

    @staticmethod
    def get_best_player(match):

        return (
            MatchPlayerScore.objects
            .filter(match=match)
            .order_by(
                "-score",
                "completion_time",
            )
            .first()
        )