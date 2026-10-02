"""Fetch MPD's public crime incidents with locations, violent offenses only, 2022 to 2025.

Source: DC Open Data "Crime Incidents in <year>", served from the MPD feed on maps2.dcgis.dc.gov.
These carry the block-level location of each incident but nothing about the victim, so they can
describe places, not people. Used only by scripts/neighborhood.py.

  python scripts/fetch_mpd_incidents.py   ->  data/external/mpd_violent_incidents.csv
"""
import json
import pathlib
import urllib.parse
import urllib.request

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
SERVICE = "https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer"
LAYERS = {2022: 4, 2023: 5, 2024: 6, 2025: 7}
OFFENSES = ["ASSAULT W/DANGEROUS WEAPON", "HOMICIDE", "ROBBERY", "SEX ABUSE"]
FIELDS = ["CCN", "REPORT_DAT", "START_DATE", "OFFENSE", "METHOD", "WARD", "DISTRICT", "PSA", "CENSUS_TRACT", "LATITUDE", "LONGITUDE"]
PAGE = 1000


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dc-assault-analysis/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def layer(year, lid):
    where = "OFFENSE IN (" + ",".join(f"'{o}'" for o in OFFENSES) + ")"
    rows, offset = [], 0
    while True:
        q = {"where": where, "outFields": ",".join(FIELDS), "returnGeometry": "false", "orderByFields": "OBJECTID",
             "resultOffset": offset, "resultRecordCount": PAGE, "f": "json"}
        d = get(f"{SERVICE}/{lid}/query?" + urllib.parse.urlencode(q))
        feats = d.get("features", [])
        rows += [f["attributes"] for f in feats]
        if len(feats) < PAGE and not d.get("exceededTransferLimit"):
            break
        offset += len(feats)
    df = pd.DataFrame(rows)
    df.insert(0, "layer_year", year)
    for c in ["REPORT_DAT", "START_DATE"]:
        df[c] = pd.to_datetime(df[c], unit="ms", errors="coerce").dt.strftime("%Y-%m-%d")
    print(f"{year}: {len(df):,} incidents", df["OFFENSE"].value_counts().to_dict())
    return df


def main():
    df = pd.concat([layer(y, lid) for y, lid in LAYERS.items()], ignore_index=True)
    before = len(df)
    df = df.drop_duplicates(["CCN", "OFFENSE"])
    if before != len(df):
        print(f"dropped {before - len(df):,} rows repeated across yearly layers")
    dest = ROOT / "data" / "external" / "mpd_violent_incidents.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    print("wrote", dest, f"({len(df):,} rows)")


if __name__ == "__main__":
    main()
