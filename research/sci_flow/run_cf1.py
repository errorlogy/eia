"""Run CF-1 prompt deletion suite (M-C)."""

from __future__ import annotations

from dataclasses import asdict
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.cf1 import C1_PASS_RATE, CF1SeedResult, run_seed, summarize  # noqa: E402


def _job(payload: tuple[int, str]) -> CF1SeedResult:
    seed, window = payload
    return run_seed(seed, window)  # type: ignore[arg-type]


def main() -> int:
    seeds = list(range(1, 101))
    windows = ("5m", "1h", "24h", "full")
    jobs = [(seed, window) for seed in seeds for window in windows]
    results: list[CF1SeedResult] = []
    with ProcessPoolExecutor() as pool:
        futures = [pool.submit(_job, job) for job in jobs]
        for i, future in enumerate(as_completed(futures), start=1):
            results.append(future.result())
            if i % 40 == 0:
                print(f"completed {i}/{len(jobs)}", flush=True)
    summary = summarize(results)
    print(json.dumps(summary, indent=2), flush=True)
    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / "cf1_results.json"
    payload = {
        "summary": summary,
        "pass_threshold": C1_PASS_RATE,
        "seeds": seeds,
        "windows": list(windows),
        "rows": [asdict(row) for row in results],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    full = summary["windows"]["full"]
    return 0 if full["c1_claim"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
