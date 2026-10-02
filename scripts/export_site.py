"""Export the numbers Justice Lens shows on its /protection page: out/site_payload.json.

Numbers only, no prose (the site writes its own sentences from these), with provenance: the commit of this
repo the numbers came from, the NIBRS years and the ACS release. The site loads it with its own
scripts/load_victimization.py into an append-only table and shows the newest row.

  python scripts/export_site.py analysis.json   ->  out/site_payload.json
"""
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.expanduser(os.environ.get("DISPARITY_KIT", "~/.claude/disparity-kit/kit")))
from common import Project  # noqa: E402

SCHEMA = 1
REPO = "https://github.com/mngoh/DC-Assault-Victims-by-Race-and-Sex-2022-2025"
REPORT = "https://mngoh.github.io/DC-Assault-Victims-by-Race-and-Sex-2022-2025/"


def main():
    p = Project(sys.argv[1])
    R, pop = p.read_json("results.json"), p.read_json("population.json")
    sev, nb, chk, rep, cl = (p.read_json(f) for f in ["severity.json", "neighborhood.json", "dc_checks.json", "replication.json", "clearance.json"])
    G, S = p.focus
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=p.root, capture_output=True, text=True).stdout.strip()
    payload = {
        "schema": SCHEMA,
        "generated": dt.date.today().isoformat(),
        "source": {"repo": REPO, "commit": commit, "report": REPORT, "test_plan": f"{REPO}/blob/main/docs/clearance-test-plan.md"},
        "data": {"agency": "Metropolitan Police Department", "nibrs_years": [int(p.cfg["window"]["start"][:4]), int(p.cfg["window"]["end"][:4])],
                 "offenses": p.cfg["kind_labels"], "acs": pop["release"], "focus": R["focus"], "groups": p.groups,
                 "victims": R["counts"]["total"], "known_race_and_sex": R["counts"]["known"]},
        "harm": {
            "rates_per_100k": R["rates"],
            "ratios": R["ratios"],
            "women_victims": {g: n for g, n in cl["victims"].items()},
            "race_coding_worst_case": R["race_coding_bound"]["ratios_worst_case"],
            "race_coding_combo_pct": round((R["race_coding_bound"]["combo_ratio"] - 1) * 100),
            "ethnicity_range": {"Hispanic": chk["ethnicity"]["hispanic_range"], "White": chk["ethnicity"]["white_range"]},
            "missing_race_redistributed": chk["missing_race"]["ratios_redistributed"],
            "halves": {g: [v["first"], v["second"]] for g, v in rep["comparison"]["all"].items()},
            "least_stable": chk.get("least_stable", {}).get("group"),
            "severity": [{"label": t["label"], "n": t["n"], "ratio": t["ratio"], "ci": t["ci"]} for t in sev["tiers"]],
            "severity_min_n": sev["min_n"],
            "neighborhood": {"predicted_aggravated": nb["predicted_ratio"]["adw_per_1000"], "observed_aggravated": nb["aggravated_observed_ratio"],
                             "remaining_aggravated": nb["aggravated_remaining_ratio"], "women_in_25pct_poverty_tracts": nb["women_in_25pct_poverty_tracts"],
                             "adw_per_1000_by_poverty": [{"label": b["label"], "rate": b["adw_per_1000"]} for b in nb["poverty_bands"]]},
        },
        "protection": {
            "window_days": cl["window_days"], "victims": cl["victims"], "unknown_race_left_out": cl["unknown_race_left_out"],
            "relationship_order": cl["relationship_order"], "relationship_labels": cl["relationship_labels"],
            "relationship_share": cl["relationship_share"], "crude": cl["crude"], "by_relationship": cl["by_relationship"],
            "comparisons": {g: {"pooled": c["pooled"], "regression": c["regression"], "by_relationship": c["by_relationship"],
                                "halves": c["checks"]["halves"], "same_day": c["checks"]["same_day"], "later": c["checks"]["later"],
                                "victim_refused": c["secondary"]["victim_refused"], "prosecution_declined": c["secondary"]["prosecution_declined"],
                                "decision": c["decision"]} for g, c in cl["comparisons"].items()},
        },
        "exclusions": {**chk["excluded"], "unknown_race_or_sex": R["counts"]["total"] - R["counts"]["known"]},
    }
    p.write_json("site_payload.json", payload)


if __name__ == "__main__":
    main()
