import random
import uuid

from django.db.models import Q

from gameapi.constants import GameChoices, Result
from gameapi.models import MultiplayerGame

win_transition = {
    GameChoices.PAPER: {GameChoices.ROCK, GameChoices.SPOCK},
    GameChoices.ROCK: {GameChoices.LIZARD, GameChoices.SCISSORS},
    GameChoices.LIZARD: {GameChoices.SPOCK, GameChoices.PAPER},
    GameChoices.SPOCK: {GameChoices.SCISSORS, GameChoices.ROCK},
    GameChoices.SCISSORS: {GameChoices.LIZARD, GameChoices.PAPER},
}


def did_player_1_win(
    player_1_choice: GameChoices, player_2_choice: GameChoices
) -> None | bool:
    if player_1_choice == player_2_choice:
        return None
    if player_2_choice in win_transition.get(player_1_choice, {}):
        return True
    return False


def get_result_from_bool(result: bool | None) -> Result:
    game_outcome = (
        Result.WIN if result else Result.LOSE if result is not None else Result.TIE
    )
    return game_outcome


def get_random_choice() -> GameChoices:
    return random.choice(list(win_transition.keys()))


def find_game_by_player_uuid(player_uuid: uuid.UUID) -> MultiplayerGame | None:
    return MultiplayerGame.objects.filter(
        Q(player_1_uuid=player_uuid) | Q(player_2_uuid=player_uuid)
    ).first()
