from teams.ai.predictors.winner_predictor import (
    WinnerPredictor
)
from teams.ai.power_ranking_service import (
    PowerRankingService,
)

from teams.ai.explanation_service import (
    ExplanationService,
)


class ChampionPredictor:

    @staticmethod
    def predict(
        teams,
        tournament,
    ):

        matchups = (
            ChampionPredictor.generate_matchups(
                teams,
            )
        )

        results = (
            ChampionPredictor.evaluate_matchups(
                matchups,
                tournament,
            )
        )

        ranking = (
            PowerRankingService.build(
                results,
            )
        )

        champion = (
            ChampionPredictor.choose_champion(
                ranking,
            )
        )

        summary = (
            ChampionPredictor.build_summary(
                champion,
                ranking,
            )
        )

        from collections import Counter
        top_reasons = Counter()

        for result in results:
            prediction = result["prediction"]
            if (
                prediction["winner"] == champion
            ):
                top_reasons.update(
                    ExplanationService.build_prediction_reasons(
                        prediction["votes"],
                        champion,
                    )
                )

        top_reasons = [
            reason
            for reason, count in
            top_reasons.most_common(3)
        ]

        return {

            "champion": champion,

            "ranking": ranking,

            "summary": summary,

            "top_reasons": top_reasons,

            "matchups": results,

        }


    @staticmethod
    def generate_matchups(
        teams,
    ):

        matchups = []

        for i in range(len(teams)):

            for j in range(
                i + 1,
                len(teams),
            ):

                matchups.append(
                    (
                        teams[i],
                        teams[j],
                    )
                )

        return matchups


    @staticmethod
    def evaluate_matchups(
        matchups,
        tournament,
    ):

        results = []

        for team1, team2 in matchups:

            prediction = (
                WinnerPredictor.predict(
                    team1,
                    team2,
                    tournament,
                )
            )

            results.append(

                {
                    "team1": team1,

                    "team2": team2,

                    "prediction": prediction,
                }

            )

        return results


    @staticmethod
    def choose_champion(
        ranking,
    ):

        if not ranking:

            return None

        return ranking[0]["team"]


    @staticmethod
    def build_summary(
        champion,
        ranking,
    ):

        if champion is None:

            return (
                "هوش مصنوعی نتوانست قهرمانی را پیش‌بینی کند."
            )

        score = round(
            ranking[0]["score"],
            1,
        )

        return (
            f"هوش مصنوعی تیم "
            f"{champion.name} "
            f"را با امتیاز "
            f"{score} "
            f"محتمل‌ترین قهرمان لیگ می‌داند."
        )