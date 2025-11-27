#include <iostream>

using namespace std;

int main() {
    int n = 5;
    int numeros[] = {5, 4, 3, 2, 1};

    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (numeros[j] > numeros[j + 1]) {
                // Missing semicolon here
                int temporal = numeros[j];
                numeros[j] = numeros[j + 1]
                numeros[j + 1] = temporal;
            }
        }
    }
    return 0;
}
