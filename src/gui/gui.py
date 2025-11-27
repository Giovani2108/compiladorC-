import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import os
from src.compiler.lexer import Lexer, Token
from src.compiler.parser import Parser, SintacticoPDF
from src.compiler.automata import Automata
from src.compiler.code_generator import CodeGeneratorFromTree
from src.compiler.symbol_table import TablaSimbolos
from src.compiler.semantics import SemanticAnalyzer
import tkinter.ttk as ttk

class CompiladorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Compilador C++ - Diseño Premium")
        self.automata = Automata()
        
        # Configuración de Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        accent_color = "#4CAF50"
        error_color = "#ff5555"
        text_bg = "#1e1e1e"
        text_fg = "#d4d4d4"
        
        master.configure(bg=bg_color)
        
        # Estilos
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        
        # Header Frame (User Info) - MOVED TO TOP
        header_frame = ttk.Frame(master)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))
        
        info_text = (
            "JOSE GIOVANI CALDERON RODRIGUEZ  |  CÓDIGO: 219551032  |  "
            "COMPILADORES D03  |  MAESTRO RAMIRO LUPERCIO"
        )
        lbl_header = ttk.Label(header_frame, text=info_text, font=("Segoe UI", 9, "bold"), foreground="#4CAF50", anchor=tk.CENTER)
        lbl_header.pack(fill=tk.X)

        # Toolbar Frame
        self.toolbar_frame = ttk.Frame(master)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Botón Ejecutar
        self.btn_run = tk.Button(self.toolbar_frame, text="▶ EJECUTAR", command=self.run_code, 
                                 bg=accent_color, fg="white", font=("Segoe UI", 12, "bold"), 
                                 relief=tk.FLAT, padx=20, pady=5, cursor="hand2")
        self.btn_run.pack(side=tk.LEFT)
        
        # Main Container (PanedWindow for vertical resizing)
        main_pane = ttk.PanedWindow(master, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Editor Frame
        self.text_frame = ttk.Frame(main_pane)
        main_pane.add(self.text_frame, weight=3) # Editor gets more space by default
        
        # Line Numbers & Text Area
        self.line_numbers = tk.Text(self.text_frame, width=4, padx=3, takefocus=0, border=0, 
                                   background=bg_color, foreground="#888888", state='disabled', font=("Consolas", 12))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.text_area = scrolledtext.ScrolledText(self.text_frame, wrap=tk.NONE, undo=True,
                                                   bg=text_bg, fg=text_fg, insertbackground="white",
                                                   font=("Consolas", 12))
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.text_area.vbar.config(command=self.sync_scroll)
        self.line_numbers.config(yscrollcommand=self.text_area.vbar.set)
        
        self.text_area.bind('<KeyRelease>', self.update_line_numbers)
        self.text_area.bind('<MouseWheel>', self.sync_scroll_wheel)
        self.text_area.bind('<Button-1>', self.update_line_numbers)
        
        self.update_line_numbers()

        # Output Frame
        self.output_frame = ttk.Frame(main_pane)
        main_pane.add(self.output_frame, weight=1)
        
        self.output_area = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, 
                                                     bg="#000000", fg="#00ff00",
                                                     font=("Consolas", 11))
        self.output_area.pack(fill=tk.BOTH, expand=True)



        # Menu
        menu_bar = tk.Menu(master)
        
        # Archivo
        archivo_menu = tk.Menu(menu_bar, tearoff=0)
        archivo_menu.add_command(label="Abrir", accelerator="Ctrl+A", command=self.abrir_archivo)
        archivo_menu.add_command(label="Guardar", accelerator="Ctrl+G", command=self.guardar_archivo)
        archivo_menu.add_command(label="Limpiar", accelerator="Ctrl+P", command=self.limpiar)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", accelerator="Ctrl+Q", command=master.quit)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

        # Compilador (Legacy)
        compilador_menu = tk.Menu(menu_bar, tearoff=0)
        compilador_menu.add_command(label="Ejecutar", accelerator="F5", command=self.run_code)
        menu_bar.add_cascade(label="Compilador", menu=compilador_menu)
        
        # Ayuda
        ayuda_menu = tk.Menu(menu_bar, tearoff=0)
        ayuda_menu.add_command(label="Insertar stdio.h", command=lambda: self.insert_include("<stdio.h>"))
        menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)

        # Variables
        variables_menu = tk.Menu(menu_bar, tearoff=0)
        variables_menu.add_command(label="int", command=lambda: self.insertar_tipo("int"))
        variables_menu.add_command(label="float", command=lambda: self.insertar_tipo("float"))
        variables_menu.add_command(label="string", command=lambda: self.insertar_tipo("string"))
        menu_bar.add_cascade(label="Variables", menu=variables_menu)

        master.config(menu=menu_bar)

        # --- Bind de atajos ---
        master.bind("<Control-a>", lambda e: self.abrir_archivo())
        master.bind("<Control-g>", lambda e: self.guardar_archivo())
        master.bind("<Control-p>", lambda e: self.limpiar())
        master.bind("<Control-q>", lambda e: master.quit())

        master.bind("<Alt-l>", lambda e: self.analisis_lexico())
        master.bind("<Alt-s>", lambda e: self.analisis_sintactico())
        master.bind("<Control-s>", lambda e: self.analisis_semantico())
        master.bind("<F5>", lambda e: self.run_code())

    # --- Funciones GUI ---
    def sync_scroll(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def sync_scroll_wheel(self, event):
        self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def update_line_numbers(self, event=None):
        line_count = self.text_area.get('1.0', tk.END).count('\n')
        if line_count is None:
            line_count = 1
        else:
            line_count += 1 # El último salto de línea
        
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        # Sincronizar vista
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def abrir_archivo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.c *.cpp *.py"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, f.read())
                self.update_line_numbers()

    def guardar_archivo(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.get(1.0, tk.END))
            messagebox.showinfo("Guardar", f"Archivo guardado: {file_path}")

    def limpiar(self):
        self.text_area.delete(1.0, tk.END)
        self.output_area.delete(1.0, tk.END)

    def analisis_lexico(self):
        expr = self.text_area.get(1.0, tk.END).strip()
        if not expr:
            messagebox.showinfo("Léxico", "Texto vacío.")
            return
        lexer = Lexer(expr)
        tokens = []
        try:
            while True:
                t = lexer.next_token()
                tokens.append(t)
                if t.type == Token.Type.Fin:
                    break
        except Exception as e:
            messagebox.showerror("Error Léxico", str(e))
            return
        # Mostrar tokens en output_area
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, "Tokens leídos (tipo, valor):\n")
        for tk_ in tokens:
            self.output_area.insert(tk.END, f"  - {tk_}\n")

    def analisis_sintactico(self):
        # Implementación del análisis sintáctico siguiendo la metodología y formato
        # de salida del documento PDF del profesor.
        # Se ignoran los analizadores anteriores y se implementa el algoritmo del
        # Sintáctico propuesto en clase (tokens M { ... } ; etc.).

        content = self.text_area.get(1.0, tk.END)
        if not content.strip():
            messagebox.showinfo("Sintáctico", "Ingrese un código para analizar.")
            return

        self.output_area.delete(1.0, tk.END)

        # ======== Ejecución real del análisis ========
        def out_gui(msg):
            self.output_area.insert(tk.END, msg)
            self.output_area.see(tk.END)

        try:
            SintacticoPDF(content, out_gui)
        except SyntaxError as e:
            self.output_area.insert(tk.END, f"\n{str(e)}\n")
        except Exception as e:
            self.output_area.insert(tk.END, f"\nError inesperado: {str(e)}\n")


    def analisis_semantico(self):
        content = self.text_area.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("Semántico", "No hay código para analizar.")
            return

        analyzer = SemanticAnalyzer()
        res = analyzer.analizar(content)
        
        tabla = res["tabla"]
        errores = res["errores"]
        usados = res["usados"]

        # 3️⃣ Mostrar resultados
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, "=== Análisis Semántico ===\n")
        self.output_area.insert(tk.END, repr(tabla) + "\n")
        self.output_area.insert(tk.END, f"Identificadores usados: {sorted(list(usados))}\n")
        if errores:
            self.output_area.insert(tk.END, "Errores detectados:\n")
            for e in errores:
                self.output_area.insert(tk.END, f"  - {e}\n")
        else:
            self.output_area.insert(tk.END, "OK: No se encontraron errores semánticos.\n")




    def codigo_intermedio(self):
        """
        Produce:
         - resultados del Automata (tokens, RPN, evaluacion)
         - genera archivo .obj con instrucciones (usando CodeGeneratorFromTree y Parser)
        """
        content = self.text_area.get(1.0, tk.END)
        expr = content.strip()
        if not expr:
            messagebox.showinfo("Código Intermedio", "No hay expresión para generar código.")
            return

        # 1) obtener resultados del automata tradicional
        res = self.automata.analizar(expr)
        self.output_area.delete(1.0, tk.END)
        if "error" in res:
            self.output_area.insert(tk.END, f"Error: {res['error']}\n")
            return

        self.output_area.insert(tk.END, "=== Resultado Automata ===\n")
        self.output_area.insert(tk.END, f"Tokens: {res['tokens']}\n")
        self.output_area.insert(tk.END, f"RPN: {res['rpn']}\n")
        self.output_area.insert(tk.END, f"Resultado final (si aplica): {res['final_result']}\n")
        self.output_area.insert(tk.END, f"Identificadores detectados: {res['identificadores']}\n")
        self.output_area.insert(tk.END, "Codigo intermedio (heurístico):\n")
        for line in res['codigo_intermedio']:
            self.output_area.insert(tk.END, f"  {line}\n")

        # 2) construir árbol con Parser (para la actividad 1.1) y generar árbol textual
        lexer = Lexer(expr)
        parser = Parser(lexer)
        try:
            tree = parser.parse()
        except Exception as e:
            self.output_area.insert(tk.END, f"\nError parseando para generar código: {e}\n")
            return

        self.output_area.insert(tk.END, "\n=== Árbol Sintáctico (Parser) ===\n")
        tree.print_tree(output_func=lambda s: self.output_area.insert(tk.END, s + "\n"))

        # 3) detectar variables declaradas (simplemente como en semántico)
        declared = set()
        for line in content.splitlines():
            line = line.strip().rstrip(';')
            m = re.match(r'^(int|float)\s+([A-Za-z_][A-Za-z0-9_]*)$', line)
            if m:
                declared.add(m.group(2))
            m2 = re.match(r'^char\s+([A-Za-z_][A-Za-z0-9_]*)\s*\[.*\]$', line)
            if m2:
                declared.add(m2.group(1))

        # 4) Generar código objeto
        cg = CodeGeneratorFromTree(declared_vars=declared)
        outfile = cg.generate_from_tree(tree, output_path="output.obj")
        self.output_area.insert(tk.END, f"\nCódigo objeto generado en: {outfile}\n")
        # mostrar contenido del fichero generado
        if os.path.exists(outfile):
            self.output_area.insert(tk.END, "\nContenido de output.obj:\n")
            with open(outfile, 'r', encoding='utf-8') as f:
                for ln in f:
                    self.output_area.insert(tk.END, ln)
        else:
            self.output_area.insert(tk.END, "No se encontró el fichero de salida.\n")

    def highlight_error(self, line_num):
        """Resalta la línea del error en el editor"""
        self.text_area.tag_remove("error", "1.0", tk.END)
        self.text_area.tag_add("error", f"{line_num}.0", f"{line_num}.end")
        self.text_area.tag_config("error", background="#ffcccc", foreground="red")
        self.text_area.see(f"{line_num}.0")

    def run_code(self):
        """
        Ejecuta el código usando el Intérprete.
        """
        from src.compiler.interpreter import Interpreter
        
        content = self.text_area.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("Ejecutar", "No hay código para ejecutar.")
            return

        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, "=== Ejecución ===\n")
        
        # Limpiar resaltado previo
        self.text_area.tag_remove("error", "1.0", tk.END)

        def gui_print(msg):
            self.output_area.insert(tk.END, str(msg))
            self.output_area.see(tk.END)

        try:
            # 1. Parsear
            lexer = Lexer(content)
            parser = Parser(lexer)
            ast = parser.parse()
            
            # 2. Interpretar
            interpreter = Interpreter(output_callback=gui_print)
            interpreter.interpret(ast)
            
            self.output_area.insert(tk.END, "\n=== Fin de Ejecución ===\n")
        except Exception as e:
            # Error de sintaxis (ValueError) o Semántico (RuntimeError)
            msg = str(e)
            self.output_area.insert(tk.END, f"\n{msg}\n")
            # Intentar extraer línea
            match = re.search(r"línea (\d+)", msg, re.IGNORECASE)
            if match:
                line_num = int(match.group(1))
                self.highlight_error(line_num)

    def insert_include(self, header_str):
        content = self.text_area.get(1.0, tk.END)
        if header_str in content:
            return
        lines = content.splitlines()
        insert_index = 0
        for idx, ln in enumerate(lines):
            if ln.strip().startswith("#include"):
                insert_index = idx + 1
        lines.insert(insert_index, f"#include {header_str}")
        new_content = "\n".join(lines) + ("\n" if not content.endswith("\n") else "")
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, new_content)
        self.update_line_numbers()

    def insertar_tipo(self, tipo):
        tipos_def = {
            "int": ("int miVariable;", "<stdio.h>"),
            "float": ("float miVariable;", "<stdio.h>"),
            "string": ("char miVariable[256];", "<string.h>")
        }
        if tipo not in tipos_def:
            return
        decl, lib = tipos_def[tipo]
        self.insert_include(lib)
        # insertar la declaración al final
        cur = self.text_area.get(1.0, tk.END)
        if not cur.endswith("\n"):
            cur += "\n"
        cur += decl + "\n"
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, cur)
        self.update_line_numbers()
