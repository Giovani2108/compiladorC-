import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter

def test_bubble_sort_cpp():
    with open('tests/bubble_sort_cpp.txt', 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("Code loaded.")
    
    lexer = Lexer(code)
    parser = Parser(lexer)
    ast = parser.parse()
    print("AST parsed.")
    
    output = []
    def capture_output(text):
        output.append(text)
        
    interpreter = Interpreter(output_callback=capture_output)
    interpreter.interpret(ast)
    print("Execution finished.")
    
    full_output = "".join(output)
    print("Output:", full_output)
    
    expected_sorted = "11 12 22 25 34 64 90"
    if expected_sorted in full_output:
        print("SUCCESS: Bubble Sort verified!")
    else:
        print(f"FAILURE: Expected to find '{expected_sorted}' in output.")
        sys.exit(1)

if __name__ == "__main__":
    test_bubble_sort_cpp()
