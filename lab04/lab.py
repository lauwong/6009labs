#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """

    return new_game_nd((num_rows, num_cols), bombs)

    # visible = []
    # board = []
    #
    # for row in range(num_rows):
    #     board.append([0] * num_cols)
    #     visible.append([False] * num_cols)
    #
    # for bomb in bombs:
    #     bomb_row, bomb_col = bomb
    #     board[bomb_row][bomb_col] = '.'
    #
    #     for r in range(-1, 2):
    #         for c in range(-1, 2):
    #             i_row = bomb_row + r
    #             i_col = bomb_col + c
    #             if (0 <= i_row < num_rows) and (0 <= i_col < num_cols):
    #                 if (i_row, i_col) not in bombs:
    #                     board[i_row][i_col] += 1
    #
    # return {
    #     'dimensions': (num_rows, num_cols),
    #     'board': board,
    #     'visible': visible,
    #     'state': 'ongoing'
    # }


def dig_2d(game, row, col, parent=True):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """

    return dig_nd(game, (row,col))
    # visible = game['visible']
    # board = game['board']
    # n_rows, n_cols = game['dimensions']
    #
    # if game['state'] == 'defeat' or game['state'] == 'victory':
    #     return 0
    #
    # if board[row][col] == '.':
    #     visible[row][col] = True
    #     game['state'] = 'defeat'
    #     return 1
    #
    # if visible[row][col]:
    #     return 0
    #
    # visible[row][col] = True
    # revealed = 1
    #
    # if board[row][col] == 0:
    #     for r in range(-1, 2):
    #         for c in range(-1, 2):
    #             i_row = row + r
    #             i_col = col + c
    #             if (0 <= i_row < n_rows) and (0 <= i_col < n_cols):
    #                 if board[i_row][i_col] != '.':
    #                     revealed += dig_2d(game, i_row, i_col, parent=False)
    #
    # if parent:
    #     visible_bombs = 0
    #     covered_squares = 0
    #     for r in range(n_rows):
    #         for c in range(n_cols):
    #             if board[r][c] == '.':
    #                 if visible[r][c] == True:
    #                     visible_bombs += 1
    #             elif visible[r][c] == False:
    #                 covered_squares += 1
    #     bad_squares = visible_bombs + covered_squares
    #
    #     if bad_squares == 0:
    #         game['state'] = 'victory'
    #
    # return revealed

def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)
    # display_board = []
    #
    # for row in range(game['dimensions'][0]):
    #     display_row = []
    #     for col in range(game['dimensions'][1]):
    #         if xray or game['visible'][row][col]:
    #             if game['board'][row][col] == 0:
    #                 display_row.append(' ')
    #             else:
    #                 display_row.append(str(game['board'][row][col]))
    #         else:
    #             display_row.append('_')
    #     display_board.append(display_row)
    #
    # return display_board

def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    locations_list = render_2d_locations(game, xray)

    temp_list = []
    for row in locations_list:
        row_string = ''.join(row)
        temp_list.append(row_string)

    return '\n'.join(temp_list)



# N-D IMPLEMENTATION
def construct_blank_board(dimensions, value):
    """
    Recursively creates a blank board given dimensions filled with a given value

    Parameters:
        * dimensions (tuple) : the dimensions to construct the board with,
            a tuple of length n will be an n-dimensional board
        * value : the default value to fill the board with
    Returns:
        A board of the specified dimensions where each item is the given value
    """

    # Base case: if no further dimensions, return the value to fill the board with
    if not dimensions:
        return value

    # Retrieves the board constructed from all deeper dimensions,
    # duplicates it dimension[0] times, and returns it all in another list
    board = construct_blank_board(dimensions[1:], value)
    return [board for i in range(dimensions[0])]

def set_value(board, location, value=None, dim=0):
    """
    Recursively sets the item at a specific coordinate to the given value or
    increments it by 1

    Parameters:
        * board (list) : an n-dimensional list containing the item to change
        * location (tuple) : the coordinates of the item to change
        * value : the new value of the item
            * if value is specified, set the item to the given value
            * if value is not specified, assume that it is the neighbor to a
                bomb and increment the value of the space by 1 instead
        * dim (int) : the current recursion depth

    Returns:
        A new board with the item at index location changed to value
    """

    # Base case: if the depth has reached the final dimension
    # board is now an int or string, perform the value change on it
    if dim == len(location):
        if value:
            board = value
        else:
            board += 1
        return board

    # Gets the inner list where the value has been set
    new_board = set_value(board[location[dim]], location, value=value, dim=dim+1)

    # Duplicates the board and sets the value at the given index to the new inner board
    dupe_board = board[:]
    dupe_board[location[dim]] = new_board

    return dupe_board

def get_value(board, location, dim=0):
    """
    Retrieves the value from board at a specific coordinate

    Parameters:
        * board (list) : an n-dimensional list containing the item to get
        * location (tuple) : the coordinates of the item to retrieve
        * dim (int) : the current recursion depth

    Returns:
        The value of the item at index location in board
    """
    # Base case: if the depth has reached the final dimension
    # Return the discovered value
    if dim == len(location):
        return board

    # Gets the value of the nested list at the index specified by the dim
    return get_value(board[location[dim]], location, dim=dim+1)

def generate_neighbors(loc, dimensions, neighbors=set(), dim=0):
    """
    Generates a list of neighboring coordinates to a given coordinate

    Parameters:
        * loc (tuple) : the location to get the neighbors of
        * dimensions (tuple) : the dimensions of the board to get the neighbors from
        * neighbors (set) : the current set of neighbors
        * dim (int) : the current recursion depth

    Returns:
        A list of all neighbors for a given coordinate
    """

    # Base case: if the depth has reached the final dimension, all neighbors
    # are found, return the set of neighbors as a list
    if dim == len(dimensions):
        return list(neighbors)

    # Fill with loc so program can enter for loop
    if not neighbors:
        neighbors = {loc}

    new_neighbors = set()

    # For each coordinate currently in neighbors, replicate it 3 times
    # with the coordinate for the dimension specified by dim shifted by
    # each {-1, 0, 1}. Add the value to the set of new_neighbors
    for neighbor in neighbors:
        for i in range(-1,2):
            new_loc_i = neighbor[dim] + i
            if 0 <= new_loc_i < dimensions[dim]:
                new_loc = list(neighbor)
                new_loc[dim] = new_loc_i
                new_neighbors.add(tuple(new_loc))

    neighbors.update(new_neighbors)

    # Do this again for the next dimension
    return generate_neighbors(loc, dimensions, neighbors, dim=dim+1)

def fill_board(board, bombs, dimensions):
    """
    Fills an empty board with numbers and bombs given bomb coordinates

    Parameters:
        * board (list) : the current game board to populate with values
        * bombs (list) : a list of coordinates where the bombs are located
        * dimensions (tuple) : the dimensions of the board to get the neighbors for

    Returns:
        A board filled with '.'s at bomb locations and number of nearby bombs
        in non-bomb squares
    """

    for bomb in bombs:
        board = set_value(board, bomb, '.')
        neighbors = generate_neighbors(bomb, dimensions)

        for neighbor in neighbors:
            if neighbor not in bombs:
                board = set_value(board, neighbor)

    return board

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    blank_board = construct_blank_board(dimensions, 0)
    visible = construct_blank_board(dimensions, False)

    full_board = fill_board(blank_board, bombs, dimensions)

    return {
        'dimensions': dimensions,
        'board': full_board,
        'visible': visible,
        'state': 'ongoing'
    }

def count_bad_squares(board, visible, count=0):
    """
    Counts the number of visible bombs and covered safe squares on the board.
    This will be the victory check condition for the game, since if there are
    any visible bombs or covered safe squares, victory has not been achieved.

    Parameters:
        * board (list) : an n-dimensional board to search, contains the bombs
            and numbered squares
        * visible (list) : an n-dimensional board to search, contains the visible
            True/False values
    Returns:
        The number of visible bombs and covered safe squares
    """
    if type(board) != list:
        if (board == '.' and visible) or (board != '.' and not visible):
            return 1
        else:
            return 0

    # Recursively iterates through the entire board and adds the values to count
    for i in range(len(board)):
        count += count_bad_squares(board[i], visible[i])

    return count

def get_possible_coords(dimensions):
    """
    Gets all possible coordinates in a board for use in iteration

    Parameters:
        * dimensions (tuple) : the dimensions of the board

    Returns:
        * A list containing all possible coordinates of the board
    """

    # Base case: function has reached the final dimension
    # Returns a list [(0,), (1,)... (n,)] where n is the size of the final dimension
    if len(dimensions)==1:
        return [(i,) for i in range(dimensions[0])]

    # Gets all of the coordinates from the previous, deeper dimensions
    # and fills a new list with each coordinate replicated m times with an
    # additional value at the beginning from 0 to m-1
    # E.g. [(0,0,0), (1,0,0)... (m-1,0,0), (0,1,0)... (0,n,0)...]
    coords = get_possible_coords(dimensions[1:])
    coords_list = [(i,) + coord for i in range(dimensions[0]) for coord in coords]

    return coords_list

def dig_nd(game, coordinates, parent=True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    board = game['board']

    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0

    loc_value = get_value(board, coordinates)

    if loc_value == '.':
        game['visible'] = set_value(game['visible'], coordinates, True)
        game['state'] = 'defeat'
        return 1

    if get_value(game['visible'], coordinates) == True:
        return 0

    game['visible'] = set_value(game['visible'], coordinates, True)
    revealed = 1

    # If there are no neighboring bombs, do a recursive dig
    if loc_value == 0:
        neighbors = generate_neighbors(coordinates, game['dimensions'])
        for neighbor in neighbors:
            if get_value(board, neighbor) != '.':
                revealed += dig_nd(game, neighbor, parent=False)

    # Only do a victory check if it's a parent call (victory check iterates
    # through the entire board and is very expensive)
    if parent:
        bad_squares = count_bad_squares(board, game['visible'])

        if bad_squares == 0:
            game['state'] = 'victory'

    return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    dimensions = game['dimensions']
    board = game['board']
    visible = game['visible']

    new_board = construct_blank_board(dimensions, '')

    coordinates = get_possible_coords(dimensions)

    if not xray:
        for coord in coordinates:
            val = get_value(board, coord)
            vis = get_value(visible, coord)

            if vis:
                if val == 0:
                    new_board = set_value(new_board, coord, ' ')
                else:
                    new_board = set_value(new_board, coord, str(val))
            else:
                new_board = set_value(new_board, coord, '_')
    else:
        for coord in coordinates:
            val = get_value(board, coord)

            if val == 0:
                new_board = set_value(new_board, coord, ' ')
            else:
                new_board = set_value(new_board, coord, str(val))

    return new_board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    doctest.run_docstring_examples(
       dig_2d,
       globals(),
       optionflags=_doctest_flags,
       verbose=False
    )

    # g = {'dimensions': (2, 4, 2),
    #         'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #             [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    #     'visible': [[[False, False], [False, True], [False, False],
    #         [False, False]], [[False, False], [False, False], [False, False],
    #         [False, False]]],
    #     'state': 'ongoing'}

    # board = [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #         [['.', 3], [3, '.'], [1, 1], [0, 0]]]
    #
    # coords = get_possible_coords((2,4,2))
    #
    # print(len(coords)==16)
    # print(get_possible_coords((2,4,2)))
