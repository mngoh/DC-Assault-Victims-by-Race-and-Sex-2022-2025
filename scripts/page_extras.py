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

    # protection: the clearance test written down in docs/clearance-test-plan.md before it ran
    cl = p.read_json("clearance.json")
    cmp_, crude, byrel, lab = cl["comparisons"], cl["crude"], cl["by_relationship"], cl["relationship_labels"]
    order = cl["relationship_order"]
    ci = lambda r: f"{r['rr']}x (95% CI {r['ci'][0]} to {r['ci'][1]})"
    verdict = {"lower": "lower", "higher": "higher", "mixed": "mixed", "no clear difference": "no clear difference"}
    decisions = {g: cmp_[g]["decision"] for g in (W, H)}
    same = decisions[W] == decisions[H]
    rate_box = {"id": "clearRel", "title": "Arrest within 90 days, by relationship",
                "text": f"In partner assaults, {byrel['partner'][G]['arrest90']}% of {FL}'s cases end in an arrest within {cl['window_days']} days, against "
                        f"{byrel['partner'][W]['arrest90']}% of {W} {sexw}'s and {byrel['partner'][H]['arrest90']}% of {H} {sexw}'s. Among strangers: "
                        f"{byrel['stranger'][G]['arrest90']}%, {byrel['stranger'][W]['arrest90']}% and {byrel['stranger'][H]['arrest90']}%. "
                        f"Asian {sexw} are left out of the chart: {cl['victims']['Asian']} victims in all.",
                "labels": [lab[r] for r in order],
                "datasets": [{"label": f"{g} {sexw}", "data": [byrel[r][g]["arrest90"] for r in order], "color": "red" if g == G else COLOR[others.index(g)]}
                             for g in [G, H, W]],
                "ytitle": f"% arrested within {cl['window_days']} days"}
    rr_box = {"id": "clearRR", "title": "Compared like with like",
              "text": f"{FL}'s arrest rate as a multiple of each group's, inside each relationship (below 1 means less often). "
                      f"All relationships together, compared like with like: {ci(cmp_[W]['pooled'])} against {W} {sexw}, {ci(cmp_[H]['pooled'])} against {H} {sexw}.",
              "labels": [lab[r] for r in order] + ["All, like with like"],
              "datasets": [{"label": f"vs {g} {sexw}", "data": [cmp_[g]["by_relationship"][r]["rr"] for r in order] + [cmp_[g]["pooled"]["rr"]],
                            "color": COLOR[others.index(g)]} for g in [H, W]],
              "ytitle": "Rate ratio"}
    below = lambda r: r["ci"][1] is not None and r["ci"][1] < 1        # interval entirely under 1
    above = lambda r: r["ci"][0] is not None and r["ci"][0] > 1
    unclear = lambda r: not below(r) and not above(r)
    times = lambda r, who: f"{r['rr']} times as often as {who}'s (95% CI {r['ci'][0]} to {r['ci'][1]})"
    pw, ph = cmp_[W]["pooled"], cmp_[H]["pooled"]
    lead = (f"Both comparisons are {decisions[W]}" if same else
            "The result is " + " and ".join(f"{decisions[g]} against {g} {sexw}" for g in (W, H))) + " by the rule written before the test."
    gap_in = [lab[r].lower() for r in order if all(below(cmp_[g]["by_relationship"][r]) for g in (W, H))]
    none_in = [lab[r].lower() for r in order if all(unclear(cmp_[g]["by_relationship"][r]) for g in (W, H))]
    parts = [lead, f"Compared like with like, {FL}'s cases end in an arrest {times(pw, f'{W} {sexw}')} and {times(ph, f'{H} {sexw}')}."]
    if gap_in:
        parts.append(f"The gap sits in {' and '.join(gap_in)} assaults: in partner assaults, {times(cmp_[W]['by_relationship']['partner'], f'{W} {sexw}')}." if "partner" in gap_in
                     else f"The gap sits in {' and '.join(gap_in)} assaults.")
    if none_in:
        parts.append(f"There is no clear difference for {' or '.join(none_in)} relationships.")
    halves = [x for g in (W, H) for x in cmp_[g]["checks"]["halves"].values()]
    if all(below(x) for x in halves) or all(above(x) for x in halves):
        parts.append("It holds in both halves of the window.")
    sd, lt = cmp_[W]["checks"]["same_day"], cmp_[W]["checks"]["later"]
    if below(sd) and unclear(lt):
        parts.append(f"Against {W} {sexw} it sits in same-day arrests ({sd['rr']}x), not later ones ({lt['rr']}x).")
    says = " ".join(parts)
    if crude[G]["arrest90"] > crude[W]["arrest90"] and below(pw):
        raw = (f"Before comparing like with like, {FL}'s cases look more likely to end in an arrest ({crude[G]['arrest90']}% against {crude[W]['arrest90']}% for {W} {sexw}). "
               f"More of them are partner assaults ({cl['relationship_share'][G]['partner']}% against {cl['relationship_share'][W]['partner']}%), where DC Code 16-1031 requires an "
               f"arrest when there is probable cause, and fewer have an unknown relationship ({cl['relationship_share'][G]['unknown']}% against {cl['relationship_share'][W]['unknown']}%), "
               "where arrests are rare.")
    else:
        raw = (f"Before comparing like with like: {crude[G]['arrest90']}% of {FL}'s cases end in an arrest, against {crude[W]['arrest90']}% of {W} {sexw}'s and "
               f"{crude[H]['arrest90']}% of {H} {sexw}'s. Relationship mixes differ by group, so these raw rates are not the comparison.")
    vr = cmp_[W]["secondary"]["victim_refused"]
    closed = (f"Cases with {FL} victims are closed as \"victim refused to cooperate\" {times(vr, f'{W} {sexw}')}, like with like "
              f"({crude[G]['victim_refused']}% against {crude[W]['victim_refused']}% before adjusting). That is the reason police recorded. It cannot separate a victim's choice, "
              "or her safety, from how the case was handled.")
    cannot_c = ("Clearance is not a measure of police effort. It depends on whether the person who did it was still there, whether there was probable cause, "
                "the victim's cooperation and the evidence. Nothing here measures offenders.")
    protection = {"title": "Protection: are cases cleared by arrest equally?",
                  "note": f"Written down before it was run (docs/clearance-test-plan.md). An arrest within {cl['window_days']} days of the incident, from MPD's arrest records "
                          f"in the same NIBRS files, for {sexw} victims, compared inside each relationship and assault type, because DC law requires an arrest in "
                          "domestic and family cases when there is probable cause.",
                  "boxes": [rate_box, rr_box],
                  "findings": [{"title": "What the test says", "text": says, "red": True},
                               {"title": "Why the raw rates mislead", "text": raw},
                               {"title": "How cases close without an arrest", "text": closed},
                               {"title": "What it cannot say", "text": cannot_c}]}

    readme = [["Severity", f"against {W} {sexw} {x(simple['ratio'][W])}x for simple assault without serious injury, {x(serious['ratio'][W])}x with serious injury, "
                           f"{x(gun['ratio'][W])}x with a gun, {x(hom['ratio'][W])}x for homicide (95% CI {hom['ci'][W][0]} to {hom['ci'][W][1]}, {hom['n'][W]} {W} {sexw} killed)"],
              ["Reporting", reporting["text"].rstrip(".")],
              ["Neighborhood", f"{FL}'s tracts record {x(pr['adw_per_1000'][W])}x {W} {sexw}'s rate of assaults with a dangerous weapon per resident; "
                               f"that predicts a {x(pr['adw_per_1000'][W])}x aggravated assault gap against the {x(obs_a[W])}x observed, leaving about {x(rem[W])}x"],
              ["Protection", f"{decisions[W]} against {W} {sexw} and {decisions[H]} against {H} {sexw} by the pre-set rule; like with like, {ci(cmp_[W]['pooled'])} {W} {sexw}'s arrest rate "
                             f"and {ci(cmp_[H]['pooled'])} {H} {sexw}'s; partner assaults {byrel['partner'][G]['arrest90']}% against {byrel['partner'][W]['arrest90']}% ({W}) and "
                             f"{byrel['partner'][H]['arrest90']}% ({H}); strangers {cmp_[W]['by_relationship']['stranger']['rr']}x and {cmp_[H]['by_relationship']['stranger']['rr']}x"]]
    out = {"tests": [severity_box], "reporting": reporting, "sections": [section, protection], "readme": readme}
    p.write_json("extra_sections.json", out)


if __name__ == "__main__":
    main()
