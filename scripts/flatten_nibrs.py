"""Flatten the FBI's NIBRS tables for Washington, DC into one row per victim per offense.

Reads the four yearly downloads straight from data/raw/DC-<year>.zip (the 2023 zip nests its files
one folder deeper) and joins incident, offense, victim, victim-offense, victim-offender relationship,
weapon and injury tables with their code lookups. Nothing is imputed: a missing value stays missing.

  python scripts/flatten_nibrs.py        ->  data/interim/victim_offenses.csv (every offense, for the audit)

Each row is one victim linked to one offense. A victim of two offenses in one incident has two rows.
"""
import io
import pathlib
import zipfile

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
YEARS = [2022, 2023, 2024, 2025]


def reader(year):
    z = zipfile.ZipFile(RAW / f"DC-{year}.zip")
    names = {pathlib.PurePosixPath(n).name: n for n in z.namelist() if n.endswith(".csv")}

    def read(table, **kw):
        return pd.read_csv(io.BytesIO(z.read(names[f"{table}.csv"])), low_memory=False, **kw)
    return read


def joined(values):
    vals = sorted({str(v) for v in values if pd.notna(v)})
    return ";".join(vals) if vals else None


def one_year(year):
    read = reader(year)
    look = lambda t, k, v: read(t).set_index(k)[v].to_dict()
    agency = look("agencies", "agency_id", "pub_agency_name")
    off_name = look("NIBRS_OFFENSE_TYPE", "offense_code", "offense_name")
    loc_name = look("NIBRS_LOCATION_TYPE", "location_id", "location_name")
    vtype = look("NIBRS_VICTIM_TYPE", "victim_type_id", "victim_type_name")
    race = look("REF_RACE", "race_id", "race_code")
    eth = look("NIBRS_ETHNICITY", "ethnicity_id", "ethnicity_code")
    age_code = look("NIBRS_AGE", "age_id", "age_code")
    rel_code = look("NIBRS_RELATIONSHIP", "relationship_id", "relationship_code")
    weapon_name = look("NIBRS_WEAPON_TYPE", "weapon_id", "weapon_name")
    injury_name = look("NIBRS_INJURY", "injury_id", "injury_name")

    inc = read("NIBRS_incident", usecols=["incident_id", "agency_id", "incident_date", "report_date_flag", "incident_hour"])
    off = read("NIBRS_OFFENSE", usecols=["offense_id", "incident_id", "offense_code", "attempt_complete_flag", "location_id"])
    vo = read("NIBRS_VICTIM_OFFENSE", usecols=["victim_id", "offense_id"])
    vic = read("NIBRS_VICTIM", dtype={"age_num": str})
    rel = read("NIBRS_VICTIM_OFFENDER_REL", usecols=["victim_id", "relationship_id"])
    wea = read("NIBRS_WEAPON", usecols=["offense_id", "weapon_id"])
    inj = read("NIBRS_VICTIM_INJURY", usecols=["victim_id", "injury_id"])

    rel["code"] = rel["relationship_id"].map(rel_code)
    rel_by_victim = rel.groupby("victim_id")["code"].agg(joined)
    wea["name"] = wea["weapon_id"].map(weapon_name)
    weapon_by_offense = wea.groupby("offense_id")["name"].agg(joined)
    inj["name"] = inj["injury_id"].map(injury_name)
    injury_by_victim = inj.groupby("victim_id")["name"].agg(joined)

    d = (vo.merge(off, on="offense_id", how="left")
           .merge(vic, on=["victim_id"], how="left", suffixes=("", "_v"))
           .merge(inc, on="incident_id", how="left"))
    out = pd.DataFrame({
        "file_year": year,
        "agency": d["agency_id"].map(agency),
        "incident_id": d["incident_id"],
        "incident_date": d["incident_date"],
        "report_date_flag": d["report_date_flag"],
        "incident_hour": d["incident_hour"],
        "offense_id": d["offense_id"],
        "offense_code": d["offense_code"],
        "offense_name": d["offense_code"].map(off_name),
        "attempt_complete": d["attempt_complete_flag"],
        "location": d["location_id"].map(loc_name),
        "victim_id": d["victim_id"],
        "victim_seq_num": d["victim_seq_num"],
        "victim_type": d["victim_type_id"].map(vtype),
        "age_code": d["age_id"].map(age_code),
        "age_num": d["age_num"],
        "sex": d["sex_code"],
        "race": d["race_id"].map(race),
        "ethnicity": d["ethnicity_id"].map(eth),
        "resident_status": d["resident_status_code"],
        "relationship": d["victim_id"].map(rel_by_victim),
        "weapon": d["offense_id"].map(weapon_by_offense),
        "injury": d["victim_id"].map(injury_by_victim),
    })
    print(f"{year}: {len(inc):,} incidents, {len(vic):,} victims, {len(out):,} victim-offense rows")
    return out


def main():
    df = pd.concat([one_year(y) for y in YEARS], ignore_index=True)
    dest = ROOT / "data" / "interim" / "victim_offenses.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    print("wrote", dest, f"({len(df):,} rows)")


if __name__ == "__main__":
    main()
