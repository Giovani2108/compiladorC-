# generador_codigo.py
# ===========================================
# Módulo independiente para la clase GeneradorCodigo
# ===========================================

class GeneradorCodigo:
    """
    Implementación en Python inspirada en la clase GeneraCodigo del PDF.
    Genera instrucciones tipo máquina virtual en un fichero de salida.
    """
    def __init__(self, nombre_fichero="output.obj"):
        self.nombre_fichero = nombre_fichero
        try:
            self.salida = open(self.nombre_fichero, "w", encoding="utf-8")
        except Exception as e:
            raise IOError(f"No se puede crear el fichero {nombre_fichero}: {e}")

    def close(self):
        try:
            self.salida.close()
        except:
            pass

    def code(self):
        self.salida.write(".CODE\n")
        self.salida.flush()

    def pushc(self, constante):
        # constante puede ser numérico o cadena representada
        self.salida.write(f"PUSHC {constante}\n")
        self.salida.flush()

    def push(self, direccion):
        self.salida.write(f"PUSHA {direccion}\n")
        self.salida.flush()

    def load(self):
        self.salida.write("LOAD\n")
        self.salida.flush()

    def store(self):
        self.salida.write("STORE\n")
        self.salida.flush()

    def neg(self):
        self.salida.write("NEG\n")
        self.salida.flush()

    def add(self):
        self.salida.write("ADD\n")
        self.salida.flush()

    def mul(self):
        self.salida.write("MUL\n")
        self.salida.flush()

    def div(self):
        self.salida.write("DIV\n")
        self.salida.flush()

    def mod(self):
        self.salida.write("MOD\n")
        self.salida.flush()

    def input(self, direccion):
        self.salida.write(f"INPUT {direccion}\n")
        self.salida.flush()

    def output(self, direccion):
        self.salida.write(f"OUTPUT {direccion}\n")
        self.salida.flush()

    def end(self):
        self.salida.write("END\n")
        self.salida.flush()
