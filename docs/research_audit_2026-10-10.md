# California Elder Fraud Observatory — reproducibility and audit note (October 10, 2026)

## Basis and scope
Verified against supplied `seniors_clean (3).ipynb`, `Chandran-MolesLaia_paper.pdf`, `master_soc242 (1).csv`, `county_master_verified (1).csv`, `county_annual_65plus_population_2019_2024.csv`, and `statewide_trend_rates_CORRECTED (1).csv`. Independent local numerical re-fits were performed for the pooled point-estimate model and all 58 county trend/null pairs under two censoring intervals. **This is not a full top-to-bottom notebook execution or a validation of every manuscript result.** Original paper, notebook, and input CSVs were not modified.

## 1. Sample integrity — verified
Six fiscal years, 58 counties, 4,176 county-month records: **2,901 exact (including 328 zeros), 1,195 suppressed, 80 completely blank**; 4,096 likelihood-eligible records. All necessary county predictors and annual population entries merge without missing values. Smallest published positive count in the relevant financial-abuse field is **11**, supporting (but not officially confirming) an inferred primary suppression interval of 1–10.

## 2. Statewide rate discrepancy — EXPLAINED; wording correction needed
In FY 2019–20, the midpoint count is 47,561; full 65+ population 5,486,041; rate **86.694576**. No fully blank county-months in that fiscal year.

In FY 2024–25, the midpoint count is 76,258; full 65+ population **6,158,371**; 6 missing county-months (Inyo 2; Lake, San Mateo, Santa Barbara, Sierra 1 each). Dividing the **observed numerator by the full-year senior population** gives **123.828201**, an increase of **42.83%** from 2019–20. This is the manuscript's 123.8/42.8 figure. However, calling the rate `annualized` is misleading: the numerator does *not* impute missing months.

The frozen statewide CSV gives the same FY 2024–25 midpoint numerator but a smaller *coverage-weighted senior exposure* of **6,138,991.4167**; the result is **124.219102**, an increase of **43.28%**. The two rates answer somewhat different coverage questions. Neither is a wholly invented number. It is misleading to assert that both are the same statewide rate.

A third approach, extrapolating each county's observed monthly rate to 12 months and dividing by the full 6,158,371 population, gives **124.128162** (not 124.2191). This demonstrates why the precise annualization method must be named.

**Suggested manuscript correction (without silently changing numerical results):** replace `midpoint annualized reported allegation rate` with `midpoint reported allegation count per 10,000 adults age 65 and older, calculated using observed months and the full-year population denominator`; add: `Six county-month reports were fully blank in FY2024–25, so this descriptive rate does not impute allegations for those missing months. Coverage-adjusted exposure produces a slightly higher rate (124.2).` Consider using the consistent coverage-adjusted convention as the *primary* rate instead, but only after explicitly choosing and updating the website, manuscript, and frozen files together.

## 3. Pooled interval-censored NB point estimates — REPRODUCED FIT, NOT ORIGINAL VALUES
Data preparation from notebook cells 456–457 and five optimizer starts from cell 383 now execute locally. All five starts converge to roughly **negative log-likelihood 13,330.30795 and alpha 0.187557**. The notebook's previous reported output is **negative log-likelihood 13,346.4609 and alpha 0.190138**. Thus we **cannot claim exact reproduction of the published association model**. The discrepancy may stem from different source versions/design matrices or older fitted outputs; it needs reconciliation. The original 500 county bootstrap runs and confidence limits have **not** been reproduced here. Do not substitute the new coefficients into the paper without doing that full investigation.

## 4. County trend sensitivity — newly reproduced
Using the notebook's common-calendar-time likelihood and BH-adjusted likelihood-ratio tests:

| Suppression interval | Increasing | No clear trend | Decreasing | Successful trend/null fits |
|---|---:|---:|---:|---:|
| 1–10 (primary) | 34 | 23 | 1 | 58/58 and 58/58 |
| 0–11 (hypothetical wider) | 33 | 24 | 1 | 58/58 and 58/58 |

Changes under wider interval: **Glenn and Mono** from increasing to no clear trend; **Lassen** from no clear trend to increasing. Nevada is decreasing under both of these censoring assumptions, but the pre-existing notebook HAC sensitivity suggests Nevada's decrease is **not** robust to some autocorrelation adjustments. These are different forms of uncertainty and should both be disclosed.

The alternative interval **0–11 is hypothetical**, not evidence that suppressed values actually include 0 or 11. On the primary 1–10 run, Alpine's alpha hits **10**, while Calaveras and Glenn hit the **0.0001** alpha floor. Under 0–11, Calaveras, Del Norte, Lassen, Mariposa, Trinity, and Yuba hit a bound. A numerical success flag does not establish unconstrained optimization or valid asymptotic significance at such boundaries.

## 5. Manuscript and inference changes recommended
- **I1 (autocorrelation and seasonality):** already tested in later notebook cells (seasonality, HAC, block-bootstrap pilot), but paper does not clearly summarize county-classification sensitivity. In particular, Nevada must not be presented as robust across all specifications. Do not present original BH model p-values as autocorrelation-robust.
- **I2:** qualify `Multiple optimization starting points` to the **pooled association model**. The county trend fits use one start; report bound-hitting counties as a limitation.
- **I3:** only `county_trend_censored_nb_COMMON_TIME.csv` represents the intended 34/23/1 primary classification; clearly mark older `FINAL` or exploratory files as superseded. This audit outputs a new, explicitly named sensitivity file.
- **I4:** the statement that **26 of 58** exploratory classifications changed should be identified as *the earlier expected-rate model*, not the final censored NB model. Whether that exploratory figure survives updated denominators remains unverified. Consider removing the numeric claim if its provenance cannot be demonstrated.
- **I5:** the interval is empirically inferred, not CDSS documented. The new 0–11 test finds three county-classification changes; report that transparently.
- **I6:** county annual percent change currently lacks uncertainty intervals; avoid claiming the figure itself displays interval estimates. Plot/display uncertainty or explicitly label it as point-estimate only. Alpine extreme estimate warrants special caution.
- **I7:** five predictor CIs include 1, which means evidence is inconclusive, **not** proof of no association. Re-standardizing within each bootstrap replicate is a methodological choice that alters the scale of resulting IRRs; assess before revising published 95% CIs.

## 6. Still unresolved before declaring the paper fully reproducible
1. Why the new pooled likelihood/alpha differ from saved earlier outputs; confirm original data/version, design matrix, and coefficients; then rerun 500 county-resampled bootstrap fits.
2. Reproduce or remove the 26/58 exploratory sensitivity statistic and confirm provenance.
3. Confirm/qualify claimed ACS population `validation against county and statewide totals` with saved checks; confirm minimum positive 11 has now been programmatically verified.
4. Decide the statewide missing-month exposure convention and align manuscript, website, and downloaded datasets.
5. Evaluate whether optimization-bound counties need profile likelihood, multi-start fits, or classification caveats. Model sensitivity analysis is not proof of correctness under alternate assumptions.
6. Publication-quality chart uncertainty, careful reference/citation checks, and final website-to-paper consistency remain outside this local rerun.

## Output files
- `association_multistart_verified.csv`: five independent pooled-model starts.
- `association_point_estimates_verified.csv`: coefficients from the best *newly reconstructed* pooled model (do not replace submitted results automatically).
- `county_trend_suppression_interval_sensitivity_verified.csv`: two complete 58-county model runs, including q values, alpha, and convergence.
- `run_reconciliation.py` / `reproduce_trends.py`: runnable local scripts (require the supplied source CSVs in the same `/mnt/data` directory).

**Bottom line:** the suppression-aware trend result is locally reproducible and somewhat sensitive in individual counties; the statewide discrepancy is explainable but its label needs correction; the association model remains a genuine outstanding reproduction discrepancy. Do not characterize the entire analysis as independently reproduced yet.
