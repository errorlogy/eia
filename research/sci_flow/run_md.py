"""Run M-D / CF-5 Kuramoto coupling sweep."""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.cf5 import CF5SeedResult, run_seed, summarize  # noqa: E402


def _job(payload: tuple[int, str]) -> CF5SeedResult:
    seed, condition = payload
    return run_seed(seed, condition)  # type: ignore[arg-type]


def main() -> int:
    seeds = list(range(1, 101))
    conditions = ("coupled", "scramble", "k0", "sparse", "delay_32", "delay_128")
    jobs = [(seed, condition) for seed in seeds for condition in conditions]
    results: list[CF5SeedResult] = []
    with ProcessPoolExecutor() as pool:
        futures = [pool.submit(_job, job) for job in jobs]
        for i, future in enumerate(as_completed(futures), start=1):
            results.append(future.result())
            if i % 60 == 0:
                print(f"completed {i}/{len(jobs)}", flush=True)
    summary = summarize(results)
    print(json.dumps(summary, indent=2), flush=True)
    out = Path(__file__).resolve().parent / "md_results.json"
    out.write_text(
        json.dumps(
            {
                "summary": summary,
                "seeds": seeds,
                "conditions": list(conditions),
                "rows": [asdict(row) for row in results],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0 if summary["c2_claim"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
