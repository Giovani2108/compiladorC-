from .lexer import Token

class TreeNode:
    def __init__(self, token: Token):
        self.token = token
        self.left = None
        self.right = None

    def __repr__(self):
        return f"TreeNode({self.token.type}, {self.token.value})"

    def print_tree(self, level=0, output_func=print):
        indent = "  " * level
        t = self.token
        if t.type == Token.Type.Numero:
            output_func(f"{indent}Numero: {t.value}")
        elif t.type == Token.Type.Ident:
            output_func(f"{indent}Identificador: {t.value}")
        elif t.type == Token.Type.ParAbre or t.type == Token.Type.ParCierra:
            output_func(f"{indent}Parentesis: {t.value}")
        else:
            # Mostrar operador con recursión
            op_map = {
                Token.Type.Suma: "+",
                Token.Type.Resta: "-",
                Token.Type.Multiplica: "*",
                Token.Type.Divide: "/",
                Token.Type.Mod: "%"
            }
            op = op_map.get(t.type, t.value)
            output_func(f"{indent}Operador: {op}")
            if self.left:
                output_func(f"{indent} L:")
                self.left.print_tree(level + 2, output_func)
            if self.right:
                output_func(f"{indent} R:")
                self.right.print_tree(level + 2, output_func)


class Node:
    def __init__(self, op=None, value=None, left=None, right=None):
        self.op = op
        self.value = value
        self.left = left
        self.right = right
        self.eval_order = None
        self.result = None

    def is_leaf(self):
        return self.value is not None

class BlockNode(TreeNode):
    def __init__(self, statements=None):
        super().__init__(Token(Token.Type.Invalido, 'BLOCK')) # Dummy token
        self.statements = statements if statements else []

    def add(self, statement):
        self.statements.append(statement)

    def print_tree(self, level=0, output_func=print):
        indent = "  " * level
        output_func(f"{indent}Block:")
        for stmt in self.statements:
            stmt.print_tree(level + 1, output_func)

class DeclarationNode(TreeNode):
    def __init__(self, type_token, vars=None):
        super().__init__(type_token)
        self.vars = vars if vars else [] # List of (name, size_if_array, init_value)

    def add_var(self, name, size=None, init=None):
        self.vars.append({'name': name, 'size': size, 'init': init})

    def print_tree(self, level=0, output_func=print):
        indent = "  " * level
        output_func(f"{indent}Declaration ({self.token.value}): {self.vars}")


