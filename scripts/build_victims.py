"""Build the analysis files from the flattened NIBRS table: one row per assault victim.

Definition (decided after the audit, see out/audit_assault.md):
  offenses   13A aggravated assault and 13B simple assault; 13C intimidation is left out
  agency     Metropolitan Police Department ("Washington" in the FBI agency table); Metro Transit Police left out
  victims    individuals of any age; law enforcement officers left out

Race group follows the ACS convention used for the denominators: Hispanic (ethnicity H) of any race first,
otherwise the recorded race. Unknown race, unknown ethnicity and unknown age stay unknown.

  python scripts/build_victims.py   ->  data/dc_aggravated_assault.csv, data/dc_simple_assault.csv
"""
import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODES = {"13A": "aggravated", "13B": "simple"}
AGENCY = "Washington"
VICTIM_TYPE = "Individual"
PARTNER = {"SE", "CS", "BG", "HR", "XS", "XR"}  # spouse, common-law, boyfriend/girlfriend, same-sex, ex-spouse, ex-relationship
INFANT = {"NN", "NB", "BB"}  # under 24 hours, 1 to 6 days, 7 to 364 days
UNKNOWN_AGE = {"00", "NS"}
# short display labels for NIBRS location names, which are too long for chart axes on a phone;
# the raw name stays in the `location` column, and names not listed keep their raw form
PREMISE = {
    "Residence/Home": "Home", "Highway/Road/Alley/Street/Sidewalk": "Street & Sidewalk",
    "School-Elementary/Secondary": "K-12 School", "School-College/University": "College", "School/College": "School & College",
    "Government/Public Building": "Government Building", "Commercial/Office Building": "Office Building",
    "Other/Unknown": "Other & Unknown", "Air/Bus/Train Terminal": "Transit Station", "Parking/Drop Lot/Garage": "Parking Lot",
    "Hotel/Motel/Etc.": "Hotel & Motel", "Bar/Nightclub": "Bar & Nightclub", "Drug Store/Doctor's Office/Hospital": "Hospital & Clinic",
    "Department/Discount Store": "Department Store", "Grocery/Supermarket": "Grocery Store", "Park/Playground": "Park & Playground",
    "Shelter-Mission/Homeless": "Shelter", "Jail/Prison/Penitentiary/Corrections Facility": "Jail & Prison",
    "Church/Synagogue/Temple/Mosque": "Religious Building", "Service/Gas Station": "Gas Station", "Field/Woods": "Field & Woods",
    "Lake/Waterway/Beach": "Waterway & Beach", "Arena/Stadium/Fairgrounds/Coliseum": "Arena & Stadium",
    "Bank/Savings and Loan": "Bank", "ATM Separate from Bank": "Cash Machine", "Abandoned/Condemned Structure": "Abandoned Building",
    "Rental Storage Facility": "Storage Facility", "Auto Dealership New/Used": "Auto Dealership", "Camp/Campground": "Campground",
    "Dock/Wharf/Freight/Modal Terminal": "Dock & Wharf", "Gambling Facility/Casino/Race Track": "Casino & Race Track",
    "Military Installation": "Military Base", "Farm Facility": "Farm",
}


def main():
    d = pd.read_csv(ROOT / "data/interim/victim_offenses.csv", low_memory=False, dtype={"age_num": str, "age_code": str})
    d = d[d["offense_code"].isin(CODES) & (d["agency"] == AGENCY) & (d["victim_type"] == VICTIM_TYPE)].copy()
    age = pd.to_numeric(d["age_num"], errors="coerce")
    age[d["age_code"].isin(INFANT)] = 0
    age[d["age_code"].isin(UNKNOWN_AGE)] = np.nan
    codes = d["relationship"].fillna("").str.split(";")
    out = pd.DataFrame({
        "victim_id": d["victim_id"],
        "incident_id": d["incident_id"],
        "incident_date": d["incident_date"],
        "offense_code": d["offense_code"],
        "race_group": np.where(d["ethnicity"] == "H", "H", d["race"]),
        "race": d["race"],
        "ethnicity": d["ethnicity"],
        "sex": d["sex"],
        "age": age.astype("Int64"),
        "resident_status": d["resident_status"],
        "partner": np.where(codes.apply(lambda xs: bool(PARTNER & set(xs))), "Y", "N"),
        "relationship": d["relationship"],
        "location": d["location"],
        "premise": d["location"].map(lambda v: PREMISE.get(v, v)),
        "weapon": d["weapon"],
        "injury": d["injury"],
        "attempt_complete": d["attempt_complete"],
    })
    assert out["victim_id"].is_unique, "a victim appears twice"
    for code, kind in CODES.items():
        part = out[out["offense_code"] == code].sort_values(["incident_date", "victim_id"])
        dest = ROOT / "data" / f"dc_{kind}_assault.csv"
        part.to_csv(dest, index=False)
        print(f"wrote {dest.name}: {len(part):,} victims")


if __name__ == "__main__":
    main()
