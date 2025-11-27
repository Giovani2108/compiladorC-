import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from compiler.lexer import Lexer
from compiler.parser import Parser

def run_test():
    # Code with error on line 3
    source_code = """int main() {
    int x = 10
    return 0;
}"""
    
    print("--- Source Code ---")
    print(source_code)
    print("-------------------")

    print("\n[1] Parsing...")
    try:
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        ast = parser.parse()
        print("Parsing successful! (Unexpected)")
    except ValueError as e:
        print(f"Caught Expected Error: {e}")

if __name__ == "__main__":
    run_test()
