from django.db.models import Sum

from games.models import MatchPlayerScore


class StarDependencyAnalyzer:

    @staticmethod
    def analyze(match):

        team1_scores = list(
            MatchPlayerScore.objects.filter(
                match=match,
                team=match.team1
            ).values_list(
                "score",
                flat=True
            )
        )

        team2_scores = list(
            MatchPlayerScore.objects.filter(
                match=match,
                team=match.team2
            ).values_list(
                "score",
                flat=True
            )
        )

        team1_dependency = (
            StarDependencyAnalyzer.dependency_percentage(
                team1_scores
            )
        )

        team2_dependency = (
            StarDependencyAnalyzer.dependency_percentage(
                team2_scores
            )
        )

        return {
            "team1": team1_dependency,
            "team2": team2_dependency,
            "summary": StarDependencyAnalyzer.build_summary(
                match,
                team1_dependency,
                team2_dependency,
            ),
        }


    @staticmethod
    def dependency_percentage(scores):

        if not scores:

            return {
                "total": 0,
                "top_score": 0,
                "percentage": 0,
            }

        total = sum(scores)

        if total == 0:

            return {
                "total": 0,
                "top_score": 0,
                "percentage": 0,
            }

        top_score = max(scores)

        percentage = (
            top_score / total
        ) * 100

        return {
            "total": total,
            "top_score": top_score,
            "percentage": percentage,
        }
    

    @staticmethod
    def build_summary(
        match,
        team1_dependency,
        team2_dependency,
    ):

        team1_percentage = (
            team1_dependency["percentage"]
        )

        team2_percentage = (
            team2_dependency["percentage"]
        )

        if (
            team1_percentage < 40
            and
            team2_percentage < 40
        ):

            return (
                "امتیازات هر دو تیم "
                "به شکل متوازن بین اعضا "
                "تقسیم شده بود و وابستگی "
                "زیادی به یک بازیکن وجود نداشت."
            )

        if team1_percentage > team2_percentage:

            if team1_percentage >= 60:

                return (
                    f"بیش از "
                    f"{team1_percentage:.0f}٪ "
                    f"از امتیازات تیم "
                    f"{match.team1.name} "
                    f"توسط یک بازیکن کسب شد و "
                    f"این تیم وابستگی زیادی "
                    f"به او داشت."
                )

            return (
                f"بهترین بازیکن تیم "
                f"{match.team1.name} "
                f"{team1_percentage:.0f}٪ "
                f"از امتیازات تیم را "
                f"کسب کرد و نقش مهمی "
                f"در نتیجه مسابقه داشت."
            )

        if team2_percentage > team1_percentage:

            if team2_percentage >= 60:

                return (
                    f"بیش از "
                    f"{team2_percentage:.0f}٪ "
                    f"از امتیازات تیم "
                    f"{match.team2.name} "
                    f"توسط یک بازیکن کسب شد و "
                    f"این تیم وابستگی زیادی "
                    f"به او داشت."
                )

            return (
                f"بهترین بازیکن تیم "
                f"{match.team2.name} "
                f"{team2_percentage:.0f}٪ "
                f"از امتیازات تیم را "
                f"کسب کرد و نقش مهمی "
                f"در نتیجه مسابقه داشت."
            )

        return (
            "هر دو تیم میزان وابستگی "
            "مشابهی به بهترین بازیکن "
            "خود داشتند."
        )