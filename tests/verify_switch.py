from parser import SintacticoPDF
import sys
import os

# Ensure we can import from current directory
sys.path.append(os.getcwd())

def run_test(filename):
    print(f"--- Testing {filename} ---")
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        def mock_out(msg):
            print(msg, end='')
            
        SintacticoPDF(content, mock_out)
        print("\n[SUCCESS]")
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    run_test("pruebas_switch.txt")
    run_test("pruebas_switch_error.txt")
