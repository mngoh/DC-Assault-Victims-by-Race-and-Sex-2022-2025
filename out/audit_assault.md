# Assault audit: DC NIBRS 2022 to 2025

Rows are victim-offense pairs. Files overlap on no incident id or victim id; every incident date falls in its file's year (0 mismatches).

Individual victims with more than one assault code in the same incident: 0. One assault row is one victim.

## Assault codes by victim type

| victim_type | 13A | 13B | 13C | All |
|---|---|---|---|---|
| Individual | 11,783 | 49,987 | 19,384 | 81,154 |
| Law Enforcement Officer | 337 | 4,008 | 590 | 4,935 |
| All | 12,120 | 53,995 | 19,974 | 86,089 |

## Assault codes by agency (individual victims)

| agency | 13A | 13B | 13C | All |
|---|---|---|---|---|
| Metro Transit Police | 941 | 4,737 | 693 | 6,371 |
| Washington | 10,842 | 45,250 | 18,691 | 74,783 |
| All | 11,783 | 49,987 | 19,384 | 81,154 |

## Sex (individual victims, 13A and 13B)

| sex | 13A | 13B | All |
|---|---|---|---|
| F | 4,442 | 30,029 | 34,471 |
| M | 7,284 | 19,830 | 27,114 |
| U | 57 | 128 | 185 |
| All | 11,783 | 49,987 | 61,770 |

## Race by ethnicity (individual victims, 13A and 13B)

Race and ethnicity are separate fields. H = Hispanic, N = not Hispanic, U = unknown, X = not specified.

| race | H | N | U | X | All |
|---|---|---|---|---|---|
| A | 12 | 644 | 103 | 170 | 929 |
| B | 301 | 32,131 | 6,158 | 7,950 | 46,540 |
| I | 16 | 46 | 10 | 17 | 89 |
| P | 33 | 18 | 6 | 9 | 66 |
| U | 1,599 | 688 | 933 | 1,079 | 4,299 |
| W | 3,601 | 3,657 | 1,153 | 1,436 | 9,847 |
| All | 5,562 | 37,184 | 8,363 | 10,661 | 61,770 |

White-race victims with unknown or unspecified ethnicity: 2,589 of 9,847 (26.3%). Where ethnicity is known, 49.6% of White-race victims are Hispanic.

## Ethnicity by year (individual victims, 13A and 13B)

| ethnicity | 2022 | 2023 | 2024 | 2025 | All |
|---|---|---|---|---|---|
| H | 1,259 | 1,522 | 1,545 | 1,236 | 5,562 |
| N | 9,526 | 9,530 | 8,984 | 9,144 | 37,184 |
| U | 1,995 | 2,184 | 2,123 | 2,061 | 8,363 |
| X | 2,181 | 3,127 | 2,665 | 2,688 | 10,661 |
| All | 14,961 | 16,363 | 15,317 | 15,129 | 61,770 |

## Resident status by year (individual victims, 13A and 13B)

R = resident of the jurisdiction, N = non-resident, U = unknown, blank = not reported.

| resident_status | 2022 | 2023 | 2024 | 2025 | All |
|---|---|---|---|---|---|
| N | 1,758 | 1,932 | 2,048 | 1,981 | 7,719 |
| R | 6,915 | 7,555 | 7,574 | 7,629 | 29,673 |
| U | 299 | 426 | 528 | 664 | 1,917 |
| blank | 5,989 | 6,450 | 5,167 | 4,855 | 22,461 |
| All | 14,961 | 16,363 | 15,317 | 15,129 | 61,770 |

## Victim-offender relationship (individual victims, 13A and 13B)

Blank: 8.5%. Relationship unknown (RU) as the only code: 20.3%. Any partner code (spouse, common-law, boyfriend or girlfriend, same-sex relationship, ex-spouse, ex-relationship): 22.2% of all, 30.0% of women.

| relationship codes | rows |
|---|---|
| RU | 12,560 |
| ST | 9,319 |
| OK | 7,857 |
| BG | 7,127 |
| blank | 5,277 |
| XR | 4,144 |
| AQ | 2,981 |
| PA | 1,689 |
| SB | 1,425 |
| CH | 1,185 |
| SE | 1,091 |
| OF | 923 |
| NE | 881 |
| FR | 847 |
| BG;VO | 414 |
| CS | 346 |
| RU;VO | 322 |
| ST;VO | 314 |
| OK;VO | 263 |
| XS | 205 |
| AQ;RU | 183 |
| AQ;VO | 161 |
| RU;ST | 160 |
| OK;RU | 157 |
| SC | 129 |
| VO;XR | 117 |
| IL | 115 |
| GP | 109 |
| SP | 81 |
| SB;VO | 79 |

## Age (individual victims, 13A and 13B)

Unknown or not specified: 89. Under 18: 5,627 (9.1%). Infant codes (NN, NB, BB): 65.

## Weapons and circumstances

Weapon blank: 13A 0.3%, 13B 4.0%. The victim circumstances table (aggravated assault circumstances, such as domestic violence) is empty in all four DC files.

## No location below the agency

NIBRS carries no address, coordinates, ward or police district. Location tests and the tract-level model cannot run.

## Monthly 13A and 13B individual victims by agency

Median 1,288 a month; months under 60% of that: none.

| month | Metro Transit Police | Washington |
|---|---|---|
| 2022-01 | 77 | 927 |
| 2022-02 | 86 | 953 |
| 2022-03 | 120 | 1,109 |
| 2022-04 | 94 | 1,118 |
| 2022-05 | 93 | 1,228 |
| 2022-06 | 101 | 1,188 |
| 2022-07 | 98 | 1,240 |
| 2022-08 | 101 | 1,219 |
| 2022-09 | 96 | 1,283 |
| 2022-10 | 137 | 1,201 |
| 2022-11 | 125 | 1,105 |
| 2022-12 | 132 | 1,130 |
| 2023-01 | 116 | 1,245 |
| 2023-02 | 110 | 1,155 |
| 2023-03 | 142 | 1,232 |
| 2023-04 | 148 | 1,236 |
| 2023-05 | 130 | 1,351 |
| 2023-06 | 131 | 1,296 |
| 2023-07 | 123 | 1,053 |
| 2023-08 | 127 | 1,373 |
| 2023-09 | 152 | 1,290 |
| 2023-10 | 148 | 1,352 |
| 2023-11 | 103 | 1,154 |
| 2023-12 | 118 | 1,078 |
| 2024-01 | 126 | 1,044 |
| 2024-02 | 128 | 1,010 |
| 2024-03 | 136 | 1,132 |
| 2024-04 | 113 | 1,154 |
| 2024-05 | 122 | 1,303 |
| 2024-06 | 115 | 1,288 |
| 2024-07 | 159 | 1,244 |
| 2024-08 | 134 | 1,156 |
| 2024-09 | 134 | 1,153 |
| 2024-10 | 130 | 1,188 |
| 2024-11 | 119 | 1,113 |
| 2024-12 | 98 | 1,018 |
| 2025-01 | 98 | 1,004 |
| 2025-02 | 95 | 902 |
| 2025-03 | 121 | 1,214 |
| 2025-04 | 136 | 1,143 |
| 2025-05 | 121 | 1,300 |
| 2025-06 | 131 | 1,151 |
| 2025-07 | 105 | 1,261 |
| 2025-08 | 105 | 1,193 |
| 2025-09 | 119 | 1,158 |
| 2025-10 | 113 | 1,260 |
| 2025-11 | 107 | 1,133 |
| 2025-12 | 105 | 1,054 |
