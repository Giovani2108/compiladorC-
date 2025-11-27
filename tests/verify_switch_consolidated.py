import sys
import os

# Ensure we can import from current directory (project root)
sys.path.append(os.getcwd())

from src.compiler.parser import Parser
from src.compiler.lexer import Lexer
from src.compiler.semantics import SemanticAnalyzer

def run_test_content(content, name, expect_semantic_error=False):
    print(f"--- Testing {name} ---")
    
    # Syntax Check
    print("[SYNTAX CHECK]")
    syntax_error = False
    try:
        lexer = Lexer(content)
        parser = Parser(lexer)
        parser.parse()
        print("Syntax: OK")
    except Exception as e:
        print(f"Syntax Error: {e}")
        syntax_error = True

    # Semantic Check
    print("[SEMANTIC CHECK]")
    analyzer = SemanticAnalyzer()
    res = analyzer.analizar(content)
    errores = res["errores"]
    
    if errores:
        for e in errores:
            print(f"Semantic Error: {e}")
    else:
        print("Semantic: OK")

    if expect_semantic_error:
        if errores:
            print("[SUCCESS] (Expected semantic error found)")
        else:
            print("[FAILURE] (Expected semantic error NOT found)")
    else:
        if not syntax_error and not errores:
            print("[SUCCESS]")
        else:
            print("[FAILURE]")

def parse_and_run_tests():
    file_path = 'tests/data/pruebas_anidadas.txt'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        content = f.read()

    # Split by cases
    cases = content.split('// CASO')
    
    for i, case_block in enumerate(cases[1:], 1): # Skip preamble
        # Extract title
        lines = case_block.strip().splitlines()
        title_line = lines[0].strip()
        title = f"CASO {title_line}"
        
        # Extract code (between description and SALIDA ESPERADA)
        code_lines = []
        in_code = False
        expect_error = False
        
        for line in lines:
            if "int main()" in line:
                in_code = True
            if "// SALIDA ESPERADA:" in line:
                in_code = False
            
            if in_code:
                # Remove comments if they wrap the code (like /* ... */)
                clean_line = line.replace('/*', '').replace('*/', '')
                code_lines.append(clean_line)
                
            if "[ERROR]" in line or "Error" in line:
                expect_error = True

        code = "\n".join(code_lines).strip()
        
        if not code:
            print(f"Skipping empty code block for {title}")
            continue
            
        # Determine if we expect semantic error specifically (based on description or content)
        expect_semantic = "Semantica" in title and "Invalido" in title
        
        # Run test
        print(f"\n{'='*20}\nRunning {title}\n{'='*20}")
        # print(f"Code:\n{code}\n")
        
        # We need to handle the fact that some tests are commented out in the file with /* */
        # The simple cleaner above might leave artifacts, but let's try.
        # Better approach: The file has code inside /* */ for invalid cases.
        # We should strip those.
        
        run_test_content(code, title, expect_semantic_error=expect_semantic)

if __name__ == "__main__":
    parse_and_run_tests()
