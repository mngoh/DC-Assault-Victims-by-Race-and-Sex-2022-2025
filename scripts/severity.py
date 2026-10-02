"""Does the gap shrink for crimes that reach police no matter who calls?

If the gap came from one group reporting more, it would narrow for the most severe crimes, which are
reported most often (serious injuries, guns, killings). This computes women's rates and the focus group's
ratio to each other group by severity, with exact 95% intervals (conditional binomial), from the same
MPD individual-victim records as the main analysis. Homicide victims (09A) come from the flattened file.

  python scripts/severity.py analysis.json   ->  out/severity.json
"""
import os
import sys

import pandas as pd
from scipy.stats import beta

sys.path.insert(0, os.path.expanduser(os.environ.get("DISPARITY_KIT", "~/.claude/disparity-kit/kit")))
from common import Project, year_spans  # noqa: E402

SERIOUS = {"Apparent Broken Bones", "Possible Internal Injury", "Severe Laceration", "Other Major Injury", "Loss of Teeth", "Unconscious"}
GUN = "Firearm|Handgun|Rifle|Shotgun"
MIN_N = 10  # a comparison needs this many victims in the comparison group to be charted


def ratio_ci(a, ea, b, eb):
    """Rate ratio (a/ea)/(b/eb) with an exact 95% interval, conditioning on a + b."""
    if b == 0:
        return None, None, None
    n, k = ea / eb, a + b
    lo_p = beta.ppf(0.025, a, b + 1) if a > 0 else 0.0
    hi_p = beta.ppf(0.975, a + 1, b)
    f = lambda q: q / (1 - q) / n
    return round(a / ea / (b / eb), 2), round(f(lo_p), 1), round(f(hi_p), 1)


def main():
    p = Project(sys.argv[1])
    G, S = p.focus
    pop = p.read_json("population.json")["city"]
    _, years = year_spans(p)
    start, end = p.window()
    v = pd.read_csv(p.root / "data/interim/victim_offenses.csv", low_memory=False, dtype={"age_num": str})
    v = v[(v["agency"] == "Washington") & (v["victim_type"] == "Individual") & (v["sex"] == S)
          & pd.to_datetime(v["incident_date"]).between(start, end)].copy()
    v["group"] = v["race"].where(v["ethnicity"] != "H", "H").map(p.cfg["race_map"])
    v["serious"] = v["injury"].fillna("").str.split(";").apply(lambda xs: bool(SERIOUS & set(xs)))
    v["gun"] = v["weapon"].fillna("").str.contains(GUN)
    a = v[v["offense_code"].isin(["13A", "13B"])]
    tiers = [("Simple assault, no serious injury", a[(a["offense_code"] == "13B") & ~a["serious"]]),
             ("Assault with serious injury", a[a["serious"]]),
             ("Assault with a gun", a[a["gun"]]),
             ("Homicide", v[v["offense_code"] == "09A"].drop_duplicates("victim_id"))]
    out = {"tiers": [], "min_n": MIN_N, "injury_recorded_pct": round(float(a["injury"].notna().mean() * 100), 1)}
    for label, d in tiers:
        n = d["group"].value_counts()
        expo = {g: pop[g][S] * years for g in p.groups}
        t = {"label": label, "n": {g: int(n.get(g, 0)) for g in p.groups},
             "rate": {g: round(n.get(g, 0) / expo[g] * 1e5, 1) for g in p.groups}, "ratio": {}, "ci": {}}
        for g in p.others:
            r, lo, hi = ratio_ci(int(n.get(G, 0)), expo[G], int(n.get(g, 0)), expo[g])
            t["ratio"][g], t["ci"][g] = r, [lo, hi]
        out["tiers"].append(t)
    p.write_json("severity.json", out)
    for t in out["tiers"]:
        print(f"{t['label']:36s}", {g: f"{t['ratio'][g]}x ({t['ci'][g][0]}-{t['ci'][g][1]}), n={t['n'][g]}" for g in p.others})


if __name__ == "__main__":
    main()
