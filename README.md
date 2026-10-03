# Assault victims in Washington, DC

Who gets assaulted in Washington, DC, as rates rather than counts: victims of aggravated and simple assault reported by the Metropolitan Police Department, 2022 to 2025, by race and sex, against ACS population. It is the DC companion to the Los Angeles analysis ([Los-Angeles-CA-Assault-Victim-Rates-by-Race-and-Sex-2020-2023](https://github.com/mngoh/Los-Angeles-CA-Assault-Victim-Rates-by-Race-and-Sex-2020-2023)) and uses the same method, packaged as [disparity-kit](https://github.com/mngoh/disparity-kit).

The full page is `index.html`.

## Results

Every number below is generated from `out/results.json`, `out/dc_checks.json` and `out/replication.json`.

<!-- results:start -->
**Black women in DC are assaulted at 2 to 3 times the rate of Hispanic women and about 10 times the rate of White women. The gap is widest for the most serious assaults, and neighborhood accounts for part of it.**

Rates per 100,000 residents a year, 2022-01-01 to 2025-12-31:

| Group | Women | Men |
|---|---|---|
| Black | 4,205 | 3,114 |
| Hispanic | 1,304 | 1,683 |
| White | 412 | 618 |
| Asian | 415 | 839 |

Tests:

- Age: standardized, Black women 4,852 vs 1,347 Hispanic, 382 White, 362 Asian.
- Type: aggravated assault 4.7 times Hispanic, 21.4 times Asian, 14.4 times White; simple assault 3.1 times Hispanic, 9.4 times Asian, 9.7 times White.
- Time: 4,123, 4,356, 4,155, 4,188.
- Premises: Home 65.7% vs 39.9%, Street & Sidewalk 18.2% vs 30.2%, K-12 School 2.3% vs 1.8% (Black women vs other women).
- Weapons: Firearm 4.2% vs 1.8%, Knife or cutting 2.1% vs 1.4%, Blunt object or vehicle 0.5% vs 0.2%, Hands, fists, feet 75.9% vs 76.7%, Other or unknown 17.3% vs 19.9% (Black women vs other women).
- Intimate partner: 32.7% of assaults on Black women (30.3% Hispanic, 22.0% White, 17.6% Asian); ratios with it 3.5x Hispanic, 18.9x Asian, 15.1x White; without it 3.1x Hispanic, 8.3x Asian, 8.8x White.
- Recorded non-resident: 6.3% of assaults on Black women (15.6% Hispanic, 17.3% White, 22.1% Asian); ratios with it 1.3x Hispanic, 2.9x Asian, 3.7x White; without it 3.6x Hispanic, 12.2x Asian, 11.6x White.
- Severity: against White women 9.7x for simple assault without serious injury, 13.8x with serious injury, 23.3x with a gun, 12.7x for homicide (95% CI 5.2 to 40.3, 5 White women killed).
- Reporting: If the gap came from Black women reporting more, it would narrow for the crimes reported most often, and it widens instead (Severity, above). Nationally, 40% of simple assaults reach police against 75% of crimes involving a gun, and reporting differs little by race: 51% of violent crimes against Black victims and 48% against White victims in 2024 (56% and 42% in 2023). For reporting alone to make the 10.2x gap, White women would have to report under 10% of assaults even if Black women reported all of them. Unreported assaults stay invisible here.
- Neighborhood: Black women's tracts record 2.8x White women's rate of assaults with a dangerous weapon per resident; that predicts a 2.8x aggravated assault gap against the 14.4x observed, leaving about 5.2x.
- Protection: mixed against White women and mixed against Hispanic women by the pre-set rule; like with like, 0.9x (95% CI 0.85 to 0.96) White women's arrest rate and 0.86x (95% CI 0.81 to 0.9) Hispanic women's; partner assaults 44.1% against 59.2% (White) and 57.3% (Hispanic); strangers 1.05x and 1.09x.

Replication: Hispanic 3.31x then 3.14x; White 10.12x then 10.3x; Asian 9.22x then 11.24x.

Caveats:

- This shows what, not why: The data says Black women are assaulted at a higher rate. It does not say why. Nothing here measures causes, offenders or circumstances.
- Reported crimes only: Every number is a report that reached the police. Willingness to report, and recording practice, differ by group, area and time.
- Reports, not people: Rates count reports. Someone assaulted twice counts twice, so a rate is not the share of people assaulted.
- Exposure is not population: Rates divide by where people live, not where they spend time.
- Who is recorded as Black: Race is recorded by officers; the population counts people who are Black alone. There are 9% more people who are Black alone or in combination. If multiracial victims are recorded as Black, the worst case is 2.96x Hispanic, 9.38x White, 9.31x Asian instead of 3.22x, 10.21x, 10.13x.
- Overlapping groups: 1.2% of Black residents are also Hispanic, so they sit in both denominators.
- Who is counted: 2,844 victims are left out of the rates: their sex is unknown, or their race is unknown or outside the compared groups. Race is unknown or outside the groups for 3.4% of women and 6.5% of men.
- What this number measures: Police reports, not how often women are hurt. In the national victimization survey, which counts assaults whether or not police learned of them, Black and White women describe being assaulted at about the same rate nationally and about 1.5 to 2 times in large cities. A follow-up (Police-Records-vs-Survey-Assault-Victims-by-Race-and-Sex-2015-2025, on GitHub) tested why police records differ more: not reporting rates, not (or only a little) how police write up a call, not the same women counted repeatedly, but largely where assaults happen and who calls. Hospital emergency departments, which do not depend on a call to police, see a gap like the police one (about 4.6 times for women in 2021 to 2022), which points to the survey undercounting assaults on Black women.
- Victims have no location: The FBI's NIBRS files record no address, ward or police district, so the victim-level location test and the tract-level model from the Los Angeles analysis cannot run. The neighborhood section uses MPD's public incident locations instead. Those carry no victim race, so that check describes places, not victims.
- Income is not in the victim data: NIBRS records nothing about a victim's income, and DC's economic divide is extreme. 26.3% of Black women are below the poverty line, against 5.1% of White women. Median household income is $60,764 for Black households and $170,201 for White ones. 43.1% of Black women live in census tracts with 25% or more poverty, against 6.2% of White women. Income could account for a large part of the gap; the neighborhood section measures only the part that runs through where women live.
- Agencies in the file: The DC file covers the Metropolitan Police and Metro Transit Police only. Assaults recorded only by federal or campus police are missing. If those skew toward White women, the gap is somewhat overstated.
- Policing and reporting: Police data reflects where officers patrol and who calls them. This data cannot separate more policing or more reporting from more assaults.
- Hispanic ethnicity is often missing: NIBRS records ethnicity separately from race, and it is unknown or unspecified for 30.6% of women victims. 28.8% of women recorded as White have unknown ethnicity, and where it is known, 53.8% of them are Hispanic. They are counted as White here. If they were Hispanic, Black women's rate would be 2.22x Hispanic women's instead of 3.22x, and 19.11x White women's instead of 10.21x.
- Missing race: 1,059 women victims have unknown race. NIBRS has no location, so where they cluster cannot be mapped. Spread over the four groups like known victims of the same assault type, premises and resident status, the ratios move to 3.18x Hispanic, 10.02x White, 9.88x Asian from 3.22x, 10.21x, 10.13x.
- Residents are the denominator: DC draws many commuters and visitors, and rates divide by residents only. Resident status is blank for 36.3% to 43.9% of women victims depending on group (36.3% Black, 40.9% Hispanic, 43.0% White, 43.9% Asian), so the non-resident test is partial.
- Intimate partner is a lower bound: Partner assaults are identified from the victim-offender relationship, which is unknown or blank for 18.2% of Black, 28.0% of Hispanic, 41.8% of White, 42.6% of Asian women victims. Where it is missing more often, the partner share is understated more, so partner comparisons are least certain against the groups with the most missing.
- What is counted: Aggravated (13A) and simple (13B) assault reported by the Metropolitan Police Department, individual victims of any age. Left out: 5,678 Metro Transit Police victims, whose system extends into Maryland and Virginia; 3,067 assaults on officers; 18,691 intimidation victims (threats with no attack). 57 American Indian or Alaska Native and 33 Native Hawaiian or Pacific Islander victims are counted in the totals but not compared, because counts this small give unstable rates. 138 victims with unknown age or under one year old fall out of the age test only.
- Window and population: Victims cover January 2022 to December 2025; the population is the ACS 2024 5-year estimate, an average over 2020 to 2024.
- Least stable comparison: The Asian comparison moved +22% between 2022 to 2023 and 2024 to 2025 (-25% for aggravated assault), against 5% or less for the others. It rests on 160 Asian women victims in 2022 to 2023 and 129 Asian women victims in 2024 to 2025, so it is left out of the headline.
<!-- results:end -->

## How this differs from the Los Angeles analysis

- **Source.** The FBI's NIBRS files for the District of Columbia, one download per year, each a set of linked tables. `scripts/flatten_nibrs.py` joins them into one row per victim per offense. LA used the LAPD's own portal.
- **No location.** NIBRS records no address, ward or police district. The victim-level location test and the tract-level model from LA cannot run here. Instead, a neighborhood section places MPD's public incident locations (which carry no victim race) in census tracts and compares the places where women of each group live. It describes places, not victims.
- **Protection test.** Are assaults on Black women cleared by arrest as often as other women's? Written down before it ran (`docs/clearance-test-plan.md`) and compared like with like by relationship and assault type, because DC law requires an arrest in domestic and family cases when there is probable cause.
- **Severity as a reporting check.** If the gap came from more reporting, it would narrow for the crimes reported most often (serious injuries, guns, homicide). The page tests that, with national survey reporting rates as context.
- **Race and ethnicity are separate fields.** A victim is Hispanic if the ethnicity field says so, whatever the race, and otherwise takes the recorded race. That matches the ACS tables used as denominators. Ethnicity is often missing, so the Hispanic and White comparisons carry a range (see the caveats).
- **Intimate partner comes from the relationship field**, not from separate offense codes as in LA.
- **Non-resident victims.** NIBRS records whether a victim lives in DC, so the page tests whether visitors and commuters inflate per-resident rates.
- **Replication.** DC used one records system for the whole window, so the replication compares the first two years with the last two. That checks stability over time, not a different coding system.

## Definitions

- Offenses: 13A aggravated assault and 13B simple assault. 13C intimidation (threats with no attack) is left out; the LA offense codes did not include threats either.
- Agency: Metropolitan Police Department. Metro Transit Police are left out because their system extends into Maryland and Virginia, and the data cannot say where an assault happened.
- Victims: individuals of any age. Assaults on officers are left out, as in LA.
- Window: January 2022 to December 2025. MPD began reporting to NIBRS in August 2021, so 2022 is its first full year. The audit found no coverage breaks.
- Groups: Black, Hispanic, White and Asian, as recorded by officers. Unknown race and sex stay unknown. Nothing is imputed.

## Rebuild

Python from disparity-kit (`~/.claude/disparity-kit/.venv/bin/python`); `KIT=~/.claude/disparity-kit/kit`. Needs disparity-kit commit `7112d1c` or later, which reads flags from any column and draws the page sections in `out/extra_sections.json`.

```bash
python scripts/flatten_nibrs.py                      # data/raw/DC-*.zip -> data/interim/victim_offenses.csv
python $KIT/audit.py data/interim/victim_offenses.csv --date incident_date --code offense_code --desc offense_name --id victim_id --out out/audit_victim_offenses.md
python scripts/audit_assault.py                      # -> out/audit_assault.md
python scripts/build_victims.py                      # -> data/dc_aggravated_assault.csv, data/dc_simple_assault.csv
python $KIT/denominators.py analysis.json            # -> out/population.json
python $KIT/analyze.py analysis.json                 # -> out/results.json
python scripts/replication_counts.py analysis.json   # -> out/replication_counts.json
python $KIT/replicate.py analysis.json               # -> out/replication.json
python scripts/severity.py analysis.json             # -> out/severity.json
python scripts/neighborhood.py analysis.json         # -> out/neighborhood.json (needs data/external/mpd_violent_incidents.csv)
python scripts/clearance.py analysis.json            # -> out/clearance.json (the test in docs/clearance-test-plan.md)
python scripts/dc_checks.py analysis.json            # -> out/dc_checks.json, extra_caveats in analysis.json
python scripts/page_extras.py analysis.json          # -> out/extra_sections.json (severity, reporting, neighborhood, protection)
python $KIT/build_page.py analysis.json              # -> index.html, results block above
python $KIT/bias_scan.py analysis.json               # -> out/bias_review.md
python scripts/export_site.py analysis.json          # -> out/site_payload.json (numbers for Justice Lens /protection)
```

## Files

- `data/raw/DC-2022.zip` to `DC-2025.zip`: the FBI NIBRS state files for DC, as received. Each zip has a README describing its tables.
- `data/dc_aggravated_assault.csv`, `data/dc_simple_assault.csv`: one row per victim, the analysis input.
- `data/external/mpd_violent_incidents.csv`: MPD's public violent incidents with locations, 2022 to 2025, fetched by `scripts/fetch_mpd_incidents.py`. Refetch to update.
- `docs/clearance-test-plan.md`: the clearance test as written before it was run.
- `data/external/bjs_ncvs.json`: the national survey figures quoted on the page, with the table each came from.
- `out/`: the audits, population, results, DC checks, replication and bias review. `out/site_payload.json` holds the numbers Justice Lens shows at justicelensai.com/protection, with the commit they came from.

## Sources

- FBI NIBRS state files for the District of Columbia, 2022 to 2025 (`data/raw/`).
- US Census Bureau, ACS 2020 to 2024 five-year estimates, via [Census Reporter](https://censusreporter.org/profiles/16000US1150000-washington-dc/).
- DC Open Data, [MPD Crime Incidents](https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer), 2022 to 2025.
- BJS, [Criminal Victimization, 2024](https://bjs.ojp.gov/document/cv24.pdf) (NCJ 310547), Tables 3, 4, 5 and 10.
- [DC Code § 16-1031](https://code.dccouncil.gov/us/dc/council/code/sections/16-1031), arrests in intrafamily offenses.
- BJS, [Household Poverty and Nonfatal Violent Victimization, 2008-2012](https://bjs.ojp.gov/library/publications/household-poverty-and-nonfatal-violent-victimization-2008-2012) (NCJ 248384).
