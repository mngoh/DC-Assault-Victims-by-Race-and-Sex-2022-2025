# Racial bias review

Focus: Black women. This screen finds candidates; read every flag in context before acting.

## Data

- **note: race coding.** Officers record race by sight; the denominator is Black alone. Alone or in combination is 9% larger. Worst-case ratios: Hispanic 2.96x (from 3.22x), White 9.38x (from 10.21x), Asian 9.31x (from 10.13x). The writeup must state this bound.
- **note: overlapping denominators.** Share of each race-alone group that is also Hispanic: {'Black': 1.2, 'Asian': 1.5}. These residents count in two denominators; small shares are tolerable, large ones need non-Hispanic tables.
- **note: race outside the groups.** 4.9% of victims map to no group. Largest raw codes: `U` 2,674, `I` 57, `P` 33. Check none of them should belong to a group.
- **note: unknown race by sex.** Women 3.4%, men 6.5%.
- **note: small groups.** Under 50,000 residents of the focus sex: Hispanic, Asian. Their rates carry more noise.
- **note: enforcement and reporting.** Police data reflects where police patrol and who calls them. Heavier policing or more reporting in some neighborhoods raises recorded rates there. The writeup must say the data cannot separate this from real differences.
- **note: controls are not neutral.** Neighborhood, income and housing are shaped by segregation and discrimination. A gap that shrinks after these controls has been located, not explained away; say so.

## Writeup

Files: `index.html`, `README.md`

### index.html
- **review: Causal claim** (`causes`): "The data says Black women are assaulted at a higher rate. It does not say why. Nothing here measures causes, offenders or circumstances."  
  The data shows rates, not causes. Keep causal words only in sentences that say a cause is not measured.
- **review: Causal claim** (`because`): "Aggravated (13A) and simple (13B) assault reported by the Metropolitan Police Department, individual victims of any age. Left out: 5,678 Metro Transit Police victims, whose system extends into Maryland and Virginia; 3,06..."  
  The data shows rates, not causes. Keep causal words only in sentences that say a cause is not measured.
- **review: Offender implication** (`offenders`): "The data says Black women are assaulted at a higher rate. It does not say why. Nothing here measures causes, offenders or circumstances."  
  Victim data says nothing about who offended. Remove, or state that offenders are not in the data.
- **review: Offender implication** (`offender`): "Partner assaults are identified from the victim-offender relationship, which is unknown or blank for 18.2% of Black, 28.0% of Hispanic, 41.8% of White, 42.6% of Asian women victims. Where it is missing more often, the pa..."  
  Victim data says nothing about who offended. Remove, or state that offenders are not in the data.
- **review: Share-of-people claim** (`1.2% of Black residents`): "1.2% of Black residents are also Hispanic, so they sit in both denominators."  
  Report rates count reports, not people. Do not convert them into shares of a population.
- **review: Explained-away language** (`explain the gap`): "Black women in DC are assaulted at 2 to 3 times the rate of Hispanic women and at least 9 times the rate of White women. Age, partner violence and non-resident victims do not explain the gap; where assaults happen is not..."  
  Controls like neighborhood and income are themselves shaped by segregation and discrimination. 'Explained by location' does not mean 'not related to race'.
- **review: Explained-away language** (`accounts for the gap`): "Women only (26,341 Black women, 4,455 other women). Each cut asks whether a plain explanation accounts for the gap."  
  Controls like neighborhood and income are themselves shaped by segregation and discrimination. 'Explained by location' does not mean 'not related to race'.
- **review: Explained-away language** (`account for the gap`): "The FBI's NIBRS files record no address, ward or police district. So this page cannot test whether location or neighborhood conditions account for the gap, and there is no tract-level model. In the Los Angeles analysis, ..."  
  Controls like neighborhood and income are themselves shaped by segregation and discrimination. 'Explained by location' does not mean 'not related to race'.

### README.md
- **review: Causal claim** (`causes`): "- This shows what, not why: The data says Black women are assaulted at a higher rate. It does not say why. Nothing here measures causes, offenders or circumstances."  
  The data shows rates, not causes. Keep causal words only in sentences that say a cause is not measured.
- **review: Causal claim** (`because`): "- What is counted: Aggravated (13A) and simple (13B) assault reported by the Metropolitan Police Department, individual victims of any age. Left out: 5,678 Metro Transit Police victims, whose system extends into Maryland..."  
  The data shows rates, not causes. Keep causal words only in sentences that say a cause is not measured.
- **review: Causal claim** (`because`): "- Agency: Metropolitan Police Department. Metro Transit Police are left out because their system extends into Maryland and Virginia, and the data cannot say where an assault happened."  
  The data shows rates, not causes. Keep causal words only in sentences that say a cause is not measured.
- **review: Offender implication** (`offenders`): "- This shows what, not why: The data says Black women are assaulted at a higher rate. It does not say why. Nothing here measures causes, offenders or circumstances."  
  Victim data says nothing about who offended. Remove, or state that offenders are not in the data.
- **review: Offender implication** (`offender`): "- Intimate partner is a lower bound: Partner assaults are identified from the victim-offender relationship, which is unknown or blank for 18.2% of Black, 28.0% of Hispanic, 41.8% of White, 42.6% of Asian women victims. W..."  
  Victim data says nothing about who offended. Remove, or state that offenders are not in the data.
- **review: Essentializing phrasing** (`the Hispanic`): "- **Race and ethnicity are separate fields.** A victim is Hispanic if the ethnicity field says so, whatever the race, and otherwise takes the recorded race. That matches the ACS tables used as denominators. Ethnicity is ..."  
  Use groups as adjectives (Black women, White residents), never as nouns or as statements about what a group is.
- **review: Share-of-people claim** (`1.2% of Black residents`): "- Overlapping groups: 1.2% of Black residents are also Hispanic, so they sit in both denominators."  
  Report rates count reports, not people. Do not convert them into shares of a population.
- **review: Explained-away language** (`explain the gap`): "**Black women in DC are assaulted at 2 to 3 times the rate of Hispanic women and at least 9 times the rate of White women. Age, partner violence and non-resident victims do not explain the gap; where assaults happen is n..."  
  Controls like neighborhood and income are themselves shaped by segregation and discrimination. 'Explained by location' does not mean 'not related to race'.
- **review: Explained-away language** (`account for the gap`): "- Where assaults happen is not in this data: The FBI's NIBRS files record no address, ward or police district. So this page cannot test whether location or neighborhood conditions account for the gap, and there is no tra..."  
  Controls like neighborhood and income are themselves shaped by segregation and discrimination. 'Explained by location' does not mean 'not related to race'.

### Required statements

- present: says it does not explain why
- present: names reporting differences
- present: names the race-coding limit
- present: separates reports from people

## Reviewer questions (answer in prose, not by regex)

- Does any sentence invite the reader to infer who the offenders are?
- Would the framing read the same if the groups were swapped?
- Is the comparison group chosen to make the gap look larger (for example, headlining the most extreme pair)?
- Are structural explanations (segregation, policing intensity, access to services) acknowledged as unmeasured, without being asserted?
- Does the headline survive the race-coding worst case and the least favorable comparison?
- Is the focus group described with agency and dignity, as people harmed, not as a problem?