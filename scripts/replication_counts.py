"""Counts for the replication check: the first two years of the window against the last two.

DC has one records system for the whole window (MPD reports to NIBRS from August 2021), so there is no
second system to compare. Splitting the window in half tests whether the ratios hold over time with the
same definitions; it does not test a different way of coding.

  python scripts/replication_counts.py analysis.json   ->  out/replication_counts.json
  then: python ~/.claude/disparity-kit/kit/replicate.py analysis.json
"""
import json
import pathlib
import sys

import pandas as pd

HALVES = {"primary": (2022, 2023), "secondary": (2024, 2025)}


def main():
    cfg_path = pathlib.Path(sys.argv[1]).resolve()
    root = cfg_path.parent
    cfg = json.loads(cfg_path.read_text())
    focus_sex = cfg["focus"].get("sex", "F")
    frames = [pd.read_csv(root / s["path"]).assign(kind=s["kind"]) for s in cfg["incidents"]]
    d = pd.concat(frames, ignore_index=True)
    d["year"] = pd.to_datetime(d["incident_date"]).dt.year
    d["group"] = d["race_group"].map(cfg["race_map"])
    d = d[(d["sex"] == focus_sex) & d["group"].notna()]
    sources = {}
    for key, (a, b) in HALVES.items():
        h = d[d["year"].between(a, b)]
        cats = {"all": h, "partner": h[h["partner"] == "Y"]}
        cats.update({k: h[h["kind"] == k] for k in sorted(h["kind"].unique())})
        sources[key] = {"label": f"{a} to {b}", "years": float(b - a + 1),
                        "counts": {c: {g: int((x["group"] == g).sum()) for g in cfg["groups"]} for c, x in cats.items()}}
    spec = {"sources": sources,
            "definition_notes": "DC has one records system for the whole window, so the check compares the first two years with the last two, "
                                "with identical definitions (MPD, offenses 13A and 13B, individual victims, the same race mapping and population). "
                                "It tests whether the ratios hold over time, not whether a different coding system would find them."}
    out = root / "out" / "replication_counts.json"
    out.write_text(json.dumps(spec, indent=1))
    print("wrote", out)
    for k, s in sources.items():
        print(k, s["label"], s["counts"]["all"])


if __name__ == "__main__":
    main()
