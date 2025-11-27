import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter

def run_test():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'bubble_sort_repro.cpp')
    
    print(f"Reading file: {file_path}")
    with open(file_path, 'r') as f:
        source_code = f.read()

    print("--- Source Code ---")
    print(source_code)
    print("-------------------")

    print("\n[1] Lexical Analysis & Parsing...")
    try:
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        ast = parser.parse()
        print("Parsing successful!")
    except Exception as e:
        print(f"Parsing Failed: {e}")
        return

    print("\n[2] Interpreting...")
    try:
        interpreter = Interpreter()
        interpreter.interpret(ast)
        print("\nInterpretation finished.")
    except Exception as e:
        print(f"Runtime Error: {e}")

if __name__ == "__main__":
    run_test()
