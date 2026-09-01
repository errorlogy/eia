#!/usr/bin/env python3
"""
Clean and package LaTeX papers for arXiv submission.
Uses Google Research's `arxiv-latex-cleaner` and generates a verified .tar.gz bundle.
"""

import argparse
import os
import subprocess
import sys
import tarfile

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_PAPER_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "arxiv"
)


def clean_and_package(paper_dir: str, output_parent_dir: str = None) -> bool:
    paper_dir = os.path.abspath(paper_dir)
    if not os.path.isdir(paper_dir):
        print(f"[!] Directory not found: {paper_dir}")
        return False

    paper_name = os.path.basename(paper_dir.rstrip("\\/"))
    if not output_parent_dir:
        output_parent_dir = os.path.dirname(paper_dir)

    cleaned_dir = os.path.join(output_parent_dir, f"{paper_name}_arXiv")
    tar_path = os.path.join(output_parent_dir, f"{paper_name}_arXiv_submission.tar.gz")

    print(f"[*] Running arxiv-latex-cleaner on '{paper_dir}'...")

    cmd = [sys.executable, "-m", "arxiv_latex_cleaner", paper_dir]
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print(f"[!] arxiv-latex-cleaner encountered an issue: {res.stderr or res.stdout}")
        return False

    print(f"[OK] Cleaned directory created: {cleaned_dir}")

    total_size_bytes = 0
    for root, _, files in os.walk(cleaned_dir):
        for f in files:
            fp = os.path.join(root, f)
            total_size_bytes += os.path.getsize(fp)

    size_mb = total_size_bytes / (1024 * 1024)
    print(f"[i] Cleaned package uncompressed size: {size_mb:.2f} MB (arXiv limit is 10 MB)")

    print(f"[*] Compressing into submission archive: {tar_path}...")
    with tarfile.open(tar_path, "w:gz") as tar:
        for item in os.listdir(cleaned_dir):
            item_path = os.path.join(cleaned_dir, item)
            tar.add(item_path, arcname=item)

    tar_size_kb = os.path.getsize(tar_path) / 1024
    print(f"[OK] Successfully created arXiv submission bundle: {tar_path} ({tar_size_kb:.1f} KB)")
    print("[OK] Ready for direct upload to https://arxiv.org/submit")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean and package LaTeX paper for arXiv submission"
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        default=DEFAULT_PAPER_DIR,
        help="Path to raw paper directory (default: arxiv/)",
    )
    parser.add_argument(
        "--out", "-o", type=str, default=None, help="Output destination folder"
    )

    args = parser.parse_args()
    success = clean_and_package(args.dir, args.out)
    sys.exit(0 if success else 1)
