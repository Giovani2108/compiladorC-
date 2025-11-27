from .ast_nodes import Node

class Automata:
    def __init__(self):
        self.operators = {
            'u-': (5, 'right'),
            '^': (4, 'right'),
            '*': (3, 'left'),
            '/': (3, 'left'),
            '+': (2, 'left'),
            '-': (2, 'left'),
        }
        self.derivations = []
        self.identificadores = []
        self.codigo_intermedio = []

    def validar_variable(self, nombre: str) -> bool:
        if not nombre:
            return False
        if not (nombre[0].isalpha() or nombre[0] == "_"):
            return False
        prohibidos = "$#/@."
        for c in nombre:
            if c in prohibidos:
                return False
            if not (c.isalnum() or c == "_"):
                return False
        return True

    def tokenize(self, expr: str):
        self.identificadores = []
        self.codigo_intermedio = []
        tokens = []
        i = 0
        n = len(expr)
        while i < n:
            c = expr[i]
            if c.isspace():
                i += 1
                continue
            if c.isalpha() or c == "_":
                ident = c
                i += 1
                while i < n and (expr[i].isalnum() or expr[i] == "_"):
                    ident += expr[i]
                    i += 1
                if self.validar_variable(ident):
                    tokens.append(ident)
                    self.identificadores.append(ident)
                    self.codigo_intermedio.append("Identificador: " + ident)
                continue
            if c.isdigit() or c == '.':
                num = c
                i += 1
                while i < n and (expr[i].isdigit() or expr[i] == '.'):
                    num += expr[i]
                    i += 1
                tokens.append(num)
                continue
            if c in '+*/^()':
                tokens.append(c)
                i += 1
                continue
            if c == '-':
                prev = tokens[-1] if tokens else None
                if prev is None or prev in ('(', '+', '-', '*', '/', '^'):
                    tokens.append('u-')
                else:
                    tokens.append('-')
                i += 1
                continue
            if c == '%':
                tokens.append('%')
                i += 1
                continue
            i += 1
        return tokens

    def is_number(self, tok):
        try:
            float(tok)
            return True
        except:
            return False

    def to_rpn(self, tokens):
        output = []
        stack = []
        for tok in tokens:
            if self.is_number(tok):
                output.append(tok)
            elif isinstance(tok, str) and tok.isidentifier():
                output.append(tok)
            elif tok in self.operators:
                p_tok, assoc = self.operators[tok]
                while stack:
                    top = stack[-1]
                    if top in self.operators:
                        p_top, _ = self.operators[top]
                        if (assoc == 'left' and p_tok <= p_top) or (
                            assoc == 'right' and p_tok < p_top):
                            output.append(stack.pop())
                            continue
                    break
                stack.append(tok)
            elif tok == '(':
                stack.append(tok)
            elif tok == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Paréntesis desbalanceados: falta '('")
                stack.pop()
            else:
                raise ValueError(f"Token desconocido: {tok}")
        while stack:
            top = stack.pop()
            if top in ('(', ')'):
                raise ValueError("Paréntesis desbalanceados")
            output.append(top)
        return output

    def rpn_to_ast(self, rpn):
        stack = []
        self.derivations = []
        for tok in rpn:
            if self.is_number(tok) or (isinstance(tok, str) and tok.isidentifier()):
                node = Node(value=tok)
                stack.append(node)
                self.derivations.append(f"Terminal -> {tok}")
            elif tok == 'u-':
                if not stack:
                    raise ValueError("Operador unario sin operando")
                child = stack.pop()
                node = Node(op='u-', left=child)
                stack.append(node)
                self.derivations.append(f"Unary Expression -> u- {self.subexpr_text(child)}")
            else:
                if len(stack) < 2:
                    raise ValueError(f"Operador binario '{tok}' sin suficientes operandos")
                right = stack.pop()
                left = stack.pop()
                node = Node(op=tok, left=left, right=right)
                stack.append(node)
                self.derivations.append(
                    f"Binary Expression -> {self.subexpr_text(left)} {tok} {self.subexpr_text(right)}"
                )
        if len(stack) != 1:
            raise ValueError("Expresión inválida: sobran operandos")
        return stack[0]

    def subexpr_text(self, node):
        if node.is_leaf():
            return str(node.value)
        if node.op == 'u-':
            child = self.subexpr_text(node.left)
            return f"-({child})"
        L = self.subexpr_text(node.left)
        R = self.subexpr_text(node.right)
        return f"({L} {node.op} {R})"

    def evaluate_and_assign_order(self, node, counter):
        if node.is_leaf():
            try:
                node.result = float(node.value)
            except ValueError:
                node.result = None
            return
        if node.op == 'u-':
            self.evaluate_and_assign_order(node.left, counter)
            node.result = -node.left.result if node.left.result is not None else None
        else:
            self.evaluate_and_assign_order(node.left, counter)
            self.evaluate_and_assign_order(node.right, counter)
            if node.left.result is None or node.right.result is None:
                node.result = None
            else:
                if node.op == '+':
                    node.result = node.left.result + node.right.result
                elif node.op == '-':
                    node.result = node.left.result - node.right.result
                elif node.op == '*':
                    node.result = node.left.result * node.right.result
                elif node.op == '/':
                    if node.right.result == 0:
                        raise ValueError("División por cero")
                    node.result = node.left.result / node.right.result
                elif node.op == '^':
                    if node.left.result < 0 and not node.right.result.is_integer():
                        raise ValueError("Potencia de base negativa con exponente no entero")
                    node.result = node.left.result**node.right.result
                elif node.op == '%':
                    node.result = node.left.result % node.right.result
        counter[0] += 1
        node.eval_order = counter[0]

    def analizar(self, expr: str):
        try:
            tokens = self.tokenize(expr)
            if not tokens:
                return {"error": "No se encontraron tokens válidos."}
            rpn = self.to_rpn(tokens)
            ast = self.rpn_to_ast(rpn)
        except Exception as e:
            return {"error": f"Error durante tokenización, RPN o AST: {e}"}
        try:
            counter = [0]
            self.evaluate_and_assign_order(ast, counter)
        except Exception as e:
            return {"error": f"Error durante la evaluación: {e}"}
        return {
            'tokens': tokens,
            'rpn': rpn,
            'ast': ast,
            'final_result': ast.result,
            'identificadores': self.identificadores,
            'codigo_intermedio': self.codigo_intermedio,
            'derivations': self.derivations
        }
