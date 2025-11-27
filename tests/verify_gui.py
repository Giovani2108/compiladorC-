import sys
import os
import tkinter as tk

# Add project root to path (COMPILADORES)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.gui.gui import CompiladorGUI
    print("Successfully imported CompiladorGUI")
    
    # Optional: Try to instantiate if possible (headless might be tricky but we can try)
    root = tk.Tk()
    app = CompiladorGUI(root)
    print("Successfully instantiated CompiladorGUI")
    root.destroy()
    
except Exception as e:
    print(f"Failed: {e}")
