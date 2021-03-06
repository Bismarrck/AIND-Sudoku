from __future__ import print_function

from operator import add

assignments = []

def cross(A, B):
    """
    Cross product of elements in A and elements in B.
    """
    return [s + t for s in A for t in B]


rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) 
                for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
t_diag_units = [list(map(lambda s,t: s + t, rows, cols))]
r_diag_units = [list(map(lambda s,t: s + t, rows, reversed(cols)))]
diag_units = t_diag_units + r_diag_units
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all boxes with two possible digits.
    boxes = [box for box, value in values.items() if len(value) == 2]

    # Pair the boxes and remove duplicates.
    twins_list = []
    twins_ids = []
    for a in boxes:
        for b in peers[a]:
            if values[a] != values[b]:
                continue
            twins_id = "".join(sorted([a, b]))
            if twins_id in twins_ids:
                continue
            twins_list.append([a, b])
            twins_ids.append(twins_id)

    for a, b in twins_list:
        # Find the common peers of twins a and b.
        boxes = peers[a].intersection(peers[b])

        # Only remove values from the boxes with at least two possible digits.
        for box in [box for box in boxes if len(values[box]) >= 2]:
            for v in values[a]:
                if v in values[box]:
                    assign_value(values, box, values[box].replace(v, ""))
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.

    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, 
                then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, 
    eliminate this value from the values of all its peers.
    
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ""))
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that 
    only fits in one box, assign the value to this box.
    
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Go through all the boxes, and whenever there is a box with a value, 
    eliminate this value from the values of all its peers.
    
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False

    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() 
                                    if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

         # Use the Only Choice Strategy
        values = only_choice(values)

        # Use the Naked Twins Strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() 
                                   if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False

    # Choose one of the unfilled squares with the fewest possibilities
    unsolved = sorted([box for box, value in values.items() if len(value) > 1], 
                      key=lambda k: len(values[k]))
    if len(unsolved) == 0:
        return values

    # Now use recursion to solve each one of the resulting sudokus, and if one 
    # returns a value (not False), return that answer!
    box = unsolved[0]
    for assign in values[box]:
        trial = values.copy()
        trial[box] = assign
        result = search(trial)
        if result:
            return result


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    diag_sudoku_grid = '........4......1.....6......7....2.8...372.4.......3.7......4......5.6....4....2.'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
