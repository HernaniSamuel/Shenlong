class Node:
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements

class VarDecl(Node):
    def __init__(self, var_type, name, value, annotation=None):
        self.var_type = var_type
        self.name = name
        self.value = value
        self.annotation = annotation

class Assignment(Node):
    def __init__(self, name, value, cast_type=None, annotation=None):
        self.name = name
        self.value = value
        self.cast_type = cast_type
        self.annotation = annotation

class TypeNode(Node):
    def __init__(self, name):
        self.name = name

class Number(Node):
    def __init__(self, value):
        self.value = value

class VarReference(Node):
    def __init__(self, name):
        self.name = name

class PrintStatement(Node):
    def __init__(self, args, annotation=None):
        self.args = args
        self.annotation = annotation

class String(Node):
    def __init__(self, value):
        self.value = value

class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # string: '+', '-', '*', etc.
        self.right = right

class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op = op  # '-', 'not', '~'
        self.operand = operand
