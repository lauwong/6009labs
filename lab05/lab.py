#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def simplify(formula, assignment):
    """
    Simplifies the CNF based on a particular variable assignment

    Parameters:
        * formula (list) : a list of lists of tuples composing
            the CNF to simplify
        * assignment (tuple) : a tuple containing the variable and truth value
            to simplify based on

    Returns:
        A simplified CNF such that all clauses containing the literal are
        removed and all inverses of the literal are removed
    """

    new_formula = []

    name, val = assignment

    for clause in formula:
        if assignment not in clause:
            new_clause = [literal for literal in clause if literal != (name, not val)]
            if new_clause:
                new_formula.append(new_clause)

    return new_formula

def check_contradiction(formula):
    """
    Checks the CNF for a contradiction between unit clauses

    Parameters:
        * formula (list) : the CNF to check

    Returns:
        A boolean that is True if there is a contradiction, otherwise False
    """
    required_literals = {}
    for clause in formula:
        if len(clause) == 1:
            item = clause[0][0]
            # If the variable has been encountered before but its value
            # was the opposite, there is a contradiction
            if item in required_literals:
                if required_literals[item] != clause[0][1]:
                    return True
            else: # Keep track of the new variable and value
                required_literals[item] = clause[0][1]
    return False

def get_unit_clauses(formula):
    """
    Gets all unit clauses in the formula

    Parameters:
        * formula (list) : the CNF to search

    Returns:
        A set of the literals from all unit clauses
    """
    unit_clauses = set()

    for clause in formula:
        if len(clause) == 1:
            unit_clauses.add(clause[0])

    return unit_clauses

def simplify_recursive(formula, unit_clauses, parent=True):
    """
    Recursively simplifies the formula until there are no more unit clauses

    Parameters:
        * formula (list) : the CNF to simplify
        * unit_clauses (set) : a set of all literals from discovered
            unit clauses
        * parent (bool) : tracks whether it's a parent call

    Returns:
        A fully simplified CNF and a set of all the unit clauses that
        it simplified the formula based on
    """
    if not parent:
        # Terminate if it cannot simplify any further
        new_unit_clauses = get_unit_clauses(formula)

        if not new_unit_clauses:
            return formula, unit_clauses

    all_unit_clauses = unit_clauses.copy()
    new_formula = formula[:]

    for var in unit_clauses:
        # Simplify based on each variable
        new_formula = simplify(new_formula, var)
        # Stop if there's a contradiction
        if check_contradiction(new_formula):
            return new_formula, unit_clauses
        # Add the newly discovered unit clauses to the simplifcation agenda
        all_unit_clauses |= get_unit_clauses(new_formula)

    return simplify_recursive(new_formula, all_unit_clauses, parent=False)

def satisfying_helper(formula, assigned):
    """
    Recursively solve the CNF with backtracking

    Parameters:
        * formula (list) : the CNF to solve
        * assigned (dict) : a dictionary containing the variables and their
            presently assigned values

    Returns:
        A dictionary containing the variables and their boolean values
        such that the CNF is solved
    """

    # Base case: if there's a contradiction, backtrack
    if check_contradiction(formula):
        return None

    # Base case: if the formula is empty and there's no contradiction,
    # the CNF is solved, return the solution
    if not formula:
        return assigned

    assigned_copy = dict(assigned)

    # Takes the first variable of the first literal of the first clause
    # in the CNF
    var = formula[0][0][0]

    # Simplifies based on the assumption that the variable is True
    # v_true is the simplified formula, g_v is the set of unit clauses
    # that it simplified using
    v_true, g_v = simplify_recursive(formula, {(var, True)})

    if not check_contradiction(v_true):
        # For each unit clause resulting from the original assignment, set
        # the assumed value to be the value of the contained literal
        for name, val in g_v:
            assigned_copy[name] = val

        # Call the function recursively on the simplified formula
        satisfies = satisfying_helper(v_true, assigned_copy)

        # If the solution is found, return it
        if satisfies:
            return satisfies

    # Do the same for if the variable is False
    v_false, g_v = simplify_recursive(formula, {(var, False)})

    if not check_contradiction(v_false):
        for name, val in g_v:
            assigned_copy[name] = val

        satisfies = satisfying_helper(v_false, assigned_copy)

        if satisfies:
            return satisfies

    # If no solution found, backtrack
    return None


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """

    variables = {}

    # Simplifies the formula based on any pre-existing unit clauses
    # since these are givens (we know what the value must be)
    guaranteed_variables = get_unit_clauses(formula)
    formula, g_v = simplify_recursive(formula, guaranteed_variables)

    # If the formula is fully solved after the first simplifcation, just
    # return the values. Otherwise, try to solve.
    if formula:
        return satisfying_helper(formula, dict(g_v))
    else:
        return dict(g_v)


def get_combinations(students, group_size):
    """
    Recursively finds all possible combinations of students for a given
    group size (nCr)

    Parameters:
        * students (list) : contains the names of all students (strings)
        * group_size (int) : the desired size of the groups to create

    Returns:
        A list of tuples of student names, contains all possible combinations
        of students of size group_size
    """

    # Base case: if the desired group size has been achieved, return
    # an empty list to fill
    if group_size == 0:
        return [()]

    new_combos = []

    # For each student, get all current combinations not involving the student
    # (not yet full size) and add the student to the combination
    for s in range(len(students)):
        student = students[s]
        combos = get_combinations(students[s+1:], group_size-1)

        for combo in combos:
            new_combo = combo + (student,)
            new_combos.append(new_combo)

    return new_combos


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """

    cnf = []

    num_rooms = len(room_capacities)
    students = list(student_preferences.keys())
    rooms = list(room_capacities.keys())
    hopeful_students = {}

    for student in student_preferences:
        # Students only in desired sections
        clause = [(student+'_'+room, True) for room in student_preferences[student]]
        cnf.append(clause)

        # Students in at most one room
        for r in range(num_rooms-1):
            for i in range(r+1, num_rooms):
                clause = [(student+'_'+rooms[r], False), (student+'_'+rooms[i], False)]
                cnf.append(clause)

        # Saves the number of students who put each room as a preference
        for room in student_preferences[student]:
            if room in hopeful_students:
                hopeful_students[room] += 1
            else:
                hopeful_students[room] = 1


    for room in room_capacities:
        # Only if there is a size constraint
        max_size = room_capacities[room]

        # No oversubscribed sections (for a room of size max_size, any group
        # of max_size + 1 will have at least one student who cannot be in
        # the room)
        if max_size < hopeful_students[room]:
            groups = get_combinations(students, max_size + 1)

            for group in groups:
                clause = [(s+'_'+room, False) for s in group]
                cnf.append(clause)

    return cnf




if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)

    # doctest.run_docstring_examples(
    #    satisfying_assignment,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )

    print(get_combinations(['A', 'B', 'C', 'D'], 3))
