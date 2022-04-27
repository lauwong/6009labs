"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
sys.setrecursionlimit(10_000)

#!/usr/bin/env python3
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

    def true_eq(num_list):
        first_num = num_list[0]

        for num in num_list:
            if num != first_num:
                return False
        return True

    def great(num_list):
        prev_num = num_list[0]

        for num in num_list[1:]:
            if num >= prev_num:
                return False
            prev_num = num
        return True

    def geq(num_list):
        prev_num = num_list[0]

        for num in num_list[1:]:
            if num > prev_num:
                return False
            prev_num = num
        return True

    def less(num_list):
        prev_num = num_list[0]

        for num in num_list[1:]:
            if num <= prev_num:
                return False
            prev_num = num
        return True

    def leq(num_list):
        prev_num = num_list[0]

        for num in num_list[1:]:
            if num < prev_num:
                return False
            prev_num = num
        return True

    def unpack(arg_lst, *types):
        num_args = len(arg_lst)

        if num_args != len(types):
            raise CarlaeEvaluationError

        for i in range(num_args):
            if not isinstance(arg_lst[i], types[i]):
                raise CarlaeEvaluationError

        if num_args == 1:
            return arg_lst[0]
        else:
            return arg_lst

    def eval_not(arg):
        bool_val = BuiltIns.unpack(arg, bool)
        return not bool_val

    def pair(items):

        if len(items) != 2:
            raise CarlaeEvaluationError
        return Pair(items[0], items[1])

    def head(arg):
        p = BuiltIns.unpack(arg, Pair)
        return p.head

    def tail(arg):
        p = BuiltIns.unpack(arg, Pair)
        return p.tail

    def lst(args):
        linked_list = None

        for arg in args[::-1]:
            linked_list = Pair(arg, linked_list)

        return linked_list

    def is_list(obj):

        def search_list(lst):
            if lst is None:
                return True
            if not isinstance(lst, Pair):
                return False
            return search_list(lst.tail)

        if isinstance(obj, list):
            return search_list(obj[0])
        else:
            return search_list(obj)

    def length(pair_list):

        if len(pair_list) != 1:
            raise CarlaeEvaluationError

        pair_obj = pair_list[0]

        if pair_obj is None:
            return 0

        elif isinstance(pair_obj, Pair):
            return len(pair_obj)
        else:
            raise CarlaeEvaluationError

    def nth(args):

        l, i = BuiltIns.unpack(args, Pair, int)

        def nth_idx(lst, idx):
            if not isinstance(lst, Pair):
                raise CarlaeEvaluationError

            if idx == 0:
                return lst.head

            return nth_idx(lst.tail, idx-1)

        return nth_idx(l, i)

    def concat(args):

        if len(args) == 0:
            return None

        def insert(lst, lst2):
            if lst is None:
                return lst2
            return Pair(lst.head, insert(lst.tail, lst2))

        my_lst = args[-1]

        if not BuiltIns.is_list([my_lst]):
            raise CarlaeEvaluationError

        for l in range(len(args)-2, -1, -1):
            if not BuiltIns.is_list([args[l]]):
                raise CarlaeEvaluationError
            my_lst = insert(args[l], my_lst)

        return my_lst

    def map_lst(args):

        if len(args) != 2:
            raise CarlaeEvaluationError

        f, l = args

        if not BuiltIns.is_list(l):
            raise CarlaeEvaluationError

        my_lst = None

        def map_helper(func, lst):
            if lst is None:
                return None
            return Pair(func([lst.head]), map_helper(func, lst.tail))

        return map_helper(f,l)

    def filter_lst(args):

        if len(args) != 2:
            raise CarlaeEvaluationError

        f, l = args

        if not BuiltIns.is_list(l):
            raise CarlaeEvaluationError

        my_lst = None

        def filter_helper(func, lst):
            if lst is None:
                return None
            if func([lst.head]) == True:
                return Pair(lst.head, filter_helper(func, lst.tail))
            else:
                return filter_helper(func, lst.tail)

        return filter_helper(f, l)

    def reduce_lst(args):

        if len(args) != 3:
            raise CarlaeEvaluationError

        func, lst, init = args

        if lst is not None:
            for val in lst:
                init = func([init, val])
        return init


    variables = {
        "+": sum,
        "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
        "*": prod,
        "/": div,
        "=?": true_eq,
        ">": great,
        ">=": geq,
        "<": less,
        "<=": leq,
        "not": eval_not,
        "@t": True,
        "@f": False,
        "nil": None,
        "pair": pair,
        "head": head,
        "tail": tail,
        "list": lst,
        "list?": is_list,
        "length": length,
        "nth": nth,
        "concat": concat,
        "map": map_lst,
        "filter": filter_lst,
        "reduce": reduce_lst,
        "begin": lambda args: args[-1],
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
    carlae expression (represented as a Python string), and a pointer to the
    parent environment
    """
    def __init__(self, params, expression, pointer):
        self.params = params
        self.expression = expression
        self.pointer = pointer

    def __call__(self, args):
        """
        Calls the function by creating a new environment with the arguments
        as variables and evaluating the function within that environment
        """
        new_env = Environment(self.pointer)

        if len(self.params) != len(args):
            raise CarlaeEvaluationError

        new_env.variables = dict(zip(self.params, args))
        result = evaluate(self.expression, new_env)
        return result

def eval_and(args, env):
    for arg in args:
        arg_val = evaluate(arg, env)
        if arg_val == False:
            return False
        if not isinstance(arg_val, bool):
            raise CarlaeEvaluationError
    return True

def eval_or(args, env):
    for arg in args:
        arg_val = evaluate(arg, env)
        if arg_val == True:
            return True
        if not isinstance(arg_val, bool):
            raise CarlaeEvaluationError
    return False

class Pair:
    """
    Represents a composite type that can hold two elements, one in its
    head and one in its tail
    """
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __iter__(self):
        yield self.head

        if isinstance(self.tail, Pair):
            yield from self.tail
        if not (isinstance(self.tail, Pair) or self.tail is None):
            raise CarlaeEvaluationError

    def __len__(self):
        for ix, _ in enumerate(self):
            pass
        return ix+1

def evaluate(tree, env=Environment(BuiltIns)):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

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
        if len(tree) == 0:
            raise CarlaeEvaluationError

        key_token = tree[0]

        if key_token == ":=":
            return define_variable(tree[1], tree[2], env)
        elif key_token == "function":
            if len(tree) != 3:
                raise CarlaeEvaluationError
            return Function(tree[1], tree[2], env)
        elif key_token == "and":
            return eval_and(tree[1:], env)
        elif key_token == "or":
            return eval_or(tree[1:], env)
        elif key_token == "if":
            if len(tree) != 4:
                raise CarlaeEvaluationError
            cond = tree[1]
            true_exp = tree[2]
            false_exp = tree[3]
            if evaluate(cond, env) == True:
                return evaluate(true_exp, env)
            else:
                return evaluate(false_exp, env)
        elif key_token == "del":
            if tree[1] in env.variables:
                return env.variables.pop(tree[1])
            else:
                raise CarlaeNameError
        elif key_token == "let":
            vars_list = [(var, evaluate(val, env)) for var, val in tree[1]]
            body = tree[2]

            temp_env = Environment(env)
            temp_env.variables = dict(vars_list)

            return evaluate(body, temp_env)
        elif key_token == "set!":
            name = tree[1]
            new_val = evaluate(tree[2], env)
            try:
                environment = env
                while True:
                    if name in environment.variables:
                        environment.variables[name] = new_val
                        return new_val
                    environment = getattr(environment, 'parent')
            except AttributeError:
                raise CarlaeNameError

        else: # This should be an function call
            fn = evaluate(key_token, env)

            if isinstance(fn, int) or isinstance(fn, float):
                raise CarlaeEvaluationError("Not a function")
            # print(tree)
            args = [evaluate(arg, env) for arg in tree[1:]]
            result = fn(args)
            return result

def result_and_env(tree, env=None):
    if not env:
        env = Environment(BuiltIns)
    return evaluate(tree, env), env

def evaluate_file(file_name, env=None):
    if not env:
        env = Environment(BuiltIns)

    with open(file_name) as f:
        expr_str = f.read()
        return evaluate(parse(tokenize(expr_str)), env)


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            print(evaluate_file(f))

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
