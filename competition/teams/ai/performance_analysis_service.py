class PerformanceAnalysisService:

    @staticmethod
    def generate(match):

        if match.winner is None:

            return (
                "این مسابقه کاملاً نزدیک بود و "
                "هیچ تیمی برتری محسوسی نداشت."
            )

        diff = abs(
            match.score_team1 -
            match.score_team2
        )

        if diff >= 50:

            return (
                "اختلاف امتیاز بسیار زیاد بود و "
                "تیم برنده عملکردی کاملاً برتر داشت."
            )

        if diff >= 20:

            return (
                "تیم برنده در طول مسابقه "
                "برتری محسوسی نسبت به حریف داشت."
            )

        return (
            "مسابقه نزدیک و رقابتی بود و "
            "تیم برنده با اختلاف کمی پیروز شد."
        )