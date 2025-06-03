from slast.nodes import Program, VarDecl, Assignment, TypeNode, Number, VarReference, PrintStatement, String, UnaryOp, BinaryOp

class CoreTranslator:
    def translate(self, node):
        # "Desempacota" árvores Lark intermediárias (Tree) — pula pro filho real
        if hasattr(node, 'data') and node.data == 'statement' and len(node.children) == 1:
            node = node.children[0]

        # O resto do código igual:
        from slast.nodes import Program, VarDecl, Assignment, TypeNode, Number, VarReference

        if isinstance(node, Program):
            return "\n".join(self.translate(stmt) for stmt in node.statements)

        elif isinstance(node, VarDecl):
            return f"{node.var_type.name} {node.name} = {self.translate(node.value)};"

        elif isinstance(node, Assignment):
            if node.cast_type:
                return f"{node.name} = ({node.cast_type.name}) {self.translate(node.value)};"
            else:
                return f"{node.name} = {self.translate(node.value)};"

        elif isinstance(node, Number):
            return str(node.value)

        elif isinstance(node, VarReference):
            return node.name

        elif isinstance(node, PrintStatement):
            # Gera código C++: cout << ... << ...;
            parts = " << ".join([self.translate(arg) for arg in node.args])
            return f'std::cout << {parts} << std::endl;'

        elif isinstance(node, String):
            # Gera a string com aspas duplas
            return f'"{node.value}"'

        elif isinstance(node, BinaryOp):
            left = self.translate(node.left)
            right = self.translate(node.right)
            if node.op == "**":
                # Em C++, usa pow() para exponenciação
                return f"pow({left}, {right})"
            else:
                return f"({left} {node.op} {right})"

        elif isinstance(node, UnaryOp):
            if node.op == "not":
                return f"!({self.translate(node.operand)})"
            else:
                return f"{node.op}({self.translate(node.operand)})"

        else:
            raise Exception(f"Unknown node: {node}")
