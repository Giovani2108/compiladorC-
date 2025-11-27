#include <iostream>

using namespace std;

int main() {
    int n = 5;
    int numeros[] = {5, 4, 3, 2, 1};

    for (int i = 0; i < n; i++) {
        // Missing semicolon here
        cout << numeros[i] << " "
    }
    cout << endl;
    return 0;
}
