# 6.009 Lab 2: Snekoban

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def deep_copy(game):
    """
    Returns a deep copy of the internal game representation
    """
    return {'rows': game['rows'], 'cols': game['cols'],
        'walls': game['walls'].copy(), 'targets': game['targets'].copy(),
         'computers': game['computers'].copy(), 'player': game['player']}

def new_game(level_description):
    """
    Given a description of a game state, create and return an alternate
    game representation for internal use

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    Returns a dictionary containing the following:
      * 'rows' (int) : the number of rows in the board
      * 'cols' (int) : the number of columns in the board
      * 'walls' (set) : a set containing the coordinates of each wall
      * 'targets' (set) : a set containing the coordinates of each target
      * 'computers' (set) : a set containing the coordinates of each computer
      * 'player' (tuple) : a tuple of length 2 in the form (row, col)
        describing the index of the player's location

    Coordinates are in the form (r,c), where each is a tuple of length 2
    containing the row and column index of the object's location

    """

    board_rows = len(level_description)
    board_cols = len(level_description[0])

    walls = set()
    targets = set()
    computers = set()
    player = (0,0)

    for r, row in enumerate(level_description):
        for c, cell in enumerate(row):
            if 'wall' in cell:
                walls.add((r,c))
            if 'target' in cell:
                targets.add((r,c))
            if 'computer' in cell:
                computers.add((r,c))
            if 'player' in cell:
                player = (r,c)

    return {'rows': board_rows, 'cols': board_cols, 'walls': walls,
        'targets': targets, 'computers': computers, 'player': player}



def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """

    return (game['targets'] == game['computers'] and len(game['targets']) > 0)


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    player_row, player_col = game['player']

    dir_r, dir_c = direction_vector[direction]

    new_loc = (player_row+dir_r, player_col + dir_c)

    new_board = deep_copy(game)

    # if there's a wall, don't move
    if new_loc in game['walls']:
        return game


    if (new_loc in game['computers']):

        extended_loc = (player_row+dir_r*2, player_col + dir_c*2)
        # if there's a second computer or a wall behind, don't move
        if (extended_loc in game['computers']) or (extended_loc in game['walls']):
            return game
        else: # otherwise push the computer
            new_board['computers'].remove(new_loc)
            new_board['computers'].add(extended_loc)

    new_board['player'] = new_loc

    return new_board


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """

    board = []

    for r in range(game['rows']):
        row = []
        for c in range(game['cols']):
            cell = []
            if (r,c) in game['walls']:
                cell.append('wall')
            if (r,c) in game['targets']:
                cell.append('target')
            if (r,c) in game['computers']:
                cell.append('computer')
            if (r,c) == game['player']:
                cell.append('player')
            row.append(cell)
        board.append(row)
    return board

def pare_and_freeze(game):
    """
    Extracts the computer locations and player location from the internal
    game description, freezes the set of computer locations, and returns
    a tuple containing both, hereby referred to as a "state".

    The value it returns is immutable, thus can be added to the visited_states
    set.

    For the purposes of checking visited states, the computers and player
    are the only relevant objects to save since the walls and targets do
    not move.

    """
    return (frozenset(game['computers']), game['player'])

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game),
    conducts a Breadth-First Search to find a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """

    # Initializes a set containing visited states, an agenda containing
    # pared game representation paths, and an agenda containing direction paths

    state = pare_and_freeze(game)
    visited_states = {state}

    state_agenda = [(state,)] # Contains paths of computers-player states
    direction_agenda = [()] # Contains paths of direction strings

    if victory_check(game):
        return []

    while state_agenda:

        # Retrieves the first path on the agenda and gets the terminal vertex
        # Each vertex is a computers-player state
        state_path = state_agenda.pop(0)
        terminal_state = state_path[-1]

        # Also retrieves the corresponding direction path
        player_path = direction_agenda.pop(0)

        for direction in direction_vector:
            # Restore terminal state to full game representation
            terminal_game = {'rows': game['rows'], 'cols': game['cols'],
                'walls': game['walls'], 'targets': game['targets'],
                'computers': set(terminal_state[0]), 'player': terminal_state[1]}

            child_game = step_game(terminal_game, direction)
            child_state = pare_and_freeze(child_game)

            if victory_check(child_game):
                directions_list = list(player_path)
                directions_list.append(direction)
                return directions_list

            if child_state not in visited_states:

                # Appends a new path containing the old path + child vertex
                # to the agenda
                child_state_path = state_path + (child_state,)
                state_agenda.append(child_state_path)

                child_player_path = player_path + (direction,)
                direction_agenda.append(child_player_path)

                visited_states.add(child_state)

    return None



if __name__ == "__main__":
    pass
