from teams.ai.analyzers.average_analyzer import (
    AverageAnalyzer,
)


class AverageVote:

    @staticmethod
    def vote(
        team1,
        team2,
    ):
        # مرحله اول نتیجه Analyzerها را بگیر
        team1_result = (
            AverageAnalyzer.analyze(
                team1
            )
        )

        team2_result = (
            AverageAnalyzer.analyze(
                team2
            )
        )
        # مرحله دوم میانگین‌ها را استخراج کن
        team1_average = (
            team1_result["average"]
        )

        team2_average = (
            team2_result["average"]
        )
        # مرحله سوم فعلاً فقط رأی را مشخص می‌کنیم
        if team1_average > team2_average:

            vote = team1

        elif team2_average > team1_average:

            vote = team2

        else:

            vote = None
        # مرحله چهارم فعلاً Confidence را ساده نگه می‌داریم
        confidence = abs(
            team1_average -
            team2_average
        )
        # مرحله پنجم Reason
        if vote == team1:

            reason = (
                f"میانگین امتیاز "
                f"{team1.name} "
                f"بالاتر است."
            )

        elif vote == team2:

            reason = (
                f"میانگین امتیاز "
                f"{team2.name} "
                f"بالاتر است."
            )

        else:

            reason = (
                "میانگین امتیاز "
                "دو تیم برابر است."
            )

        # مرحله ششم خروجی
        return {

            "analyzer": "AverageVote",

            "vote": vote,

            "confidence": confidence,

            "reason": reason,
        }