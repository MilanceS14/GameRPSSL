import uuid
from dataclasses import dataclass

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from gameapi.constants import GameChoices, choice_to_id, Result


@dataclass(frozen=True)
class Choice:
    id: int
    name: str

    @classmethod
    def get_all_choices(cls) -> list["Choice"]:
        return [cls(_id, choice.value) for choice, _id in choice_to_id.items()]

    @classmethod
    def from_game_choice(cls, game_choice: GameChoices) -> "Choice":
        return cls(choice_to_id[game_choice], game_choice.value)


class MultiplayerGame(models.Model):
    player_1_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    player_2_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    waiting_another_player = models.BooleanField(default=True)
    player_1_choice = models.IntegerField(
        validators=[MaxValueValidator(len(choice_to_id)), MinValueValidator(1)],
        null=True,
        blank=True,
    )
    player_2_choice = models.IntegerField(
        validators=[MaxValueValidator(len(choice_to_id)), MinValueValidator(1)],
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Outcome(models.Model):
    game = models.ForeignKey(
        MultiplayerGame, related_name="outcomes", on_delete=models.PROTECT, null=True
    )
    result = models.CharField(
        max_length=255,
        choices=[(value, value) for value in Result],
        null=False,
        blank=False,
    )
    player_1_choice = models.IntegerField(
        validators=[MaxValueValidator(len(choice_to_id)), MinValueValidator(1)]
    )
    player_2_choice = models.IntegerField(
        validators=[MaxValueValidator(len(choice_to_id)), MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
