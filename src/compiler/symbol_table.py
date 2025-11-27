class TablaSimbolos:
    def __init__(self):
        self.tabla = {}

    def insertar(self, nombre, naturaleza, tipo=None, valor=None, direccion=None):
        if nombre in self.tabla:
            raise ValueError(f"Error semántico: '{nombre}' ya fue declarado.")
        self.tabla[nombre] = {
            "naturaleza": naturaleza,
            "tipo": tipo,
            "valor": valor,
            "direccion": direccion
        }

    def buscar(self, nombre):
        return self.tabla.get(nombre, None)

    def existe(self, nombre):
        return nombre in self.tabla

    def __repr__(self):
        salida = "Tabla de Símbolos:\n"
        for nombre, info in self.tabla.items():
            salida += f"  {nombre} -> {info}\n"
        return salida
