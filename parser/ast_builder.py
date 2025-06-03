from lark import Transformer, Tree
from slast.nodes import Program, VarDecl, Assignment, TypeNode, Number, VarReference, PrintStatement, String, UnaryOp, \
    BinaryOp


class ASTBuilder(Transformer):
    def statement(self, children):
        if len(children) == 2:
            annotation, stmt = children
            stmt.annotation = annotation
            return stmt
        else:
            return children[0]

    def assignment(self, children):
        name = children[0]
        assign_op = children[1]
        value = children[2]

        # Se for atribuição composta (ex: +=), transformamos em: x = x + y
        if hasattr(assign_op, 'type') and assign_op.type == "ASSIGN_OP":
            real_op = assign_op.value[:-1]  # Remove o '=' de '+='
            value = BinaryOp(VarReference(name.value), real_op, value)
            return Assignment(name.value, value)

        # Atribuição simples (com ou sem cast)
        if isinstance(assign_op, Tree):
            if assign_op.data == "simple_assign":
                if len(assign_op.children) == 1:
                    cast_type = assign_op.children[0]
                    return Assignment(name.value, value, cast_type)
                else:
                    return Assignment(name.value, value)
            elif assign_op.data == "compound_assign":
                # assign_op.children[0] é o token ASSIGN_OP
                token = assign_op.children[0]
                real_op = token.value[:-1]  # Remove o '=' de '+='
                value = BinaryOp(VarReference(name.value), real_op, value)
                return Assignment(name.value, value)

        raise Exception(f"Operador de atribuição inesperado: {assign_op}")

    def annotation(self, children):
        return children[0].value

    def program(self, children):
        return Program(children)

    def var_decl(self, children):
        var_type, name, value = children
        return VarDecl(var_type, name, value)

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

    def unaryop(self, children):
        # Converte operadores unários para operações binárias equivalentes
        if len(children) == 1:
            # Só temos o operando, assume negação
            operand = children[0]
            # -x vira (0 - x)
            return BinaryOp(Number("0"), "-", operand)
        else:
            # Temos operador e operando
            op_token, operand = children
            op_str = str(op_token.value if hasattr(op_token, 'value') else op_token)

            if op_str == "-":
                # -x vira (0 - x)
                return BinaryOp(Number("0"), "-", operand)
            elif op_str == "not":
                # not x vira !(x) - mantemos como UnaryOp pra gerar código C++ correto
                return UnaryOp("not", operand)
            elif op_str == "~":
                # ~x vira ~(x) - bitwise NOT, mantemos como UnaryOp
                return UnaryOp("~", operand)
            else:
                return UnaryOp(op_str, operand)

    # Converte cadeias do tipo expr op expr op expr …
    def binop_chain(self, children):
        """
        children vem na forma:
            [expr0, op_token1, expr1, op_token2, expr2, …]
        ou, caso a gramática use recursão à esquerda,
            [expr0, op_token1, Tree('binop_chain', [...])]
        Esta função reduz tudo a BinaryOp encadeados.
        """
        def _to_binop(left, op_tok, right):
            op = op_tok.value if hasattr(op_tok, "value") else str(op_tok)
            return BinaryOp(left, op, right)

        # Se o parser gerou recursão → desmonta recursivamente
        if len(children) == 3 and isinstance(children[2], Tree) and children[2].data == "binop_chain":
            left, op_tok, rest = children
            return _to_binop(left, op_tok, self.binop_chain(rest.children))

        # Forma achatada (expr op expr op expr …)
        node = children[0]
        i = 1
        while i < len(children):
            op_tok = children[i]
            right  = children[i + 1]
            node   = _to_binop(node, op_tok, right)
            i += 2
        return node
