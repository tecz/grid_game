# Grid Game

## Setup

In the terminal (OSX/Linux), enter the virtual environment by running

```bash
source .venv/bin/activate
```

From the virtual environment, install the required dependencies using

```bash
pip install -r requirements.txt
```

To run the game, start the FastAPI server using uvicorn while still in the virtual env:

```bash
uvicorn main:app --reload
```

## Usage

### Create game
To create a new game, send a POST request to the endpoint at http://localhost:8000/games.

The return value is the ID of the newly created game.

### Retrieve game
To retrieve a game, send a GET request to http://localhost:8000/games/{id}, where {id} is the value of the game you are looking up.

The response will include the player's current position, health, remaining moves, the layout of the board, and the start and end positions for that game.

### Make moves
To make a move, send a POST request to http://localhost:8000/games/{id}/move with a JSON payload in the following format:

```json
{
  "direction": "up"
}
```

where the direction is one of the four possible move directions (up, down, left, right).

This endpoint will return the following information after a successful move: the type of tile the player landed on, their new position, remaining moves, remaining health, health lost, moves lost, and the winning end position.

## Documentation

FastAPI automatically creates documentation which is accessible at http://localhost:8000/docs provided the server is running. The FastAPI documentation site can also be used to access and test the API endpoints.
