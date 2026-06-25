from .score_based import ScoreBasedGameType


GAME_TYPES = {
    'quiz': ScoreBasedGameType,
    'puzzle': ScoreBasedGameType,
    'math': ScoreBasedGameType,
    'memory': ScoreBasedGameType,
}

def get_game_type(game_type):

    game_class = GAME_TYPES.get(
        game_type.key
    )

    if not game_class:
        raise ValueError(
            f"Unknown game type: {game_type.key}"
        )

    return game_class