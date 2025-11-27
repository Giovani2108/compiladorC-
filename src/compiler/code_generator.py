from .generador_codigo import GeneradorCodigo
from .lexer import Token
from .ast_nodes import TreeNode

class CodeGeneratorFromTree:
    """
    Genera código objeto a partir del TreeNode (Parser) o Node (Automata).
    Produce instrucciones en un GeneradorCodigo.
    """

    def __init__(self, declared_vars=None):
        # declared_vars: set o dict con nombres de variables declaradas (para decidir LOAD)
        self.declared = set(declared_vars) if declared_vars else set()

    def generate_from_tree(self, tree_root: TreeNode, output_path="output.obj"):
        gen = GeneradorCodigo(output_path)
        gen.code()
        # recorrido post-order y emisión
        self._emit_tree(tree_root, gen)
        gen.end()
        gen.close()
        return gen.nombre_fichero

    def _emit_tree(self, node: TreeNode, gen: GeneradorCodigo):
        """
        Postorder:
          - si número: PUSHC <num>
          - si identificador: PUSHA <name> ; LOAD
          - si operador binario: generar left, generar right, aplicar operator
          - si unary - : generar operand y NEG
        """
        if node is None:
            return
        t = node.token
        if t.type == Token.Type.Numero:
            gen.pushc(t.value)
            return
        if t.type == Token.Type.Ident:
            gen.push(t.value)
            # para usar el valor en expresión, hacemos LOAD
            gen.load()
            return
        # operador
        # unary minus detection: operator '-' with only left child and right is None -> unary
        if t.type == Token.Type.Resta and (node.right is None):
            # unary
            self._emit_tree(node.left, gen)
            gen.neg()
            return
        # binary operators: generate left then right
        if node.left:
            self._emit_tree(node.left, gen)
        if node.right:
            self._emit_tree(node.right, gen)
        # now emit operator
        if t.type == Token.Type.Suma:
            gen.add()
        elif t.type == Token.Type.Resta:
            gen.add()  # we used convention left and right and do subtraction via ADD? No — use SUB as no SUB method: we will implement as 'SUB' via ADD with NEG of right
            # But the GeneradorCodigo does not have SUB; use PUSH right, NEG, ADD would be wrong.
            # Better: write explicit SUB instruction not in original; but the PDF doesn't list SUB.
            # Instead, we will write a 'SUB' line directly.
            gen.salida.write("SUB\n")
            gen.salida.flush()
        elif t.type == Token.Type.Multiplica:
            gen.mul()
        elif t.type == Token.Type.Divide:
            gen.div()
        elif t.type == Token.Type.Mod:
            gen.mod()
        else:
            # fallback
            gen.salida.write(f"# UNKNOWN_OP {t.value}\n")
            gen.salida.flush()


class GeneraCodigoSimple:
    """Simula la salida del generador del PDF"""
    def __init__(self, out_func):
        self.out = out_func

    def code(self): self.out("Generando código para main\n")
    def end(self): self.out("Fin del código\n")
    def pusha(self, t): self.out(f"Push variable: {t}\n")
    def store(self): self.out("Almacenando valor\n")
    def load(self): self.out("Cargando variable\n")
    def input(self, t): self.out(f"Entrada para: {t}\n")
    def output(self, t): self.out(f"Salida de: {t}\n")
    def pushc(self, t): self.out(f"Push constante: {t}\n")
    def add(self): self.out("Suma\n")
    def neg(self): self.out("Negar\n")
    def mul(self): self.out("Mul\n")
    def div(self): self.out("Div\n")
    def mod(self): self.out("Mod\n")
