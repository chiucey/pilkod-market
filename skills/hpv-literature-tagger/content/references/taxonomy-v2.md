# Taxonomy V2

Use exactly this 8-subdirectory system. Every article must have all 8 fields.

## 1. age

Parent: `participants`

Format: `number1,number2` or single median value.

- `number1` = minimum age.
- `number2` = maximum age.

Rules:

- If only a minimum age is given, keep the trailing comma: `>=18 years` -> `18,`.
- If only a maximum age is given, keep the leading comma: `<=12 years` -> `,12`.
- If both minimum and maximum ages are given: `18-25 years` -> `18,25`.
- If only median age is given: `median age 18` -> `18` with no comma.
- Convert months to years: `6 months` -> `0.5`.
- Do not infer unreported minimum age. `12 years and younger` -> `,12`, not `0,12`.
- If only age-group incidence/prevalence is shown and enrollment age cannot be inferred, use `na,na`.
- If age cannot be identified, use `na,na`.

## 2. population

Parent: `participants`

Format: `abbr1[,abbr1...],abbr2`

`abbr1` is the population tag set and can be multi-select. `abbr2` is the source/setting tag.

### abbr1 allowed values

- `g`: ordinary male/general male
- `msm`: men who have sex with men
- `msw`: men who have sex with women; do not use for generic mixed-sex studies
- `uk`: other sex/gender types, including transgender or other unclear types
- `children`: >=6 and <12 years
- `adolescent`: >=12 and <18 years
- `hcp`: health care provider
- `parents`: parents/guardians
- `staff`: school/institution staff
- `bi`: bisexual
- `female`: female
- `HIV`: HIV
- `diabetes`: diabetes
- `sle`: systemic lupus erythematosus
- `ckd`: chronic kidney disease or kidney failure on hemodialysis
- `students`: all students
- `PCa`: prostate cancer
- `BPH`: benign prostatic hyperplasia
- `les`: lesbian
- `syphilis`: syphilis
- `GNH`: gonorrhea
- `HSV`: herpes simplex virus
- `HTN`: hypertension
- `CAD`: coronary artery disease
- `Obesity`: obesity
- `HLD`: hyperlipidemia
- `PID`: primary immunodeficiency
- `MC`: circumcision in male
- `HBV`: hepatitis B
- `CT`: Chlamydia trachomatis
- `PLWH`: people living with HIV
- `SPN`: synchronous primary neoplasia
- `P`: pregnancy
- `Neo`: neonate
- `CDH`: chronic disease history
- `thyroid cancer`: thyroid cancer
- `EBV`: Epstein-Barr virus; human herpesvirus 4; not HSV
- `CAT`: cancer-associated thrombosis
- `PNI`: perineural invasion
- `COPD`: chronic obstructive pulmonary disease
- `IS`: ischemic stroke
- `Liver disease`: liver disease
- `Renal disease`: renal disease
- `AMI`: acute myocardial infarction
- `HF`: heart failure
- `Peripheral vascular disease`: peripheral vascular disease
- `Cerebrovascular disease`: cerebrovascular disease
- `Dementia`: dementia
- `CLRD`: chronic lower respiratory disease
- `CTD`: connective tissue disease
- `PUD`: peptic ulcer disease
- `Diabetes mellitus with complications`: diabetes with complications
- `HP`: hemiplegia
- `Malignancy`: malignancy, only when no specific condition tag covers the disease
- `Metastatic cancer`: metastatic cancer
- `Psych dis`: psychiatric disorder
- `RF`: respiratory failure
- `Tracheotomy`: tracheotomy
- `FSWs`: female sex workers
- `depression`: depression
- `stroke`: stroke
- `Alcohol-related illness`: alcohol-related illness
- `AID`: autoimmune disease
- `psoriasis`: psoriasis
- `osteoporosis`: osteoporosis
- `ischemic heart disease`: ischemic heart disease
- `TB`: tuberculosis
- `na`: none of the listed populations apply

Only add new special-disease population tags after human confirmation.

### abbr2 allowed values

- `cl`: clinical setting
- `co`: community setting. Health examination and screening belong to `co`.
- `na`: not applicable or unidentifiable, especially for meta/review/model unless the article is clearly based on an original clinical/community population.

Correction rules:

- Mixed male/female studies should include `g,female`, not `msw`.
- Do not use `msw` unless the study explicitly concerns men who have sex with women or heterosexual male sexual behavior.
- Do not duplicate a disease in population if that disease is already captured specifically in condition. Example: penile cancer -> condition `4`; population should usually be `g,na`, not `g,Malignancy,na`.
- For meta, review, and model, population setting usually ends with `na`.

## 3. ethnicity/region

Parent: `participants`

Format: `abbr3,abbr4`

### abbr3 region

- `c`: within mainland China/China domestic data or China-focused content
- `y`: no China domestic data but East Asia is included
- `n`: neither China domestic nor East Asia
- `na`: cannot identify

### abbr4 center type

- `m`: multicenter
- `s`: single-center
- `na`: not applicable or cannot identify

Correction rules:

- `m/s` applies mainly to original studies. For meta/review/model, usually use `na` for abbr4.
- If a review includes or discusses China data substantially, abbr3 may be `c`, but abbr4 is still usually `na`.

## 4. type/exposure

Parent: `intervention`

Second-level labels: `type`, `exposure`

Format: `abbr5[,abbr5...],number8`

### abbr5 study type allowed values

`type` must never be `na`.

- `cross`: cross-sectional study
- `cho`: cohort study
- `casec`: case-control study
- `caser`: case report or case series
- `meta`: meta-analysis
- `rev`: review
- `mec`: mechanism study
- `resp`: retrospective study
- `rct`: randomized controlled clinical trial
- `nrct`: clinical study without randomization or control
- `model`: model study
- `guide`: guideline
- `consensus`: consensus
- `prospective`: prospective study
- `implementation`: implementation science
- `qualitative study`: qualitative study

Rules:

- Distinguish `rev` and `meta`: systematic review with meta-analysis -> `meta`; review without meta-analysis -> `rev`.
- Multiple types may apply: `rct,implementation`, `rev,mec`, `prospective,cross`.
- HIV is never part of `type/exposure`; it belongs to population.

### number8 exposure allowed values

Use numbers only, not text.

- `1`: g4
- `2`: g9
- `3`: g4 & g9
- `4`: other & g4
- `5`: other & g9
- `6`: not distinguished / all vaccine types / vaccine data not separable / other & g9g4
- `7`: na / not vaccine-related / no applicable exposure

Examples:

- `cross,7`
- `meta,7`
- `resp,6`
- `rev,mec,6`
- `nrct,prospective,2`

## 5. condition/relate disease

Parent: `condition`

Second-level label: `relate disease`

Format: `number5[,number5...]`

Allowed values:

- `0`: cannot distinguish any related disease
- `0.5`: wart, but explicitly not genital warts
- `1`: Genital warts
- `2`: Anal cancer
- `2.1`: Anal adenocarcinoma
- `2.2`: anal canal cancer
- `2.5`: AIN
- `3`: HPV infection
- `4`: Penile cancer
- `5`: Head and neck cancer
- `5.1`: Oropharyngeal cancer
- `5.2`: nasopharynx cancer
- `5.3`: tongue cancer
- `5.4`: laryngocarcinoma
- `5.5`: esophagus cancer
- `5.6`: cheilcacinoma
- `5.7`: oral cancer
- `5.8`: tonsillar cancer
- `6`: Recurrent respiratory papillomatosis
- `7`: Inferility
- `8`: vaccination, meaning studies of vaccinated populations or vaccination intention
- `8.1`: strategy, meaning research under vaccination/screening/implementation strategies
- `9`: Bladder Cancer
- `10`: prostate cancer

Rules:

- HPV infection, HPV genotype, or HPV-caused disease usually requires adding `3`.
- If a child/subtype is tagged, also tag the parent: `5,5.1`; `2,2.5`.
- Do not tag diseases mentioned only as background in the introduction when not part of the study object, results, or main analysis.
- Vaccination intention or vaccinated-population research -> `8`.
- Strategy studies -> `8.1`.
- If condition is `0`, other disease-related fields may stay `na` where applicable.

## 6. outcome

Parent: `outcome`

Second-level label: `prevalence/incidence/burden`

Format: `abbr6[,abbr6...]`

Allowed values:

- `pre`: prevalence
- `in`: incidence
- `or`: odds ratio
- `rr`: relative risk
- `pi`: persistent infection
- `gen`: genotype
- `hr`: hazard ratio or Cox regression
- `dr`: death rate/mortality
- `safety`: safety
- `rein`: recurrence rate
- `psy`: psychological outcomes
- `cost`: cost-related
- `clear`: clearance rate
- `sur`: survival-related
- `imm`: immune-related
- `qlife`: quality-of-life related
- `kap`: vaccine knowledge, attitude, practice, willingness, acceptability
- `vcr`: vaccine coverage rate / vaccination rate / uptake rate
- `recommendation`: recommendation
- `concern`: vaccine concerns, hesitancy, barriers, worries
- `avertcases`: averted/prevented cases
- `policies`: policies
- `effectiveness`: real-world effectiveness
- `efficacy`: clinical trial efficacy
- `fertility`: fertility/reproductive outcomes
- `na`: no recognizable outcome

Rules:

- Do not under-tag outcomes. Include multiple outcome tags when central to the article.
- `Risk ratio`, `rate ratio`, and `relative risk` all map to `rr`.
- `prevalence ratios` still map to `pre`; if an explicit ratio measure is analyzed, also consider `rr` or `or` based on the metric.
- Use `efficacy` for clinical trial efficacy; use `effectiveness` for real-world/observational effectiveness.
- Outcomes must be core content or results, not only background statements.

## 7. sample'size

Parent and second-level label: `sample'size`

Format: `number6`

Rules:

- Fill only the number of male participants.
- If all participants are male, fill total sample size.
- If total and female counts are given, calculate male count = total - female count.
- If male count cannot be separated, use `na`.
- For meta/review/model, use `na` unless the article explicitly reports male sample size.

## 8. time

Parent: `time`

Second-level label: `Start time, period`

Format: `number7,abbr7`

- `number7`: study/data start year, such as `2004`.
- `abbr7`: study duration/period.

Allowed period units/examples:

- `0`: single-year or no duration in a cross-sectional point estimate
- `1d`: one day
- `1m`: one month
- `1y`: one year
- compound decimals such as `5.5y` are allowed when needed
- `na`: not identifiable

Rules:

- Missing time -> `na,na`.
- Single-year cross-sectional data -> `YYYY,0`.
- Same-year date ranges -> calculate months or days.
- Any cross-year range -> prioritize year subtraction: Dec 2021 to Jun 2022 -> `2021,1y`.
- Multiple time periods -> earliest start year plus sum of all durations.
