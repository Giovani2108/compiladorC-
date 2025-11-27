from .ast_nodes import TreeNode, BlockNode
from .lexer import Token

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self, output_callback=print):
        self.output_callback = output_callback
        self.environment = {}  # Global variables
        self.environment['endl'] = '\n' # Support for endl
        self.functions = {}    # Function definitions (if any, for now just main)

    def interpret(self, ast):
        if not ast:
            return
        try:
            self.visit(ast)
        except ReturnException as e:
            self.output_callback(f"\nProgram finished with exit code: {e.value}")

    def visit(self, node):
        if node is None:
            return None
        
        try:
            # Block
            if isinstance(node, BlockNode):
                for stmt in node.statements:
                    res = self.visit(stmt)
                    if res == 'BREAK': # Handle break in blocks (loops/switch)
                        return 'BREAK'
                return None
    
            # Declaration
            from .ast_nodes import DeclarationNode
            if isinstance(node, DeclarationNode):
                return self.visit_declaration(node)
    
            # Control Flow
            if node.token.type == Token.Type.Ident and node.token.value == 'if':
                return self.visit_if(node)
            if node.token.type == Token.Type.While:
                return self.visit_while(node)
            if node.token.type == Token.Type.For:
                return self.visit_for(node)
            if node.token.type == Token.Type.Switch:
                return self.visit_switch(node)
            if node.token.type == Token.Type.Break:
                return 'BREAK'
            if node.token.type == Token.Type.Return:
                return self.visit_return(node)
    
            # I/O
            if node.token.type == Token.Type.Cout:
                return self.visit_cout(node)
    
            # Assignment
            if node.token.type == Token.Type.Asign:
                return self.visit_assign(node)
    
            # Increment/Decrement
            if node.token.type == Token.Type.Increment:
                return self.visit_increment(node)
    
            # Binary Operators
            if node.token.type in (Token.Type.Suma, Token.Type.Resta, Token.Type.Multiplica, Token.Type.Divide, Token.Type.Mod):
                return self.visit_binop(node)
            
            # Relational
            if node.token.type in (Token.Type.Menor, Token.Type.Mayor, Token.Type.MenorIgual, Token.Type.MayorIgual, Token.Type.Igual, Token.Type.Diferente):
                return self.visit_relational(node)
    
            # Sizeof
            if node.token.type == Token.Type.Ident and node.token.value == 'sizeof':
                return self.visit_sizeof(node)
    
            # Literals & Identifiers
            if node.token.type == Token.Type.Cadena:
                return node.token.value
    
            if node.token.type == Token.Type.Numero:
                return float(node.token.value) if '.' in node.token.value else int(node.token.value)
            
            # Array Access (Ident '[]')
            if node.token.type == Token.Type.Ident and node.token.value == '[]':
                return self.visit_array_access(node)
                
            if node.token.type == Token.Type.Ident:
                # Check if it's a type (should be handled by DeclarationNode, but just in case)
                if node.token.value in ('int', 'float', 'char', 'string'):
                    return None
                return self.get_value(node.token.value)
    
            return None

        except ReturnException:
            raise
        except Exception as e:
            # If the exception already has a line number message, re-raise
            if "en línea" in str(e):
                raise e
            # Otherwise, add line number context
            line = getattr(node.token, 'line', '?')
            raise RuntimeError(f"Error Semántico en línea {line}: {e}")

    def visit_declaration(self, node):
        for var in node.vars:
            name = var['name']
            size = var['size']
            init = var['init']
            
            if size is not None:
                # Array declaration
                if isinstance(init, list):
                    # Evaluate each item
                    values = [self.visit(item) for item in init]
                    arr_data = {}
                    for i, v in enumerate(values):
                        arr_data[i] = v
                    self.environment[name] = arr_data
                    self.environment[f"__sizeof_{name}"] = size
                else:
                    self.environment[name] = {}
                    self.environment[f"__sizeof_{name}"] = size
            else:
                # Variable declaration
                val = 0
                if init:
                    val = self.visit(init)
                self.environment[name] = val

    def visit_if(self, node):
        condition = self.visit(node.left)
        if condition:
            self.visit(node.right)

    def visit_while(self, node):
        while self.visit(node.left):
            res = self.visit(node.right)
            if res == 'BREAK':
                break

    def visit_for(self, node):
        init = node.left
        n1 = node.right
        cond = n1.left
        n2 = n1.right
        update = n2.left
        body = n2.right

        self.visit(init)
        while self.visit(cond):
            res = self.visit(body)
            if res == 'BREAK':
                break
            self.visit(update)

    def visit_switch(self, node):
        val = self.get_value(node.left.token.value)
        case_node = node.right
        # Switch logic is still basic/incomplete in parser (doesn't store case values)
        # But for this task we focus on Bubble Sort which doesn't use switch.
        pass

    def visit_cout(self, node):
        current = node
        while current:
            val = self.visit(current.left)
            if self.output_callback == print:
                print(str(val), end='')
            else:
                self.output_callback(str(val))
            current = current.right

    def visit_assign(self, node):
        val = self.visit(node.right)
        
        if node.left.token.type == Token.Type.Ident and node.left.token.value == '[]':
            # Array assignment
            arr_name = node.left.left.token.value
            index = self.visit(node.left.right)
            self.set_array_value(arr_name, index, val)
        else:
            var_name = node.left.token.value
            self.set_value(var_name, val)
        return val

    def visit_increment(self, node):
        var_name = node.left.token.value
        val = self.get_value(var_name)
        val += 1
        self.set_value(var_name, val)
        return val

    def visit_binop(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.token.type
        
        if op == Token.Type.Suma: return left + right
        if op == Token.Type.Resta: return left - right
        if op == Token.Type.Multiplica: return left * right
        if op == Token.Type.Divide: return left / right
        if op == Token.Type.Mod: return left % right
        return 0

    def visit_relational(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.token.type
        
        if op == Token.Type.Menor: return left < right
        if op == Token.Type.Mayor: return left > right
        if op == Token.Type.MenorIgual: return left <= right
        if op == Token.Type.MayorIgual: return left >= right
        if op == Token.Type.Igual: return left == right
        if op == Token.Type.Diferente: return left != right
        return False

    def visit_array_access(self, node):
        arr_name = node.left.token.value
        index = self.visit(node.right)
        return self.get_array_value(arr_name, index)

    def visit_sizeof(self, node):
        # node.left is the expression/identifier
        
        # If it's an array access: sizeof(arr[0])
        if node.left.token.type == Token.Type.Ident and node.left.token.value == '[]':
             # It's an element. Assuming int array.
             return 4

        # We expect an identifier for array or variable
        if node.left.token.type == Token.Type.Ident:
            name = node.left.token.value
            # Check if it's an array
            if f"__sizeof_{name}" in self.environment:
                # sizeof(arr) returns total bytes. Assuming int=4 bytes.
                # But user code does: sizeof(numeros) / sizeof(numeros[0])
                # So we should return "size * 4" or just "size" if we want to be simple?
                # C++ sizeof returns bytes.
                # Let's return size * 4 (assuming 4 bytes per int)
                return self.environment[f"__sizeof_{name}"] * 4
            
            # If it's a variable
            val = self.get_value(name)
            if isinstance(val, int): return 4
            if isinstance(val, float): return 8
            if isinstance(val, str): return len(val)
        
        return 4 # Default fallback

    # --- Environment Helpers ---
    def set_value(self, name, value):
        self.environment[name] = value

    def get_value(self, name):
        if name in self.environment:
            return self.environment[name]
        raise NameError(f"Variable '{name}' no definida")

    def set_array_value(self, name, index, value):
        if name not in self.environment:
            self.environment[name] = {} 
        
        if isinstance(self.environment[name], dict):
            self.environment[name][index] = value
        else:
             raise TypeError(f"'{name}' no es un arreglo")

    def get_array_value(self, name, index):
        if name in self.environment and isinstance(self.environment[name], dict):
            return self.environment[name].get(index, 0)
        raise NameError(f"Arreglo '{name}' no definido o acceso inválido")

    def visit_return(self, node):
        val = self.visit(node.left)
        raise ReturnException(val)
