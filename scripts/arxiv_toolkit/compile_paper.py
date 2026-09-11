#!/usr/bin/env python3
"""
Compile LaTeX documents into PDF using latexmk or pdflatex.
Checks for missing references, overfull \\hbox, and compilation errors.
"""

import argparse
import os
import subprocess
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_PAPER_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "arxiv"
)


def compile_latex(paper_dir: str, main_tex: str = "main.tex") -> bool:
    main_path = os.path.join(paper_dir, main_tex)
    if not os.path.exists(main_path):
        print(f"[!] Error: File not found: {main_path}")
        return False

    print(f"[*] Compiling {main_tex} in {paper_dir}...")

    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-file-line-error", main_tex]

    try:
        res = subprocess.run(
            cmd,
            cwd=paper_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        output = res.stdout

        errors = [
            line
            for line in output.splitlines()
            if "error:" in line.lower() or "! " in line
        ]
        warnings = [
            line
            for line in output.splitlines()
            if "warning:" in line.lower() or "overfull" in line.lower()
        ]

        if res.returncode == 0:
            pdf_name = main_tex.replace(".tex", ".pdf")
            pdf_path = os.path.join(paper_dir, pdf_name)
            print(f"[OK] Compilation successful! PDF generated: {pdf_path}")
            if warnings:
                print(f"[i] Found {len(warnings)} layout notices / warnings.")
            return True

        print(f"[!] Compilation failed (code {res.returncode}):")
        for err in errors[:10]:
            print(f"    {err}")
        return False

    except FileNotFoundError:
        print("[*] latexmk not found, attempting pdflatex + bibtex fallback...")
        base = main_tex.replace(".tex", "")
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", main_tex],
            cwd=paper_dir,
            check=False,
        )
        subprocess.run(["bibtex", base], cwd=paper_dir, check=False)
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", main_tex],
            cwd=paper_dir,
            check=False,
        )
        res = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", main_tex],
            cwd=paper_dir,
            check=False,
        )
        return res.returncode == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile LaTeX paper into PDF")
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        default=DEFAULT_PAPER_DIR,
        help="Directory containing main.tex (default: arxiv/)",
    )
    parser.add_argument(
        "--main", "-m", type=str, default="main.tex", help="Main tex file name"
    )

    args = parser.parse_args()
    target_dir = os.path.abspath(args.dir)
    success = compile_latex(target_dir, args.main)
    sys.exit(0 if success else 1)
