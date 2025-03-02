from enum import Enum


class Result(Enum):
    WIN = "win"
    LOSE = "lose"
    TIE = "tie"


class GameChoices(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"
    SPOCK = "spock"
    LIZARD = "lizard"


choice_to_id = {
    GameChoices.ROCK: 1,
    GameChoices.PAPER: 2,
    GameChoices.SCISSORS: 3,
    GameChoices.SPOCK: 4,
    GameChoices.LIZARD: 5,
}

id_to_choice = {value: key for key, value in choice_to_id.items()}
