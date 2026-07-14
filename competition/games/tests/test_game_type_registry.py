from django.test import TestCase
from types import SimpleNamespace

from games.game_types.registry import (
    get_game_type,
)

from games.game_types.quiz import QuizGameType
from games.game_types.puzzle import PuzzleGameType
from games.game_types.math import MathGameType
from games.game_types.memory import MemoryGameType


class GameTypeRegistryTest(TestCase):

    def test_get_quiz_game_type(self):

        game_type = SimpleNamespace(
            key="quiz",
        )

        self.assertIs(
            get_game_type(game_type),
            QuizGameType,
        )


    def test_get_puzzle_game_type(self):

        game_type = SimpleNamespace(
            key="puzzle",
        )

        self.assertIs(
            get_game_type(game_type),
            PuzzleGameType,
        )


    def test_get_math_game_type(self):

        game_type = SimpleNamespace(
            key="math",
        )

        self.assertIs(
            get_game_type(game_type),
            MathGameType,
        )


    def test_get_memory_game_type(self):

        game_type = SimpleNamespace(
            key="memory",
        )

        self.assertIs(
            get_game_type(game_type),
            MemoryGameType,
        )


    def test_unknown_game_type_raises_error(self):

        game_type = SimpleNamespace(
            key="unknown",
        )

        with self.assertRaises(ValueError):

            get_game_type(
                game_type,
            )