import json
import uuid

import mock
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from gameapi.constants import id_to_choice, Result, GameChoices
from gameapi.factories import OutcomeFactory, MultiplayerGameFactory
from gameapi.models import MultiplayerGame


class APITest(APITestCase):
    @pytest.mark.django_db
    def test_choices(self):
        url = reverse("choices")
        response = self.client.get(url)

        for choice in response.data:
            self.assertEqual(choice["name"], id_to_choice[choice["id"]].value)

    @pytest.mark.django_db
    def test_choice(self):
        url = reverse("choice")
        with mock.patch(
            "gameapi.api.v1.views.get_random_choice",
            return_value=GameChoices.ROCK,
        ):
            response = self.client.get(url)
        choice = response.data
        self.assertEqual(choice["name"], id_to_choice[choice["id"]].value)

    @pytest.mark.django_db
    def test_play(self):
        url = reverse("play")
        test_cases = [
            (2, 1, Result.WIN.value),
            (2, 2, Result.TIE.value),
            (1, 2, Result.LOSE.value),
        ]

        for player, computer, result in test_cases:
            data = {"player": player}

            with mock.patch(
                "gameapi.api.v1.views.get_random_choice",
                return_value=id_to_choice[computer],
            ):
                response = self.client.post(
                    path=url,
                    data=json.dumps(data, default=str),
                    content_type="application/json",
                )
                response_json = response.json()
            self.assertEqual(response_json["results"], result)
            self.assertEqual(response_json["player"], player)
            self.assertEqual(response_json["computer"], computer)

    def test_scoreboard(self):
        url = reverse("scoreboard")

        # Create 11 random outcomes
        for _ in range(11):
            outcome = OutcomeFactory(game=None)
            outcome.save()

        response = self.client.get(
            path=url,
        )
        response_json = response.json()

        # check to see if the only 10 Outcomes are returned
        self.assertEqual(len(response_json), 10)

        # Delete the scoreboard
        self.client.delete(path=url)

        # Check that 0 outcomes are returned
        response = self.client.get(
            path=url,
        )
        response_json = response.json()

        self.assertEqual(len(response_json), 0)

    def test_create_game(self):
        url = reverse("create_game")

        # creating a game
        response = self.client.post(
            path=url,
            data=None,
            content_type="application/json",
        )
        player_1_uuid = response.json()["player_uuid"]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MultiplayerGame.objects.count(), 1)
        game = MultiplayerGame.objects.first()
        self.assertEqual(player_1_uuid, str(game.player_1_uuid))
        self.assertEqual(game.waiting_another_player, True)

        # Creating a game for 2nd player, it should return the same game, only uuid for second player
        response = self.client.post(
            path=url,
            data=None,
            content_type="application/json",
        )
        player_2_uuid = response.json()["player_uuid"]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MultiplayerGame.objects.count(), 1)
        self.assertEqual(player_2_uuid, str(game.player_2_uuid))
        game.refresh_from_db()
        self.assertEqual(game.waiting_another_player, False)

        # testing if it will create multiple games for 4 more players, meaning 2 more games
        for _ in range(4):
            self.client.post(
                path=url,
                data=None,
                content_type="application/json",
            )
        self.assertEqual(MultiplayerGame.objects.count(), 3)

    def test_multiplayer_game(self):
        # Initializing data
        player_1_uuid = uuid.uuid4()
        player_2_uuid = uuid.uuid4()
        url_player_1 = reverse(
            "multiplayer_game", kwargs={"player_uuid": player_1_uuid}
        )
        url_player_2 = reverse(
            "multiplayer_game", kwargs={"player_uuid": player_2_uuid}
        )
        request_data = json.dumps({"player": 1}, default=str)

        # Game doesn't exist, testing 404 for game status
        response = self.client.get(path=url_player_1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Game doesn't exist, testing 404 for non-existent user play
        response = self.client.post(
            path=url_player_1,
            data=request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # create a game manually with defined player uuids
        game = MultiplayerGameFactory(
            player_1_uuid=player_1_uuid, player_2_uuid=player_2_uuid
        )
        game.save()

        # First valid request for player 1
        response = self.client.post(
            path=url_player_1,
            data=request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Second valid request for player 2, but repeated - testing 405
        response = self.client.post(
            path=url_player_1,
            data=request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Valid play for player 2
        response = self.client.post(
            path=url_player_2,
            data=request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test if both responses match for the same game
        response_1 = self.client.get(path=url_player_1).json()
        response_2 = self.client.get(path=url_player_2).json()

        self.assertEqual(response_1, response_2)
        self.assertEqual(len(response_1["outcomes"]), 1)
