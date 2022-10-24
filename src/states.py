from enum import Enum, auto


class GameStates(Enum):
    Guess = auto()
    Correct = auto()
    Incorrect = auto()
    Neutral = auto()
