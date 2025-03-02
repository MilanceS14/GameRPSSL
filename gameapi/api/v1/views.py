from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from gameapi.api.v1.serializers import (
    ChoiceSerializer,
    PlayInputSerializer,
    PlayOutputSerializer,
    PlayerSerializer,
    GameSerializer,
)
from gameapi.constants import choice_to_id, id_to_choice
from gameapi.models import Choice, Outcome, MultiplayerGame
from gameapi.utils import (
    get_random_choice,
    did_player_1_win,
    find_game_by_player_uuid,
    get_result_from_bool,
)


class ChoicesView(APIView):

    @extend_schema(
        description="This endpoint will return a list of all valid choices",
        responses={status.HTTP_200_OK: ChoiceSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        data = Choice.get_all_choices()
        serializer = ChoiceSerializer(data, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ChoiceView(APIView):

    @extend_schema(
        description="This endpoint will return a randomly selected valid choice",
        responses={status.HTTP_200_OK: ChoiceSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        choice = get_random_choice()
        serializer = ChoiceSerializer(Choice.from_game_choice(choice))
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PlayView(APIView):
    serializer_class = PlayInputSerializer

    @extend_schema(
        description="This endpoint will return an outcome of a play with computer. Computer answer is randomly chosen",
        responses={
            status.HTTP_200_OK: PlayOutputSerializer(many=False),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request.",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = PlayInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player_choice_id = serializer.validated_data["player"]
        player_choice = id_to_choice[player_choice_id]

        random_choice = get_random_choice()
        result = did_player_1_win(player_choice, random_choice)
        game_outcome = get_result_from_bool(result)
        outcome = Outcome(
            result=game_outcome.value,
            player_1_choice=player_choice_id,
            player_2_choice=choice_to_id[random_choice],
        )
        outcome.save()
        serializer = PlayOutputSerializer(outcome)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ScoreboardView(APIView):
    @extend_schema(
        description="This endpoint will return the last 10 outcomes of the game",
        responses={200: PlayOutputSerializer(many=False)},
    )
    def get(self, request, *args, **kwargs):
        last_10_outcomes = Outcome.objects.all().order_by("-created_at")[:10]
        data = PlayOutputSerializer(last_10_outcomes, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="This endpoint will restart the scoreboard by deleting all outcomes",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                response=None, description="Data is deleted"
            )
        },
    )
    def delete(self, request, *args, **kwargs):
        # TODO: Possible improvement would be to create a cron job that would periodically delete Outcomes
        #  that aren't used for scoreboard (last 10 Outcomes)
        Outcome.objects.all().delete()
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)


class CreateGameView(APIView):
    @extend_schema(
        description="This endpoint will pair two players for the same game. First request will create a game with two "
        "unique uuids for 2 players, and return the uuid for the first one. The second request will locate "
        "the game that is waiting for another player and return the second player_uuid",
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=PlayerSerializer,
            )
        },
    )
    def post(self, request, *args, **kwargs):
        # TODO: Possible improvement for the multiplayer game is to add an idempotency key for game creation
        #  (repeated request with the same idempotency key will return the same player_uuid). Or changing to only
        #  allowing signed in users to play
        with transaction.atomic():
            game, created = MultiplayerGame.objects.select_for_update().get_or_create(
                waiting_another_player=True
            )
            if not created:
                game.waiting_another_player = False
                game.save(update_fields=["waiting_another_player"])
        player_uuid = game.player_1_uuid if created else game.player_2_uuid
        serializer = PlayerSerializer(data={"player_uuid": player_uuid})
        serializer.is_valid(raise_exception=True)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PlayGameView(APIView):
    @extend_schema(
        description="This endpoint will return all outcomes for a valid player_uuid. The correct user could be checked "
        "in the response (both player's uuids are accounted for). The result of an outcome is taken from "
        "the perspective of the player 1",
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=GameSerializer),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=None, description="Not found."
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        # TODO: Possible improvement would be to change the outcome result to the perspective of the player who
        #  requested the results
        player_uuid = kwargs.get("player_uuid")
        game = find_game_by_player_uuid(player_uuid)
        if not game:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"error": "Game not found"}
            )
        serializer = GameSerializer(game)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @extend_schema(
        request=PlayInputSerializer,
        description="This endpoint is used for multiplayer games. For one round, player is allowed only one answer "
        "(repeated request either the same or different for the same round will be ignored). When both "
        "players have played, it will create an Outcome, and allow for another round to be played.",
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=None,
                description="Both answers are present. This round is finished.",
            ),
            status.HTTP_202_ACCEPTED: OpenApiResponse(
                response=None,
                description="This is the first answer from the player. Answer is saved.",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=None, description="Not found."
            ),
            status.HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                response=None,
                description="Player already has an answer for this round.",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = PlayInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        choice_id = serializer.data["player"]
        player_uuid = kwargs.get("player_uuid")

        with transaction.atomic():
            game = find_game_by_player_uuid(player_uuid)
            if not game:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "Game not found"}
                )
            player_1_played = game.player_1_uuid == player_uuid
            player_1_choice_id = game.player_1_choice
            player_2_choice_id = game.player_2_choice

            if player_1_played:
                # We know that the player 1 has played, the question is does the player already have an answer or not
                if player_1_choice_id:
                    # if he has an answer we need to block the update of it. Answers can't be updated
                    # Also only the one who was the last to answer should create an Outcome
                    return Response(
                        status=status.HTTP_405_METHOD_NOT_ALLOWED, data=None
                    )
                if not player_2_choice_id:
                    # This is the first answer from player 1, and also player 2 hasn't played,
                    # we need to wait for player 2
                    game.player_1_choice = choice_id
                    game.save(update_fields=["player_1_choice"])
                    return Response(status=status.HTTP_202_ACCEPTED, data=None)
                # Both players played
                player_1_choice_id = choice_id

            else:
                # Same logic as for player 1
                if player_2_choice_id:
                    # player has already played
                    return Response(
                        status=status.HTTP_405_METHOD_NOT_ALLOWED, data=None
                    )
                if not player_1_choice_id:
                    # This is the first answer from player 2, and also player 1 hasn't played,
                    # we need to wait for player 2
                    game.player_2_choice = choice_id
                    game.save(update_fields=["player_2_choice"])
                    return Response(status=status.HTTP_202_ACCEPTED, data=None)
                # Both players played
                player_2_choice_id = choice_id

            result = did_player_1_win(
                id_to_choice[player_1_choice_id], id_to_choice[player_2_choice_id]
            )
            game_outcome = get_result_from_bool(result)
            Outcome.objects.create(
                game=game,
                player_1_choice=player_1_choice_id,
                player_2_choice=player_2_choice_id,
                result=game_outcome.value,
            )
            game.player_1_choice = None
            game.player_2_choice = None
            game.save(update_fields=["player_1_choice", "player_2_choice"])
        return Response(status=status.HTTP_201_CREATED, data=None)
