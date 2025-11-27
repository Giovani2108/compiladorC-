import sys
import os
import glob

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter

def run_test(file_path):
    print(f"\n{'='*20} Running Test: {os.path.basename(file_path)} {'='*20}")
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    print("--- Source Code ---")
    print(source_code)
    print("-------------------")

    print("\n[1] Parsing...")
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

def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        'bubble_valid.cpp',
        'bubble_syntax_error.cpp',
        'bubble_semantic_error_1.cpp',
        'bubble_semantic_error_2.cpp'
    ]
    
    for test_file in test_files:
        run_test(os.path.join(test_dir, test_file))

if __name__ == "__main__":
    main()
