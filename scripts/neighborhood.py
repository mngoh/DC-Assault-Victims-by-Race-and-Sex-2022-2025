"""Neighborhood and income: how much recorded violence surrounds the places where women of each group live.

NIBRS carries no location, so this cannot test victims directly. Instead it places MPD's public incidents
(data/external/mpd_violent_incidents.csv, no victim race) in census tracts, computes each tract's rate per
resident, and averages those rates over where each group's women live (ACS). The ratio of those averages is
the gap neighborhood alone would produce if everyone in a tract faced the same risk. It describes places,
not victims.

Also: the share of each group's women by tract poverty, recorded violence by tract poverty, and DC's
citywide poverty and household income by race (ACS), so the income caveat is generated, not typed.

  python scripts/neighborhood.py analysis.json   ->  out/neighborhood.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

sys.path.insert(0, os.path.expanduser(os.environ.get("DISPARITY_KIT", "~/.claude/disparity-kit/kit")))
from common import Project, year_spans  # noqa: E402
from denominators import acs  # noqa: E402

ADW = "ASSAULT W/DANGEROUS WEAPON"
MIN_POP = 500  # tracts with fewer residents (the Mall, downtown) get no per-resident rate in the main measure
BANDS = [(0.0, 0.10, "Under 10%"), (0.10, 0.25, "10% to 25%"), (0.25, 1.01, "25% or more")]
INCOME = {"Black": "B", "White": "H", "Hispanic": "I", "Asian": "D"}  # ACS race-iterated suffixes, White = non-Hispanic


def main():
    p = Project(sys.argv[1])
    G, S = p.focus
    groups = p.groups
    pop = p.read_json("population.json")
    R = p.read_json("results.json")
    _, years = year_spans(p)

    # tracts: geometry, total residents, women by group, poverty
    feats = json.loads((p.cache / "tracts_geometry.json").read_text())["features"]
    ses = json.loads((p.cache / "acs_tracts_ses.json").read_text())["data"]
    geom = {f["properties"]["geoid"].split("US")[1]: f for f in feats}
    rows = []
    for t in pop["tracts"]:
        f = geom[t["geoid"]]
        total = (ses.get("14000US" + t["geoid"], {}).get("B01003", {}).get("estimate", {}) or {}).get("B01003001")
        rows.append({"geoid": t["geoid"], "residents": total or 0, "km2": float(f["properties"].get("aland") or 0) / 1e6,
                     "poverty": t["ses"]["poverty"], **{g: sum(t["pop"][g][S]) for g in groups}})
    tr = pd.DataFrame(rows).set_index("geoid")

    # incidents to tracts by coordinates
    inc = pd.read_csv(p.root / "data/external/mpd_violent_incidents.csv")
    ids, shapes = list(tr.index), [shape(geom[g]["geometry"]) for g in tr.index]
    tree = STRtree(shapes)
    pts = [Point(x, y) for x, y in zip(inc["LONGITUDE"], inc["LATITUDE"])]
    pi, ti = tree.query(pts, predicate="intersects")
    first = pd.Series(ti, index=pi).groupby(level=0).first()
    # simplified tract shapes leave slivers along streets; a point in one goes to the nearest tract within about 100 m
    gap = [i for i in range(len(pts)) if i not in first.index]
    near = tree.query_nearest([pts[i] for i in gap], max_distance=0.001) if gap else ([], [])
    first = pd.concat([first, pd.Series(near[1], index=[gap[j] for j in near[0]]).groupby(level=0).first()])
    inc["geoid"] = [ids[first[i]] if i in first.index else None for i in range(len(inc))]
    snapped = len(set(gap) & set(first.index))
    tr["adw"] = inc[inc["OFFENSE"] == ADW].groupby("geoid").size().reindex(tr.index, fill_value=0)
    tr["violent"] = inc.groupby("geoid").size().reindex(tr.index, fill_value=0)

    def per_resident(col, min_pop):
        return np.where(tr["residents"] >= min_pop, tr[col] / tr["residents"].clip(lower=1) / years * 1000, np.nan)

    measures = {
        "adw_per_1000": per_resident("adw", MIN_POP),
        "violent_per_1000": per_resident("violent", MIN_POP),
        "adw_per_km2": np.where(tr["km2"] > 0, tr["adw"] / tr["km2"].replace(0, np.nan) / years, np.nan),
    }
    exposure, covered = {}, {}
    for name, r in measures.items():
        ok = ~np.isnan(r)
        exposure[name] = {g: round(float((tr.loc[ok, g] * r[ok]).sum() / tr.loc[ok, g].sum()), 2) for g in groups}
        covered[name] = {g: round(float(tr.loc[ok, g].sum() / tr[g].sum() * 100), 1) for g in groups}
    pred = {name: {g: round(e[G] / e[g], 2) for g in groups if g != G} for name, e in exposure.items()}

    # observed aggravated assault ratios, from the kit's results, against the neighborhood prediction
    agg = R["tests"]["type"]["aggravated"]
    observed = {g: round(agg[G] / agg[g], 2) for g in groups if g != G and agg[g]}
    main_pred = pred["adw_per_1000"]
    remaining = {g: round(observed[g] / main_pred[g], 2) for g in observed}
    located_pct = {g: round(np.log(main_pred[g]) / np.log(observed[g]) * 100) for g in observed if observed[g] > 1}

    # poverty bands
    bands = []
    for lo, hi, label in BANDS:
        b = tr[(tr["poverty"] >= lo) & (tr["poverty"] < hi)]
        rated = b[b["residents"] >= MIN_POP]
        bands.append({"label": label, "tracts": len(b),
                      "adw_per_1000": round(float(rated["adw"].sum() / rated["residents"].sum() / years * 1000), 2),
                      "women_pct": {g: round(float(b[g].sum() / tr[g].sum() * 100), 1) for g in groups}})
    high_poverty = {g: round(float(tr.loc[tr["poverty"] >= 0.25, g].sum() / tr[g].sum() * 100), 1) for g in groups}

    # citywide poverty and household income by race (ACS)
    place = p.cfg["place"]["census_geoid"]
    tables = [f"B17001{s}" for s in INCOME.values()] + [f"B19013{s}" for s in INCOME.values()]
    e = acs(p, tables, place, "acs_place_income.json")["data"][place]
    income = {}
    for g, s in INCOME.items():
        if g not in groups:
            continue
        pv = e[f"B17001{s}"]["estimate"]
        below, above = pv[f"B17001{s}017"], pv[f"B17001{s}046"]  # women below / at or above poverty
        income[g] = {"women_below_poverty_pct": round(below / (below + above) * 100, 1),
                     "median_household_income": int(e[f"B19013{s}"]["estimate"][f"B19013{s}001"])}

    out = {"incidents": len(inc), "incidents_by_offense": inc["OFFENSE"].value_counts().to_dict(),
           "snapped_to_nearest_tract": snapped, "unassigned_incidents": int(inc["geoid"].isna().sum()), "tracts": len(tr), "min_pop": MIN_POP, "years": years,
           "exposure": exposure, "women_covered_pct": covered, "predicted_ratio": pred,
           "aggravated_observed_ratio": observed, "aggravated_remaining_ratio": remaining, "aggravated_located_pct_log": located_pct,
           "poverty_bands": bands, "women_in_25pct_poverty_tracts": high_poverty, "citywide_income": income,
           "release": pop["release"]}
    p.write_json("neighborhood.json", out)
    print(json.dumps({k: out[k] for k in ["snapped_to_nearest_tract", "unassigned_incidents", "exposure", "women_covered_pct", "predicted_ratio",
                                          "aggravated_observed_ratio", "aggravated_remaining_ratio", "aggravated_located_pct_log",
                                          "poverty_bands", "women_in_25pct_poverty_tracts", "citywide_income"]}, indent=1))


if __name__ == "__main__":
    main()
