# Clearance test: plan, written before the test was run

**Date:** 2026-10-02 · **Script:** `scripts/clearance.py` (written after this plan was committed)

Before this plan was committed, only overall coverage was checked, never by race: 38.6% of incidents with a woman victim have an arrest, 83% of arrests happen the same day, 98% within 90 days, and the FBI's `clearance_ind` field is blank in every row. Whatever the result, it is published on the DC report and on Justice Lens at the same prominence.

## Question

Among women who were victims of aggravated (13A) or simple (13B) assault reported by the Metropolitan Police Department, 2022 to 2025, are assaults on Black women cleared by arrest as often as assaults on Hispanic women and on White women?

## Data

- Victims: `data/dc_aggravated_assault.csv` and `data/dc_simple_assault.csv` (individual victims, MPD, the same files as the main analysis), women only, race group as in the main analysis (Hispanic of any race first, then recorded race). Unknown race is left out and counted.
- Arrests: `NIBRS_ARRESTEE` in each year's file, linked to the victim's incident by `incident_id`. Every arrestee row links to an incident in the same year's file.
- Exceptional clearance: `cleared_except_id` in `NIBRS_incident` (anything other than "not applicable").

## Outcomes

1. **Primary: arrest within 90 days.** The incident has an arrestee whose arrest date is 0 to 90 days after the incident date. A fixed window gives every year the same follow-up.
2. Secondary, reported without a separate decision rule:
   - exceptional clearance, split into victim refused to cooperate, prosecution declined, and other;
   - same-day arrest (day 0) and later arrest (days 1 to 90) separately.

## Comparisons

Black women against Hispanic women, and Black women against White women, each on its own. Asian women are reported, but no direction is asserted for them (small numbers, and the least stable comparison in the main analysis).

## Like with like

DC Code § 16-1031 requires an arrest when there is probable cause of an intrafamily offense that caused injury or reasonable fear of serious injury. Relationship therefore drives arrest, and it differs by group. Every comparison is made inside strata:

- **Relationship of victim to offender**, one category per victim by precedence:
  1. partner (SE, CS, BG, HR, XS, XR)
  2. other family (PA, CH, SB, GP, GC, IL, SP, SC, SS, OF, CF)
  3. known, not family (AQ, FR, NE, BE, EE, ER, OK)
  4. stranger (ST)
  5. unknown (RU, blank, or only VO)
- **Assault type**: aggravated or simple.

That gives 10 strata.

## Method

- **Main estimate:** a Mantel-Haenszel risk ratio across the 10 strata, Black women against the comparison group, with a 95% interval (Greenland-Robins variance).
- **Check:** a Poisson regression with robust errors, with the strata plus year, age band (0-17, 18-29, 30-44, 45-64, 65+, unknown), serious injury, gun and home as premises.
- **Robustness:**
  - the two halves of the window (2022-2023, 2024-2025)
  - incidents with a single victim only
  - the ethnicity bound: White women with unknown ethnicity moved to the Hispanic group
  - same-day and later arrests separately

## Decision rule

For each comparison, a direction is asserted only if both hold:

1. the Mantel-Haenszel 95% interval excludes 1;
2. the partner stratum and the stranger stratum, each pooled over assault type, point the same way as the overall estimate.

Otherwise the result reads "no clear difference" (interval includes 1) or "mixed" (interval excludes 1 but the two strata disagree).

## What the result cannot say

- Clearance by arrest is not a measure of police effort. It also depends on whether the offender was at the scene and identified, whether the victim cooperated, and the evidence.
- Exceptional clearances reflect victims and prosecutors as well as police.
- Nothing here measures who the offenders were.
