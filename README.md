# Rock, Paper, Scissors, Lizard, Spock API

This project implements an API for playing the extended version of the classic game "Rock, Paper, Scissors", as
popularized on the TV show "The Big Bang Theory". The game is called **Rock, Paper, Scissors, Lizard, Spock**, which
adds two extra moves, **Lizard** and **Spock**, to the traditional game.

## Features

- **Play the Game against the computer**: Players can make their choices (Rock, Paper, Scissors, Lizard, Spock) and play
  against a computer. The API will return the result of the match (whether Player 1 wins, computer wins, or if it’s a
  tie).
- **Play against another player**: Two players can also play one against the other by using multyplayer_game endpoints.
  Check them out!
- **Scoreboard**: The API can provide a history of previous games played, including choices made by both players and the
  result.

## Game Rules

Here are the extended rules for the game:

- **Rock** crushes **Scissors**.
- **Scissors** cuts **Paper**.
- **Paper** covers **Rock**.
- **Rock** crushes **Lizard**.
- **Lizard** poisons **Spock**.
- **Spock** smashes **Scissors**.
- **Scissors** decapitates **Lizard**.
- **Lizard** eats **Paper**.
- **Paper** disproves **Spock**.
- **Spock** vaporizes **Rock**.

Each move can defeat two other moves, and each move can be defeated by two other moves. The game is designed to reduce
the chances of a tie.

## How to run

Game API is dockerized, which means that running it is really easy! Just follow these steps:

1. Add .env file, that contains needed environment variables

```
DB_NAME=gamedb
DB_USER=admin
DB_PASS=sadga8sd46a5s1g98awed
DB_HOST=postgres
DB_PORT=5432

DJANGO_SECRET_KEY=django-insecure-4^4%0^8djj@i#^=bzxh=)0v-xd&$5*rm1#l&cos@z7#tyujj4t
DEBUG=False
```

2. Run `docker compose build` to build needed images
3. Run `docker compose up -d` to run services
4. Run `docker compose run game_api python manage.py migrate` to run needed db migrations
5. Go to http://localhost:8000/schema/swagger-ui (or whatever you set in the .env file) and check out all the endpoints.
   You can use them to play freely, no user registration needed.
