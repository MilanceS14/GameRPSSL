import factory

from gameapi.constants import Result, id_to_choice
from gameapi.models import MultiplayerGame, Outcome


class MultiplayerGameFactory(factory.Factory):
    class Meta:
        model = MultiplayerGame


class OutcomeFactory(factory.Factory):
    class Meta:
        model = Outcome

    game = factory.SubFactory(MultiplayerGameFactory)
    result = factory.Faker(
        "random_element", elements=[result.value for result in Result]
    )
    player_1_choice = factory.Faker("random_int", min=1, max=len(id_to_choice))
    player_2_choice = factory.Faker("random_int", min=1, max=len(id_to_choice))
