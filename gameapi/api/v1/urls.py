from django.urls import path

from gameapi.api.v1.views import (
    ChoicesView,
    PlayView,
    ChoiceView,
    ScoreboardView,
    PlayGameView,
    CreateGameView,
)

urlpatterns = [
    path("choices", ChoicesView.as_view(), name="choices"),
    path("choice", ChoiceView.as_view(), name="choice"),
    path("play", PlayView.as_view(), name="play"),
    path("scoreboard", ScoreboardView.as_view(), name="scoreboard"),
    path("multiplayer_game", CreateGameView.as_view(), name="create_game"),
    path(
        "multiplayer_game/<uuid:player_uuid>",
        PlayGameView.as_view(),
        name="multiplayer_game",
    ),
]
