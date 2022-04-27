import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    """
    Represents all possible mathematical symbols including variables,
    numerical values, and binary operations
    """
    WRAP_LEFT = False
    WRAP_RIGHT = False

    # Allowing built-in arithmetic operations to be performed on symbols

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    def simplify(self):
        return self

    def eval_helper(self, mapping):
        return self

    def eval(self, mapping):
        """
        Simplifies the result of eval_helper and try to return it as an integer
        unless the mapping provided is incomplete, in which case just return
        the formula with all provided values inserted
        """
        new_ex = self.eval_helper(mapping)
        try:
            return new_ex.simplify().n
        except:
            return new_ex.simplify()



class Var(Symbol):
    """
    Represents a single-character alphabetical mathematical variable
    """
    PRECEDENCE = 0

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        """
        Returns a string of the variable name for printing
        """
        return str(self.name)

    def __repr__(self):
        """
        Returns a representation of the variable in the format Var(name)
        for printing
        """
        return "Var(" + repr(self.name) + ")"

    def __eq__(self, other):
        """
        Performs an equality check on the variable
        """
        if isinstance(other, Var):
            return self.name == other.name

    def deriv(self, wrt_var):
        """
        Calculates the partial derivative of the input with respect to
        a variable wrt_var
        """
        if self.name == wrt_var:
            return Num(1)
        else:
            return Num(0)

    def eval_helper(self, mapping):
        """
        Given a mapping of variables to values, replace all instances of
        the variable with equivalent Nums
        """
        if self.name in mapping:
            return Num(mapping[self.name])


class Num(Symbol):
    """
    Represents numerical values, can be ints or floats
    """
    PRECEDENCE = 0

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"

    def __eq__(self, other):
        if isinstance(other, Num):
            return self.n == other.n

    def deriv(self, wrt_var):
        return Num(0)

class BinOp(Symbol):
    """
    Represents operations between two mathematical symbols
    """
    def __init__(self, left, right):
        """
        Initializer. Stores instance variables `left` and `right`.
        Accepts integers and strings as well and converts them to
        Num and Var objects
        """
        if isinstance(left, str):
            self.left = Var(left)
        elif isinstance(left, int) or isinstance(left, float):
            self.left = Num(left)
        else:
            self.left = left

        if isinstance(right, str):
            self.right = Var(right)
        elif isinstance(right, int) or isinstance(right, float):
            self.right = Num(right)
        else:
            self.right = right

    def __repr__(self):
        return self.LABEL+"("+repr(self.left) + ", " + repr(self.right)+")"

    def __str__(self):
        left_str = str(self.left)
        right_str = str(self.right)

        # Parenthesization rules. If PRECEDENCE value for class of one
        # side of an expression is larger than the precedence of itself,
        # wrap in parenthesis (or if WRAP_LEFT/WRAP_RIGHT is true,
        # determined by special parethetization rules inside the __str__
        # methods of the classes)
        if (self.left.PRECEDENCE > self.PRECEDENCE) or self.WRAP_LEFT:
            left_str = "(" + left_str + ")"

        if (self.right.PRECEDENCE > self.PRECEDENCE) or self.WRAP_RIGHT:
            right_str = "(" + right_str + ")"

        return left_str + " " + self.OP + " " + right_str

    def eval_helper(self, mapping):
        """
        Takes the result of the left and right sides of the binary operation
        after running eval_helper individually and rewraps them
        """
        left = self.left.eval_helper(mapping)
        right = self.right.eval_helper(mapping)

        return self.__class__(left, right)
Autum

class Add(BinOp):
    """
    Represents the addition operation between two mathematical symbols
    """
    PRECEDENCE = 3
    LABEL = "Add"
    OP = "+"

    def deriv(self, wrt_var):
        return self.left.deriv(wrt_var) + self.right.deriv(wrt_var)

    def simplify(self):

        left = self.left.simplify()
        right = self.right.simplify()

        if left == Num(0):
            return right

        if right == Num(0):
            return left

        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n + right.n)

        return Add(left, right)

class Sub(BinOp):
    """
    Represents the subtraction operation between two mathematical symbols
    """
    PRECEDENCE = 3
    LABEL = "Sub"
    OP = "-"

    def __str__(self):
        if self.right.PRECEDENCE == self.PRECEDENCE:
            self.WRAP_RIGHT = True
        return BinOp.__str__(self)

    def deriv(self, wrt_var):
        return self.left.deriv(wrt_var) - self.right.deriv(wrt_var)

    def simplify(self):

        left = self.left.simplify()
        right = self.right.simplify()

        if right == Num(0):
            return left

        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n - right.n)

        return Sub(left, right)

class Mul(BinOp):
    """
    Represents the multiplication operation between two mathematical symbols
    """
    PRECEDENCE = 2
    LABEL = "Mul"
    OP = "*"

    def deriv(self, wrt_var):
        return self.left * self.right.deriv(wrt_var) + self.right * self.left.deriv(wrt_var)

    def simplify(self):

        left = self.left.simplify()
        right = self.right.simplify()

        if left == Num(1):
            return right

        if right == Num(1):
            return left

        if left == Num(0) or right == Num(0):
            return Num(0)

        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n * right.n)

        return Mul(left, right)


class Div(BinOp):
    """
    Represents the division operation between two mathematical symbols
    """
    PRECEDENCE = 2
    LABEL = "Div"
    OP = "/"

    def __str__(self):
        if self.right.PRECEDENCE == self.PRECEDENCE:
            self.WRAP_RIGHT = True
        return BinOp.__str__(self)

    def deriv(self, wrt_var):
        return (self.right * self.left.deriv(wrt_var)
            - self.left * self.right.deriv(wrt_var)) / (self.right*self.right)

    def simplify(self):

        left = self.left.simplify()
        right = self.right.simplify()

        if right == Num(1):
            return left

        if left == Num(0):
            return Num(0)

        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n / right.n)

        return Div(left, right)

class Pow(BinOp):
    """
    Represents the exponentiation operation between two mathematical symbols
    """
    PRECEDENCE = 1
    LABEL = "Pow"
    OP = "**"

    def __str__(self):
        if self.left.PRECEDENCE >= self.PRECEDENCE:
            self.WRAP_LEFT = True
        return BinOp.__str__(self)

    def deriv(self, wrt_var):
        if not isinstance(self.right, Num):
            raise TypeError("Cannot take a derivative of a non-polynomial function")

        return self.right * self.left**(self.right-1) * self.left.deriv(wrt_var)

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()

        if right == Num(1):
            return left

        if right == Num(0):
            return Num(1)

        if left == Num(0):
            return Num(0)

        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n ** right.n)

        return Pow(left, right)


def tokenize(expression):
    """
    Splits a string into a list of tokens that can be passed to a parser
    to interpret

    Breaks the string into left and right parentheses, variables, and integers
    """

    tokens = expression.split()

    new_tokens = []

    for token in tokens:
        number = '' # Tracks integer strings
        for char in token:
            if char.isalpha() or char in "()":
                # If it encounters a character that must stand alone, the
                # integer is finished so append it to the list before appending
                # the new character and clear the integer that was added
                if len(number) > 0:
                    new_tokens.append(number)
                    number = ''

                new_tokens.append(char)
            else:
                # Otherwise it's part of an integer, so add the new character to
                # the number string
                number += char

        # If we reach the end of the token and the integer hasn't been returned,
        # return it
        if len(number) > 0:
            new_tokens.append(number)

    return new_tokens

def parse(tokens):
    op_map = {
        "*" : Mul,
        "/" : Div,
        "+" : Add,
        "-" : Sub,
        "**" : Pow
    }
    def parse_expression(index):
        token = tokens[index]
        if token.isalpha(): # If it's a variable, wrap it in Var()
            return Var(token), index+1
        elif token == '(':
            left, op_idx = parse_expression(index+1)
            op = tokens[op_idx]
            right, next = parse_expression(op_idx+1)
            return op_map[op](left, right), next+1
        else:
            return Num(int(token)), index+1


    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def expression(expr_str):
    tokens = tokenize(expr_str)
    return parse(tokens)


if __name__ == "__main__":
    # doctest.testmod()

    x = Var('x')
    y = Var('y')
    z = 2*x - x*y + 3*y

    # a = Num(0) + 'x'
    # print(a.simplify())

    # print(z.deriv('y'))

    print(expression("(x * (2 + 3))"))
    # print(Add(Add(Num(2), Num(-2)), Add(Var('x'), Num(0))).simplify())
