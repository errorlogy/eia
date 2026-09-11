#!/usr/bin/env python3
"""
Fetch verified academic papers from arXiv API.
Generates hallucination-free BibTeX entries for your manuscript.
"""

import argparse
import re
import sys
from typing import Dict, List

import arxiv

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def clean_bibtex_key(author: str, year: str, title: str) -> str:
    first_author = (
        re.sub(r"[^a-zA-Z]", "", author.split()[0].lower()) if author else "paper"
    )
    first_word = (
        re.sub(r"[^a-zA-Z]", "", title.split()[0].lower()) if title else "key"
    )
    return f"{first_author}{year}{first_word}"


def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    results = []
    for r in client.results(search):
        authors = [a.name for a in r.authors]
        year = str(r.published.year) if r.published else "2024"
        key = clean_bibtex_key(authors[0] if authors else "arxiv", year, r.title)

        bibtex = f"""@article{{{key},
  author    = {{{' and '.join(authors)}}},
  title     = {{{r.title.strip()}}},
  journal   = {{arXiv preprint arXiv:{r.get_short_id()}}},
  year      = {{{year}}},
  url       = {{{r.entry_id}}},
  doi       = {{{r.doi or ''}}}
}}"""
        results.append(
            {
                "key": key,
                "title": r.title,
                "authors": authors,
                "year": year,
                "summary": r.summary,
                "arxiv_id": r.get_short_id(),
                "bibtex": bibtex,
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Fetch literature and produce verified BibTeX"
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        required=True,
        help="Search query (e.g. 'proactive LLM agents')",
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=5, help="Number of papers to fetch"
    )
    parser.add_argument(
        "--output-bib",
        "-o",
        type=str,
        default=None,
        help="Append entries to specified .bib file (e.g. arxiv/references.bib)",
    )

    args = parser.parse_args()
    print(f"[*] Searching arXiv for: '{args.query}' (limit: {args.limit})...")

    papers = search_arxiv(args.query, args.limit)
    print(f"[+] Found {len(papers)} papers:\n")

    all_bib = []
    for i, p in enumerate(papers, 1):
        print(f"[{i}] {p['title']}")
        print(
            f"    Authors: {', '.join(p['authors'][:3])}{'...' if len(p['authors']) > 3 else ''} ({p['year']})"
        )
        print(f"    arXiv: {p['arxiv_id']} | Key: \\citep{{{p['key']}}}")
        print()
        all_bib.append(p["bibtex"])

    combined_bib = "\n\n".join(all_bib)
    if args.output_bib:
        with open(args.output_bib, "a", encoding="utf-8") as f:
            f.write("\n\n" + combined_bib + "\n")
        print(
            f"[OK] Successfully appended {len(papers)} BibTeX entries to {args.output_bib}"
        )
    else:
        print("--- Generated BibTeX ---")
        print(combined_bib)


if __name__ == "__main__":
    main()
