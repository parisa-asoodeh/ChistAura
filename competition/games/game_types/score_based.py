class ScoreBasedGameType:

    @staticmethod
    def is_better(
        value1,
        value2
    ):
        return value1 > value2
    

    @classmethod
    def calculate_score(
        cls,
        raw_score,
        completion_time
    ):
        return raw_score
    

    @classmethod
    def determine_winner(
        cls,
        match,
        team1_score,
        team2_score
    ):

        if cls.is_better(
            team1_score,
            team2_score
        ):
            return match.team1

        if cls.is_better(
            team2_score,
            team1_score
        ):
            return match.team2

        return None