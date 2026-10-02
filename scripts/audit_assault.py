"""Assault-specific audit of the flattened NIBRS file, to read beside out/audit_victim_offenses.md.

Covers what the generic audit cannot see in linked NIBRS tables: victim types and agencies for each
assault code, how race and ethnicity are coded together, resident status, relationship coverage,
and monthly counts by agency.

  python scripts/audit_assault.py        ->  out/audit_assault.md
"""
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSAULT = ["13A", "13B", "13C"]
PARTNER = {"SE", "CS", "BG", "HR", "XS", "XR"}


def table(ct):
    ct = ct.copy()
    head = "| " + " | ".join([ct.index.name or ""] + [str(c) for c in ct.columns]) + " |"
    rows = ["| " + " | ".join([str(i)] + [f"{v:,}" if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v) for v in r]) + " |"
            for i, r in zip(ct.index, ct.values.tolist())]
    return [head, "|" + "---|" * (len(ct.columns) + 1)] + rows + [""]


def main():
    d = pd.read_csv(ROOT / "data/interim/victim_offenses.csv", low_memory=False, dtype={"age_num": str})
    d["date"] = pd.to_datetime(d["incident_date"])
    a = d[d["offense_code"].isin(ASSAULT)]
    ind = a[a["victim_type"] == "Individual"]
    core = ind[ind["offense_code"].isin(["13A", "13B"])]
    L = ["# Assault audit: DC NIBRS 2022 to 2025", ""]
    L += [f"Rows are victim-offense pairs. Files overlap on no incident id or victim id; every incident date falls in its file's year "
          f"({(d['date'].dt.year != d['file_year']).sum()} mismatches).", ""]
    per_victim = ind.groupby(["file_year", "victim_id"])["offense_code"].nunique()
    L += [f"Individual victims with more than one assault code in the same incident: {(per_victim > 1).sum()}. One assault row is one victim.", ""]

    L += ["## Assault codes by victim type", ""] + table(pd.crosstab(a["victim_type"], a["offense_code"], margins=True))
    L += ["## Assault codes by agency (individual victims)", ""] + table(pd.crosstab(ind["agency"], ind["offense_code"], margins=True))
    L += ["## Sex (individual victims, 13A and 13B)", ""] + table(pd.crosstab(core["sex"], core["offense_code"], margins=True))
    L += ["## Race by ethnicity (individual victims, 13A and 13B)", "",
          "Race and ethnicity are separate fields. H = Hispanic, N = not Hispanic, U = unknown, X = not specified.", ""]
    L += table(pd.crosstab(core["race"], core["ethnicity"], margins=True))
    w = core[core["race"] == "W"]
    known = w["ethnicity"].isin(["H", "N"])
    L += [f"White-race victims with unknown or unspecified ethnicity: {(~known).sum():,} of {len(w):,} ({(~known).mean() * 100:.1f}%). "
          f"Where ethnicity is known, {(w.loc[known, 'ethnicity'] == 'H').mean() * 100:.1f}% of White-race victims are Hispanic.", ""]
    L += ["## Ethnicity by year (individual victims, 13A and 13B)", ""] + table(pd.crosstab(core["ethnicity"], core["file_year"], margins=True))
    L += ["## Resident status by year (individual victims, 13A and 13B)", "",
          "R = resident of the jurisdiction, N = non-resident, U = unknown, blank = not reported.", ""]
    L += table(pd.crosstab(core["resident_status"].fillna("blank"), core["file_year"], margins=True))
    rel = core["relationship"]
    partner = rel.fillna("").str.split(";").apply(lambda xs: bool(PARTNER & set(xs)))
    L += ["## Victim-offender relationship (individual victims, 13A and 13B)", "",
          f"Blank: {rel.isna().mean() * 100:.1f}%. Relationship unknown (RU) as the only code: {(rel == 'RU').mean() * 100:.1f}%. "
          f"Any partner code (spouse, common-law, boyfriend or girlfriend, same-sex relationship, ex-spouse, ex-relationship): {partner.mean() * 100:.1f}% of all, "
          f"{partner[core['sex'] == 'F'].mean() * 100:.1f}% of women.", ""]
    L += ["| relationship codes | rows |", "|---|---|"] + [f"| {k} | {v:,} |" for k, v in rel.fillna("blank").value_counts().head(30).items()] + [""]
    age = pd.to_numeric(core["age_num"], errors="coerce")
    L += ["## Age (individual victims, 13A and 13B)", "",
          f"Unknown or not specified: {core['age_code'].isin(['00', 'NS']).sum():,}. Under 18: {(age < 18).sum():,} ({(age < 18).mean() * 100:.1f}%). "
          f"Infant codes (NN, NB, BB): {core['age_code'].isin(['NN', 'NB', 'BB']).sum():,}.", ""]
    L += ["## Weapons and circumstances", "",
          f"Weapon blank: 13A {core.loc[core.offense_code == '13A', 'weapon'].isna().mean() * 100:.1f}%, 13B {core.loc[core.offense_code == '13B', 'weapon'].isna().mean() * 100:.1f}%. "
          "The victim circumstances table (aggravated assault circumstances, such as domestic violence) is empty in all four DC files.", ""]
    L += ["## No location below the agency", "",
          "NIBRS carries no address, coordinates, ward or police district. Location tests and the tract-level model cannot run.", ""]
    m = core.groupby([core["date"].dt.to_period("M").astype(str), "agency"]).size().unstack(fill_value=0)
    m.index.name = "month"
    med = m.sum(axis=1).median()
    low = m.sum(axis=1)[m.sum(axis=1) < 0.6 * med]
    L += ["## Monthly 13A and 13B individual victims by agency", "",
          f"Median {med:,.0f} a month; months under 60% of that: {', '.join(low.index) if len(low) else 'none'}.", ""] + table(m)
    out = ROOT / "out" / "audit_assault.md"
    out.write_text("\n".join(L))
    print("wrote", out)


if __name__ == "__main__":
    main()
