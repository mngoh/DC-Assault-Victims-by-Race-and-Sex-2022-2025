"""DC-specific checks the kit cannot run on NIBRS, and the caveats they produce.

  ethnicity bound      NIBRS records Hispanic ethnicity separately from race, and it is often missing. White-race
                       victims with unknown ethnicity are counted as White; here they are moved to Hispanic, or split
                       in the known proportion, to bound the Hispanic and White comparisons.
  missing race         NIBRS has no location, so the kit's district check cannot run. Victims with unknown race are
                       spread over the four groups in proportion to known victims inside each cell of type x premises
                       x resident status, and the ratios recomputed.
  uneven fields        resident status and victim-offender relationship missing, by group
  exclusions           Metro Transit Police, officer victims, intimidation, unknown and infant ages

Writes out/dc_checks.json and regenerates `extra_caveats` in analysis.json from it, so every number in
the caveats comes from this output.

  python scripts/dc_checks.py analysis.json
"""
import json
import os
import pathlib
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get("DISPARITY_KIT", "~/.claude/disparity-kit/kit")))
from common import Project, load_incidents, year_spans  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def ratio(a, b):
    return round(a / b, 2) if b else None


def main():
    p = Project(sys.argv[1])
    G, S = p.focus
    pop = p.read_json("population.json")["city"]
    R = p.read_json("results.json")
    _, years = year_spans(p)
    rate = lambda n, g: round(n / pop[g][S] / years * 1e5)  # rounded like the kit, so "as mapped" matches results.json
    df = load_incidents(p)
    raw = pd.concat([pd.read_csv(p.path(s["path"]), dtype={"victim_id": str}) for s in p.cfg["incidents"]])
    raw["date"] = pd.to_datetime(raw["incident_date"])
    start, end = p.window()
    raw = raw[(raw["date"] >= start) & (raw["date"] <= end)]
    women = raw[raw["sex"] == S]
    out = {}

    # ethnicity bound: White-race women with unknown or unspecified ethnicity
    w = women[women["race"] == "W"]
    w_known_h, w_known_n = int((w["ethnicity"] == "H").sum()), int((w["ethnicity"] == "N").sum())
    w_unknown = int(w["ethnicity"].isin(["U", "X"]).sum())
    share_h = w_known_h / (w_known_h + w_known_n)
    n = {g: int(((women["race_group"] == {"Black": "B", "Hispanic": "H", "White": "W", "Asian": "A"}[g])).sum()) for g in p.groups}
    scen = {"as mapped": (n["Hispanic"], n["White"]),
            "unknown ethnicity left out": (n["Hispanic"], n["White"] - w_unknown),
            "split in known proportion": (n["Hispanic"] + share_h * w_unknown, n["White"] - share_h * w_unknown),
            "all Hispanic": (n["Hispanic"] + w_unknown, n["White"] - w_unknown)}
    fr = rate(n[G], G)
    out["ethnicity"] = {
        "white_race_women": len(w), "white_unknown_ethnicity": w_unknown, "white_unknown_pct": round(w_unknown / len(w) * 100, 1),
        "hispanic_share_where_known_pct": round(share_h * 100, 1),
        "all_unknown_ethnicity_pct": round(float(women["ethnicity"].isin(["U", "X"]).mean() * 100), 1),
        "hispanic_recovered_from_unknown_race": int(((women["race"] == "U") & (women["ethnicity"] == "H")).sum()),
        "scenarios": {k: {"Hispanic": ratio(fr, rate(h, "Hispanic")), "White": ratio(fr, rate(wh, "White"))} for k, (h, wh) in scen.items()},
    }
    sc = out["ethnicity"]["scenarios"]
    out["ethnicity"]["hispanic_range"] = [min(v["Hispanic"] for v in sc.values()), max(v["Hispanic"] for v in sc.values())]
    out["ethnicity"]["white_range"] = [min(v["White"] for v in sc.values()), max(v["White"] for v in sc.values())]

    # missing race, redistributed inside cells of type x premises x resident status
    fs = df[df["sex"] == S].copy()
    fs["resident"] = raw.set_index("victim_id").reindex(fs["id"].astype(str))["resident_status"].fillna("blank").values
    fs["cell"] = fs["kind"] + "|" + fs["premise"].fillna("blank").astype(str) + "|" + fs["resident"]
    counts = {g: 0.0 for g in p.groups}
    for _, c in fs.groupby("cell"):
        known = c["race"].value_counts()
        unknown = c["race"].isna().sum() - int(c["race_raw"].isin(["I", "P"]).sum())
        tot = sum(known.get(g, 0) for g in p.groups)
        for g in p.groups:
            counts[g] += known.get(g, 0) + (unknown * known.get(g, 0) / tot if tot else 0)
    rr = {g: rate(counts[g], g) for g in p.groups}
    out["missing_race"] = {
        "unknown_women": int((fs["race"].isna() & ~fs["race_raw"].isin(["I", "P"])).sum()),
        "unknown_pct_by_resident": {k: round(float(v * 100), 1) for k, v in fs.groupby("resident")["race"].apply(lambda s: s.isna().mean()).items()},
        "ratios_redistributed": {g: ratio(rr[G], rr[g]) for g in p.others},
        "ratios_as_mapped": R["ratios"],
    }

    # uneven missing fields among women, by group
    women_g = women.assign(group=women["race_group"].map(p.cfg["race_map"])).dropna(subset=["group"])
    out["resident_blank_pct"] = {g: round(float(s.isna().mean() * 100), 1) for g, s in women_g.groupby("group")["resident_status"]}
    rel_unknown = women_g["relationship"].isna() | (women_g["relationship"] == "RU")
    out["relationship_unknown_pct"] = {g: round(float(s.mean() * 100), 1) for g, s in rel_unknown.groupby(women_g["group"])}

    # exclusions, from the flattened file
    v = pd.read_csv(ROOT / "data/interim/victim_offenses.csv", low_memory=False, dtype={"age_num": str})
    v = v[pd.to_datetime(v["incident_date"]).between(start, end)]
    core = v["offense_code"].isin(["13A", "13B"])
    out["excluded"] = {
        "metro_transit_victims": int((core & (v["agency"] != "Washington") & (v["victim_type"] == "Individual")).sum()),
        "officer_victims": int((core & (v["agency"] == "Washington") & (v["victim_type"] == "Law Enforcement Officer")).sum()),
        "intimidation_victims": int(((v["offense_code"] == "13C") & (v["agency"] == "Washington") & (v["victim_type"] == "Individual")).sum()),
        "age_unknown": int(raw["age"].isna().sum()),
        "infants": int((raw["age"] == 0).sum()),
        "not_rated_race": {k: int((raw["race_group"] == k).sum()) for k in ["I", "P"]},
    }
    p.write_json("dc_checks.json", out)

    # caveats, generated from the checks above
    e, m, x = out["ethnicity"], out["missing_race"], out["excluded"]
    release = p.read_json("population.json")["release"]
    acs_year = int(re.search(r"\d{4}", release).group())
    rb = out["resident_blank_pct"]
    ru = out["relationship_unknown_pct"]
    caveats = [
        ["Where assaults happen is not in this data",
         "The FBI's NIBRS files record no address, ward or police district. So this page cannot test whether location or neighborhood conditions account for the gap, "
         "and there is no tract-level model. In the Los Angeles analysis, location was the control that moved the gap most. "
         "Even where it can be tested, a gap that shrinks after location has been located, not explained away: neighborhoods are shaped by segregation."],
        ["Policing and reporting",
         "Police data reflects where officers patrol and who calls them. This data cannot separate more policing or more reporting from more assaults."],
        ["Hispanic ethnicity is often missing",
         f"NIBRS records ethnicity separately from race, and it is unknown or unspecified for {e['all_unknown_ethnicity_pct']}% of women victims. "
         f"{e['white_unknown_pct']}% of women recorded as White have unknown ethnicity, and where it is known, {e['hispanic_share_where_known_pct']}% of them are Hispanic. "
         f"They are counted as White here. If they were Hispanic, Black women's rate would be {e['hispanic_range'][0]}x Hispanic women's instead of {R['ratios']['Hispanic']}x, "
         f"and {e['white_range'][1]}x White women's instead of {R['ratios']['White']}x."],
        ["Missing race",
         f"{m['unknown_women']:,} women victims have unknown race. NIBRS has no location, so where they cluster cannot be mapped. "
         f"Spread over the four groups like known victims of the same assault type, premises and resident status, the ratios move to "
         + ", ".join(f"{m['ratios_redistributed'][g]}x {g}" for g in p.others) + " from "
         + ", ".join(f"{R['ratios'][g]}x" for g in p.others) + "."],
        ["Residents are the denominator",
         f"DC draws many commuters and visitors, and rates divide by residents only. Resident status is blank for {min(rb.values())}% to {max(rb.values())}% of women victims "
         f"depending on group ({', '.join(f'{rb[g]}% {g}' for g in p.groups)}), so the non-resident test is partial."],
        ["Intimate partner is a lower bound",
         f"Partner assaults are identified from the victim-offender relationship, which is unknown or blank for "
         + ", ".join(f"{ru[g]}% of {g}" for g in p.groups) + " women victims. Where it is missing more often, the partner share is understated more, "
         "so partner comparisons are least certain against the groups with the most missing."],
        ["What is counted",
         f"Aggravated (13A) and simple (13B) assault reported by the Metropolitan Police Department, individual victims of any age. Left out: "
         f"{x['metro_transit_victims']:,} Metro Transit Police victims, whose system extends into Maryland and Virginia; "
         f"{x['officer_victims']:,} assaults on officers; {x['intimidation_victims']:,} intimidation victims (threats with no attack). "
         f"{x['not_rated_race']['I']} American Indian or Alaska Native and {x['not_rated_race']['P']} Native Hawaiian or Pacific Islander victims are counted in the totals "
         f"but not compared, because counts this small give unstable rates. {x['age_unknown'] + x['infants']} victims with unknown age or under one year old fall out of the age test only."],
        ["Window and population",
         f"Victims cover {start:%B %Y} to {end:%B %Y}; the population is the {release} estimate, an average over {acs_year - 4} to {acs_year}."],
    ]
    rep_path = p.out / "replication.json"
    if rep_path.exists():
        rep = json.loads(rep_path.read_text())
        allc = rep["comparison"]["all"]
        worst = max(allc, key=lambda g: abs(allc[g]["change_pct"]))
        rest = max(abs(allc[g]["change_pct"]) for g in allc if g != worst)
        biggest = max(((c, v[worst]["change_pct"]) for c, v in rep["comparison"].items() if worst in v), key=lambda t: abs(t[1]))
        labels = [src["label"] for src in rep["sources"].values()]
        counts = json.loads((p.out / "replication_counts.json").read_text())["sources"].values()
        n_small = {src["label"]: src["counts"]["all"][worst] for src in counts}
        out["least_stable"] = {"group": worst, "change_pct": allc[worst]["change_pct"], "others_max_pct": rest, "largest": biggest, "victims": n_small}
        p.write_json("dc_checks.json", out)
        caveats.append(["Least stable comparison",
                        f"The {worst} comparison moved {allc[worst]['change_pct']:+d}% between {labels[0]} and {labels[1]} "
                        f"({biggest[1]:+d}% for {p.cfg.get('kind_labels', {}).get(biggest[0], biggest[0]).lower()}), against {rest}% or less for the others. "
                        f"It rests on " + " and ".join(f"{v:,} {worst} women victims in {k}" for k, v in n_small.items()) + ", so it is left out of the headline."])
    cfg = json.loads(p.config_path.read_text())
    cfg["extra_caveats"] = caveats
    p.config_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
    print("updated extra_caveats in", p.config_path.name)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
