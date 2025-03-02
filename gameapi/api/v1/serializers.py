from rest_framework import serializers

from gameapi.constants import id_to_choice
from gameapi.models import Outcome, MultiplayerGame


class ChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.ChoiceField(
        choices=[choice.value for choice in id_to_choice.values()]
    )


class PlayInputSerializer(serializers.Serializer):
    player = serializers.ChoiceField(choices=range(1, len(id_to_choice) + 1, 1))


class PlayOutputSerializer(serializers.ModelSerializer):
    results = serializers.CharField(source="result")
    player = serializers.IntegerField(source="player_1_choice")
    computer = serializers.IntegerField(source="player_2_choice")

    class Meta:
        model = Outcome
        fields = ["results", "player", "computer"]


class OutcomeSerializer(serializers.ModelSerializer):
    results = serializers.CharField(source="result")
    player_1 = serializers.IntegerField(source="player_1_choice")
    player_2 = serializers.IntegerField(source="player_2_choice")

    class Meta:
        model = Outcome
        fields = ["results", "player_1", "player_2"]


class GameSerializer(serializers.ModelSerializer):
    player_1_uuid = serializers.UUIDField()
    player_2_uuid = serializers.UUIDField()
    outcomes = OutcomeSerializer(many=True)

    class Meta:
        model = MultiplayerGame
        fields = ["player_1_uuid", "player_2_uuid", "outcomes"]


class PlayerSerializer(serializers.Serializer):
    player_uuid = serializers.UUIDField()
