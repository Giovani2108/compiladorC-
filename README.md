# Documentación del Compilador C++

Este documento detalla el funcionamiento interno del compilador, la función de cada módulo, y el mecanismo de detección y resaltado de errores, utilizando el algoritmo de Ordenamiento Burbuja como caso de estudio.

## 1. Arquitectura del Proyecto

El compilador sigue una arquitectura modular clásica dividida en las siguientes fases:

1.  **Análisis Léxico (`lexer.py`)**: Convierte el código fuente en una secuencia de tokens.
2.  **Análisis Sintáctico (`parser.py`)**: Verifica la estructura gramatical y construye un Árbol de Sintaxis Abstracta (AST).
3.  **Análisis Semántico e Interpretación (`interpreter.py`)**: Ejecuta el AST, gestiona la memoria y verifica reglas semánticas (tipos, variables definidas).
4.  **Interfaz Gráfica (`gui.py`)**: Proporciona un editor de código con resaltado de errores y visualización de salida.

### Descripción de Archivos

*   **`src/compiler/lexer.py`**:
    *   **Clase `Token`**: Representa la unidad mínima (ej. `int`, `numeros`, `[`, `;`). Guarda el tipo, valor y **número de línea**.
    *   **Clase `Lexer`**: Lee el código carácter por carácter. Ignora espacios y comentarios. Genera tokens o reporta errores léxicos (caracteres inválidos).

*   **`src/compiler/parser.py`**:
    *   **Clase `Parser`**: Solicita tokens al Lexer. Usa descenso recursivo para validar la gramática (ej. `declaración -> tipo identificador = expresión ;`).
    *   **Construcción del AST**: Crea nodos (`TreeNode`, `DeclarationNode`, `BlockNode`) que representan la estructura lógica del programa.
    *   **Manejo de Errores**: Si encuentra un token inesperado, lanza `ValueError` con la línea y el token esperado.

*   **`src/compiler/interpreter.py`**:
    *   **Clase `Interpreter`**: Recorre el AST generado por el Parser.
    *   **Entorno (`environment`)**: Un diccionario que simula la memoria RAM, guardando variables y sus valores.
    *   **Ejecución**: Realiza operaciones matemáticas, lógica de control (`if`, `for`), y entrada/salida (`cout`).
    *   **Errores Semánticos**: Detecta variables no definidas, tipos incorrectos, etc., y lanza excepciones con la línea del error.

*   **`src/gui/gui.py`**:
    *   **Clase `CompiladorGUI`**: Gestiona la ventana principal.
    *   **Editor**: Usa `ScrolledText` para el código.
    *   **Resaltado**: Intercepta errores y marca la línea correspondiente en rojo.

---

## 2. El Viaje del Código: Caso "Ordenamiento Burbuja"

Analicemos cómo el compilador procesa el siguiente fragmento:

```cpp
int main() {
    int numeros[] = {64, 34, 25};
    int n = sizeof(numeros) / sizeof(numeros[0]);
    // ... lógica de burbuja ...
}
```

### Fase 1: Análisis Léxico (`lexer.py`)
El Lexer lee `int numeros[] = ...` y genera:
1.  `Token(Ident, "int", Line:2)`
2.  `Token(Ident, "numeros", Line:2)`
3.  `Token(CorcheteAbre, "[", Line:2)`
4.  `Token(CorcheteCierra, "]", Line:2)`
5.  `Token(Asign, "=", Line:2)`
... y así sucesivamente.

**Detección de Error Léxico**: Si escribieras `int $var;`, el Lexer encontraría `$` (no válido) y lanzaría un error indicando la línea.

### Fase 2: Análisis Sintáctico (`parser.py`)
El Parser recibe los tokens y busca patrones conocidos.
1.  Ve `int` (tipo) y `numeros` (nombre).
2.  Ve `[` y `]`, deduce que es un arreglo.
3.  Ve `=`, espera una inicialización.
4.  Ve `{`, entra en modo "lista de inicialización" y parsea cada número separado por comas.
5.  **Validación**: Al final, verifica estrictamente que haya un `;`. Si falta, lanza: `Error Sintáctico en línea 2: Se esperaba ';'`.

### Fase 3: Interpretación (`interpreter.py`)
El Intérprete recibe el nodo `DeclarationNode` del AST.
1.  **Memoria**: Crea una entrada en `self.environment` para `numeros`.
2.  **Arreglos**: A diferencia de C++ real (memoria contigua), aquí se simula con un diccionario: `{0: 64, 1: 34, 2: 25}`.
3.  **Sizeof**: Calcula y guarda el tamaño total (ej. 3 elementos * 4 bytes = 12 bytes) en una variable interna `__sizeof_numeros`.
4.  **Ejecución de `sizeof`**: Cuando encuentra `sizeof(numeros)`, busca esa variable interna y devuelve 12.

**Detección de Error Semántico**: Si intentas `cout << x;` y `x` no fue declarado, el Intérprete busca en `self.environment`, no lo encuentra, y lanza `RuntimeError: Variable 'x' no definida`.

---

## 3. Sistema de Resaltado de Errores

El sistema de errores es integral y funciona en tres capas para asegurar que **siempre** se marque la línea correcta.

1.  **Origen (Lexer/Parser/Interpreter)**:
    *   Cada vez que se crea un nodo del AST o un token, se guarda `self.line`.
    *   Cuando ocurre un error (ej. `ValueError` en Parser o `RuntimeError` en Interpreter), la excepción se lanza incluyendo el mensaje `"... en línea X: ..."`.

2.  **Captura (GUI)**:
    *   El método `run_code()` en `gui.py` envuelve toda la ejecución en un bloque `try-catch`.
    *   Captura cualquier `Exception`.

3.  **Visualización**:
    *   La GUI usa una Expresión Regular (`re.search(r"línea (\d+)", msg)`) para buscar el número de línea en el mensaje de error.
    *   Si lo encuentra, llama a `highlight_error(line_num)`.
    *   Este método usa "tags" de Tkinter para cambiar el fondo de esa línea a rojo (`#ffcccc`) y hacer scroll hasta ella.

### Por qué se detectan los errores

*   **Falta de `;`**: El Parser está programado para esperar obligatoriamente un `;` después de cada sentencia (`eat(Token.Type.PuntoYComa)`). Si encuentra otra cosa (ej. `cout` o `}`), falla inmediatamente.
*   **Variable no definida**: El Intérprete mantiene un registro estricto de variables declaradas. No permite uso implícito.
*   **Tipos inválidos**: Aunque Python es dinámico, el Intérprete verifica operaciones (ej. no puedes sumar un número a un arreglo completo).

---

## Conclusión

Este compilador es una simulación robusta de un subconjunto de C++. Aunque está escrito en Python, impone las reglas estrictas de C++ (tipado estático simulado, sintaxis de punto y coma, declaración previa) para proporcionar una experiencia educativa fiel. La integración profunda entre el Lexer (que rastrea líneas), el Parser (que valida estructura) y la GUI (que visualiza errores) permite una depuración visual efectiva.
