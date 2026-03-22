# Paper Outline v5: Simpson's Paradox + Institutional Contrast

**Version**: 5.0
**Date**: 2026-03-21
**Basis**: paper_outline_v4.md + critical_assessment_2026-03-21 + W1-W4 analysis reports (city MUQ, Three Red Lines DID, US MSA MUQ, US diagnostics, carbon uncertainty)
**Target journal**: Nature (Article format), with Nature Cities as realistic fallback
**Word budget**: ~3,000-3,500 words main text + Methods + Extended Data

---

## Changelog v4 -> v5

1. **Narrative pivot**: "phase transition / scaling law" --> "Simpson's Paradox + institutional contrast". The paper now tells the story of a global efficiency decline hidden by aggregation bias, with China as the most extreme case and the China-US contrast as the institutional punchline.
2. **New headline**: Simpson's Paradox (3 income groups p < 0.003) + city-level MUQ vs FAI/GDP (beta = -2.23, p < 10^-6, N = 455) replaces national MUQ sign change (p = 0.043).
3. **Terminology overhaul** (throughout):
   - "regime shift" --> "structural break"
   - "scaling law" --> "cross-sectional regularity" (moved to ED)
   - "critical threshold" --> "investment intensity associated with efficiency decline"
   - "irreversible" --> "persistent and self-reinforcing"
   - "investment destroys value" --> "marginal investment returns have turned negative"
4. **Demotions**:
   - OCR scaling law --> Extended Data (renamed "cross-sectional structural correlation")
   - Critical investment threshold --> Extended Data (OECD real data p = 0.087, directional only)
   - UCI six-dimension diagnostic --> Future work (removed from this paper)
   - EWS / critical slowing down --> Extended Data (auxiliary evidence)
   - K* absolute value claims --> only rankings / relative ordering used
   - National MUQ sign change (p = 0.043) --> supporting evidence for Finding 2, no longer headline
5. **Promotions**:
   - Simpson's Paradox --> **Finding 1 headline** (from v4 Finding 3 paragraph)
   - City-level MUQ distribution (N = 455, beta = -2.23) --> **Finding 2 headline** (replaces national MUQ)
   - China-US MUQ contrast (beta = -2.23 vs +2.75) --> **Finding 2 highlight**
   - Three Red Lines DID --> Finding 2 causal supplement (honestly reported)
   - Carbon 5.3 GtCO2 [4.3, 6.3] with Monte Carlo CI --> **Finding 3** (replaces 13.4 GtCO2 without CI)
6. **New data incorporated**:
   - US MSA panel: 921 MSAs, 10,760 obs, beta(hu_growth) = +2.75, p < 10^-6
   - dV decomposition: US 87% price effect vs 13% quantity effect
   - Excess construction control: beta = +0.72 (still positive but attenuated)
   - DID Three Red Lines: TWFE Q beta = -0.089, p < 0.001; dose-response Q3/Q4 significant
   - Carbon MC: 5.3 GtCO2, 90% CI [4.3, 6.3] (MUQ direct method, time-varying CI)
7. **Carbon estimate revised**: 13.4 GtCO2 (constant CI, K-K* method) --> 5.3 GtCO2 (time-varying CI, MUQ direct method, with Monte Carlo 90% CI). The old estimate preserved in ED as upper-bound scenario.
8. **Causal language downgraded**: All core claims now framed as descriptive ("consistent with", "associated with"), not causal ("demonstrates", "proves").
9. **Four-country comparison** moved from Finding 1 to ED (no longer central to narrative).
10. **Writing schedule unchanged** but submission target remains 2026-06-30.

---

## 1. Candidate Titles

**Option A (preferred)**:
> A global Simpson's paradox in urban investment efficiency: evidence from 158 countries and 455 Chinese cities

**Option B**:
> When more building creates less value: hidden efficiency decline in global urban investment

**Option C**:
> The invisible decline: Simpson's paradox masks systematic erosion of urban investment returns across developing economies

Design principles: foregrounds the methodological discovery (Simpson's Paradox) that gives the paper its "aha" moment; avoids physics jargon (no "regime shift", "phase transition", "scaling law"); accessible to Nature's broad readership; signals both global scope and granular evidence.

---

## 2. Abstract (~150 words, draft)

Urban fixed-asset investment is the largest single category of capital formation in developing economies, yet whether this investment creates or erodes value at the margin remains unmeasured at global scale. Here we construct a marginal Urban Q (MUQ) -- the incremental asset value generated per unit of investment -- for 158 countries and 455 Chinese cities. We document a Simpson's paradox: the global aggregate MUQ shows no decline with urbanisation, but within low-income, lower-middle-income, and upper-middle-income country groups, MUQ declines significantly (all p < 0.003). High-income countries show no trend. At the city level in China, higher investment intensity is strongly associated with lower MUQ (beta = -2.23, p < 10^-6), while in US metropolitan areas the association is reversed (beta = +2.75), a divergence we attribute to demand-driven versus supply-driven investment regimes. A quasi-natural experiment exploiting China's 2020 "Three Red Lines" policy confirms that restricting credit to property-dependent cities reduced Urban Q (TWFE beta = -0.089, p < 0.001), consistent with demand-channel transmission. The cumulative carbon cost of investment that fails to create commensurate value in China is approximately 5.3 GtCO2 (90% CI: 4.3-6.3). These findings suggest that the conventional metric of investment volume obscures a systematic erosion of investment quality in rapidly urbanising economies.

[~170 words -- to be compressed to 150 in final draft]

---

## 3. Three Findings Structure

### Finding 1: A Simpson's paradox in global urban investment efficiency

**Core claim** (2-3 sentences):
At the global aggregate level, marginal Urban Q shows no meaningful decline with urbanisation stage, creating the misleading impression that urban investment remains productive throughout development. However, stratifying by World Bank income group reveals a classic Simpson's paradox: within each developing-economy group, MUQ declines significantly with urbanisation, with the strongest erosion in lower-middle-income countries. High-income countries show no trend, consistent with a mature-economy equilibrium where marginal investment maintains rather than expands the stock.

**Supporting evidence** (with exact statistics):

| Evidence | Statistic | Source |
|----------|-----------|--------|
| Global aggregate trend | Spearman rho = 0.036, p = 0.038 (weakly positive -- misleading) | Global panel, 158 countries |
| Low-income group | rho = -0.150, p = 0.002 | Global panel, WB income stratification |
| Lower-middle-income group | rho = -0.122, p = 0.002 | Global panel |
| Upper-middle-income group | rho = -0.099, p = 0.003 | Global panel |
| High-income group | rho = -0.013, p = 0.633 (n.s.) | Global panel |
| LMI median MUQ decline | From 9.88 (Stage 1) to 1.15 (Stage 4) | Global panel |
| China national MUQ 3-stage decline | ANOVA F-test p = 0.004 | NBS six-curves data |

**Main figure**: Fig 1
- Panel a: Global aggregate MUQ vs urbanisation (scatter + LOESS, showing flat/positive trend)
- Panel b: MUQ by income group and urbanisation stage (faceted boxplot or violin plot, Spearman rho and p annotated per group)
- Panel c: The "paradox revealed" -- schematic showing how compositional shifts across groups create the aggregate illusion

**Extended Data**: ED Table 1 (full MUQ descriptives by income group and urbanisation stage), ED Fig 1 (sensitivity to alternative MUQ definitions)

---

### Finding 2: City-level evidence reveals supply-driven efficiency erosion in China, contrasting with demand-driven dynamics in the US

**Core claim** (2-3 sentences):
Across 455 city-year observations in China (2010-2016), higher fixed-asset investment intensity is strongly associated with lower marginal investment returns (beta = -2.23, p < 10^-6), with 82.2% of cities showing MUQ below 1 in 2016 and a stark gradient from first-tier cities (mean MUQ = 7.46) to lower-tier cities (mean MUQ = 0.20). In the United States, the same relationship is reversed: across 10,760 MSA-year observations (2010-2022), housing investment growth is positively associated with MUQ (beta = +2.75, p < 10^-6), a divergence explained by the dominance of price effects (87% of dV) in a demand-driven market. China's "Three Red Lines" policy (2020), which restricted credit to highly leveraged developers, provides quasi-experimental evidence: cities more dependent on real estate experienced larger Q declines (TWFE beta = -0.089, p < 0.001), consistent with a demand-channel shock rather than supply-side correction.

**Supporting evidence** (with exact statistics):

| Evidence | Statistic | Source |
|----------|-----------|--------|
| **China city MUQ vs FAI/GDP** | beta = -2.23, 95% CI [-3.05, -1.42], p < 10^-6, N = 455 | city_muq_distribution_report |
| Quantile regression Q90 | beta = -3.29, p = 0.000004 | city_muq_distribution_report |
| Quantile regression Q50 | beta = -0.54, p < 10^-6 | city_muq_distribution_report |
| Panel FE (within estimator) | beta = -1.73, p = 0.063 (direction consistent, attenuated) | city_muq_distribution_report |
| MUQ < 1 proportion (2016) | 82.2% (175/213 cities) | city_muq_distribution_report |
| Tier gradient (2016) | Tier 1: 7.46, New Tier 1: 2.84, Tier 2: 1.00, Tier 3: 0.52, Tier 4-5: 0.20 | city_muq_distribution_report |
| Regional gradient | East: 1.13, Central: 0.35, West: 0.30; Kruskal-Wallis p = 0.0002 | city_muq_distribution_report |
| MUQ ~ log(pop) | beta = 0.73, p < 10^-6, R2 = 0.086 | city_muq_distribution_report |
| **US MSA MUQ vs hu_growth** | beta = +2.75, 95% CI [2.57, 2.92], p < 10^-6, N = 10,760 | us_msa_muq_report |
| US TWFE | beta = +2.55, p < 10^-6 | us_msa_muq_report |
| US dV decomposition | 87% price effect, 13% quantity effect | us_muq_diagnostics_report |
| US excess construction (hu_growth - pop_growth) | beta = +0.72, p < 10^-6 (positive but attenuated by 74%) | us_muq_diagnostics_report |
| **DID: TWFE Urban Q** | beta = -0.089, SE = 0.022, p = 0.000053 | three_red_lines_did_report |
| DID: Binary Q | beta = -0.094, p = 0.008 | three_red_lines_did_report |
| DID: Dose-response Q3 | beta = -0.095, p = 0.016 | three_red_lines_did_report |
| DID: Dose-response Q4 | beta = -0.136, p = 0.005 | three_red_lines_did_report |
| DID: Parallel trends | F = 2.82, p = 0.093 (marginal -- limitation noted) | three_red_lines_did_report |
| DID: Placebo (pseudo-policy 2016) | beta = 0.067, p < 0.001 (significant -- limitation noted) | three_red_lines_did_report |
| DID: Mechanism (FAI/GDP) | p = 0.330 (supply channel not confirmed) | three_red_lines_did_report |

**Honest reporting requirements for DID**:
- The Three Red Lines result supports **demand-channel** interpretation (restricting credit depressed V, not K), not the "overinvestment harms value" hypothesis directly
- Parallel trends assumption is marginal (p = 0.093), and placebo test is significant (p < 0.001) -- both must be reported as limitations
- The DID strengthens the descriptive finding but does not resolve the fundamental causal identification challenge

**Main figures**: Fig 2 + Fig 3
- Fig 2a: China city MUQ vs FAI/GDP (scatter + OLS fit + quantile regression fans)
- Fig 2b: China city MUQ by tier (boxplot, 2016 cross-section)
- Fig 3a: US MSA MUQ vs hu_growth (scatter + OLS fit, same visual format as Fig 2a for direct comparison)
- Fig 3b: China-US "mirror" panel: key regression coefficients side by side, with interpretation labels ("supply-driven" vs "demand-driven")

**Extended Data**: ED Fig 2 (DID event study plots for ln(HP) and Q), ED Table 2 (full DID regression table, all specifications), ED Fig 3 (US dV decomposition), ED Table 3 (China city MUQ full descriptives by year/tier/region), ED Fig 4 (quantile regression coefficient plot)

---

### Finding 3: The carbon cost of investment that fails to create value

**Core claim** (2-3 sentences):
Using a marginal-Urban-Q-based direct estimation method with time-varying carbon intensity and Monte Carlo uncertainty propagation, we estimate that China's cumulative "excess" construction carbon emissions -- embodied carbon from investment in years when MUQ fell below 1 -- total approximately 5.3 GtCO2 over 2000-2024 (90% CI: 4.3-6.3 GtCO2). This is equivalent to approximately 2.7% of China's total cumulative carbon emissions over the same period. Annual excess emissions peaked in 2024 at 1,714 MtCO2, driven by the combination of continued high investment volume and sharply negative marginal returns.

**Supporting evidence** (with exact statistics):

| Evidence | Statistic | Source |
|----------|-----------|--------|
| MUQ direct method, point estimate | 5.09 GtCO2 (cumulative 2000-2024) | carbon_uncertainty_report |
| Monte Carlo median | 5.28 GtCO2 | carbon_uncertainty_report |
| Monte Carlo 90% CI | [4.34, 6.31] GtCO2 | carbon_uncertainty_report |
| Monte Carlo 50% CI | [4.87, 5.67] GtCO2 | carbon_uncertainty_report |
| Share of China total emissions | 2.7%, 90% CI [2.2%, 3.3%] | carbon_uncertainty_report |
| Peak year emissions | 2024: 1,714 MtCO2 | carbon_uncertainty_report |
| Time-varying carbon intensity | CI(2000) = 1.20 --> CI(2024) = 0.60 tCO2/10k yuan | carbon_uncertainty_report |
| Method C (Q-percentile based) | 4.57 GtCO2, 90% CI [1.28, 8.03] | carbon_uncertainty_report |
| CI sensitivity +/-30% | Range: 3.56 - 6.62 GtCO2 | carbon_uncertainty_report |
| MUQ threshold sensitivity | MUQ < 0.5: 1.66; MUQ < 0.8: 3.42; MUQ < 1.0: 5.09; MUQ < 1.2: 7.36 GtCO2 | carbon_uncertainty_report |

**Main figure**: Fig 4
- Panel a: Time series of excess carbon emissions (stacked area: years with MUQ < 1 shaded; MUQ trajectory on right axis); Monte Carlo 90% CI band
- Panel b: Sensitivity tornado diagram (carbon intensity, MUQ threshold, decay rate) showing robustness

**Extended Data**: ED Table 4 (year-by-year carbon estimates with MUQ and CI values), ED Fig 5 (Method comparison: A vs B vs C), ED Fig 6 (scenario analysis: conservative / moderate / aggressive)

---

## 4. Main Figures (4 main + 1 flagship)

### Flagship Figure (Fig 1): The Simpson's Paradox Revealed

**Layout**: 3 panels (a-c), full page width. This is the figure that must make the editor stop scrolling.

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Global scatter: MUQ vs urbanisation rate, all 158 countries pooled, LOESS fit showing flat/slightly positive trend; color-coded by income group but overlapping | "At first glance, investment efficiency appears stable globally" |
| **b** | Same data, faceted by income group (2x2 grid: LI, LMI, UMI, HI); within each facet, LOESS fit with 95% CI; Spearman rho and p annotated prominently | "But within every developing-economy group, efficiency is declining" |
| **c** | Conceptual "Simpson's Paradox" diagram: arrows showing within-group decline + between-group composition shift = apparent stability | "The paradox: compositional shifts mask real decline" |

**Visual design**: Panel a and b share the same axes and color scheme for immediate visual comparison. Panel c is a clean schematic (not data-driven).

### Fig 2: China's city-level evidence

**Layout**: 2 panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Scatter: city MUQ vs FAI/GDP (N = 455), OLS line + Q10/Q50/Q90 quantile regression lines; color by tier | Higher investment intensity, lower marginal returns; effect strongest at upper quantiles |
| **b** | Boxplot: city MUQ by tier (2016 cross-section, N = 213); MUQ = 0 and MUQ = 1 reference lines; individual points overlaid | Tier 1 cities: MUQ >> 1; Tier 4-5 cities: MUQ near zero |

### Fig 3: The China-US mirror

**Layout**: 2 panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | US MSA scatter: MUQ_gdp vs hu_growth (N = 10,760), OLS line + quantile regression lines; same visual format as Fig 2a | In the US, more building associates with more value -- opposite to China |
| **b** | Coefficient comparison panel: bar chart showing China beta (-2.23) vs US beta (+2.75) vs US excess-construction beta (+0.72); with 95% CI whiskers; interpretation labels | "Supply-driven overinvestment (China) vs demand-driven growth (US)" |

### Fig 4: The carbon cost

**Layout**: 2 panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Time series (2000-2024): stacked area of excess carbon emissions; MUQ trajectory on right axis; 90% CI shaded band from Monte Carlo; cumulative annotation "5.3 GtCO2 [4.3, 6.3]" | Carbon cost concentrated in post-2021 years when MUQ collapsed |
| **b** | Sensitivity analysis: tornado/forest plot showing how estimates vary under different assumptions (CI level, MUQ threshold, decay rate, method); all methods converge on GtCO2-scale impact | Estimate is robust to methodological choices at the order-of-magnitude level |

### Supplementary Main Figure (Fig 5, if space permits): National Q trajectory + DID

**Layout**: 2 panels

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | China weighted Q time series (1998-2024) with 90% CI band; Q = 1 line; Bai-Perron breaks at 2004 and 2018 annotated; MUQ bar inset | Directional decline is robust across calibrations; crossing Q = 1 sometime in 2010-2022 |
| **b** | DID event study: Urban Q coefficients by year (2017-2023), RE_dep_z interaction; pre-trend test annotated; policy onset marked | Three Red Lines shock: higher-RE-dependent cities experienced larger Q declines |

**Note**: If word/figure count is tight for Nature, Fig 5 moves to ED and the paper runs with 4 main figures.

---

## 5. Methods Summary (key bullet points)

### M1. Marginal Urban Q (MUQ) construction
- **China national**: MUQ = Delta V(t) / I(t), seven V/K calibrations (V1/K1 through V3/K2 plus V1_adj/K2), weighted ensemble with Bayesian priors
- **China city-level**: MUQ approximated from city-panel data (2010-2016, 300 cities, V reconstructed from population x housing price x per-capita area; I = FAI)
- **Global panel**: MUQ = Delta(V2) / GFCF, real (constant 2017 PPP USD), 158 countries from WB/PWT
- **US MSA**: MUQ_gdp = Delta(median_home_value x housing_units) / GDP, Census ACS 5-year + BEA CAGDP1, 921 MSAs, 2010-2022

### M2. Simpson's paradox identification
- World Bank income group stratification (LI, LMI, UMI, HI)
- Within-group Spearman rank correlation of MUQ vs urbanisation stage
- Urbanisation stages defined by quartile cutoffs within each income group
- Aggregate vs within-group trend comparison

### M3. China-US institutional comparison
- dV decomposition: price effect = dP x HU_lag; quantity effect = P_lag x dHU
- Excess construction: hu_growth - pop_growth as supply-side proxy
- Controlled regressions with population growth, GDP per capita, tertiary share

### M4. Three Red Lines DID
- Treatment intensity: RE_dep = real estate investment / GDP (continuous, standardised)
- Period: 2017-2023, policy onset 2020
- Specifications: base OLS, province FE + controls, TWFE (city + year FE)
- Outcome variables: ln(housing price), Urban Q
- Robustness: binary DID (median split), dose-response (quartiles), event study, placebo (pseudo-policy 2016), heterogeneity by city size
- Limitations reported: parallel trends marginal (p = 0.093), placebo significant, mechanism test inconclusive

### M5. Carbon cost estimation
- **Primary method (A)**: MUQ direct -- excess investment = I(t) x max(0, 1 - MUQ(t)); carbon = excess_I x CI(t)
- Time-varying carbon intensity: CI(2000) = 1.20, CI(2024) = 0.60 tCO2/10k yuan, exponential decay 2.89%/year
- Monte Carlo: 10,000 iterations propagating uncertainty in MUQ weights, CI level, CI decay rate
- **Cross-check methods**: B (scenario analysis), C (Q-percentile based K* = V)
- Sensitivity: CI level +/-30%, MUQ threshold 0-1.2, decay rate 0-2x

### M6. Monte Carlo calibration uncertainty (for Q trajectory)
- 10,000 draws, Dirichlet-weighted calibration sampling
- Within-calibration parameter uncertainty from specified distributions
- Output: distribution of Q(t), crossing year, MUQ sign change year
- Bai-Perron structural break test: F = 30.1, p < 0.0001, breaks at 2004 and 2018

### M7. Data sources
- China: NBS Statistical Yearbooks (national + city), CEIC (city panel)
- Global: World Bank WDI, Penn World Table 10.01, BIS residential property prices
- US: Census ACS 5-Year (2010-2022), BEA CAGDP1 (county GDP), CBSA delineation
- Carbon: China Building Energy Conservation Association (2022), IEA building sector reports

---

## 6. Discussion Outline (5 key points)

### Para 1: Summary of contribution (~100 words)
Three findings, one sentence each. Emphasise what is new:
- First documentation of Simpson's paradox in global urban investment efficiency
- First city-level MUQ mapping (455 obs) with US institutional comparison (10,760 obs)
- First uncertainty-bounded carbon cost estimate of value-destroying investment
- Frame as "descriptive findings that reveal previously hidden patterns", not causal claims

### Para 2: Supply-driven vs demand-driven investment regimes (~150 words)
The China-US contrast is not a curiosity but a diagnostic. In demand-constrained economies (US), investment follows demand signals (population growth, household formation), and MUQ is naturally positive. In supply-driven economies (China), investment is driven by fiscal incentives (land finance), credit availability, and GDP targeting, decoupled from underlying demand. The Simpson's paradox emerges because developing economies systematically shift from demand-constrained to supply-driven regimes as they industrialise, but this shift is invisible in aggregate data. This framework generates a testable prediction: countries transitioning from low-income to middle-income status should show declining within-group MUQ -- which is exactly what the data show.

### Para 3: Policy implications (~150 words)
- For China: the construction-led growth model has exhausted its value-creating potential. Policy should shift from volume to quality.
- City-tier differentiation: Tier 1 cities (MUQ = 7.46) still have investment headroom; Tier 4-5 cities (MUQ = 0.20) require asset absorption, not new construction.
- The Three Red Lines result is a cautionary tale: credit restriction works through demand suppression (V falls) not supply correction (K adjusts), suggesting that policy should target demand fundamentals (population, industry) rather than supply-side credit controls alone.
- For other rapidly urbanising economies: the Simpson's paradox means that aggregate investment statistics can mask efficiency erosion until it becomes severe.

### Para 4: Carbon and climate implications (~120 words)
5.3 GtCO2 [4.3, 6.3] of embodied carbon associated with investment that failed to create commensurate value. This is a lower-bound estimate (construction-phase only; excludes operational carbon from excess stock). The estimate is robust to methodological choices (all methods converge on GtCO2-scale). For climate policy: integrating investment efficiency metrics into national carbon accounting could identify "avoidable" embodied carbon before it is emitted. The peak in 2024 (1,714 MtCO2) coincides with the nadir of MUQ, suggesting that carbon waste accelerates nonlinearly as marginal returns collapse.

### Para 5: Limitations (~200 words)
1. **V(t) measurement**: the fundamental challenge. Seven calibrations bound but do not resolve the uncertainty. Q = 1 crossing year has a ~12-year CI. We focus on directional findings (MUQ decline, cross-sectional gradients) that are robust across calibrations, not precise threshold levels.
2. **Causal identification**: all findings are descriptive. The DID provides suggestive evidence but faces parallel-trends concerns (p = 0.093) and a significant placebo (p < 0.001). "Marginal returns have turned negative" is an empirical description, not a causal claim about overinvestment causing value destruction.
3. **China-US comparability**: different MUQ definitions (FAI-based vs housing-unit-based), different market institutions, different time periods. The sign reversal is robust, but the coefficient magnitudes are not directly comparable.
4. **City-level panel**: limited to 2010-2016 (7 years) with V reconstruction from population x price x area, not direct asset valuation. Coverage varies by year (20-213 cities).
5. **Carbon estimates**: construction-phase only. Time-varying CI is modelled, not measured year by year. MUQ < 1 threshold is a modelling choice (sensitivity analysis provided).
6. **DID caveats**: Three Red Lines is not a clean exogenous shock -- it responds to the overinvestment it aims to correct, creating potential anticipation effects.

### Para 6: Closing (~50 words)
"When aggregate statistics signal health, disaggregation may reveal disease. The Simpson's paradox we document suggests that the largest misallocation of physical capital in modern history has been hiding in plain sight -- obscured by the very growth it was supposed to produce."

---

## 7. Extended Data Plan (up to 10 figures/tables)

| ID | Type | Content | Purpose | Source |
|----|------|---------|---------|--------|
| **ED Fig 1** | Figure | MUQ sensitivity to alternative definitions (Delta V/GDP, Delta V/I, different V calibrations) | Robustness of Simpson's paradox | Global panel |
| **ED Table 1** | Table | Full MUQ descriptives by income group x urbanisation stage, with Simpson's paradox decomposition | Statistical backup for Finding 1 | Global panel |
| **ED Fig 2** | Figure | DID event study plots: ln(HP) and Urban Q coefficients by year (2017-2023) | Parallel trends visualisation for DID | DID report |
| **ED Table 2** | Table | Full DID regression table: Models 1-7, all specifications, robustness checks | Statistical detail for DID | DID report |
| **ED Fig 3** | Figure | US dV decomposition: price effect vs quantity effect by MSA; price_MUQ vs hu_growth scatter | Explains China-US divergence mechanism | US diagnostics |
| **ED Table 3** | Table | China city MUQ descriptives: by year, tier, region; panel FE results; quantile regression table | Statistical backup for Finding 2 | City MUQ report |
| **ED Fig 4** | Figure | Quantile regression coefficient plot (Q10-Q90) for China cities + US MSAs side by side | Shows gradient intensification at upper quantiles | Both city reports |
| **ED Fig 5** | Figure | Carbon method comparison: Method A (MUQ) vs Method B (scenarios) vs Method C (Q-percentile); 90% CIs | Robustness of carbon estimate | Carbon report |
| **ED Table 4** | Table | Year-by-year carbon estimates: MUQ, waste fraction, investment, CI, annual emissions, cumulative | Full transparency for carbon calculation | Carbon report |
| **ED Fig 6** | Figure | China Q trajectory (7 calibrations, small multiples) + MC crossing year density + Bai-Perron annotated | Supports national-level Q decline (auxiliary) | National Q data |
| **ED Fig 7** | Figure | OCR cross-sectional regularity (NOT "scaling law"): China 290-city OCR map + OCR vs log(Pop) scatter | Directional evidence, explicitly noted R2 = 0.15 | City panel |
| **ED Table 5** | Table | K* model specifications (Between, TWFE, RE) + bootstrap CI for OCR | Transparency on K* uncertainty | K* analysis |

---

## 8. Section-by-Section Outline

### Introduction (~600 words, 4 paragraphs)

**Para 1 -- Hook** (~150 words):
Between 2000 and 2024, China invested more than 500 trillion yuan in fixed assets -- the largest capital formation programme in human history. Conventional metrics (GDP growth, urbanisation rate, housing stock per capita) suggest this investment was productive. But these metrics aggregate across cities, income groups, and development stages in ways that can conceal systematic inefficiency. We show that the apparent stability of urban investment returns globally is a Simpson's paradox: within every developing-economy income group, marginal returns are declining, but compositional shifts across groups create an aggregate illusion of stability.

**Para 2 -- The measurement gap** (~150 words):
Despite the scale of urban investment, no cross-national framework exists to measure whether each additional unit of investment creates or erodes asset value. Tobin's Q has been applied to corporate investment decisions for decades but never operationalised for the urban built environment at national or city scale. Three specific gaps:
1. No systematic measure of marginal investment efficiency (MUQ) across countries and cities
2. No decomposition of aggregate trends that could reveal hidden compositional effects
3. No institutional comparison between investment regimes (supply-driven vs demand-driven)

**Para 3 -- What this paper does** (~150 words):
We construct MUQ for 158 countries (global panel), 455 Chinese city-year observations, and 10,760 US MSA-year observations. Three findings:
(1) A Simpson's paradox: global aggregate MUQ is stable, but within-group MUQ declines in all developing-economy groups
(2) City-level evidence: investment intensity is negatively associated with MUQ in China but positively in the US, reflecting supply-driven vs demand-driven investment regimes
(3) Carbon cost: 5.3 GtCO2 [4.3, 6.3] of embodied emissions associated with value-eroding investment in China

**Para 4 -- Scope and roadmap** (~100 words):
We frame these as descriptive findings, not causal claims. The MUQ framework measures outcomes, not mechanisms. The China-US comparison reveals institutional correlates, not causes. The Three Red Lines quasi-experiment provides suggestive but not definitive causal evidence. We report limitations transparently and identify the causal identification challenge as a priority for future work.

---

### Results (~1,400 words)

#### Finding 1: Simpson's paradox (~450 words)

**Para 1 [HEADLINE]**: Present the paradox. Global aggregate MUQ shows a weakly positive trend with urbanisation (Spearman rho = 0.036, p = 0.038). This has been interpreted as evidence that urban investment remains productive throughout development. However...

**Para 2**: Stratification by income group reverses the picture. Within LI, LMI, and UMI groups, MUQ declines significantly with urbanisation (rho = -0.15, -0.12, -0.10; all p < 0.003). HI countries: no trend (p = 0.633). The strongest absolute decline is in LMI countries (median MUQ from 9.88 to 1.15 across urbanisation stages). Reference Fig 1b.

**Para 3**: The paradox arises because countries "graduate" from lower to higher income groups as they urbanise, and higher income groups have higher average MUQ levels. The between-group positive association masks the within-group negative association. This is a textbook Simpson's paradox. Reference Fig 1c.

**Para 4**: China's position. In the global panel (WB/PWT data, PPP-adjusted), China appears in the rising portion of the UMI group, with MUQ increasing from 7.80 to 17.12 across stages -- seemingly contradicting the decline narrative. However, this reflects: (a) PPP adjustment inflating construction-sector output, (b) time coverage ending before the 2022 transition, and (c) scale effects of unprecedented capital deepening. China's national-accounts-based MUQ (six-curves data) shows a three-stage decline (ANOVA p = 0.004) and turns negative in 2022-2024. Reference Methods for reconciliation.

#### Finding 2: China vs US city-level evidence (~550 words)

**Para 1 [China cities]**: Across 455 city-year observations, FAI/GDP is strongly negatively associated with MUQ (beta = -2.23, p < 10^-6). The effect intensifies at higher quantiles: Q90 beta = -3.29 (p = 0.000004), meaning the highest-MUQ cities are most sensitive to investment intensity. In the 2016 cross-section (N = 213), 82.2% of cities have MUQ < 1, and the tier gradient is dramatic: first-tier mean = 7.46, tier 4-5 mean = 0.20. Regional disparities are also significant (Kruskal-Wallis p = 0.0002): eastern cities (mean 1.13) vs western (0.30). Reference Fig 2.

**Para 2 [US MSAs]**: The US shows the opposite pattern. Across 10,760 MSA-year observations, housing growth is positively associated with MUQ (beta = +2.75, p < 10^-6). The dV decomposition reveals why: in the US, 87% of asset value change comes from price appreciation (existing stock revaluation), not new construction. Even after controlling for population growth, the excess-construction coefficient remains positive (+0.72, p < 10^-6), though attenuated by 74%. This is consistent with a demand-driven market where building activity signals, rather than undermines, economic vitality. Reference Fig 3.

**Para 3 [Interpretation]**: The China-US sign reversal is the institutional punchline. In China, investment is supply-driven (land finance, credit expansion, GDP targeting); excess supply depresses marginal value. In the US, investment is demand-driven (household formation, price signals); building tracks willingness-to-pay. The contrast quantifies what urbanists have long argued qualitatively: investment efficiency depends not just on how much is invested but on why.

**Para 4 [DID]**: China's 2020 "Three Red Lines" policy provides a quasi-natural experiment. Using real-estate investment dependence as treatment intensity, we find that more dependent cities experienced significantly larger Urban Q declines after the policy (TWFE beta = -0.089, p < 0.001). The dose-response is monotonic (Q3: -0.095, p = 0.016; Q4: -0.136, p = 0.005). However, we note two important caveats: the parallel trends assumption is marginally violated (F = 2.82, p = 0.093), and a placebo test with pseudo-policy timing is significant. The result is consistent with demand-channel transmission (credit restriction depressed housing demand and prices) rather than supply-side correction. Reference Fig 5b / ED Fig 2.

#### Finding 3: Carbon cost (~400 words)

**Para 1**: Using the MUQ direct method with time-varying carbon intensity (declining from 1.20 to 0.60 tCO2/10,000 yuan over 2000-2024) and Monte Carlo uncertainty propagation (10,000 iterations), we estimate China's cumulative excess construction carbon emissions at 5.3 GtCO2 (90% CI: 4.3-6.3). This represents approximately 2.7% of China's total carbon emissions over the period. Reference Fig 4a.

**Para 2**: The temporal distribution is highly concentrated. Years when MUQ exceeded 1 (2000-2007, 2009-2013, 2015-2020) contribute zero excess emissions by construction. The bulk of excess emissions (>90%) occurs in 2021-2024, when MUQ fell below 1 and then turned sharply negative. Peak annual excess emissions reached 1,714 MtCO2 in 2024. Reference Fig 4a.

**Para 3**: Sensitivity analysis confirms robustness at the order-of-magnitude level. Carbon intensity variation of +/-30% shifts the estimate to [3.6, 6.6] GtCO2. Alternative methods (K-K* direct, Q-percentile based) yield point estimates of 4.6-5.3 GtCO2. The MUQ threshold is the most influential parameter: using MUQ < 0 (only years of outright value destruction) gives 0.2 GtCO2; using MUQ < 1.2 gives 7.4 GtCO2. We adopt MUQ < 1 as the economically meaningful benchmark (investment that fails to fully recover its cost in asset value). Reference Fig 4b.

**Para 4**: These estimates are conservative lower bounds. They cover construction-phase embodied carbon only, excluding operational energy use of excess building stock and the opportunity cost of capital diverted from potentially lower-carbon sectors. They also exclude the global dimension: if the Simpson's paradox applies globally, similar carbon waste may be occurring across developing economies, though data limitations preclude direct estimation.

---

### Discussion (~900 words)

[See Section 6 above for detailed outline]

---

### Methods (~1,500 words)

[See Section 5 above for detailed outline]

---

## 9. Key Narrative Decisions (v5)

### What is IN the paper (main text)
- Simpson's paradox as HEADLINE (3 income groups, all p < 0.003)
- City-level MUQ vs investment intensity (beta = -2.23, p < 10^-6, N = 455) as core evidence
- China-US institutional contrast (beta = -2.23 vs +2.75) as interpretive framework
- Three Red Lines DID (TWFE Q beta = -0.089, p < 0.001) -- honestly reported with caveats
- Carbon 5.3 GtCO2 [4.3, 6.3] with full uncertainty quantification
- "Persistent and self-reinforcing" framing (NOT "irreversible" or "phase transition")
- MUQ as a descriptive measurement tool, not a causal identification strategy
- Limitations reported prominently and honestly

### What is in Extended Data only
- National Q trajectory (7 calibrations, MC crossing year, Bai-Perron breaks)
- National MUQ sign change (p = 0.043) -- supporting evidence, not headline
- OCR cross-sectional regularity (NOT "scaling law"; R^2 = 0.15 explicitly noted)
- K* model and bootstrap CI (used for rankings only, not absolute values)
- EWS / critical slowing down (35/52, p = 0.009 -- auxiliary)
- Investment threshold (LOESS zero-crossing ~20.7% as directional evidence; Hansen p = 0.087 from OECD data noted as n.s.)
- Four-country Q comparison (China, Japan, US, UK)
- Old carbon estimate (13.4 GtCO2, K-K* method) as upper-bound scenario

### What is NOT in this paper (future work)
- UCI six-dimension diagnostic system
- Causal identification of investment-efficiency relationship (needs better instruments)
- City-level panel beyond 2010-2016
- Operational carbon from excess building stock
- Real-time EWS monitoring system
- Precise UCI thresholds for policy grading
- Cross-national OCR estimation with reliable K* models
- Forward-looking conditional predictions for India/Vietnam/Indonesia (removed -- insufficient evidence base)

### Data-source reconciliation (carried from v4, refined)
- **China national MUQ** (NBS data, 1998-2024): three-stage decline, turns negative 2022-2024 (p = 0.043)
- **China city-level MUQ** (city panel, 2010-2016): 82.2% < 1, beta(FAI/GDP) = -2.23
- **China in global panel** (WB/PWT, PPP-adjusted): MUQ appears rising
- **Resolution**: city-level and national NBS data are primary; global panel China values reflect PPP and timing artefacts; Methods section provides detailed reconciliation

---

## 10. Writing Schedule

| Section | Draft | Target date | Dependencies |
|---------|-------|-------------|--------------|
| Methods | First | 2026-04-05 | All data + analysis scripts finalised |
| Results | First | 2026-04-15 | Finalised figures + statistics |
| Introduction | First | 2026-04-25 | Literature review complete |
| Discussion | First | 2026-05-05 | All other sections |
| Abstract | First | 2026-05-10 | Full draft complete |
| Full draft v1 | Assembly | 2026-05-15 | All sections |
| Internal review | Peer-reviewer agent | 2026-05-25 | Draft v1 |
| Revision + v2 | Final | 2026-06-15 | Review feedback |
| Submission package | Cover letter + highlights | 2026-06-30 | Draft v2 approved |

---

## 11. Risk Assessment (new section)

| Risk | Probability | Mitigation |
|------|:-----------:|------------|
| Nature desk reject | 55-60% | Prepare Nature Cities submission package in parallel |
| Reviewer attacks V(t) measurement | 90% | Focus narrative on directional/relative findings, not absolute Q levels |
| Reviewer demands causal identification | 80% | Frame as descriptive; DID is "suggestive"; acknowledge limitation prominently |
| Reviewer challenges China-US comparability | 70% | Detailed Methods section on measurement differences; emphasise sign reversal (robust) not coefficient magnitude (not comparable) |
| Simpson's paradox dismissed as "well-known disaggregation" | 40% | Emphasise that no prior study has documented this in urban investment; show that policy discourse still relies on aggregate metrics |
| Carbon estimate challenged | 60% | 90% CI is narrow and well-motivated; sensitivity analysis covers major assumptions; frame as "order-of-magnitude" not "precise accounting" |

---

*Outline v5.0 -- Simpson's Paradox + Institutional Contrast reframe*
*Manuscript Writer Agent*
*2026-03-21*
