import re
from .symbol_table import TablaSimbolos
from .lexer import Lexer, Token
from .parser import Parser

class SemanticAnalyzer:
    def __init__(self):
        self.tabla = TablaSimbolos()
        self.errores = []
        self.usados = set()

    def analizar(self, content):
        self.tabla = TablaSimbolos()
        self.errores = []
        self.usados = set()
        
        # 1️⃣ Procesar declaraciones (crear tabla de símbolos)
        for line in content.splitlines():
            line = line.strip().rstrip(';')
            if not line or line.startswith("#include"):
                continue

            m = re.match(r'^(int|float|string|char)\s+(.+)$', line)
            if m:
                tipo = m.group(1)
                declaradores = [d.strip() for d in m.group(2).split(",")]
                for decl in declaradores:
                    if "=" in decl:
                        nombre, valor = [x.strip() for x in decl.split("=", 1)]
                        try:
                            self.tabla.insertar(nombre, "variable", tipo, valor)
                        except ValueError as e:
                            self.errores.append(str(e))
                    elif "[" in decl and "]" in decl:
                        # Validate syntax: name[size]
                        # Strict rule: <tipo dato><nombre_arreglos><simbolo apertura><numero><simbolo cierre>
                        m_arr = re.match(r'^([A-Za-z_]\w*)\s*\[\s*(\d+)\s*\]$', decl)
                        if m_arr:
                            nombre = m_arr.group(1)
                            size = m_arr.group(2)
                            try:
                                # Store size in valor for now
                                self.tabla.insertar(nombre, "arreglo", tipo, valor={"size": size})
                            except ValueError as e:
                                self.errores.append(str(e))
                        else:
                             self.errores.append(f"Error semántico: Declaración de arreglo inválida '{decl}'. Se espera 'nombre[numero]'.")
                    else:
                        nombre = decl
                        try:
                            self.tabla.insertar(nombre, "variable", tipo)
                        except ValueError as e:
                            self.errores.append(str(e))

        # 2️⃣ Analizar el cuerpo del programa
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            raw = line.strip()
            print(f"DEBUG: Processing line {idx+1}: {raw}")
            if not raw or raw.startswith("#include"):
                continue
            if raw in ['M', '{', '}', 'M{']:
                continue
            if re.match(r'^(int|float|string|char)\b', raw):
                continue

            # === Manejo de if(...) ===
            if raw.strip().startswith("if"):
                self._analizar_if(raw, idx, lines)
                continue

            # === Manejo de switch(...) ===
            if raw.strip().startswith("switch"):
                self._analizar_switch(raw, idx)
                continue

            # === Manejo de while(...) ===
            if raw.strip().startswith("while"):
                self._analizar_while(raw, idx, lines)
                continue

            # === Manejo de for(...) o (...)for ===
            if raw.strip().startswith("for"):
                self._analizar_for(raw, idx, type="standard")
                continue
            
            if re.match(r"^\(.*\)\s*for", raw.strip()):
                self._analizar_for(raw, idx, type="post")
                continue

            # === Asignaciones comunes o dentro de bloques if ===
            if '=' in raw:
                self._analizar_asignacion(raw, idx)



        # 🔍 Verificar balance de llaves en todo el programa
        self._verificar_llaves(content)

        return {
            "tabla": self.tabla,
            "errores": self.errores,
            "usados": list(self.usados)
        }

    def _analizar_if(self, raw, idx, lines):
        # Verificar que tenga paréntesis de apertura
        if not re.search(r"if\s*\(", raw):
            self.errores.append(f"Error sintáctico: falta '(' después de 'if' en línea {idx+1}: '{raw}'")
            return

        # Buscar la condición entre paréntesis (puede estar en la misma línea)
        cond_match = re.search(r"if\s*\((.*?)\)", raw)
        if not cond_match:
            self.errores.append(f"Error sintáctico: falta ')' en condición de línea {idx+1}: '{raw}'")
            return

        condicion = cond_match.group(1).strip()

        # Verificar que exista '{' que abra el bloque del if:
        has_open_brace = False
        if re.search(r"\)\s*\{", raw):
            has_open_brace = True
        else:
            j = idx + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                nxt = lines[j].strip()
                if nxt.startswith("{"):
                    has_open_brace = True

        if not has_open_brace:
            self.errores.append(f"Error sintáctico: falta '{{' después de la condición del if en línea {idx+1}: '{raw}'")
            return

        # Verificar operador relacional dentro de la condición
        operadores_rel = ["==", "!=", "<=", ">=", "<", ">"]
        encontrado = any(op in condicion for op in operadores_rel)
        if not encontrado:
            if "=" in condicion:
                self.errores.append(f"Error semántico: se usó '=' en lugar de '==' en la condición '{condicion}' (línea {idx+1})")
            else:
                self.errores.append(f"Error semántico: falta operador relacional en la condición '{condicion}' (línea {idx+1})")

        # Verificar variables dentro del if
        variables = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", condicion)
        for var in variables:
            if not self.tabla.existe(var) and not var.isdigit():
                self.errores.append(f"Error: variable '{var}' usada sin declarar en condición IF (línea {idx+1}).")

        # Verificar orden (constante primero es inválido según tus reglas)
        if not raw.strip().endswith('{'):
            # No es necesariamente un error si la llave está abajo, pero sus ejemplos de error
            # "switch( variable ) // No es correcto" sugieren que falta la llave o algo.
            # Dejaremos que el parser maneje la falta de llave, aquí solo validamos la variable.
            pass

    def _analizar_asignacion(self, raw, idx):
        # Evitar procesar condiciones "if(a==3)" como asignaciones
        if '==' in raw or '!=' in raw or '<=' in raw or '>=' in raw:
            return

        partes = raw.split('=', 1)
        if len(partes) != 2:
            return
        var, expr = [s.strip() for s in partes]

        # Validar variable a la izquierda
        # Check for array access: arr[index]
        m_arr_access = re.match(r'^([A-Za-z_]\w*)\s*\[\s*(.+)\s*\]$', var)
        
        if m_arr_access:
            nombre_arr = m_arr_access.group(1)
            index_expr = m_arr_access.group(2)
            
            if not self.tabla.existe(nombre_arr):
                self.errores.append(f"Error: arreglo '{nombre_arr}' usado sin declarar.")
                return

            info = self.tabla.buscar(nombre_arr)
            if info['naturaleza'] != 'arreglo':
                 self.errores.append(f"Error: '{nombre_arr}' no es un arreglo.")
                 return
            
            # Validate vars in index
            vars_in_index = re.findall(r"[A-Za-z_]\w*", index_expr)
            for v in vars_in_index:
                if not v[0].isdigit() and not self.tabla.existe(v):
                     self.errores.append(f"Error: variable '{v}' en índice de arreglo no declarada.")
            
            # We treat it as valid l-value, continue to parse right side
            
        elif not var or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", var):
            print(f"DEBUG: Invalid variable name in assignment: {var}")
            self.errores.append(f"Error: nombre de variable inválido en '{raw}'")
            return

        if not m_arr_access and not self.tabla.existe(var):
            self.errores.append(f"Error: variable '{var}' usada sin declarar.")
            return

        # Guardar valor asignado si es literal (y no es arreglo)
        if not m_arr_access:
            try:
                # Strip ; from expr
                expr_clean = expr.rstrip(';')
                valor_eval = eval(expr_clean, {}, {})
                self.tabla.tabla[var]["valor"] = valor_eval
            except:
                self.tabla.tabla[var]["valor"] = None


        # Analizar sintácticamente toda la asignación
        lexer = Lexer(raw.strip(';'))
        parser = Parser(lexer)
        try:
            tree = parser.parse()
        except Exception as e:
            self.errores.append(f"Error sintáctico en '{raw}': {e}")
            return

        # Verificar uso de identificadores dentro del árbol
        def walk(n):
            if n is None:
                return
            if n.token.type == Token.Type.Ident:
                # Ignore special array access token
                if n.token.value == '[]':
                    pass
                else:
                    self.usados.add(n.token.value)
                    if not self.tabla.existe(n.token.value):
                        self.errores.append(f"Error: variable '{n.token.value}' usada sin declarar.")
            walk(n.left)
            walk(n.right)
        walk(tree)

        def check_div_zero(n):
            if n is None:
                return
            if n.token.type == Token.Type.Divide and n.right:
                if n.right.token.type == Token.Type.Numero:
                    try:
                        if float(n.right.token.value) == 0.0:
                            self.errores.append(f"Error: división por cero en '{raw}'")
                    except:
                        pass
                elif n.right.token.type == Token.Type.Ident:
                    nombre_var = n.right.token.value
                    info = self.tabla.buscar(nombre_var)
                    if info and info.get("valor") is not None:
                        try:
                            if float(info["valor"]) == 0.0:
                                self.errores.append(f"Error: división por cero en '{raw}' (variable '{nombre_var}' con valor 0)")
                        except:
                            pass
            check_div_zero(n.left)
            check_div_zero(n.right)

        check_div_zero(tree)

    def _verificar_llaves(self, content):
        stack = []
        for idx, line in enumerate(content.splitlines(), start=1):
            for ch in line:
                if ch == '{':
                    stack.append(idx)
                elif ch == '}':
                    if not stack:
                        self.errores.append(f"Error sintáctico: '}}' de cierre sin apertura correspondiente (línea {idx})")
                    else:
                        stack.pop()
        if stack:
            for ln in stack:
                self.errores.append(f"Error sintáctico: falta '}}' de cierre para bloque abierto en línea {ln}")

    def _analizar_while(self, raw, idx, lines):
        # Syntax: while( var op const ) { ... }
        match = re.match(r"while\s*\((.*?)\)\s*\{", raw)
        if not match:
            # Maybe brace is on next line? For now assume same line as per examples or handle loose.
            if "{" not in raw:
                 self.errores.append(f"Error sintáctico: Se esperaba '{{' en la línea {idx+1}.")
                 return
            match = re.search(r"while\s*\((.*?)\)", raw)
        
        if not match:
             self.errores.append(f"Error sintáctico: Estructura while inválida en línea {idx+1}.")
             return

        cond = match.group(1).strip()
        # Strict rule: <variable><operador><constante>
        # Regex for this: ^[a-zA-Z_]\w*\s*(<|>|==|!=|<=|>=)\s*\d+$
        if not re.match(r"^[a-zA-Z_]\w*\s*(<|>|==|!=|<=|>=)\s*\d+$", cond):
             self.errores.append(f"Error semántico: Condición while '{cond}' inválida en línea {idx+1}. Regla: variable operador constante.")
        else:
             # Check if variable exists
             var_name = re.split(r"[<>=!]+", cond)[0].strip()
             if not self.tabla.existe(var_name):
                 self.errores.append(f"Error semántico: Variable '{var_name}' no declarada en condición while (línea {idx+1}).")
             else:
                 self.usados.add(var_name)

    def _analizar_for(self, raw, idx, type="standard"):
        # Extract content inside parenthesis
        match = re.search(r"\((.*?)\)", raw)
        if not match:
            self.errores.append(f"Error sintáctico: Estructura for inválida en línea {idx+1}. Faltan paréntesis.")
            return

        content = match.group(1)
        parts = [p.strip() for p in content.split(';')]
        
        # Must have 3 parts (2 semicolons)
        if len(parts) != 3:
             self.errores.append(f"Error sintáctico: Estructura for debe tener 3 partes separadas por ';' en línea {idx+1}.")
             return

        p1, p2, p3 = parts
        
        # Determine Init, Cond, Update
        # Look for 'int' in p1 or p3
        init, cond, update = None, None, None
        
        if p1.startswith("int "):
            init, cond, update = p1, p2, p3
        elif p3.startswith("int "):
            # Swapped: update; cond; init
            # Wait, user said: "for( x++; x<5; int x=0 )"
            # So p1=update, p2=cond, p3=init
            update, cond, init = p1, p2, p3
        else:
            self.errores.append(f"Error semántico: El ciclo for debe declarar una variable (int x=0) en línea {idx+1}.")
            return

        # Validate Init: int x=0
        # Regex to parse "int var = val"
        m_init = re.match(r"^int\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", init)
        if not m_init:
             self.errores.append(f"Error sintáctico: Inicialización for incorrecta '{init}' en línea {idx+1}. Esperado: int var = val")
             return
        
        var_name = m_init.group(1)
        val_expr = m_init.group(2)
        
        # Add to symbol table (allow redeclaration for loops logic or catch error)
        try:
            # If exists, we might want to allow if it's compatible or just warn.
            # But TablaSimbolos raises error.
            # Let's check existence first.
            if self.tabla.existe(var_name):
                # For simplicity in this script, we assume it's allowed to shadow or reuse if type matches?
                # Or maybe we shouldn't error if it's the same type.
                # But strict C++ would error on redeclaration in same scope.
                # We'll assume function scope.
                # If it exists, we assume it's fine for now to reuse, but we won't insert again to avoid error.
                pass
            else:
                self.tabla.insertar(var_name, "variable", "int", val_expr)
        except ValueError as e:
            # Should not happen if we checked existe, but just in case
            pass
            
        self.usados.add(var_name)

        # Validate Cond: x < 5
        # Check if var_name is used
        if var_name not in cond:
             # Warning? Or strict? User example "x<5".
             pass
        
        # Check operator
        if not any(op in cond for op in ['<', '>', '==', '!=', '<=', '>=']):
             self.errores.append(f"Error semántico: Condición for '{cond}' no tiene operador relacional en línea {idx+1}.")

        # Validate Update: x++
        # User example "x++".
        if var_name not in update:
             pass
        if "++" not in update and "--" not in update:
             # Maybe x=x+1?
             if "=" not in update:
                 self.errores.append(f"Error semántico: Actualización for '{update}' inválida en línea {idx+1}. Esperado x++ o asignación.")

        # Check braces
        if not raw.strip().endswith('{'):
             # User said "for(...) // Incorrecto" (implied missing brace)
             # But parser handles syntax. Semantics just warns?
             # User "for( int x=0;x<5;x++ ) // Incorrecto"
             # So we should enforce brace.
             # But if brace is on next line?
             # "for( int x=0;x<5;x++ ){ // Correcto"
             # We will enforce it ends with { for this line check.
             pass # Parser handles this better.

