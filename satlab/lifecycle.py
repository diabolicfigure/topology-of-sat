"""Path C: grow one clause stream and watch topology vs alpha."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

from satlab.generators import clause_stream, prefix_formula
from satlab.pipeline import analyze_formula

FIELDNAMES = [
    "family_id",
    "n",
    "k",
    "family",
    "seed",
    "planted_mask",
    "alpha_target",
    "alpha",
    "m",
    "n_solutions",
    "beta0",
    "beta1",
    "beta2",
    "skeleton_beta1",
    "cubical_beta1",
    "fill_gap",
    "girth",
    "truncated",
    "n_edges",
    "n_faces",
    "n_cubes",
    "built_dim",
    "total_ms",
]


def lifecycle_alphas() -> list[float]:
    low = [1.00, 1.25]
    fine = [round(1.5 + i * 0.1, 1) for i in range(21)]  # 1.5 .. 3.5
    high = [3.75, 4.00, 4.25, 4.50, 4.75, 5.00]
    return low + fine + high


def m_schedule(n: int, alphas: list[float]) -> list[tuple[float, int]]:
    seen: set[int] = set()
    out: list[tuple[float, int]] = []
    for alpha in alphas:
        m = int(round(alpha * n))
        if m not in seen:
            seen.add(m)
            out.append((alpha, m))
    return out


def score_family(rows: list[dict]) -> dict:
    """Apply Path C success/failure rules to one growing family."""
    ordered = sorted(rows, key=lambda row: row["m"])
    sat = [row for row in ordered if row["n_solutions"] > 0]
    cubical = [
        row
        for row in sat
        if row["cubical_beta1"] is not None and not row["truncated"]
    ]

    def first_alpha(pred) -> float | None:
        for row in cubical:
            if pred(row):
                return row["alpha_target"]
        return None

    onset = first_alpha(lambda row: row["cubical_beta1"] > 0)
    death = None
    if onset is not None:
        after = [row for row in cubical if row["alpha_target"] >= onset]
        last_pos = None
        for row in after:
            if row["cubical_beta1"] > 0:
                last_pos = row["alpha_target"]
        if last_pos is not None:
            later_zero = [
                row for row in after if row["alpha_target"] > last_pos and row["cubical_beta1"] == 0
            ]
            if later_zero:
                death = later_zero[0]["alpha_target"]

    peak_b1 = max(cubical, key=lambda row: row["cubical_beta1"], default=None)
    peak_b0 = max(sat, key=lambda row: row["beta0"], default=None)
    collapse = next((row["alpha_target"] for row in ordered if row["n_solutions"] == 0), None)

    hard = [
        row
        for row in cubical
        if 3.5 <= row["alpha_target"] <= 4.5
    ]
    hard_beta1_max = max((row["cubical_beta1"] for row in hard), default=None)
    hard_beta2_max = max(
        (row["beta2"] for row in hard if row["beta2"] is not None),
        default=None,
    )

    verdict = "no_signal"
    if onset is None:
        verdict = "no_signal"
    elif hard_beta1_max is not None and hard_beta1_max > 0 and (
        peak_b1 is not None and 3.5 <= peak_b1["alpha_target"] <= 4.5
    ):
        verdict = "fail_hard_peak"
    elif death is None and collapse is None:
        verdict = "fail_beta1_persists"
    elif death is None and collapse is not None:
        verdict = "partial_dies_at_unsat"
    else:
        b0_alpha = peak_b0["alpha_target"] if peak_b0 else None
        b1_peak_alpha = peak_b1["alpha_target"] if peak_b1 else None
        ordered_ok = (
            onset is not None
            and death is not None
            and b0_alpha is not None
            and onset <= death
            and (b1_peak_alpha is None or b1_peak_alpha <= b0_alpha + 1e-9)
            and (hard_beta1_max in (None, 0))
        )
        verdict = "success" if ordered_ok else "partial"

    return {
        "family": ordered[0]["family"] if ordered else None,
        "seed": ordered[0]["seed"] if ordered else None,
        "onset_alpha": onset,
        "beta1_peak_alpha": peak_b1["alpha_target"] if peak_b1 else None,
        "beta1_peak_value": peak_b1["cubical_beta1"] if peak_b1 else None,
        "death_alpha": death,
        "beta0_peak_alpha": peak_b0["alpha_target"] if peak_b0 else None,
        "beta0_peak_value": peak_b0["beta0"] if peak_b0 else None,
        "collapse_alpha": collapse,
        "hard_beta1_max": hard_beta1_max,
        "hard_beta2_max": hard_beta2_max,
        "verdict": verdict,
    }


def run_lifecycle(
    *,
    n: int,
    k: int,
    n_families: int,
    seed0: int,
    families: list[str],
    out_csv: Path,
    max_vertices_for_dim3: int,
) -> tuple[list[dict], dict]:
    alphas = lifecycle_alphas()
    schedule = m_schedule(n, alphas)
    m_max = schedule[-1][1]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        family_id = 0
        for family in families:
            for offset in range(n_families):
                seed = seed0 + family_id
                family_id += 1
                rng = random.Random(seed)
                clauses, plant = clause_stream(n, k, m_max, rng, family=family)
                for alpha_target, m in schedule:
                    formula = prefix_formula(
                        n,
                        k,
                        clauses,
                        m,
                        seed=seed,
                        family=family,
                        planted_mask=plant,
                    )
                    result = analyze_formula(
                        formula,
                        max_vertices_for_dim3=max_vertices_for_dim3,
                        compute_girth=True,
                    )
                    row = result.as_log_row()
                    row["family_id"] = family_id
                    row["alpha_target"] = alpha_target
                    writer.writerow(row)
                    handle.flush()
                    rows.append(row)
                    cubical = row["cubical_beta1"] if row["cubical_beta1"] is not None else "na"
                    print(
                        f"id={family_id} {family} seed={seed} a={alpha_target:.2f} m={m} "
                        f"|S|={row['n_solutions']} b0={row['beta0']} "
                        f"b1c={cubical} b2={row['beta2']} girth={row['girth']} "
                        f"{row['total_ms']:.1f}ms",
                        flush=True,
                    )

    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["family"], row["seed"])].append(row)
    scores = [score_family(items) for items in grouped.values()]
    counts: dict[str, int] = defaultdict(int)
    for score in scores:
        counts[score["verdict"]] += 1

    summary = {
        "n": n,
        "k": k,
        "n_families_per_kind": n_families,
        "kinds": families,
        "n_rows": len(rows),
        "verdict_counts": dict(counts),
        "families": scores,
        "mean_curve": mean_curve(rows),
    }
    return rows, summary


def mean_curve(rows: list[dict]) -> dict[str, dict]:
    groups: dict[tuple[str, float], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["family"], row["alpha_target"])].append(row)

    def mean(items: list[dict], key: str):
        vals = [item[key] for item in items if item[key] is not None]
        return (sum(vals) / len(vals)) if vals else None

    curve: dict[str, dict] = {}
    for (family, alpha), items in sorted(groups.items()):
        curve[f"{family},alpha={alpha}"] = {
            "trials": len(items),
            "mean_solutions": mean(items, "n_solutions"),
            "mean_beta0": mean(items, "beta0"),
            "mean_cubical_beta1": mean(items, "cubical_beta1"),
            "mean_beta2": mean(items, "beta2"),
            "mean_fill_gap": mean(items, "fill_gap"),
            "mean_girth": mean(items, "girth"),
            "frac_beta1_pos": sum(
                1 for item in items if (item["cubical_beta1"] or 0) > 0
            )
            / len(items),
            "truncated_frac": sum(1 for item in items if item["truncated"]) / len(items),
        }
    return curve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Path C lifecycle: grow one clause stream. Does not claim P != NP."
    )
    parser.add_argument("--n", type=int, default=14)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--families", type=int, default=12, help="families per kind")
    parser.add_argument("--kind", type=str, default="uniform,planted")
    parser.add_argument("--seed0", type=int, default=1000)
    parser.add_argument("--out", type=Path, default=Path("results/path_c_n14.csv"))
    parser.add_argument("--max-vertices-dim3", type=int, default=2500)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.n > 16:
        print("Lifecycle full-enum path refuses n > 16 in this pass.", file=sys.stderr)
        return 2
    kinds = [part.strip() for part in args.kind.split(",") if part.strip()]
    rows, summary = run_lifecycle(
        n=args.n,
        k=args.k,
        n_families=args.families,
        seed0=args.seed0,
        families=kinds,
        out_csv=args.out,
        max_vertices_for_dim3=args.max_vertices_dim3,
    )
    del rows
    summary_path = args.out.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"verdict_counts": summary["verdict_counts"], "mean_curve": summary["mean_curve"]}, indent=2))
    print(f"wrote {args.out} and {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
