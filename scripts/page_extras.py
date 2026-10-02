"""Write out/extra_sections.json: the severity test, the reporting note and the neighborhood section for the page.

Every number in the text comes from out/results.json, out/severity.json, out/neighborhood.json or
data/external/bjs_ncvs.json (national survey figures, each read in its source document).

  python scripts/page_extras.py analysis.json   ->  out/extra_sections.json  (read by the kit's build_page.py)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.expanduser(os.environ.get("DISPARITY_KIT", "~/.claude/disparity-kit/kit")))
from common import SEX_WORD, Project  # noqa: E402

AXIS = {"Simple assault, no serious injury": ["Simple assault,", "no serious injury"], "Assault with serious injury": ["Serious", "injury"],
        "Assault with a gun": ["With", "a gun"], "Homicide": "Homicide"}  # two-line labels so phones do not rotate and clip them
COLOR = {0: "blue", 1: "blueLight", 2: "muted"}


def x(v):
    r = round(v, 1)
    return str(int(r)) if r == int(r) else str(r)


def main():
    p = Project(sys.argv[1])
    G, S = p.focus
    FL, sexw = p.focus_label, SEX_WORD[S][0]
    others = p.others
    R, sev, nb = p.read_json("results.json"), p.read_json("severity.json"), p.read_json("neighborhood.json")
    bjs = json.loads((p.root / "data/external/bjs_ncvs.json").read_text())
    cv, pov14 = bjs["cv2024"], bjs["poverty2014"]
    W, H = "White", "Hispanic"
    tiers = {t["label"]: t for t in sev["tiers"]}
    simple, serious, gun, hom = (tiers[k] for k in ["Simple assault, no serious injury", "Assault with serious injury", "Assault with a gun", "Homicide"])

    # severity: chart the tiers with enough victims, give the rest in text with their interval
    # a tier is charted if some comparison group has enough victims in it; a group is charted only if it has enough in every charted tier
    mn = sev["min_n"]
    charted = [t for t in sev["tiers"] if max(t["n"][g] for g in others) >= mn]
    small = [t for t in sev["tiers"] if t not in charted]
    shown = [g for g in others if all(t["n"][g] >= mn for t in charted)]
    left_out = {g: [t for t in charted if t["n"][g] < mn] for g in others if g not in shown}
    sev_text = (f"Does the gap narrow for crimes that reach police anyway? It widens: against {W} {sexw} from {x(simple['ratio'][W])}x for simple assault "
                f"without serious injury to {x(gun['ratio'][W])}x for assaults with a gun, and against {H} {sexw} from {x(simple['ratio'][H])}x to {x(gun['ratio'][H])}x. "
                + " ".join(f"{t['label']}: {t['n'][G]} {FL} and {t['n'][W]} {W} {sexw} were killed, {x(t['ratio'][W])}x (95% CI {t['ci'][W][0]} to {t['ci'][W][1]}), too few to chart."
                           for t in small if t["label"] == "Homicide")
                + "".join(f" {g} {sexw} are left out of the chart: " + ", ".join(f"only {t['n'][g]} were victims of {t['label'].lower()}" for t in ts) + "."
                          for g, ts in left_out.items())
                + f" Bars need {mn} victims in the comparison group.")
    severity_box = {"id": "sevChart", "title": "Severity", "text": sev_text, "labels": [AXIS.get(t["label"], t["label"]) for t in charted],
                    "datasets": [{"label": f"vs {g} {sexw}", "data": [t["ratio"][g] for t in charted], "color": COLOR[others.index(g)]} for g in shown],
                    "ytitle": f"{FL}'s rate as a multiple"}

    # reporting: what the severity test and the national survey can and cannot say
    rr, rt = cv["reported_to_police_pct_by_race"], cv["reported_to_police_pct_by_type_2024"]
    obs = R["ratios"][W]
    reporting = {"title": "Reporting: partly testable", "text":
                 f"If the gap came from {FL} reporting more, it would narrow for the crimes reported most often, and it widens instead (Severity, above). "
                 f"Nationally, {round(rt['simple_assault'])}% of simple assaults reach police against {round(rt['firearm'])}% of crimes involving a gun, and reporting differs little by race: "
                 f"{round(rr['2024']['Black'])}% of violent crimes against Black victims and {round(rr['2024']['White'])}% against White victims in 2024 "
                 f"({round(rr['2023']['Black'])}% and {round(rr['2023']['White'])}% in 2023). For reporting alone to make the {x(obs)}x gap, {W} {sexw} would have to report "
                 f"under {math.ceil(100 / obs)}% of assaults even if {FL} reported all of them. Unreported assaults stay invisible here."}

    # neighborhood and income
    bands, ex, pr = nb["poverty_bands"], nb["exposure"]["adw_per_1000"], nb["predicted_ratio"]
    inc, hp = nb["citywide_income"], nb["women_in_25pct_poverty_tracts"]
    obs_a, rem = nb["aggravated_observed_ratio"], nb["aggravated_remaining_ratio"]
    n_adw = nb["incidents_by_offense"]["ASSAULT W/DANGEROUS WEAPON"]
    start, end = p.cfg["window"]["start"][:4], p.cfg["window"]["end"][:4]
    pov_box = {"id": "povChart", "title": "Where women live, by tract poverty",
               "text": f"{hp[G]}% of {FL} live in tracts where 25% or more of residents are poor, against {hp[W]}% of {W} {sexw}. Citywide, {inc[G]['women_below_poverty_pct']}% of {FL} "
                       f"are below the poverty line, against {inc[W]['women_below_poverty_pct']}% of {W} {sexw}, and median household income is ${inc[G]['median_household_income']:,} "
                       f"for {G} households and ${inc[W]['median_household_income']:,} for {W} ones.",
               "labels": [b["label"] for b in bands],
               "datasets": [{"label": f"{g} {sexw}", "data": [b["women_pct"][g] for b in bands], "color": "red" if g == G else COLOR[others.index(g)]} for g in p.groups],
               "ytitle": f"% of each group's {sexw}"}
    viol_box = {"id": "violChart", "title": "Recorded violence by tract poverty",
                "text": f"Tracts where 25% or more of residents are poor record {bands[-1]['adw_per_1000']} assaults with a dangerous weapon per 1,000 residents a year, against "
                        f"{bands[0]['adw_per_1000']} in tracts under 10%. Averaged over where {sexw} live, {FL}'s tracts record {x(pr['adw_per_1000'][W])}x the rate of {W} {sexw}'s "
                        f"and {x(pr['adw_per_1000'][H])}x {H} {sexw}'s.",
                "labels": [b["label"] for b in bands],
                "datasets": [{"label": "Assaults with a dangerous weapon per 1,000 residents a year", "data": [b["adw_per_1000"] for b in bands], "color": "blue"}],
                "ytitle": "Per 1,000 residents a year", "legend": False}
    alt = pr["violent_per_1000"][W], pr["adw_per_km2"][W]
    says = (f"If every woman faced her own tract's rate, {FL}'s aggravated assault rate would be {x(pr['adw_per_1000'][W])}x {W} {sexw}'s and {x(pr['adw_per_1000'][H])}x "
            f"{H} {sexw}'s. It is {x(obs_a[W])}x and {x(obs_a[H])}x. Neighborhood accounts for a factor of about {x(pr['adw_per_1000'][W])} against {W} {sexw}; a factor of "
            f"about {x(rem[W])} remains that this check cannot place. Other definitions give a smaller neighborhood factor: {x(alt[0])}x counting all violent crime, "
            f"{x(alt[1])}x per square kilometer.")
    cannot = ("These are tract averages, not victims. Neighbors on different blocks can face different risks, and assaults away from home are not placed. "
              "Neighborhood poverty is shaped by segregation and discrimination, so the part of the gap found in neighborhoods is located, not explained away.")
    vr = cv["violent_rate_per_1000_2024"]
    context = (f"The national crime survey, which counts crimes whether or not they were reported, finds similar rates of violence for Black and White people: "
               f"{vr['Black']} and {vr['White']} per 1,000 in 2024, both sexes. Poor urban Black and White residents had similar rates too "
               f"({pov14['violent_rate_per_1000_poor_urban']['Black']} and {pov14['violent_rate_per_1000_poor_urban']['White']} per 1,000, 2008 to 2012).")
    section = {"title": "Neighborhood and income",
               "note": f"NIBRS has no location. MPD's public incident data has locations but no victim race. This section places {n_adw:,} assaults with a dangerous weapon "
                       f"from {start} to {end} in census tracts and averages each tract's rate per resident over where each group's {sexw} live. It describes places, not victims.",
               "boxes": [pov_box, viol_box],
               "findings": [{"title": "What this check says", "text": says, "red": True},
                            {"title": "What it cannot say", "text": cannot},
                            {"title": "National context", "text": context}]}

    readme = [["Severity", f"against {W} {sexw} {x(simple['ratio'][W])}x for simple assault without serious injury, {x(serious['ratio'][W])}x with serious injury, "
                           f"{x(gun['ratio'][W])}x with a gun, {x(hom['ratio'][W])}x for homicide (95% CI {hom['ci'][W][0]} to {hom['ci'][W][1]}, {hom['n'][W]} {W} {sexw} killed)"],
              ["Reporting", reporting["text"].rstrip(".")],
              ["Neighborhood", f"{FL}'s tracts record {x(pr['adw_per_1000'][W])}x {W} {sexw}'s rate of assaults with a dangerous weapon per resident; "
                               f"that predicts a {x(pr['adw_per_1000'][W])}x aggravated assault gap against the {x(obs_a[W])}x observed, leaving about {x(rem[W])}x"]]
    out = {"tests": [severity_box], "reporting": reporting, "sections": [section], "readme": readme}
    p.write_json("extra_sections.json", out)


if __name__ == "__main__":
    main()
