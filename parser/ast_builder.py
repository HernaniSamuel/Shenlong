from lark import Transformer
from slast.nodes import Program, VarDecl, Assignment, TypeNode, Number, VarReference, PrintStatement, String

class ASTBuilder(Transformer):
    def statement(self, children):
        if len(children) == 2:
            annotation, stmt = children
            stmt.annotation = annotation
            return stmt
        else:
            return children[0]

    def annotation(self, children):
        return children[0].value

    def program(self, children):
        return Program(children)

    def var_decl(self, children):
        var_type, name, value = children
        return VarDecl(var_type, name, value)

    def assignment(self, children):
        name = children[0]
        if len(children) == 3:
            cast_type, value = children[1:]
            return Assignment(name, value, cast_type)
        else:
            value = children[1]
            return Assignment(name, value)

    def type(self, children):
        return TypeNode(children[0].value)

    def cast(self, children):
        return children[0]

    def number(self, children):
        return Number(children[0].value)

    def var_reference(self, children):
        return VarReference(children[0].value)

    def print_stmt(self, children):
        return PrintStatement(children)

    def print_arg(self, children):
        return children[0]

    def STRING(self, token):
        # Remove aspas do valor
        return String(token.value[1:-1])
