import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.compiler.lexer import Lexer
from src.compiler.parser import Parser
from src.compiler.interpreter import Interpreter

def test_bubble_sort():
    with open('tests/bubble_sort.txt', 'r') as f:
        code = f.read()

    print("Code loaded.")
    
    lexer = Lexer(code)
    parser = Parser(lexer)
    ast = parser.parse()
    
    print("AST parsed.")
    
    output = []
    def capture_output(msg):
        output.append(str(msg).strip())
        
    interpreter = Interpreter(output_callback=capture_output)
    interpreter.interpret(ast)
    
    print("Execution finished.")
    print("Output:", output)
    
    expected = ['9999', '8888', '12', '22', '25', '34', '64']
    
    # Filter empty lines if any
    output = [x for x in output if x]
    
    if output == expected:
        print("SUCCESS: Bubble Sort verified!")
    else:
        print(f"FAILURE: Expected {expected}, got {output}")

if __name__ == "__main__":
    test_bubble_sort()
