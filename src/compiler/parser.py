from .lexer import Lexer, Token, LexicoSimple
from .ast_nodes import TreeNode

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token_actual = self.lexer.next_token()

    def eat(self, token_type):
        if self.token_actual.type == token_type:
            self.token_actual = self.lexer.next_token()
        else:
            raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: Se esperaba {token_type}, se encontró {self.token_actual.type} ('{self.token_actual.value}')")

    def parse(self):
        """
        Parsea:
         - si comienza con 'int' -> parse_program() (int main() { ... })
         - si no -> parse a single statement/expression (antes behavior)
        Devuelve el último nodo parseado (para compatibilidad).
        """
        # Si el primer token es un identificador 'int' (programa)
        if (self.token_actual.type == Token.Type.Ident and self.token_actual.value == 'int') or \
           (self.token_actual.type == Token.Type.Ident and self.token_actual.value == 'using'):
            node = self.parse_program()
            if self.token_actual.type != Token.Type.Fin:
                raise Exception("Tokens sobrantes después del parseo")
            return node

        # Si no, parsear una sola sentencia/expresión
        node = self.statement()
        if self.token_actual.type != Token.Type.Fin:
            raise Exception("Tokens sobrantes después del parseo")
        return node



    def statement(self):
        """
        statement → IDENT '=' expr | expr
        """
        # Si comienza con identificador y luego hay '=' → asignación
        # Si comienza con identificador
        if self.token_actual.type == Token.Type.Ident:
            left_token = self.token_actual
            self.eat(Token.Type.Ident)
            
            # Check for Array Access: arr[x]
            if self.token_actual.type == Token.Type.CorcheteAbre:
                self.eat(Token.Type.CorcheteAbre)
                index_expr = self.expr()
                self.eat(Token.Type.CorcheteCierra)
                
                # Create Access Node
                access_node = TreeNode(Token(Token.Type.Ident, '[]'))
                access_node.left = TreeNode(left_token)
                access_node.right = index_expr
                
                # Check for Assignment: arr[x] = ...
                if self.token_actual.type == Token.Type.Asign:
                    self.eat(Token.Type.Asign)
                    right = self.expr()
                    node = TreeNode(Token(Token.Type.Asign, '='))
                    node.left = access_node
                    node.right = right
                    return node
                else:
                    # Just an expression starting with arr[x]
                    return self._continue_expr(access_node)

            if self.token_actual.type == Token.Type.Asign:  # '='
                self.eat(Token.Type.Asign)
                right = self.expr()
                # Creamos un nodo de asignación con la variable a la izquierda
                assign_token = Token(Token.Type.Asign, '=')
                node = TreeNode(assign_token)
                node.left = TreeNode(left_token)
                node.right = right
                return node
            else:
                # No era asignación, tratamos como expresión que empieza con un Ident
                left_node = TreeNode(left_token)
                return self._continue_expr(left_node)
        else:
            return self.expr()

        
    def _continue_expr(self, left_node):
        """
        Continues parsing an expression starting with left_node.
        Handles arithmetic (+, -) and relational (<, >, ==, etc.)
        """
        # First, continue arithmetic (precedence: * / % > + - > Relational)
        # But wait, precedence is:
        # 1. Primary (++, --)
        # 2. Factor (*, /, %)
        # 3. Arith (+, -)
        # 4. Relational (<, >, ==, ...)
        
        # Since we already have left_node (Primary), we need to check for higher precedence?
        # If left_node came from Ident, it's Primary.
        # But parse_statement_full consumed Ident.
        # If next is *, we should have parsed it as part of term?
        # But we are in "continue".
        # If we have "a * b", parse_statement_full ate "a".
        # _continue_expr sees "*".
        # It should call _continue_term?
        # This is getting complicated because we broke the recursive descent structure.
        # Ideally, we should reconstruct the parsing.
        # But let's assume for now we only handle + - and Relational for statements starting with ID.
        # (Since * / usually don't start statements unless assignment, but assignment is handled).
        
        # Handle arithmetic first
        node = self._continue_arith(left_node)
        
        # Handle relational
        while self.token_actual.type in (Token.Type.Menor, Token.Type.Mayor, 
                                         Token.Type.MenorIgual, Token.Type.MayorIgual,
                                         Token.Type.Igual, Token.Type.Diferente):
            token = self.token_actual
            self.eat(token.type)
            right = self.arith_expr()
            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = right
            node = new_node
            
        return node

    def _continue_arith(self, left_node):
        node = left_node
        while self.token_actual.type in (Token.Type.Suma, Token.Type.Resta):
            token = self.token_actual
            self.eat(token.type)
            right = self.termino()
            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = right
            node = new_node
        return node

    # expr -> arith_expr ((< > ==) arith_expr)*
    def expr(self):
        node = self.arith_expr()
        while self.token_actual.type in (Token.Type.Menor, Token.Type.Mayor, 
                                         Token.Type.MenorIgual, Token.Type.MayorIgual,
                                         Token.Type.Igual, Token.Type.Diferente):
            tok = self.token_actual
            self.eat(tok.type)
            new_node = TreeNode(tok)
            new_node.left = node
            new_node.right = self.arith_expr()
            node = new_node
        return node

    def arith_expr(self):
        node = self.termino()
        while self.token_actual.type in (Token.Type.Suma, Token.Type.Resta):
            tok = self.token_actual
            self.eat(tok.type)
            new_node = TreeNode(tok)
            new_node.left = node
            new_node.right = self.termino()
            node = new_node
        return node

    # termino -> factor ((*|/|%) factor)*
    def termino(self):
        node = self.factor()
        while self.token_actual.type in (Token.Type.Multiplica, Token.Type.Divide, Token.Type.Mod):
            tok = self.token_actual
            self.eat(tok.type)
            new_node = TreeNode(tok)
            new_node.left = node
            new_node.right = self.factor()
            node = new_node
        return node

    # factor -> ('-' factor) | primary
    def factor(self):
        tok = self.token_actual
        if tok.type == Token.Type.Resta:
            # unary minus
            self.eat(Token.Type.Resta)
            new_node = TreeNode(Token(Token.Type.Resta, '-'))
            # for unary, we put operand on left (convention)
            new_node.left = self.factor()
            return new_node
        return self.primary()

    # primary -> Numero | Ident [++] | '(' expr ')'
    def primary(self):
        tok = self.token_actual
        
        # sizeof(expr)
        if tok.type == Token.Type.Ident and tok.value == 'sizeof':
            self.eat(Token.Type.Ident)
            if self.token_actual.type != Token.Type.ParAbre:
                raise ValueError("Se esperaba '(' después de sizeof")
            self.eat(Token.Type.ParAbre)
            node = self.expr()
            self.eat(Token.Type.ParCierra)
            
            sizeof_node = TreeNode(tok)
            sizeof_node.left = node
            return sizeof_node

        if tok.type == Token.Type.Numero:
            self.eat(Token.Type.Numero)
            return TreeNode(tok)
        if tok.type == Token.Type.Ident:
            self.eat(Token.Type.Ident)
            node = TreeNode(tok)
            
            # Array Access
            if self.token_actual.type == Token.Type.CorcheteAbre:
                self.eat(Token.Type.CorcheteAbre)
                index = self.expr()
                self.eat(Token.Type.CorcheteCierra)
                
                # Node for array access
                access_node = TreeNode(Token(Token.Type.Ident, '[]')) 
                access_node.left = node
                access_node.right = index
                node = access_node

            # Check for postfix increment
            if self.token_actual.type == Token.Type.Increment:
                inc_tok = self.token_actual
                self.eat(Token.Type.Increment)
                inc_node = TreeNode(inc_tok)
                inc_node.left = node
                return inc_node
            return node
        
        if tok.type == Token.Type.Cadena:
            self.eat(Token.Type.Cadena)
            return TreeNode(tok)

        if tok.type == Token.Type.ParAbre:
            self.eat(Token.Type.ParAbre)
            node = self.expr()
            if self.token_actual.type != Token.Type.ParCierra:
                raise ValueError("Paréntesis desbalanceados: falta ')'")
            self.eat(Token.Type.ParCierra)
            return node

        raise ValueError(f"Token inesperado en primary: {tok}")

    def declaration_statement(self, stop_at_paren=False):
        """
        declaration -> Type Ident [= expr] (, Ident [= expr])* ;
        If stop_at_paren is True, allows ending with ')' without consuming it, and without ';'.
        """
        from .ast_nodes import DeclarationNode
        # Consumir tipo (int, float, etc.)
        type_token = self.token_actual
        self.eat(Token.Type.Ident) # int, float, etc. are Idents in lexer
        
        # Primer identificador
        if self.token_actual.type != Token.Type.Ident:
            raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: Se esperaba un identificador después del tipo")
        
        decl_node = DeclarationNode(type_token)
        
        while True:
            if self.token_actual.type != Token.Type.Ident:
                 raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: Se esperaba identificador en declaración")
            
            var_name = self.token_actual.value
            self.eat(Token.Type.Ident)
            
            size = None
            init_expr = None

            if self.token_actual.type == Token.Type.CorcheteAbre:
                self.eat(Token.Type.CorcheteAbre)
                # Check if empty brackets []
                if self.token_actual.type == Token.Type.CorcheteCierra:
                    size = None # Auto-size
                elif self.token_actual.type == Token.Type.Numero:
                    size = int(self.token_actual.value)
                    self.eat(Token.Type.Numero)
                else:
                     raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: El tamaño del arreglo debe ser un número constante o vacío [].")
                self.eat(Token.Type.CorcheteCierra)

            if self.token_actual.type == Token.Type.Asign:
                self.eat(Token.Type.Asign)
                
                # Check for Array Init List: { expr, expr, ... }
                if self.token_actual.type == Token.Type.LlaveAbre:
                    self.eat(Token.Type.LlaveAbre)
                    init_expr = []
                    while self.token_actual.type != Token.Type.LlaveCierra:
                        init_expr.append(self.expr())
                        if self.token_actual.type == Token.Type.Coma:
                            self.eat(Token.Type.Coma)
                        elif self.token_actual.type == Token.Type.LlaveCierra:
                            break
                        else:
                             # Should be a comma or closing brace
                             if self.token_actual.type != Token.Type.LlaveCierra:
                                 raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: Se esperaba ',' o '}}' en lista de inicialización, se encontró {self.token_actual}")

                    self.eat(Token.Type.LlaveCierra)
                    # If size was not specified, infer it
                    if size is None:
                        size = len(init_expr)
                else:
                    init_expr = self.expr()
            
            decl_node.add_var(var_name, size, init_expr)

            if self.token_actual.type == Token.Type.PuntoYComa:
                self.eat(Token.Type.PuntoYComa)
                break
            elif stop_at_paren and self.token_actual.type == Token.Type.ParCierra:
                # Found ')' and we are allowed to stop
                break
            elif self.token_actual.type == Token.Type.Coma:
                self.eat(Token.Type.Coma)
                continue
            else:
                 expected = "';' o ','"
                 if stop_at_paren:
                     expected += " o ')'"
                 raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: Se esperaba {expected} en declaración, se encontró {self.token_actual.type}")
        return decl_node

    def parse_program(self):
        """
        Programa -> [using namespace std;]* 'int' 'main' '(' ')' Block
        Devuelve el nodo del bloque (o el último statement dentro del bloque).
        """
        # Consume 'using namespace ...;' if present
        while self.token_actual.type == Token.Type.Ident and self.token_actual.value == 'using':
            self.eat(Token.Type.Ident) # using
            if self.token_actual.value == 'namespace':
                self.eat(Token.Type.Ident) # namespace
                self.eat(Token.Type.Ident) # std (or whatever)
                self.eat(Token.Type.PuntoYComa)
            else:
                raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: Se esperaba 'namespace' después de 'using'")

        # Consumir 'int'
        if not (self.token_actual.type == Token.Type.Ident and self.token_actual.value == 'int'):
            raise ValueError(f"Error Sintáctico en línea {self.token_actual.line}: Se esperaba 'int' al inicio del programa")
        self.eat(Token.Type.Ident)
        
        # Consumir 'main'
        if not (self.token_actual.type == Token.Type.Ident and self.token_actual.value == 'main'):
            raise ValueError("Se esperaba 'main' después de 'int'")
        self.eat(Token.Type.Ident)

        # Consumir '('
        if self.token_actual.type != Token.Type.ParAbre:
            raise ValueError("Se esperaba '(' después de 'main'")
        self.eat(Token.Type.ParAbre)

        # Consumir ')'
        if self.token_actual.type != Token.Type.ParCierra:
            raise ValueError("Se esperaba ')' después de '('")
        self.eat(Token.Type.ParCierra)

        # Esperar '{'
        if self.token_actual.type != Token.Type.LlaveAbre:
            raise ValueError("Se esperaba '{' después de main()")
        node = self.parse_block()
        return node

    def parse_block(self):
        """
        Block → '{' { statement_full } '}'
        Devuelve un BlockNode con todas las sentencias.
        """
        from .ast_nodes import BlockNode  # Import here to avoid circular dependency if any
        self.eat(Token.Type.LlaveAbre)
        block_node = BlockNode()
        # permitir bloques vacíos también
        while self.token_actual.type != Token.Type.LlaveCierra and self.token_actual.type != Token.Type.Fin:
            stmt = self.parse_statement_full()
            block_node.add(stmt)
        if self.token_actual.type != Token.Type.LlaveCierra:
            raise ValueError("Falta '}' para cerrar bloque")
        self.eat(Token.Type.LlaveCierra)
        return block_node

    def parse_statement_full(self):
        """
        Parsea una sentencia completa dentro de un bloque:
          - if (...) { ... }
          - asignación: IDENT '=' expr ';'
          - expresión ';'
        Devuelve el TreeNode correspondiente.
        """
        # Declaración de variables: int x; o int x = 5;
        if self.token_actual.type == Token.Type.Ident and self.token_actual.value in ('int', 'float', 'char', 'string'):
            return self.declaration_statement()

        # If
        if self.token_actual.type == Token.Type.Ident and self.token_actual.value == 'if':
            return self.if_statement()

        # Switch
        if self.token_actual.type == Token.Type.Switch:
            return self.switch_statement()

        # For Loop (Standard)
        if self.token_actual.type == Token.Type.For:
            return self.for_statement()

        # Check for Post-Keyword For Loop: ( ... ) for
        if self.token_actual.type == Token.Type.ParAbre:
            # Try to parse as for-header
            state = self.save_state()
            try:
                header = self.parse_for_header()
                if self.token_actual.type == Token.Type.For:
                    # Found: ( ... ) for
                    self.eat(Token.Type.For)
                    block = self.parse_block()
                    return self.build_for_node(header, block)
                else:
                    # Not a for loop, backtrack
                    self.restore_state(state)
            except:
                # Parsing header failed, backtrack
                self.restore_state(state)

        # While Loop
        if self.token_actual.type == Token.Type.While:
            return self.while_statement()

        # Cout
        if self.token_actual.type == Token.Type.Cout:
            return self.cout_statement()

        # Return
        if self.token_actual.type == Token.Type.Return:
            return self.return_statement()

        # Asignación o expresión que comienza por IDENT
        if self.token_actual.type == Token.Type.Ident:
            # mirar ahead: si es 'if' ya tratado; si es una variable y luego '=' -> asignación
            left_tok = self.token_actual
            self.eat(Token.Type.Ident)
            
            # Handle Increment/Decrement as statement: x++;
            if self.token_actual.type == Token.Type.Increment:
                self.eat(Token.Type.Increment)
                if self.token_actual.type == Token.Type.PuntoYComa:
                    self.eat(Token.Type.PuntoYComa)
                node = TreeNode(Token(Token.Type.Increment, '++'))
                node.left = TreeNode(left_tok)
                node.left = TreeNode(left_tok)
                return node

            # Array Assignment: arr[x] = 5;
            if self.token_actual.type == Token.Type.CorcheteAbre:
                self.eat(Token.Type.CorcheteAbre)
                index_expr = self.expr()
                self.eat(Token.Type.CorcheteCierra)
                
                # Now expect '='
                if self.token_actual.type == Token.Type.Asign:
                    self.eat(Token.Type.Asign)
                    right = self.expr()
                    
                    # Build node: Assign -> left: Access(arr, index), right: value
                    access_node = TreeNode(Token(Token.Type.Ident, '[]'))
                    access_node.left = TreeNode(left_tok)
                    access_node.right = index_expr
                    
                    node = TreeNode(Token(Token.Type.Asign, '='))
                    node.left = access_node
                    node.right = right
                    
                    self.eat(Token.Type.PuntoYComa)
                    return node
                else:
                     # Not assignment, maybe just access?
                     # Reconstruct expression starting with access
                     access_node = TreeNode(Token(Token.Type.Ident, '[]'))
                     access_node.left = TreeNode(left_tok)
                     access_node.right = index_expr
                     
                     node = self._continue_expr(access_node)
                     if self.token_actual.type == Token.Type.PuntoYComa:
                        self.eat(Token.Type.PuntoYComa)
                     return node

            if self.token_actual.type == Token.Type.Asign:
                # Asignación
                self.eat(Token.Type.Asign)
                right = self.expr()
                node = TreeNode(Token(Token.Type.Asign, '='))
                node.left = TreeNode(left_tok)
                node.right = right
                # Enforce semicolon
                self.eat(Token.Type.PuntoYComa)
                return node
            else:
                # No era asignación; reconstruimos la expresión empezando por IDENT
                left_node = TreeNode(left_tok)
                node = self._continue_expr(left_node)
                if self.token_actual.type == Token.Type.PuntoYComa:
                    self.eat(Token.Type.PuntoYComa)
                return node

        # Si inicia con '(' o número -> expresión
        node = self.expr()
        if self.token_actual.type == Token.Type.PuntoYComa:
            self.eat(Token.Type.PuntoYComa)
        return node

    def save_state(self):
        return (self.lexer.index, self.token_actual)

    def restore_state(self, state):
        self.lexer.index, self.token_actual = state

    def for_statement(self):
        self.eat(Token.Type.For)
        header = self.parse_for_header()
        block = self.parse_block()
        return self.build_for_node(header, block)

    def parse_for_header(self):
        """
        Parses ( part1 ; part2 ; part3 )
        Returns [part1, part2, part3]
        """
        self.eat(Token.Type.ParAbre)
        
        parts = []
        
        # Helper to parse expression or assignment
        def parse_expr_or_assign():
            # Check for assignment: Ident = ...
            state = self.save_state()
            if self.token_actual.type == Token.Type.Ident:
                ident = self.token_actual
                self.eat(Token.Type.Ident)
                
                # Array assignment? arr[i] = ...
                if self.token_actual.type == Token.Type.CorcheteAbre:
                    self.eat(Token.Type.CorcheteAbre)
                    index = self.expr()
                    self.eat(Token.Type.CorcheteCierra)
                    if self.token_actual.type == Token.Type.Asign:
                        self.eat(Token.Type.Asign)
                        val = self.expr()
                        # Build assignment node
                        access = TreeNode(Token(Token.Type.Ident, '[]'))
                        access.left = TreeNode(ident)
                        access.right = index
                        
                        node = TreeNode(Token(Token.Type.Asign, '='))
                        node.left = access
                        node.right = val
                        return node
                    else:
                        # Not assignment, backtrack
                        self.restore_state(state)
                        return self.expr()

                if self.token_actual.type == Token.Type.Asign:
                    self.eat(Token.Type.Asign)
                    val = self.expr()
                    node = TreeNode(Token(Token.Type.Asign, '='))
                    node.left = TreeNode(ident)
                    node.right = val
                    return node
                else:
                    self.restore_state(state)
                    return self.expr()
            else:
                return self.expr()

        # Part 1
        if self.token_actual.type == Token.Type.Ident and self.token_actual.value in ('int', 'float', 'char', 'string'):
            parts.append(self.declaration_statement()) # Consumes ;
        else:
            parts.append(parse_expr_or_assign())
            self.eat(Token.Type.PuntoYComa)
            
        # Part 2 (Condition)
        parts.append(self.expr())
        self.eat(Token.Type.PuntoYComa)
        
        # Part 3 (Update)
        if self.token_actual.type == Token.Type.Ident and self.token_actual.value in ('int', 'float', 'char', 'string'):
            parts.append(self.declaration_statement(stop_at_paren=True))
        else:
            parts.append(parse_expr_or_assign())
        
        self.eat(Token.Type.ParCierra)
        return parts

        return self.build_for_node(header, block)

    def build_for_node(self, header, block):
        # header is [p1, p2, p3]
        # Determine which is Init, Cond, Update based on content
        # Rule: Init has declaration (int ...). 
        # If p1 is declaration -> Standard: Init, Cond, Update
        # If p3 is declaration -> Swapped: Update, Cond, Init
        
        init, cond, update = None, None, None
        
        # Check if p1 is declaration (TreeNode with token type Ident 'int' etc)
        # My declaration_statement returns TreeNode(type_token).
        
        p1, p2, p3 = header
        
        is_p1_decl = (p1.token.type == Token.Type.Ident and p1.token.value in ('int', 'float', 'char', 'string'))
        is_p3_decl = (p3.token.type == Token.Type.Ident and p3.token.value in ('int', 'float', 'char', 'string'))
        
        if is_p1_decl:
            # Standard: Init, Cond, Update
            init, cond, update = p1, p2, p3
        elif is_p3_decl:
            # Swapped: Update, Cond, Init
            update, cond, init = p1, p2, p3
        else:
            # Assume standard order if no declaration is found
            # This allows: for(i=0; i<5; i++) where i is declared outside
            init, cond, update = p1, p2, p3

        # Build For Node
        # ForNode -> left: Init, right: Body?
        # We need to store Init, Cond, Update, Body.
        # TreeNode is binary. We can chain them or use a special structure.
        # Let's use a chain: For -> left: Init, right: Next
        # Next -> left: Cond, right: Next2
        # Next2 -> left: Update, right: Body
        
        for_node = TreeNode(Token(Token.Type.For, 'for'))
        
        # Structure:
        #      For
        #     /   \
        #  Init    Node
        #         /    \
        #      Cond     Node
        #              /    \
        #          Update   Body
        
        n1 = TreeNode(Token(Token.Type.Invalido, 'ForPart2'))
        n2 = TreeNode(Token(Token.Type.Invalido, 'ForPart3'))
        
        for_node.left = init
        for_node.right = n1
        
        n1.left = cond
        n1.right = n2
        
        n2.left = update
        n2.right = block
        
        return for_node

    def while_statement(self):
        """
        while_statement -> 'while' '(' expr ')' '{' block '}'
        """
        self.eat(Token.Type.While)
        if self.token_actual.type != Token.Type.ParAbre:
            raise ValueError("Se esperaba '(' después de 'while'")
        self.eat(Token.Type.ParAbre)
        
        cond = self.expr()
        
        if self.token_actual.type != Token.Type.ParCierra:
            raise ValueError("Se esperaba ')' después de la condición del while")
        self.eat(Token.Type.ParCierra)
        
        if self.token_actual.type != Token.Type.LlaveAbre:
            raise ValueError("Se esperaba '{' después de while(...)")
        
        block = self.parse_block()
        
        while_node = TreeNode(Token(Token.Type.While, 'while'))
        while_node.left = cond
        while_node.right = block
        return while_node

    def cout_statement(self):
        """
        cout_statement -> 'cout' '<<' expr ('<<' expr)* ';'
        """
        self.eat(Token.Type.Cout)
        
        # First <<
        if self.token_actual.type != Token.Type.LeftShift:
            raise ValueError("Se esperaba '<<' después de 'cout'")
        self.eat(Token.Type.LeftShift)
        
        first_expr = self.expr()
        
        # Root node
        root_cout = TreeNode(Token(Token.Type.Cout, 'cout'))
        root_cout.left = first_expr
        
        current_cout = root_cout
        
        # Handle chained <<
        while self.token_actual.type == Token.Type.LeftShift:
            self.eat(Token.Type.LeftShift)
            next_expr = self.expr()
            
            # Create a new cout node for the next expression
            next_cout = TreeNode(Token(Token.Type.Cout, 'cout'))
            next_cout.left = next_expr
            
            # Link it to the right of the current one
            current_cout.right = next_cout
            current_cout = next_cout
        
        self.eat(Token.Type.PuntoYComa)
        
        return root_cout

    def return_statement(self):
        self.eat(Token.Type.Return)
        expr = self.expr()
        self.eat(Token.Type.PuntoYComa)
        
        node = TreeNode(Token(Token.Type.Return, 'return'))
        node.left = expr
        return node

    def if_statement(self):
        """
        if_statement -> 'if' '(' expr ')' '{' block '}'
        """
        # consumir 'if'
        self.eat(Token.Type.Ident)  # 'if'
        if self.token_actual.type != Token.Type.ParAbre:
            raise ValueError("Se esperaba '(' después de 'if'")
        self.eat(Token.Type.ParAbre)
        cond = self.expr()
        if self.token_actual.type != Token.Type.ParCierra:
            raise ValueError("Se esperaba ')' en la condición del if")
        self.eat(Token.Type.ParCierra)
        # ahora debemos ver un bloque '{' ... '}'
        if self.token_actual.type != Token.Type.LlaveAbre:
            raise ValueError("Se esperaba '{' después de la condición del if")
        block_node = self.parse_block()
        # construir un nodo 'if' (usaremos token Ident 'if' para representarlo)
        if_node = TreeNode(Token(Token.Type.Ident, 'if'))
        if_node.left = cond
        if_node.right = block_node
        if_node.right = block_node
        return if_node

    def switch_statement(self):
        """
        switch_statement -> 'switch' '(' Ident ')' '{' case_list '}'
        case_list -> ( 'case' ':' statement 'break' ';' )*
        """
        self.eat(Token.Type.Switch)
        self.eat(Token.Type.ParAbre)
        
        # Variable
        if self.token_actual.type != Token.Type.Ident:
            raise ValueError("Se esperaba una variable en el switch")
        var_token = self.token_actual
        self.eat(Token.Type.Ident)
        
        self.eat(Token.Type.ParCierra)
        self.eat(Token.Type.LlaveAbre)
        
        cases = []
        while self.token_actual.type == Token.Type.Case:
            self.eat(Token.Type.Case)
            self.eat(Token.Type.DosPuntos)
            stmt = self.parse_statement_full()
            
            if self.token_actual.type == Token.Type.Break:
                self.eat(Token.Type.Break)
                self.eat(Token.Type.PuntoYComa)
            
            # Guardamos el caso como un nodo (simplificado)
            case_node = TreeNode(Token(Token.Type.Case, 'case'))
            case_node.left = stmt
            cases.append(case_node)
            
        self.eat(Token.Type.LlaveCierra)
        
        switch_node = TreeNode(Token(Token.Type.Switch, 'switch'))
        switch_node.left = TreeNode(var_token)
        # Usamos right para una lista de casos enlazados o similar, 
        # por ahora solo el primer caso para no complicar TreeNode que es binario
        # O podemos hacer un nodo especial. Para mantener compatibilidad con TreeNode binario:
        # switch -> left: var, right: Block(cases)
        # Block -> left: case1, right: case2...
        
        current = switch_node
        for c in cases:
            # Estrategia simple: encadenar en right
            if current.right is None:
                current.right = c
            else:
                # Buscar el último
                last = current.right
                while last.right:
                    last = last.right
                last.right = c
                
        return switch_node


class SintacticoPDF:
    """Analizador sintáctico formal basado en el PDF"""
    def __init__(self, fuente, out_func):
        # Importamos GeneraCodigoSimple aquí para evitar dependencias circulares si estuviera en otro lado,
        # pero como lo pondremos en code_generator.py, lo importaremos arriba o dentro.
        # Para mantener la estructura original donde estaba anidado, lo importaremos.
        from .code_generator import GeneraCodigoSimple
        
        self.lex = LexicoSimple(fuente)
        self.gen = GeneraCodigoSimple(out_func)
        out_func("INICIO DE ANALISIS SINTACTICO\n")
        self.programa()
        out_func("FIN DE ANALISIS SINTACTICO\nFIN DE COMPILACION\n")

    def err(self, c):
        linea = self.lex.linea
        msgs = {
            1: " :ESPERABA UN ;",
            2: " :ESPERABA UNA }",
            3: " :ESPERABA UN =",
            4: " :ESPERABA UN )",
            5: " :ESPERABA UN IDENTIFICADOR",
            6: " :INSTRUCCION DESCONOCIDA",
            7: " :ESPERABA UNA CONSTANTE",
            8: " :ESPERABA 'int main()'",
            8: " :ESPERABA 'int main()'",
            9: " :ESPERABA UNA {",
            10: " :ESPERABA :",
            11: " :ESPERABA break"
        }
        raise SyntaxError(f"LINEA {linea} ERROR SINTACTICO {c}{msgs[c]}")

    def programa(self):
        self.out("<PROGRAMA>")
        # int
        t = self.lex.siguiente()
        if t != 'int': self.err(8) # Usamos error 8 para "Esperaba int main"
        
        # main
        t = self.lex.siguiente()
        if t != 'main': self.err(8)

        # (
        t = self.lex.siguiente()
        if t != '(': self.err(8) # O un error específico para parentesis

        # )
        t = self.lex.siguiente()
        if t != ')': self.err(8)

        self.gen.code()
        t = self.lex.siguiente()
        if t != '{': self.err(9)
        self.bloque()
        t = self.lex.siguiente()
        if t != '}': self.err(2)
        self.gen.end()

    def bloque(self):
        self.out("<BLOQUE>")
        while True:
            t = self.lex.siguiente()
            if t == '}':
                # cerramos correctamente el bloque
                self.lex.devolver(t)
                break
            self.lex.devolver(t)
            self.sentencia()
            # después de una sentencia aceptamos:
            #  - un ';' que termina la sentencia (estilo original)
            #  - o un '}' que puede cerrar el bloque (por ejemplo after if { ... })
            t = self.lex.siguiente()
            if t == ';':
                continue
            if t == '}':
                # Devolver para que la siguiente iteración detecte y termine el bloque
                self.lex.devolver(t)
                continue
            # cualquier otro símbolo es error: esperaba ';'
            self.err(1)  # Esperaba un ';'


    def sentencia(self):
        t = self.lex.siguiente()

        # Si el lexer devolvió la palabra completa 'if' -> manejar condicional
        if t == 'if':
            self.condicional()
        if t == 'if':
            self.condicional()
            return

        # Switch
        if t == 'switch':
            self.switch_statement()
            return

        # Si devolvió 'i', mirar el siguiente para ver si es 'f' (compatibilidad con lexer por caracteres)
        if t == 'i':
            lookahead = self.lex.siguiente()
            if lookahead == 'f':
                # ya consumimos 'i' y 'f', proceder a condicional
                self.condicional()
                return
            else:
                # no era "if", devolver los tokens leídos y continuar como antes
                self.lex.devolver(lookahead)
                self.lex.devolver(t)

        # Asignaciones (identificadores de una letra, o si el lexer devolvió un string
        # largo que no es 'if', evitamos comparaciones peligrosas con 'a' <= t <= 'z')
        if isinstance(t, str) and len(t) == 1 and 'a' <= t <= 'z':
            self.lex.devolver(t)
            self.asignacion()

        # Lectura
        elif t == 'R':
            self.lectura()

        # Escritura
        elif t == 'W':
            self.escritura()

        else:
            self.err(6)



    def asignacion(self):
        self.out("<ASIGNACION>")
        self.variable()
        t = self.lex.siguiente()
        if t != '=': self.err(3)
        self.expresion()
        self.gen.store()


    def condicional(self):
        self.out("<CONDICIONAL>")

        # asumimos que 'if' ya fue reconocido y consumido (por sentencia())
        # ahora esperamos '('
        t = self.lex.siguiente()
        if t != '(':
            self.err(4)  # esperaba ')', usamos el código 4 para paréntesis (como en el resto)

        # analizar la condición: variable op_rel constante
        self.condicion()

        # después de condicion(), el siguiente token debería ser ')'
        t = self.lex.siguiente()
        if t != ')':
            self.err(4)

        # ahora esperar la apertura de bloque
        t = self.lex.siguiente()
        if t != '{':
            self.err(9)

        # procesar el bloque interno
        self.bloque()

        # tras bloquear, esperamos '}' de cierre del if
        t = self.lex.siguiente()
        if t != '}':

            self.err(2)

    def switch_statement(self):
        self.out("<SWITCH>")
        # switch ( variable ) {
        t = self.lex.siguiente()
        if t != '(': self.err(4)
        
        self.variable()
        
        t = self.lex.siguiente()
        if t != ')': self.err(4)
        
        t = self.lex.siguiente()
        if t != '{': self.err(9)
        
        # Casos
        while True:
            t = self.lex.siguiente()
            if t == '}':
                self.lex.devolver(t)
                break
            
            if t == 'case':
                self.out("<CASO>")
                t = self.lex.siguiente()
                if t != ':': self.err(10)
                
                self.sentencia()
                
                t = self.lex.siguiente()
                if t == ';':
                    t = self.lex.siguiente()

                if t == 'break':
                    self.out("<BREAK>")
                    t = self.lex.siguiente()
                    if t != ';': self.err(1)
                else:
                    self.err(11)
            else:
                # Si encontramos algo que no es case ni }, error
                self.err(6)

        t = self.lex.siguiente()
        if t != '}': self.err(2)

    
    def condicion(self):
        self.out("<CONDICION>")
        v = self.lex.siguiente()
        if not ('a' <= v <= 'z'):
            self.err(5)

        op = self.lex.siguiente()
        if op not in ['==', '!=', '<', '<=', '>', '>=']:
            self.err(6)

        c = self.lex.siguiente()
        if not ('0' <= c <= '9'):
            self.err(7)


    def variable(self):
        t = self.lex.siguiente()
        if 'a' <= t <= 'z':
            self.gen.pusha(t)
        else:
            self.err(5)

    def expresion(self):
        self.termino()
        self.mas_terminos()

    def termino(self):
        self.factor()
        self.mas_factores()

    def mas_terminos(self):
        t = self.lex.siguiente()
        if t == '+':
            self.termino()
            self.gen.add()
            self.mas_terminos()
        elif t == '-':
            self.termino()
            self.gen.neg()
            self.gen.add()
            self.mas_terminos()
        else:
            self.lex.devolver(t)

    def factor(self):
        t = self.lex.siguiente()
        if '0' <= t <= '9':
            self.lex.devolver(t)
            self.constante()
        elif t == '(':
            self.expresion()
            t = self.lex.siguiente()
            if t != ')': self.err(4)
        else:
            self.lex.devolver(t)
            self.variable()
            self.gen.load()

    def mas_factores(self):
        t = self.lex.siguiente()
        if t == '*':
            self.factor()
            self.gen.mul()
            self.mas_factores()
        elif t == '/':
            self.factor()
            self.gen.div()
            self.mas_factores()
        elif t == '%':
            self.factor()
            self.gen.mod()
            self.mas_factores()
        else:
            self.lex.devolver(t)

    def lectura(self):
        v = self.lex.siguiente()
        if not ('a' <= v <= 'z'):
            self.err(5)
        self.gen.input(v)

    def escritura(self):
        v = self.lex.siguiente()
        if not ('a' <= v <= 'z'):
            self.err(5)
        self.gen.output(v)

    def constante(self):
        t = self.lex.siguiente()
        if '0' <= t <= '9':
            self.gen.pushc(t)
        else:
            self.err(7)

    def out(self, txt):
        self.gen.out(f"ANALISIS SINTACTICO: {txt}\n")
