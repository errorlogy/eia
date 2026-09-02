# Neuraxon Game of Life Utils
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife

import os
import math
import random
import pathlib
from datetime import datetime
from datetime import timezone
from typing import List, Tuple, Optional, Any, Dict

# Import constants for color generation
from config import RESERVED_COLORS

def _variate(val: float, variance: float = 0.2) -> float:
    """Helper to apply biological heterogeneity to parameters."""
    return val * random.uniform(1.0 - variance, 1.0 + variance)

def _clamp(v, a, b):
    """Clamps value v between a and b."""
    return max(a, min(b, v))

def _now_str(): 
    """Returns current UTC timestamp as string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

def _safe_path(name: str) -> str: 
    """Resolves a filename to an absolute path in the current working directory."""
    return str((pathlib.Path(os.getcwd()) / name).resolve())

def _strip_leading_digits(name: str) -> str:
    """Removes leading digits from a string, used for generating names for offspring."""
    i = 0
    while i < len(name) and name[i].isdigit(): i += 1
    return name[i:] if i < len(name) else ""

def _rand_color(exclude: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
    """Generates a random color that is visually distinct from a list of excluded colors."""
    while True:
        c = (random.randint(30, 235), random.randint(30, 235), random.randint(30, 235))
        # Check against dynamic excluded list (other agents)
        if any(sum((c[i] - e[i]) ** 2 for i in range(3)) < 1200 for e in exclude): continue
        # Check against reserved UI/Terrain colors
        if c in RESERVED_COLORS: continue
        return c

def _rot(x, y, a):
    """Rotates a 2D point (x, y) around the origin by angle 'a'."""
    ca, sa = math.cos(a), math.sin(a)
    return (x * ca - y * sa, x * sa + y * ca)

def _chunked(seq, n):
    """Yields successive n-sized chunks from a sequence."""
    n = max(1, int(n))
    for i in range(0, len(seq), n):
        yield seq[i:i + n]

def _pick_save_file(default_name: str) -> Optional[str]:
    """Opens a native OS file dialog to choose a save location."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=default_name, filetypes=[("JSON files", "*.json")])
        root.destroy()
        return path if path else None
    except Exception:
        return _safe_path(default_name)

def _pick_open_file() -> Optional[str]:
    """Opens a native OS file dialog to choose a file to open."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        root.destroy()
        return path if path else None
    except Exception:
        # A simple fallback for environments without a GUI.
        cand = sorted([p for p in os.listdir(os.getcwd()) if p.endswith(".json") and p.startswith("nxer_")])
        return cand[-1] if cand else None
def safe_json_save(data: Dict[str, Any], filepath: str, retries: int = 3) -> bool:
    """
    Saves a dictionary to JSON and verifies integrity by reading it back immediately.
    If verification fails, it retries.
    
    Args:
        data: The dictionary to save.
        filepath: The target file path.
        retries: Number of attempts before giving up.
        
    Returns:
        True if saved and verified successfully, False otherwise.
    """
    for i in range(retries):
        try:
            # 1. Write the data
            with open(filepath, "w") as f:
                json.dump(data, f) # Removed indent for performance/size on large saves, or add indent=2 if readability needed
            
            # 2. Read it back to verify integrity
            with open(filepath, "r") as f_check:
                json.load(f_check)
            
            # If we got here, the JSON is valid
            return True
            
        except (IOError, json.JSONDecodeError) as e:
            print(f"[SAVE ERROR] Attempt {i+1}/{retries} failed for {filepath}: {e}")
            
    print(f"[SAVE FATAL] Could not save verified JSON to {filepath} after {retries} attempts.")
    
    # Emergency backup attempt (try saving with .corrupt suffix just in case it's a verify issue but data exists)
    try:
        emergency_path = filepath + ".unverified"
        with open(emergency_path, "w") as f:
            json.dump(data, f)
        print(f"[SAVE EMERGENCY] Saved unverified dump to {emergency_path}")
    except:
        pass
        
    return False