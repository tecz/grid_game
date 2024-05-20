# Grid Game

## Setup

In terminal, enter the virtual environment by running

```bash
  source .venv/bin/activate
```

From there, install the required dependencies using

```bash
pip install -r requirements.txt
```

To run the game, start the FastAPI server using uvicorn:

```bash
uvicorn main:app --reload
```

## Usage

### Create game
To create a new game, send a POST request to http://localhost:8000/games

### Retrieve game
To retrieve a game, send a GET request to http://localhost:8000/games/{id}.
The response will include the player's current position, health, remaining moves, the layout of the board, and the start and end positions for that game.

### Make moves
To make a move, send a POST request to http://localhost:8000/games/{id}/move with a JSON payload in the following format:

```json
{
  "direction": "up"
}
```

where the direction is one of the four possible move directions (up, down, left, right).

## Documentation

FastAPI automatically creates documentation which is accessible at http://localhost:8000/docs provided the server is running.
