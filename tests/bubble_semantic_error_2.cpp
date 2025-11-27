#include <iostream>

using namespace std;

int main() {
    int arr[3];
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;
    
    // Semantic error: Accessing index out of bounds (if implemented)
    // Or maybe type mismatch?
    // Let's try to assign a string to an int array if type checking is implemented, 
    // but this is an interpreter, so it might just work or fail at runtime.
    // Let's try to use a non-array as an array.
    
    int x = 10;
    x[0] = 5; // Error: x is not an array

    return 0;
}
