"""Are assaults on Black women cleared by arrest as often as assaults on other women?

Follows docs/clearance-test-plan.md, committed before this script existed. The outcome is an arrest within
90 days of the incident. Comparisons are made inside strata of relationship by assault type, because DC Code
16-1031 requires an arrest in intrafamily cases. The estimate is a Mantel-Haenszel risk ratio, with a
regression check, robustness checks and a pre-set rule for asserting a direction.

  python scripts/clearance.py analysis.json   ->  out/clearance.json
"""
import math
import os
import sys

import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, os.path.expanduser(os.environ.get("DISPARITY_KIT", "~/.claude/disparity-kit/kit")))
from common import Project  # noqa: E402
from flatten_nibrs import YEARS, reader  # noqa: E402

WINDOW_DAYS = 90
REL = [("partner", {"SE", "CS", "BG", "HR", "XS", "XR"}),
       ("family", {"PA", "CH", "SB", "GP", "GC", "IL", "SP", "SC", "SS", "OF", "CF"}),
       ("known", {"AQ", "FR", "NE", "BE", "EE", "ER", "OK"}),
       ("stranger", {"ST"})]
REL_ORDER = ["partner", "family", "known", "stranger", "unknown"]
REL_LABEL = {"partner": "Partner", "family": "Other family", "known": "Known, not family", "stranger": "Stranger", "unknown": "Unknown"}
SERIOUS = {"Apparent Broken Bones", "Possible Internal Injury", "Severe Laceration", "Other Major Injury", "Loss of Teeth", "Unconscious"}
GUN = "Firearm|Handgun|Rifle|Shotgun"
AGE = [(0, 17, "0-17"), (18, 29, "18-29"), (30, 44, "30-44"), (45, 64, "45-64"), (65, 200, "65+")]
DIRECTED = ["Hispanic", "White"]  # a direction is asserted only for these comparisons (the plan)
NOT_APPLICABLE, PROSECUTION_DECLINED, VICTIM_REFUSED = 6, 2, 4


def relationship(codes):
    s = set(codes.split(";")) if isinstance(codes, str) else set()
    for name, members in REL:
        if s & members:
            return name
    return "unknown"


def age_band(a):
    if pd.isna(a):
        return "unknown"
    return next((lab for lo, hi, lab in AGE if lo <= a <= hi), "unknown")


def pct(s):
    return round(float(s.mean() * 100), 1) if len(s) else None


def mh_rr(d, outcome, strata):
    """Mantel-Haenszel risk ratio, focus (black=1) against comparison (black=0), with the Greenland-Robins 95% interval."""
    num = den = var = 0.0
    used = 0
    for _, s in d.groupby(strata):
        n1, n0 = int((s["black"] == 1).sum()), int((s["black"] == 0).sum())
        if not n1 or not n0:
            continue
        a, b, n = float(s.loc[s["black"] == 1, outcome].sum()), float(s.loc[s["black"] == 0, outcome].sum()), n1 + n0
        num, den, used = num + a * n0 / n, den + b * n1 / n, used + 1
        var += (n1 * n0 * (a + b) - a * b * n) / n ** 2
    if num <= 0 or den <= 0:
        return {"rr": None, "ci": [None, None], "strata": used}
    rr, se = num / den, math.sqrt(var / (num * den))
    return {"rr": round(rr, 2), "ci": [round(rr * math.exp(-1.96 * se), 2), round(rr * math.exp(1.96 * se), 2)], "strata": used}


def poisson_rr(d, outcome):
    f = f"{outcome} ~ black + C(stratum) + C(year) + C(age_band) + serious + gun + home"
    try:
        fit = sm.GLM.from_formula(f, data=d, family=sm.families.Poisson()).fit(cov_type="HC0")
    except Exception as e:  # report, never hide
        return {"rr": None, "ci": [None, None], "error": str(e)[:200]}
    b, se = fit.params["black"], fit.bse["black"]
    return {"rr": round(math.exp(b), 2), "ci": [round(math.exp(b - 1.96 * se), 2), round(math.exp(b + 1.96 * se), 2)]}


def decide(pooled, partner, stranger):
    lo, hi = pooled["ci"]
    if lo is None:
        return "not estimable"
    if lo <= 1 <= hi:
        return "no clear difference"
    side = "lower" if pooled["rr"] < 1 else "higher"
    agree = all(x["rr"] is not None and (x["rr"] < 1) == (side == "lower") for x in (partner, stranger))
    return side if agree else "mixed"


def main():
    p = Project(sys.argv[1])
    G, S = p.focus
    start, end = p.window()
    v = pd.concat([pd.read_csv(p.path(s["path"])).assign(kind=s["kind"]) for s in p.cfg["incidents"]], ignore_index=True)
    victims_per_incident = v.groupby("incident_id")["victim_id"].nunique()
    v = v[(v["sex"] == S) & pd.to_datetime(v["incident_date"]).between(start, end)].copy()
    v["group"] = v["race_group"].map(p.cfg["race_map"])
    unknown_race = int(v["group"].isna().sum())
    v = v.dropna(subset=["group"])

    inc = pd.concat([reader(y)("NIBRS_incident", usecols=["incident_id", "cleared_except_id"]) for y in YEARS])
    arr = pd.concat([reader(y)("NIBRS_ARRESTEE", usecols=["incident_id", "arrest_date"]) for y in YEARS])
    first_arrest = pd.to_datetime(arr["arrest_date"]).groupby(arr["incident_id"]).min()
    exc = inc.set_index("incident_id")["cleared_except_id"]

    days = (v["incident_id"].map(first_arrest) - pd.to_datetime(v["incident_date"])).dt.days
    v["arrest90"] = days.between(0, WINDOW_DAYS).astype(int)
    v["same_day"] = (days == 0).astype(int)
    v["later"] = days.between(1, WINDOW_DAYS).astype(int)
    e = v["incident_id"].map(exc).fillna(NOT_APPLICABLE)
    v["exceptional"] = (e != NOT_APPLICABLE).astype(int)
    v["victim_refused"] = (e == VICTIM_REFUSED).astype(int)
    v["prosecution_declined"] = (e == PROSECUTION_DECLINED).astype(int)
    v["rel"] = v["relationship"].apply(relationship)
    v["stratum"] = v["rel"] + "|" + v["kind"]
    v["year"] = pd.to_datetime(v["incident_date"]).dt.year
    v["age_band"] = v["age"].apply(age_band)
    v["serious"] = v["injury"].fillna("").str.split(";").apply(lambda xs: int(bool(SERIOUS & set(xs))))
    v["gun"] = v["weapon"].fillna("").str.contains(GUN).astype(int)
    v["home"] = (v["premise"] == "Home").astype(int)
    v["single"] = (v["incident_id"].map(victims_per_incident) == 1).astype(int)

    groups = p.groups
    out = {"window_days": WINDOW_DAYS, "victims": {g: int((v["group"] == g).sum()) for g in groups}, "unknown_race_left_out": unknown_race,
           "relationship_labels": REL_LABEL, "relationship_order": REL_ORDER,
           "crude": {g: {k: pct(v.loc[v["group"] == g, k]) for k in ["arrest90", "same_day", "later", "exceptional", "victim_refused", "prosecution_declined"]}
                     for g in groups},
           "relationship_share": {g: {r: pct(v.loc[v["group"] == g, "rel"] == r) for r in REL_ORDER} for g in groups},
           "by_relationship": {r: {g: {"n": int(((v["rel"] == r) & (v["group"] == g)).sum()), "arrest90": pct(v.loc[(v["rel"] == r) & (v["group"] == g), "arrest90"])}
                                   for g in groups} for r in REL_ORDER},
           "comparisons": {}}

    for g in [x for x in groups if x != G]:
        d = v[v["group"].isin([G, g])].assign(black=lambda x: (x["group"] == G).astype(int))
        pooled = mh_rr(d, "arrest90", "stratum")
        partner = mh_rr(d[d["rel"] == "partner"], "arrest90", "kind")
        stranger = mh_rr(d[d["rel"] == "stranger"], "arrest90", "kind")
        halves = {f"{a} to {b}": mh_rr(d[d["year"].between(a, b)], "arrest90", "stratum") for a, b in [(2022, 2023), (2024, 2025)]}
        out["comparisons"][g] = {
            "pooled": pooled, "regression": poisson_rr(d, "arrest90"),
            "by_relationship": {r: mh_rr(d[d["rel"] == r], "arrest90", "kind") for r in REL_ORDER},
            "checks": {"halves": halves, "single_victim": mh_rr(d[d["single"] == 1], "arrest90", "stratum"),
                       "partner_halves": {f"{a} to {b}": mh_rr(d[(d["rel"] == "partner") & d["year"].between(a, b)], "arrest90", "kind")
                                          for a, b in [(2022, 2023), (2024, 2025)]},
                       "partner_same_day": mh_rr(d[d["rel"] == "partner"], "same_day", "kind"),
                       "partner_later": mh_rr(d[d["rel"] == "partner"], "later", "kind"),
                       "same_day": mh_rr(d, "same_day", "stratum"), "later": mh_rr(d, "later", "stratum")},
            "secondary": {k: mh_rr(d, k, "stratum") for k in ["exceptional", "victim_refused", "prosecution_declined"]},
            "decision": decide(pooled, partner, stranger) if g in DIRECTED else "not asserted (small numbers)"}

    # ethnicity bound: White women with unknown ethnicity counted as Hispanic instead
    b = v.copy()
    moved = (b["race"] == "W") & b["ethnicity"].isin(["U", "X"])
    b.loc[moved, "group"] = "Hispanic"
    out["ethnicity_bound"] = {"moved": int(moved.sum()),
                              **{g: mh_rr(b[b["group"].isin([G, g])].assign(black=lambda x: (x["group"] == G).astype(int)), "arrest90", "stratum")
                                 for g in DIRECTED}}
    p.write_json("clearance.json", out)
    for g, c in out["comparisons"].items():
        print(f"{G} vs {g}: crude {out['crude'][G]['arrest90']}% vs {out['crude'][g]['arrest90']}% | MH RR {c['pooled']['rr']} {c['pooled']['ci']} "
              f"| regression {c['regression']['rr']} {c['regression']['ci']} | partner {c['by_relationship']['partner']['rr']} "
              f"| stranger {c['by_relationship']['stranger']['rr']} | decision: {c['decision']}")


if __name__ == "__main__":
    main()
