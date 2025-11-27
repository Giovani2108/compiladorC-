#include <iostream>

using namespace std;

int main() {
    // 1. Creación del arreglo
    int numeros[] = {64, 34, 25, 12, 22, 11, 90};
    
    // Calculamos el tamaño del arreglo automáticamente
    int n = sizeof(numeros) / sizeof(numeros[0]);

    // Imprimir el arreglo original
    cout << "Arreglo original: ";
    for (int i = 0; i < n; i++) {
        cout << numeros[i] << " ";
    }
    cout << endl;

    // 2. Ordenamiento Burbuja
    // El ciclo externo controla cuántas pasadas hacemos
    for (int i = 0; i < n - 1; i++) {
        
        // El ciclo interno compara elementos adyacentes
        // Restamos 'i' porque los últimos elementos ya están ordenados
        for (int j = 0; j < n - i - 1; j++) {
            
            // Si el elemento actual es mayor que el siguiente, los intercambiamos
            if (numeros[j] > numeros[j + 1]) {
                int temporal = numeros[j];
                numeros[j] = numeros[j + 1];
                numeros[j + 1] = temporal;
            }
        }
    }

    // 3. Imprimir el arreglo ordenado
    cout << "\nArreglo ordenado con Burbuja: ";
    for (int i = 0; i < n; i++) {
        cout << numeros[i] << " ";
    }
    cout << endl;

    return 0;
}
