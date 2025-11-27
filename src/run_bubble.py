import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compiler.lexer import Lexer, Token
from compiler.parser import Parser
from compiler.interpreter import Interpreter

def run_test():
    # Target the file provided by the user
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'bubble_sort_cpp.txt')
    
    print(f"Reading file: {file_path}")
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    print("--- Source Code ---")
    print(source_code)
    print("-------------------")

    print("\n[0] Token Debugging...")
    lexer = Lexer(source_code)
    while True:
        token = lexer.next_token()
        print(token)
        if token.type == Token.Type.Fin:
            break

    print("\n[1] Lexical Analysis & Parsing...")
    try:
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        ast = parser.parse()
        print("Parsing successful!")
    except Exception as e:
        print(f"Parsing Failed: {e}")
        # Print current token if possible (accessing internal state)
        try:
            print(f"Current Token in Parser: {parser.token_actual}")
        except:
            pass
        import traceback
        traceback.print_exc()
        return

    print("\n[2] Interpreting...")
    try:
        interpreter = Interpreter()
        interpreter.interpret(ast)
        print("\nInterpretation finished.")
    except Exception as e:
        print(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
