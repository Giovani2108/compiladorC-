class Token:
    class Type:
        Numero = "Numero"
        Suma = "Suma"
        Resta = "Resta"
        Multiplica = "Multiplica"
        Divide = "Divide"
        Mod = "Modulo"
        ParAbre = "ParAbre"
        ParCierra = "ParCierra"
        Ident = "Identificador"
        Fin = "Fin"
        Invalido = "Invalido"
        Asign = "Asign"
        LlaveAbre = "LlaveAbre"    # '{'
        LlaveCierra = "LlaveCierra" # '}'
        PuntoYComa = "PuntoYComa"   # ';'
        Switch = "Switch"
        Case = "Case"
        Break = "Break"
        Default = "Default"
        DosPuntos = "DosPuntos"     # ':'
        For = "For"
        Increment = "Increment"
        Menor = "Menor"
        Mayor = "Mayor"
        MenorIgual = "MenorIgual"
        MayorIgual = "MayorIgual"
        Igual = "Igual"
        Diferente = "Diferente"
        While = "While"
        Cout = "Cout"
        LeftShift = "LeftShift"
        CorcheteAbre = "CorcheteAbre" # '['
        CorcheteCierra = "CorcheteCierra" # ']'
        Cadena = "Cadena" # "string"
        Coma = "Coma" # ','
        Return = "Return"

    def __init__(self, type_, value, line=1):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value}, Line:{self.line})"


class Lexer:
    def __init__(self, origen: str):
        self.origen = origen
        self.index = 0
        self.length = len(origen)
        self.line = 1

    def _peek_isdigit(self):
        # Después de haber leído ch y ya avanzado self.index, el "próximo" carácter
        # está en self.index, no en self.index + 1.
        return (self.index < self.length) and self.origen[self.index].isdigit()


    def next_token(self):
        while self.index < self.length and self.origen[self.index].isspace():
            if self.origen[self.index] == '\n':
                self.line += 1
            self.index += 1
        if self.index >= self.length:
            return Token(Token.Type.Fin, "", self.line)

        ch = self.origen[self.index]
        self.index += 1

        # Número (enteros o flotantes)
        if ch.isdigit() or (ch == '.' and self._peek_isdigit()):
            num = ch                          # <-- incluir el carácter leído
            dot_count = 1 if ch == '.' else 0
            while self.index < self.length and (self.origen[self.index].isdigit() or self.origen[self.index] == '.'):
                if self.origen[self.index] == '.':
                    dot_count += 1
                    if dot_count > 1:
                        break
                num += self.origen[self.index]
                self.index += 1
            return Token(Token.Type.Numero, num, self.line)

        # Identificador (letras, _, seguido de alfanum o _)
        if ch.isalpha() or ch == '_':
            ident = ch                        # <-- incluir el carácter leído
            while self.index < self.length and (self.origen[self.index].isalnum() or self.origen[self.index] == '_'):
                ident += self.origen[self.index]
                self.index += 1
            
            # Palabras reservadas para el Lexer moderno
            if ident == 'switch':
                return Token(Token.Type.Switch, ident, self.line)
            if ident == 'case':
                return Token(Token.Type.Case, ident, self.line)
            if ident == 'break':
                return Token(Token.Type.Break, ident, self.line)
            if ident == 'default':
                return Token(Token.Type.Default, ident, self.line)
            if ident == 'for':
                return Token(Token.Type.For, ident, self.line)
            if ident == 'while':
                return Token(Token.Type.While, ident, self.line)
            if ident == 'cout':
                return Token(Token.Type.Cout, ident, self.line)
            if ident == 'return':
                return Token(Token.Type.Return, ident, self.line)
            if ident == 'int': # También es bueno tener int/main si queremos parsear completo
                return Token(Token.Type.Ident, ident, self.line) # Dejamos como Ident por compatibilidad con parser actual o cambiamos si necesario

            if ident == 'sizeof':
                return Token(Token.Type.Ident, ident, self.line) # Treat as Ident for now, Parser will handle it

            return Token(Token.Type.Ident, ident, self.line)

        # ya avanzamos self.index en 1 arriba; ahora devolvemos tokens según ch
        if ch == '+':
            if self.index < self.length and self.origen[self.index] == '+':
                self.index += 1
                return Token(Token.Type.Increment, "++", self.line)
            return Token(Token.Type.Suma, ch, self.line)
        if ch == '-':
            return Token(Token.Type.Resta, ch, self.line)
        if ch == '*':
            return Token(Token.Type.Multiplica, ch, self.line)
        if ch == '/':
            # Check for comment //
            if self.index < self.length and self.origen[self.index] == '/':
                self.index += 1
                while self.index < self.length and self.origen[self.index] != '\n':
                    if self.origen[self.index] == '\n': self.line += 1
                    self.index += 1
                return self.next_token() # Recursively call to get next real token
            return Token(Token.Type.Divide, ch, self.line)
        if ch == '%':
            return Token(Token.Type.Mod, ch, self.line)
        if ch == '(':
            return Token(Token.Type.ParAbre, ch, self.line)
        if ch == ')':
            return Token(Token.Type.ParCierra, ch, self.line)
        if ch == '{':
            return Token(Token.Type.LlaveAbre, ch, self.line)
        if ch == '}':
            return Token(Token.Type.LlaveCierra, ch, self.line)
        if ch == '[':
            return Token(Token.Type.CorcheteAbre, ch, self.line)
        if ch == ']':
            return Token(Token.Type.CorcheteCierra, ch, self.line)
        if ch == ';':
            return Token(Token.Type.PuntoYComa, ch, self.line)
        if ch == ':':
            return Token(Token.Type.DosPuntos, ch, self.line)
        if ch == '=':
            if self.index < self.length and self.origen[self.index] == '=':
                self.index += 1
                return Token(Token.Type.Igual, "==", self.line)
            return Token(Token.Type.Asign, ch, self.line)
        if ch == '<':
            if self.index < self.length and self.origen[self.index] == '=':
                self.index += 1
                return Token(Token.Type.MenorIgual, "<=", self.line)
            if self.index < self.length and self.origen[self.index] == '<':
                self.index += 1
                return Token(Token.Type.LeftShift, "<<", self.line)
            return Token(Token.Type.Menor, ch, self.line)
        if ch == '>':
            if self.index < self.length and self.origen[self.index] == '=':
                self.index += 1
                return Token(Token.Type.MayorIgual, ">=", self.line)
            return Token(Token.Type.Mayor, ch, self.line)
        if ch == '!':
            if self.index < self.length and self.origen[self.index] == '=':
                self.index += 1
                return Token(Token.Type.Diferente, "!=", self.line)
            return Token(Token.Type.Invalido, ch, self.line)

        if ch == '#':
            # Preprocessor directive: skip until newline
            while self.index < self.length and self.origen[self.index] != '\n':
                self.index += 1
            return self.next_token()

        if ch == '"':
            # String literal
            s = ""
            while self.index < self.length and self.origen[self.index] != '"':
                if self.origen[self.index] == '\n': self.line += 1
                s += self.origen[self.index]
                self.index += 1
            
            if self.index < self.length:
                self.index += 1 # Consume closing quote
            
            return Token(Token.Type.Cadena, s, self.line)

        if ch == ',':
            return Token(Token.Type.Coma, ch, self.line)

        return Token(Token.Type.Invalido, ch, self.line)


class LexicoSimple:
    """Analizador léxico básico según ejemplos del PDF"""
    def __init__(self, fuente, traza=False):
        self.fuente = fuente or ""
        self.pos = 0
        self.traza = traza
        self.linea = 1
        self._devuelto = None


    def siguiente(self):
        # Si hay un token devuelto previamente, regresarlo
        if self._devuelto is not None:
            t = self._devuelto
            self._devuelto = None
            return t

        # Avanzar sobre espacios y contar líneas
        while self.pos < len(self.fuente) and self.fuente[self.pos].isspace():
            if self.fuente[self.pos] == "\n":
                self.linea += 1
            self.pos += 1

        # Fin de entrada
        if self.pos >= len(self.fuente):
            return ''

        # Reconocer palabras reservadas "if", "int", "main"
        # Verificamos si es una palabra
        if self.fuente[self.pos].isalpha():
            start = self.pos
            while self.pos < len(self.fuente) and (self.fuente[self.pos].isalnum() or self.fuente[self.pos] == '_'):
                self.pos += 1
            word = self.fuente[start:self.pos]
            
            if word == 'if':
                return 'if'
            if word == 'int':
                return 'int'
            if word == 'main':
                return 'main'
            if word == 'R': # Mantener compatibilidad con R/W si se usan como keywords simples
                return 'R'
            if word == 'W':
                return 'W'
            if word == 'switch':
                return 'switch'
            if word == 'case':
                return 'case'
            if word == 'break':
                return 'break'
            if word == 'default':
                return 'default'
            
            # Si no es reservada, devolvemos caracter a caracter si es de longitud 1 (comportamiento original para variables de 1 letra)
            # O devolvemos la palabra si el parser lo soporta.
            # El parser original SintacticoPDF espera caracteres individuales para variables 'a'-'z'.
            # Así que si la palabra es larga y no es reservada, tenemos un problema con el parser original que era muy simple.
            # Pero el usuario pidió "Adapta... para que se parezca más a C++".
            # Para no romper el parser SintacticoPDF que espera 'a'...'z', si la palabra es de 1 letra, la devolvemos.
            if len(word) == 1:
                return word
            
            # Si es más larga, devolvemos la palabra, pero el SintacticoPDF podría fallar si no se actualiza.
            # Sin embargo, el SintacticoPDF usa `variable()` que chequea 'a' <= t <= 'z'.
            # Vamos a devolver la palabra y dejar que el parser decida.
            return word

        # Detectar operadores relacionales de dos caracteres: ==, !=, <=, >=
        c = self.fuente[self.pos]
        if c in ('=', '!', '<', '>'):
            # si hay un '=' justo después, formamos el operador compuesto
            if (self.pos + 1) < len(self.fuente) and self.fuente[self.pos + 1] == '=':
                op = c + '='
                self.pos += 2
                return op
            else:
                # caso de un solo carácter: '=', '<', '>', '!' (nota: '!' solo será válido como '!=' en uso correcto)
                self.pos += 1
                return c
        
        if c == ':':
            self.pos += 1
            return ':'

        # Por defecto, devolver el carácter actual
        t = self.fuente[self.pos]
        self.pos += 1
        return t

    def devolver(self, t):
        self._devuelto = t
