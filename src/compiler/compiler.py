from .lexer import Lexer
from .parser import Parser
from .semantics import SemanticAnalyzer
from .code_generator import CodeGenerator

class Compiler:
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = CodeGenerator()

    def compile(self, source_code):
        """
        Compiles the given source code.
        Returns a dict with:
        - status: 'success' or 'error'
        - errors: list of error strings
        - ast: the abstract syntax tree (optional)
        - symbol_table: the symbol table
        - output: generated code or execution result
        """
        results = {
            "status": "success",
            "errors": [],
            "ast": None,
            "symbol_table": None,
            "output": ""
        }

        # 1. Lexical Analysis & Parsing
        try:
            lexer = Lexer(source_code)
            parser = Parser(lexer)
            ast = parser.parse()
            results["ast"] = ast
        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Syntax Error: {str(e)}")
            return results

        # 2. Semantic Analysis
        semantic_result = self.semantic_analyzer.analizar(source_code)
        results["symbol_table"] = semantic_result["tabla"]
        
        if semantic_result["errores"]:
            results["status"] = "error"
            results["errors"].extend(semantic_result["errores"])
            return results

        # 3. Code Generation (Optional/Placeholder)
        # Assuming CodeGenerator has a generate method
        # generated_code = self.code_generator.generate(ast)
        # results["output"] = generated_code

        return results
