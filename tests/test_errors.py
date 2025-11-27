import sys
import os
import re

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter

def run_test(file_name, description):
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', file_name)
    print(f"\n--- Testing {description} ({file_name}) ---")
    
    with open(file_path, 'r') as f:
        content = f.read()

    try:
        # 1. Lexer
        lexer = Lexer(content)
        # 2. Parser
        parser = Parser(lexer)
        ast = parser.parse()
        # 3. Interpreter
        interpreter = Interpreter()
        interpreter.interpret(ast)
        print("SUCCESS: No error raised (Unexpected for this test)")
    except Exception as e:
        msg = str(e)
        print(f"CAUGHT ERROR: {msg}")
        # Check for line number
        match = re.search(r"línea (\d+)", msg, re.IGNORECASE)
        if match:
            print(f"PASS: Line number found: {match.group(1)}")
        else:
            print("FAIL: No line number found in error message")

if __name__ == "__main__":
    run_test("error_lexical.cpp", "Lexical Error")
    run_test("error_syntax.cpp", "Syntax Error")
    run_test("error_semantic.cpp", "Semantic Error")
