import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from compiler.lexer import Lexer
from compiler.parser import Parser

def run_test():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'repro_missing_semicolon_cout.cpp')
    
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

    print("\n[1] Parsing...")
    try:
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        ast = parser.parse()
        print("Parsing successful! (This is unexpected if there is a syntax error)")
    except Exception as e:
        print(f"Parsing Failed: {e}")

if __name__ == "__main__":
    run_test()
