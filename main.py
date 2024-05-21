from fastapi import FastAPI
from pydantic import BaseModel
from collections import deque
import random

app = FastAPI()

# Models
class GameState(BaseModel):
    player_position: tuple
    board: list
    health: int
    moves: int
    end_position: tuple

class Move(BaseModel):
    direction: str

# Game storage
games = {}

# Utility functions
def initialize_board():
    """
    Create a new game board with random cell types.

    The board is a 50x50 grid, where each cell can be one of the following types:
    - "Blank": No effect on health, reduces moves by one.
    - "Speeder": Reduces health by 5, no effect on moves.
    - "Lava": Reduces health by 50 and moves by 10.
    - "Mud": Reduces health by 10 and moves by 5.

    The board is initalized with a random number of between 200 and 400 of each non-blank tile type.

    Returns:
        list: The initialized game board.
    """
    board = [["Blank" for _ in range(50)] for _ in range(50)]
    tile_types = ["Speeder", "Lava", "Mud"]
    tile_counts = {
        # 200-400 range of each made >= 90% of puzzles solvable
        "Speeder": random.randint(200, 400),
        "Lava": random.randint(200, 400),
        "Mud": random.randint(200, 400)
    }

    for tile_type, count in tile_counts.items():
        while count > 0:
            row, col = random.randint(0, 49), random.randint(0, 49)
            if board[row][col] == "Blank":
                board[row][col] = tile_type
                count -= 1

    return board

def update_game_state(game, row, col):
    """
    Update the game state based on the cell type the player lands on.

    Args:
        game (GameState): The current game state.
        row (int): The row index of the cell the player landed on.
        col (int): The column index of the cell the player landed on.
    """
    cell_type = game.board[row][col]
    if cell_type == "Blank":
        game.health += 0
        game.moves -= 1
    elif cell_type == "Speeder":
        game.health -= 5
        game.moves -= 0
    elif cell_type == "Lava":
        game.health -= 50
        game.moves -= 10
    elif cell_type == "Mud":
        game.health -= 10
        game.moves -= 5

    game.player_position = (row, col)

# API endpoints
@app.post("/games")
def create_game():
    """
    Create a new game and return the game ID.

    The starting position is randomly selected on the left side of the board,
    and the ending position is randomly selected on the right side of the board.

    Returns:
        dict: A dictionary containing the game ID.
    """
    game_id = str(len(games))
    rows = 50
    cols = 50
    start_row, start_col = random.randint(0, rows - 1), 0
    end_row, end_col = random.randint(0, rows - 1), cols - 1

    board = initialize_board()
    board[start_row][start_col] = "Start"
    board[end_row][end_col] = "End"

    games[game_id] = GameState(
        player_position=(start_row, start_col),
        board=board,
        health=200,
        moves=450,
        end_position=(end_row, end_col)
    )

    return {"game_id": game_id}

@app.get("/games/{game_id}")
def get_game_state(game_id: str):
    """
    Retrieve the current state of a game.

    Args:
        game_id (str): The ID of the game to retrieve.

    Returns:
        dict: A dictionary containing the game state, including the player position,
        board configuration, remaining health, remaining moves, start position, and end position.
    """
    if game_id not in games:
        return {"error": "Game not found"}
    game = games[game_id]
    rows = len(game.board)
    cols = len(game.board[0])
    start_position = None
    end_position = None
    for i in range(rows):
        if game.board[i][0] == "Start":
            start_position = (i, 0)
        if game.board[i][cols - 1] == "End":
            end_position = (i, cols - 1)
        if start_position and end_position:
            break
    return {
        "player_position": game.player_position,
        "board": game.board,
        "health": game.health,
        "moves": game.moves,
        "start_position": start_position,
        "end_position": end_position
    }

@app.post("/games/{game_id}/move")
def make_move(game_id: str, move: Move):
    """
    Handle a player move and update the game state accordingly.

    Args:
        game_id (str): The ID of the game.
        move (Move): The move to be made, specified by the direction ("up", "down", "left", "right").

    Returns:
        dict: A dictionary containing the result of the move, including the type of tile
        the player landed on, their new position, remaining moves, remaining health,
        health lost, moves lost, end position, and a message indicating the outcome.
    """
    if game_id not in games:
        return {"error": "Game not found"}
    game = games[game_id]
    row, col = game.player_position
    if move.direction == "up":
        row = max(0, row - 1)
    elif move.direction == "down":
        row = min(len(game.board) - 1, row + 1)
    elif move.direction == "left":
        col = max(0, col - 1)
    elif move.direction == "right":
        col = min(len(game.board[0]) - 1, col + 1)
    else:
        return {"error": "Invalid move"}

    tile_type = game.board[row][col]
    health_before = game.health
    moves_before = game.moves
    update_game_state(game, row, col)
    health_lost = health_before - game.health
    moves_lost = moves_before - game.moves

    if game.health <= 0 or game.moves <= 0:
        return {
            "tile_type": tile_type,
            "new_position": (row, col),
            "health_lost": health_lost,
            "moves_lost": moves_lost,
            "end_position": game.end_position,
            "message": "Game over, you lost!"
        }
    if (row, col) == game.end_position:
        return {
            "tile_type": tile_type,
            "new_position": (row, col),
            "end_position": game.end_position,
            "message": "You won!"
        }

    return {
        "tile_type": tile_type,
        "new_position": (row, col),
        "remaining_moves": game.moves,
        "remaining_health": game.health,
        "health_lost": health_lost,
        "moves_lost": moves_lost,
        "end_position": game.end_position,
        "message": f"Move successful. You landed in {tile_type} and lost {health_lost} health and {moves_lost} moves."
    }

@app.get("/games/{game_id}/winning_path")
def check_winning_path(game_id: str):
    """
    Check if a winning path exists for the current game board using breadth-first search (BFS).

    Args:
        game_id (str): The ID of the game.

    Returns:
        dict: A dictionary indicating whether a winning path exists.
    """
    if game_id not in games:
        return {"error": "Game not found"}
    game = games[game_id]

    def find_winning_path(board, start, end, health, moves):
        rows = len(board)
        cols = len(board[0])
        visited_tiles = set()  # track visited positions
        queue = deque([(start, health, moves)])  # BFS queue

        # Breadth-first search to find a winning path:
        # explores all possible paths starting from the player's position and iteratively
        # moves to adjacent tiles based on the remaining health and moves available until
        # it reaches the end, runs out of health/moves, or explores all possible paths
        while queue:
            (row, col), health, moves = queue.popleft()  # get next position from the queue
            if (row, col) == end:
                return True # winning path found
            if health <= 0 or moves <= 0:
                continue    # skip this position if health or moves run out
            if (row, col) in visited_tiles:
                continue    # skip this position if already visited

            visited_tiles.add((row, col)) # mark position as visited

            # explore adjacent tiles (right, left, down, up)
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < rows and 0 <= new_col < cols: # check if new position is within the board
                    tile_type = board[new_row][new_col]
                    if tile_type == "Speeder":
                        new_health = health - 5
                        new_moves = moves
                    elif tile_type == "Lava":
                        new_health = health - 50
                        new_moves = moves - 10
                    elif tile_type == "Mud":
                        new_health = health - 10
                        new_moves = moves - 5
                    else:
                        new_health = health
                        new_moves = moves - 1

                    queue.append(((new_row, new_col), new_health, new_moves))   # add new position to the queue

        return False    # no winning path was found

    start = game.player_position
    end = game.end_position
    health = game.health
    moves = game.moves

    winning_path_exists = find_winning_path(game.board, start, end, health, moves)

    return {"winning_path_exists": winning_path_exists}
