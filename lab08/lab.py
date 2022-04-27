#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

import doctest

# NO ADDITIONAL IMPORTS!


###########################
# Carlae-related Exceptions #
###########################


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    """

    # Splits the string by line
    initial_tokens = source.split('\n')
    comments_removed = []
    new_tokens = []

    # Loops through the lines and removes comments
    for token in initial_tokens:
        for c, character in enumerate(token):
            if character == '#':
                token = token[:c]
                break
        if len(token) > 0:
            comments_removed.append(token)

    # Reassembles string without comments and splits it on all whitespace
    whitespace_split = '\n'.join(comments_removed).split()

    # Adds all tokens to a new list. Tokens with parentheses are split into
    # the parenthesis and the rest of the token
    for token in whitespace_split:
        val = ''
        for char in token:
            if char == '(':
                new_tokens.append(char)
            elif char == ')':
                if len(val) > 0:
                    new_tokens.append(val)
                val = ''
                new_tokens.append(char)
            else:
                val += char
        if len(val) > 0:
            new_tokens.append(val)

    return new_tokens

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def parsed_expression(index):
        """
        Iterates through list of tokens, replacing '()' with lists
        containing the values between
        """
        token = number_or_symbol(tokens[index])
        if token == '(':
            idx = index+1
            expression = []
            try:
                # Iterate through until closing parenthesis found
                # and append everything to a list
                while tokens[idx] != ')':
                    token, idx = parsed_expression(idx)
                    expression.append(token)
                return expression, idx+1
            except:
                # If no closing parenthesis found
                raise CarlaeSyntaxError
        elif token == ')':
            # If there's an unmatched ')'
            raise CarlaeSyntaxError
        else:
            return token, index+1

    expr, idx = parsed_expression(0)

    # If there is more after the final closing parenthesis, raise error
    if idx < len(tokens):
        raise CarlaeSyntaxError
    else:
        return expr



######################
# Built-in Functions #
######################

class BuiltIns:
    """
    Contains built-in functions
    """
    def prod(num_list):
        total = 1
        for n in num_list:
            total *= n
        return total

    def div(num_list):
        if len(num_list) == 0:
            raise CarlaeSyntaxError
        elif len(num_list) == 1:
            return 1/num_list[0]
        else:
            num = num_list[0]
            for n in num_list[1:]:
                num /= n
            return num

    variables = {
        "+": sum,
        "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
        "*": prod,
        "/": div,
    }

class Environment:
    """
    Represents a new environment that holds variable definitions and a pointer
    to a parent class
    """
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}


##############
# Evaluation #
##############

def retrieve_variable(name, env):
    """
    Searches environments for a variable of the given name, following the
    pointer if the variable is not found
    """
    environment = env
    while True:
        if name in environment.variables:
            return environment.variables[name]
        environment = getattr(environment, 'parent')

def define_variable(name, expression, env):
    """
    Associates a name with an expression and adds it to the given
    environment's dictionary of variables
    """
    if isinstance(name, list):
        # If NAME is an S-expression, implicitly translate and
        # define
        fn_name = name[0]
        args = name[1:]
        expr = Function(args, expression, env)
        env.variables[fn_name] = expr
        return expr
    else:
        # Otherwise just evaluate the expression and save to
        # the environment
        result = evaluate(expression, env)
        env.variables[name] = result
        return result

class Function:
    """
    Represents a custom function object containing parameters, the
    carlae S-expression, and a pointer to the parent environment
    """
    def __init__(self, params, expression, pointer):
        self.params = params
        self.expression = expression
        self.pointer = pointer

    def __call__(self, args):
        """
        Allows Function to be called. Creates a new environment with the arguments
        as variables and evaluates the function within that environment.
        """
        new_env = Environment(self.pointer)

        if len(self.params) != len(args):
            raise CarlaeEvaluationError

        new_env.variables = dict(zip(self.params, args))
        result = evaluate(self.expression, new_env)
        return result

def evaluate(tree, env=None):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        env (Environment or BuiltIns): a class containing a dictionary with
            variable mappings, the environment in which to evaluate the
            expression in
    """

    if env is None:
        env = Environment(BuiltIns)

    if isinstance(tree, int) or isinstance(tree, float):
        return tree

    # Is a variable
    if isinstance(tree, str):
        try:
            return retrieve_variable(tree, env)
        except AttributeError:
            raise CarlaeNameError

    # Is an S-expression
    if isinstance(tree, list):
        if tree[0] == ":=":
            return define_variable(tree[1], tree[2], env)
        elif tree[0] == "function":
            if len(tree) != 3:
                raise CarlaeEvaluationError
            return Function(tree[1], tree[2], env)
        else: # This should be an function call
            fn = evaluate(tree[0], env)

            if isinstance(fn, int) or isinstance(fn, float):
                raise CarlaeEvaluationError
            args = [evaluate(arg, env) for arg in tree[1:]]
            result = fn(args)
            return result

def result_and_env(tree, env=None):
    """
    Returns the result of evaluating a tree in a given env, and returns the env
    """
    if not env:
        env = Environment(BuiltIns)
    return evaluate(tree, env), env

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()


    # REPL
    env = Environment(BuiltIns)
    while True:
        user_input = input('in> ')

        if user_input == "EXIT":
            break

        try:
            print(evaluate(parse(tokenize(user_input)), env))
        except CarlaeSyntaxError:
            print("CarlaeSyntaxError")
            continue
        except CarlaeNameError:
            print("CarlaeNameError")
            continue
        except CarlaeEvaluationError:
            print("CarlaeEvaluationError")
            continue
