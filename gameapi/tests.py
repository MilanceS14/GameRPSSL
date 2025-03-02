import uuid

import pytest

from gameapi.constants import GameChoices, Result
from gameapi.factories import MultiplayerGameFactory
from gameapi.utils import (
    did_player_1_win,
    get_result_from_bool,
    find_game_by_player_uuid,
)


@pytest.mark.parametrize(
    "player_1_choice, player_2_choice, expected",
    [
        # paper
        (GameChoices.PAPER, GameChoices.PAPER, None),
        (GameChoices.PAPER, GameChoices.ROCK, True),
        (GameChoices.PAPER, GameChoices.LIZARD, False),
        (GameChoices.PAPER, GameChoices.SPOCK, True),
        (GameChoices.PAPER, GameChoices.SCISSORS, False),
        # rock
        (GameChoices.ROCK, GameChoices.PAPER, False),
        (GameChoices.ROCK, GameChoices.ROCK, None),
        (GameChoices.ROCK, GameChoices.LIZARD, True),
        (GameChoices.ROCK, GameChoices.SPOCK, False),
        (GameChoices.ROCK, GameChoices.SCISSORS, True),
        # lizard
        (GameChoices.LIZARD, GameChoices.PAPER, True),
        (GameChoices.LIZARD, GameChoices.ROCK, False),
        (GameChoices.LIZARD, GameChoices.LIZARD, None),
        (GameChoices.LIZARD, GameChoices.SPOCK, True),
        (GameChoices.LIZARD, GameChoices.SCISSORS, False),
        # spock
        (GameChoices.SPOCK, GameChoices.PAPER, False),
        (GameChoices.SPOCK, GameChoices.ROCK, True),
        (GameChoices.SPOCK, GameChoices.LIZARD, False),
        (GameChoices.SPOCK, GameChoices.SPOCK, None),
        (GameChoices.SPOCK, GameChoices.SCISSORS, True),
        # scissors
        (GameChoices.SCISSORS, GameChoices.PAPER, True),
        (GameChoices.SCISSORS, GameChoices.ROCK, False),
        (GameChoices.SCISSORS, GameChoices.LIZARD, True),
        (GameChoices.SCISSORS, GameChoices.SPOCK, False),
        (GameChoices.SCISSORS, GameChoices.SCISSORS, None),
    ],
)
def test_player_choice(
    player_1_choice: GameChoices, player_2_choice: GameChoices, expected: None | bool
):
    assert did_player_1_win(player_1_choice, player_2_choice) == expected


@pytest.mark.parametrize(
    "result, expected", [(True, Result.WIN), (False, Result.LOSE), (None, Result.TIE)]
)
def test_get_result_from_bool(result, expected):
    assert get_result_from_bool(result) == expected


@pytest.mark.django_db
def test_find_game_by_player_uuid():
    game_1 = MultiplayerGameFactory()
    game_2 = MultiplayerGameFactory()
    game_3 = MultiplayerGameFactory()

    # uuid that doesn't exist
    found_game = find_game_by_player_uuid(uuid.uuid4())
    assert found_game is None

    # checking if filter for player_1_uuid works
    found_game = find_game_by_player_uuid(game_2.player_1_uuid)
    assert found_game is not None
    assert found_game.id == game_2.id

    # checking if filter for player_2_uuid works
    found_game = find_game_by_player_uuid(game_3.player_2_uuid)
    assert found_game is not None
    assert found_game.id == game_3.id
