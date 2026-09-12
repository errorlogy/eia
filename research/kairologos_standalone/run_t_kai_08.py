#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from harnesses.t_kai_08_syntax_vs_semantics import main

if __name__ == "__main__":
    main()
