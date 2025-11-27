import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from compiler.lexer import Lexer, Token

def run_test():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'repro_missing_semicolon_array.cpp')
    
    with open(file_path, 'r') as f:
        source_code = f.read()

    print("--- Source Code ---")
    print(source_code)
    print("-------------------")

    print("\n[1] Lexing...")
    lexer = Lexer(source_code)
    while True:
        token = lexer.next_token()
        print(token)
        if token.type == Token.Type.Fin:
            break

if __name__ == "__main__":
    run_test()
