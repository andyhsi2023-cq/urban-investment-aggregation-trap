# Comprehensive Data Audit Report — Full Draft v4

**Audit Date**: 2026-03-21
**Auditor**: Data Analyst Agent
**Target**: Nature main journal submission
**Manuscript**: `full_draft_v4.md` (Simpson's paradox masks declining returns on urban investment worldwide)

---

## Executive Summary

| Category | PASS | CAUTION | FAIL | Total |
|----------|:----:|:-------:|:----:|:-----:|
| Audit 1: Data Source Authenticity | 13 | 2 | 0 | 15 |
| Audit 2: Statistical Verification | 39 | 0 | 0 | 39 |
| Audit 3: Data Sufficiency | 4 | 2 | 0 | 6 |
| Audit 4: Data Quality Disclosure | 4 | 2 | 1 | 7 |
| Audit 5: Reproducibility | 2 | 1 | 0 | 3 |
| Audit 6: Coverage Claims | 5 | 2 | 0 | 7 |
| **Total** | **67** | **9** | **1** | **77** |

**Overall Data Credibility Score: 8.0 / 10**

The data infrastructure is solid. All 39 key statistics in the paper match their source analysis reports with appropriate rounding. Two issues require attention before submission: (1) the "158 countries" claim is misleading because only 144 countries have MUQ observations; (2) the stated N=2,629 is the nominal MUQ count, but the Simpson's Paradox tests were run on real (deflated) MUQ with N~3,329 observations. Both issues require minor textual corrections, not re-analysis.

---

## Audit 1: Data Source Authenticity Verification

### Raw Data Files (`02-data/raw/`)

| File | Size | Lines | Cols | Key Dimensions | Verdict |
|------|-----:|------:|-----:|----------------|---------|
| world_bank_all_countries.csv | 2,812 KB | 13,889 | 18 | 158+ countries, multi-decade | PASS |
| penn_world_table.csv | 3,913 KB | 12,811 | 26 | PWT 10.01 format confirmed | PASS |
| china_national_real_data_v2.csv | 22 KB | 36 | 51 | 35 years national time series | PASS |
| china_provincial_real_data.csv | 71 KB | 590 | 10 | ~31 provinces x ~19 years | PASS |
| us_msa_data.csv | 318 KB | 922 | 26 | 921 MSAs (header + 921 rows) | PASS |
| japan_prefecture_data.csv | 12 KB | 48 | 21 | 47 prefectures | PASS |
| brazil_municipio_data.csv | 612 KB | 5,571 | 11 | 5,570 municipios | PASS |
| eu_nuts3_data.csv | 67 KB | 1,261 | 7 | 1,260 NUTS-3 regions | PASS |
| bis_property_prices.csv | 3,045 KB | 40,258 | 8 | BIS residential property prices | PASS |
| oecd_gfcf_by_asset_real.csv | 3,249 KB | 6,601 | 46 | OECD GFCF by asset type | PASS |
| un_population.csv | 3,723 KB | 14,171 | 21 | UN World Population Prospects | PASS |

**Data Provenance**: All raw files are present and have plausible sizes for their claimed sources. The World Bank, PWT, Census/BEA, BIS, OECD, and UN data appear to have been downloaded via API or bulk CSV download. The `data_acquisition_report.txt` and `data_provenance.md` document the download process.

### Processed Data Files (`02-data/processed/`)

| File | Shape | Key Dimensions | Verified Against | Verdict |
|------|-------|----------------|------------------|---------|
| global_q_revised_panel.csv | 10,112 x 31 | 158 countries, 1960-2023 | WB + PWT merge | PASS |
| china_city_panel_real.csv | 10,200 x 44 | 300 cities, 1990-2023 | China City Database | PASS |
| us_msa_muq_panel.csv | 11,681 x 33 | 921 MSAs, 2010-2022 | Census ACS + BEA | CAUTION |
| oecd_construction_gdp_panel.csv | 10,112 x 39 | Same as global panel | OECD supplement | PASS |

**CAUTION on US MSA**: The panel has 1046 unique CBSA codes in the raw Census download (varying by year: 955 in 2010, 929-945 in middle years, 939 in 2022), but after merging with BEA county-level GDP and applying CBSA delineation, 921 MSAs are retained. This merge-induced attrition should be documented in Methods.

**CAUTION on global panel**: The panel contains 158 country codes but only 144 have at least one valid MUQ observation. The 14 countries without MUQ include small island states (KIR, MHL, PLW, TON, VUT, SLB), territories (GRL, NCL, PYF, PRI), and countries with data gaps (CUB, LBY, TLS, UKR). See Audit 6 for implications.

---

## Audit 2: Key Statistical Quantity Verification

Every key statistic in the paper was traced to its source analysis report. All 39 verified quantities match with appropriate rounding.

### Simpson's Paradox (source: `muq_real_correction_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| LI rho | -0.150 | -0.1499 | PASS |
| LI p | 0.002 | 0.001557 | PASS |
| LMI rho | -0.122 | -0.1223 | PASS |
| LMI p | 0.002 | 0.002006 | PASS |
| UMI rho | -0.099 | -0.0991 | PASS |
| UMI p | 0.003 | 0.002626 | PASS |
| HI rho | -0.013 | -0.0131 | PASS |
| HI p | 0.633 | 0.633466 | PASS |
| Pooled rho | +0.04 | +0.0358 | PASS |
| Pooled p | 0.038 | 0.038257 | PASS |

### Scaling Gap (sources: `scaling_law_ocr_report.txt`, `scaling_gap_crossnational_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| beta_V China | 1.34 | 1.3390 | PASS |
| beta_V R2 | 0.82 | 0.8195 | PASS |
| beta_K China | 0.86 | 0.8610 | PASS |
| beta_K R2 | 0.63 | 0.6317 | PASS |
| beta_GDP China | 1.04 | 1.0377 | PASS |
| beta_GDP R2 | 0.69 | 0.6871 | PASS |
| Delta_beta_VK China | 0.48 | 0.4780 | PASS |
| Delta_beta_VGDP China | 0.30 | 0.3014 | PASS |
| Delta_beta_VGDP US | 0.086 | 0.0861 | PASS |
| Delta_beta_VGDP US p | 5e-11 | 4.79e-11 | PASS |

### City-Level MUQ (source: `city_muq_distribution_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| beta(FAI/GDP) | -2.23 | -2.2342 | PASS |
| 82.2% cities MUQ < 1 | 175/213 | 175/213 | PASS |
| First-tier MUQ | 7.46 | 7.4565 | PASS |
| Fourth-fifth-tier MUQ | 0.20 | 0.1951 | PASS |

### US MSA (source: `us_msa_muq_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| beta(hu_growth) | +2.75 | +2.7458 | PASS |

### Unified Measure & Mechanical Correlation (source: `mechanical_correlation_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| China DeltaV/GDP beta | -0.37 | -0.3669 | PASS |
| China DeltaV/GDP p | 0.019 | 0.01935 | PASS |
| US DeltaV/GDP beta | +1.78 | +1.7845 | PASS |
| MC simulated beta | -0.29 | -0.2945 | PASS |
| MC observed beta | -2.26 | -2.2571 | PASS |

### DeltaV Decomposition (source: `china_dv_decomposition_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| China price effect | 53% | 53.4% (aggregate) | PASS |
| US price effect | 87% | 86.9% (mean) | PASS |

### Carbon Estimates (source: `carbon_uncertainty_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| Cumulative carbon | 5.3 GtCO2 | MC median 5.28 GtCO2 | PASS |
| 90% CI | [4.3, 6.3] | [4.34, 6.31] | PASS |

### DID (source: `three_red_lines_did_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| TWFE Q beta_DID | -0.089 | -0.0890 | PASS |
| TWFE Q p | <0.001 | 0.000053 | PASS |

### Robustness (sources: `robustness_batch_report.txt`, `simpsons_paradox_robustness_report.txt`)

| Statistic | Paper Value | Report Value | Match |
|-----------|-------------|-------------|:-----:|
| Balanced panel beta | -4.55 | -4.5491 | PASS |
| LOO direction | 47/47 | 47/47 | PASS |
| FDR correction | 22/25 zero sign reversals | 22/25 | PASS |

---

## Audit 3: Data Sufficiency Assessment

| Claim | Required Data | Actual Data | Verdict |
|-------|--------------|-------------|---------|
| Global Simpson's Paradox | Multi-country multi-year MUQ | 144 countries, ~3,329 real MUQ obs | **PASS** |
| City-level MUQ gradient | 100+ cities | 455 city-year obs (213 cities in 2016) | **PASS** |
| China-US sign reversal | Comparable data for both | China 455 + US 10,760 | **PASS** |
| Scaling Gap cross-national | 3+ countries with V data | China + US (full); Japan/EU/Brazil GDP only | **CAUTION** |
| Carbon emission CI | Reliable CI parameters | Single-source calibration + modeled decay | **CAUTION** |
| 10-country forward | Complete MUQ time series | India 5 obs, Indonesia 6 obs | **PASS** (paper uses cautious language) |

### CAUTION Details

**Scaling Gap cross-national**: Only China and the US have city-level asset value (V) data. Japan, EU, and Brazil contribute only GDP scaling (beta_GDP). The paper correctly labels Delta_beta_VGDP as "cross-nationally comparable" and reports full V-K gap only for China. However, the claim "The same ordering holds across 921 US metropolitan areas" could be strengthened if the US also had independent K data rather than using housing units as a K proxy.

**Carbon emission CI**: The carbon intensity decay model (1.20 to 0.60 tCO2/10,000 yuan over 2000-2024) is calibrated from a single primary source (China Building Energy Conservation Association 2022) with cross-checks against IEA. The Monte Carlo propagation is sound (10,000 iterations, three independent uncertainty sources), but the time-varying CI is modeled rather than year-by-year measured. The sensitivity analysis adequately bounds this uncertainty (3.6-6.6 GtCO2 with +/-30% CI variation). The paper's language ("approximately 5.3 GtCO2") is appropriately hedged.

---

## Audit 4: Data Quality Issue Disclosure

| Issue | Disclosed in Paper? | Verdict |
|-------|:-------------------:|---------|
| 1. China FAI 2017+ discontinuation | Yes (Methods M7: "FAI after 2017 was estimated from published growth rates due to discontinuation of the total-society series") | **PASS** |
| 2. City house price coverage variation (2011: 20 vs 2016: 213 cities) | Yes (Methods M9: references balanced sub-panels; the compositional bias concern is explicitly addressed) | **PASS** |
| 3. ACS 5-year rolling average overlap | Yes (Methods M9: "Newey-West standard errors (lag = 4, matching the ACS 5-year overlap)") | **PASS** |
| 4. Seven V calibration variants | Yes (Methods M1: detailed description of seven calibrations with Dirichlet weights; Discussion limitation 1: "seven calibration variants bound but do not resolve uncertainty") | **PASS** |
| 5. PWT data cutoff (2019 for some countries) | Not explicitly disclosed | **CAUTION** |
| 6. Carbon intensity time-varying assumption | Yes (Methods M5: "CI was modelled as an exponential decay...calibrated to construction-sector emission factors") | **PASS** |
| 7. India/Indonesia sparse MUQ data in 10-country panel | Not explicitly disclosed | **FAIL** |

### CAUTION: PWT data cutoff

The PWT 10.01 data ends at 2019 for most countries. The global panel extends to 2023 for some variables (via World Bank WDI), but the MUQ calculation requires `rnna` from PWT which stops at 2019. This means the most recent 4 years of data for some countries are unavailable. This should be noted in Methods M7.

### FAIL: India/Indonesia data sparsity

The ten-country trajectory analysis (Fig. 5) includes India with only 5 MUQ observations (1993-2018) and Indonesia with only 6 observations (1970-1997). Indonesia's data ends 29 years before the present. The paper makes forward-looking claims about India, Vietnam, and Indonesia ("urbanisation rates of 35-58%, are in the phase where the scaling gap predicts accelerating efficiency divergence") without noting that India has only 5 data points and Indonesia's data is three decades old. This should be disclosed in the paper, either in the Results description of Fig. 5 or in the Discussion limitations.

**Recommended fix**: Add a sentence such as: "We note that data coverage varies across the ten countries (from 5 observations for India to 44 for China; see Extended Data), and the forward-looking implications for data-sparse countries should be interpreted with appropriate caution."

---

## Audit 5: Reproducibility Check

### Script 1: `90_city_muq_distribution.py`

| Check | Status | Notes |
|-------|--------|-------|
| Input file exists | PASS | `02-data/processed/china_city_panel_real.csv` confirmed |
| Output paths valid | PASS | Report and figure paths use project BASE |
| Random seed fixed | CAUTION | Seed is 42, not 20260321 as stated in Methods |
| Dependencies standard | PASS | pandas, numpy, scipy, statsmodels, sklearn, matplotlib |
| Logic review | PASS | MUQ computed as (V(t) - V(t-1)) / FAI(t), with V = pop x house_price x per_capita_area |

**CAUTION**: The random seed in this script is `np.random.seed(42)`, while the Methods section states "Random seed was fixed at 20260321 for all stochastic procedures." This inconsistency should be resolved. The script does not appear to use stochastic procedures in its core analysis (OLS, quantile regression), so the impact is minimal, but the seed should be unified for consistency.

### Script 2: `96_simpsons_paradox_robustness.py`

| Check | Status | Notes |
|-------|--------|-------|
| Input file exists | PASS | `02-data/processed/global_q_revised_panel.csv` confirmed |
| Output paths valid | PASS | Report path uses BASE |
| Random seed fixed | PASS | No stochastic procedures; no seed needed |
| Dependencies standard | PASS | pandas, numpy, scipy only |
| Logic review | PASS | Spearman correlations, leave-one-out, within-between decomposition |

### Script 3: `102_scaling_gap_crossnational.py`

| Check | Status | Notes |
|-------|--------|-------|
| Input files exist | PASS | All 4 raw data files confirmed present |
| Output paths valid | PASS | Report, figure, and source data paths use PROJECT |
| Random seed fixed | PASS | `np.random.seed(20260321)` -- matches Methods |
| Dependencies standard | PASS | pandas, numpy, statsmodels, scipy, matplotlib |
| Logic review | PASS | OLS with HC1 robust SE for each country's scaling exponents |

---

## Audit 6: Paper Claims vs Actual Data

| Claim | Paper Value | Actual Value | Verdict | Issue |
|-------|------------|-------------|---------|-------|
| Countries in panel | 158 | 158 | PASS | -- |
| Countries with MUQ | "158 countries" (implied) | 144 | **CAUTION** | Paper says "Pooling all 158 countries and 2,629 MUQ observations" but 14 countries have no MUQ |
| MUQ observations | 2,629 | 2,629 (nominal) / ~3,329 (real) | **CAUTION** | Paper's count matches nominal MUQ; tests use real MUQ with higher N |
| Chinese city-year obs | 455 | 455 | PASS | -- |
| US MSA-year obs | 10,760 | 10,760 | PASS | -- |
| US MSAs | 921 | 921 | PASS | -- |
| Chinese cities (scaling) | 248 | 248 | PASS | -- |

### CAUTION: "158 countries" with MUQ

The paper states in multiple places: "across 158 countries" and "Pooling all 158 countries and 2,629 MUQ observations." The natural reading is that all 158 countries contribute MUQ data. In reality, only 144 countries have at least one MUQ observation. The 14 without MUQ are: CUB, GRL, KIR, LBY, MHL, NCL, PLW, PRI, PYF, SLB, TLS, TON, UKR, VUT.

**Recommended fix**: Change "158 countries" to "144 countries" where referring to MUQ analysis, or say "a panel of 158 countries, of which 144 contribute 2,629 MUQ observations."

### CAUTION: Nominal vs Real MUQ observation count

The Methods M2 correctly states that real (deflated) MUQ is used for the Simpson's Paradox tests. However, the real MUQ has ~3,329 valid observations (more than nominal because it can be computed for country-years where GFCF in current USD is unavailable but rnna and basic deflators exist). The paper consistently cites "2,629 MUQ observations" which is the nominal count.

**Recommended fix**: Either (a) report the actual N used in the real MUQ analysis (~3,329), or (b) if the paper intends to use only the 2,629 nominal observations, re-run the Spearman tests on that subset and report updated statistics. Option (a) is preferred as it uses more data.

---

## Detailed CAUTION/FAIL Items and Recommendations

### FAIL-1: India/Indonesia data sparsity undisclosed

**Severity**: Moderate
**Impact**: Affects forward-looking claims about developing economies
**Fix**: Add a note on data coverage heterogeneity in the ten-country analysis. Estimated effort: one sentence addition.

### CAUTION-1: 158 vs 144 countries

**Severity**: Moderate
**Impact**: Misleading sample size claim; Nature reviewers will check
**Fix**: Change wording to "144 countries contributing 2,629 MUQ observations" or "a panel of 158 countries, of which 144 contribute MUQ data." Estimated effort: find-and-replace in 4-5 locations.

### CAUTION-2: Nominal vs real MUQ N

**Severity**: Low-to-Moderate
**Impact**: The Spearman rho values and p-values are correct, but the reported N is wrong
**Fix**: Report the actual real MUQ sample size (~3,329) or re-run on the 2,629 nominal subset. Given that the simpsons_paradox_robustness_report already shows the results are robust across specifications, this is unlikely to change conclusions.

### CAUTION-3: Random seed inconsistency

**Severity**: Low
**Impact**: Reproducibility pedantry; unlikely to affect results
**Fix**: Unify random seed to 20260321 in `90_city_muq_distribution.py` (currently 42). The script's core analyses are deterministic, so this is cosmetic.

### CAUTION-4: PWT data cutoff undisclosed

**Severity**: Low
**Impact**: Minor transparency issue
**Fix**: Add one sentence to Methods M7 noting that PWT 10.01 data extends to 2019.

### CAUTION-5: Scaling Gap limited to two countries with V data

**Severity**: Low
**Impact**: Already acknowledged by using Delta_beta_VGDP as "cross-nationally comparable" metric
**Fix**: No action required; paper handles this appropriately.

### CAUTION-6: US MSA merge attrition

**Severity**: Low
**Impact**: Minor data pipeline documentation
**Fix**: Optional; could note that Census returns ~939-955 MSAs per year and 921 survive the Census-BEA merge.

---

## Data Pipeline Integrity Summary

```
Raw Data Sources              Processed Panels              Analysis Reports
-----------------            ------------------            -----------------
World Bank API     ──┐
PWT 10.01 bulk     ──┤──> global_q_revised_panel.csv ──> muq_real_correction_report.txt
BIS API            ──┘                                    simpsons_paradox_robustness_report.txt

China City DB      ──┐
NBS Yearbooks      ──┤──> china_city_panel_real.csv  ──> city_muq_distribution_report.txt
58.com/Anjuke      ──┘    china_city_real_window.csv ──> scaling_law_ocr_report.txt

Census ACS API     ──┐
BEA CAGDP1 bulk    ──┤──> us_msa_muq_panel.csv      ──> us_msa_muq_report.txt
OMB CBSA file      ──┘                                    us_muq_diagnostics_report.txt

Japan/EU/Brazil    ──────> country-specific files     ──> scaling_gap_crossnational_report.txt
```

All input files for all three audited scripts exist. The pipeline from raw data to processed panels to analysis reports is traceable. No hardcoded data values were found in the audited scripts; all data is read from files.

---

## Final Assessment

| Criterion | Score (1-10) | Notes |
|-----------|:----------:|-------|
| Data authenticity | 9 | All raw files present, plausible sizes, API-sourced |
| Statistical accuracy | 10 | 39/39 statistics verified against source reports |
| Data sufficiency | 7 | Core claims well-supported; scaling gap and carbon CI have inherent limitations |
| Transparency | 7 | Most issues disclosed; 158-vs-144 and India/Indonesia gaps need fixing |
| Reproducibility | 8 | Scripts exist, inputs present, one seed inconsistency |
| Internal consistency | 8 | Paper self-consistent; nominal vs real MUQ N needs clarification |

**Overall Score: 8.0 / 10**

**Summary of required actions before submission**:

1. **[Must fix]** Correct "158 countries" to "144 countries" where referring to MUQ analysis, or add a qualifier
2. **[Must fix]** Clarify the MUQ observation count (2,629 nominal vs ~3,329 real) and ensure the reported N matches the actual analysis
3. **[Must fix]** Disclose India (5 obs) and Indonesia (6 obs, ending 1997) data sparsity in the ten-country trajectory discussion
4. **[Should fix]** Unify random seed to 20260321 across all scripts
5. **[Should fix]** Note PWT 10.01 data cutoff at 2019 in Methods M7
6. **[Nice to have]** Document US MSA Census-BEA merge attrition

None of these issues affect the core statistical conclusions. The data infrastructure is robust, the analysis pipeline is traceable, and the key findings are well-supported by the underlying data.
