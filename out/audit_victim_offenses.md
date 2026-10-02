# Audit: data/interim/victim_offenses.csv

326,527 rows, 23 columns. Guessed: date `incident_date`, code `offense_code`, description `offense_name`, id `victim_id`. Override with flags if wrong.

## Missing and coded-missing values

| column | blank | coded missing (0, X, UNKNOWN...) | distinct |
|---|---|---|---|
| file_year | 0.0% | 0.0% | 4 |
| agency | 0.0% | 0.0% | 2 |
| incident_id | 0.0% | 0.0% | 255,615 |
| incident_date | 0.0% | 0.0% | 1,461 |
| report_date_flag | 0.0% | 0.0% | 2 |
| incident_hour | 1.1% | 7.4% | 24 |
| offense_id | 0.0% | 0.0% | 298,206 |
| offense_code | 0.0% | 0.0% | 45 |
| offense_name | 0.0% | 0.0% | 46 |
| attempt_complete | 0.0% | 0.0% | 2 |
| location | 0.0% | 0.0% | 45 |
| victim_id | 0.0% | 0.0% | 295,747 |
| victim_seq_num | 0.0% | 0.0% | 49 |
| victim_type | 0.0% | 1.3% | 9 |
| age_code | 0.0% | 0.0% | 104 |
| age_num | 0.0% | 0.0% | 104 |
| sex | 0.0% | 21.6% | 4 |
| race | 0.0% | 12.8% | 7 |
| ethnicity | 0.0% | 51.6% | 4 |
| resident_status | 53.2% | 2.4% | 3 |
| relationship | 56.7% | 0.0% | 248 |
| weapon | 70.5% | 0.5% | 113 |
| injury | 86.3% | 0.0% | 58 |

## Duplicates

30,780 rows share an id in `victim_id`. One row per victim or offense? Decide before counting.

## Every offense value

Read the whole list. Related offenses are often coded separately (intimate partner, on police, on children, attempts).

| offense_code | offense_name | rows |
|---|---|---|
| 290 | Destruction/Damage/Vandalism of Property | 65,193 |
| 13B | Simple Assault | 53,995 |
| 23F | Theft From Motor Vehicle | 29,578 |
| 240 | Motor Vehicle Theft | 22,347 |
| 23H | All Other Larceny | 20,381 |
| 13C | Intimidation | 19,974 |
| 520 | Weapon Law Violations | 15,700 |
| 23C | Shoplifting | 15,692 |
| 120 | Robbery | 15,664 |
| 13A | Aggravated Assault | 12,120 |
| 35A | Drug/Narcotic Violations | 10,221 |
| 23D | Theft From Building | 10,044 |
| 220 | Burglary/Breaking & Entering | 7,216 |
| 26B | Credit Card/Automated Teller Machine Fraud | 4,595 |
| 26F | Identity Theft | 4,500 |
| 23G | Theft of Motor Vehicle Parts or Accessories | 3,922 |
| 26A | False Pretenses/Swindle/Confidence Game | 3,498 |
| 280 | Stolen Property Offenses | 2,244 |
| 250 | Counterfeiting/Forgery | 2,176 |
| 11D | Criminal Sexual Contact | 1,170 |
| 26E | Wire Fraud | 867 |
| 11A | Rape | 795 |
| 09A | Murder and Nonnegligent Manslaughter | 757 |
| 23B | Purse-snatching | 561 |
| 11D | Fondling | 437 |
| 210 | Extortion/Blackmail | 425 |
| 26D | Welfare Fraud | 420 |
| 35B | Drug Equipment Violations | 420 |
| 26G | Hacking/Computer Invasion | 334 |
| 370 | Pornography/Obscene Material | 289 |
| 100 | Kidnapping/Abduction | 207 |
| 23A | Pocket-picking | 181 |
| 26C | Impersonation | 145 |
| 270 | Embezzlement | 134 |
| 11B | Sodomy | 82 |
| 11C | Sexual Assault With An Object | 77 |
| 40C | Purchasing Prostitution | 42 |
| 39A | Betting/Wagering | 32 |
| 23E | Theft From Coin-Operated Machine or Device | 30 |
| 720 | Animal Cruelty | 24 |
| 200 | Arson | 16 |
| 40A | Prostitution | 9 |
| 510 | Bribery | 5 |
| 36B | Statutory Rape | 4 |
| 40B | Assisting or Promoting Prostitution | 2 |
| 09B | Negligent Manslaughter | 2 |

## Coverage by month

0 unparseable dates. Range 2022-01-01 to 2025-12-31.

Median 6,735 rows a month. Months under 60% of that (system changes, partial periods, reporting lag):

- none

Full series:

2022-01:5974 2022-02:5525 2022-03:6211 2022-04:6064 2022-05:6567 2022-06:6530 2022-07:6742 2022-08:6611 2022-09:6392 2022-10:6797 2022-11:6449 2022-12:6609 2023-01:7561 2023-02:6891 2023-03:7324 2023-04:7123 2023-05:8280 2023-06:8490 2023-07:8184 2023-08:8864 2023-09:7455 2023-10:8156 2023-11:7294 2023-12:6904 2024-01:6632 2024-02:6459 2024-03:6356 2024-04:6406 2024-05:7304 2024-06:7266 2024-07:7213 2024-08:7081 2024-09:7440 2024-10:7585 2024-11:6969 2024-12:6728 2025-01:5940 2025-02:5447 2025-03:6727 2025-04:6638 2025-05:7062 2025-06:6792 2025-07:6909 2025-08:6353 2025-09:5901 2025-10:5745 2025-11:5457 2025-12:5120

Use only full calendar years where you can; weight any partial year by its share of the year.