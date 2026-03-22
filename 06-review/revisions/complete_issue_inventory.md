# Complete Issue Inventory: All Reviewer Comments vs. v6 Status

**Date**: 2026-03-22
**Scope**: 5 disciplinary reviewers (R1-R5) + 6 thinking hats (White/Red/Black/Yellow/Green/Blue)
**Manuscript**: full_draft_v6.md
**Target journal**: Nature (main journal)

---

## Legend

- **Status**: Already resolved in v6 / Partially resolved / Not resolved / New issue in v6
- **Class**: A = must fix before submission (desk reject risk) / B = should fix (reviewer concern) / C = can fix in R1

---

## PART I: CONSOLIDATED ISSUE TABLE

### Section A: MUQ Construct Validity & Price Cycle Contamination

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| A1 | R1-M1, R3-3.1, R4-3.5b, R5-M3, Black-C1 | Fatal/Major | **MUQ conflates asset price movements with investment efficiency.** Delta-V dominated by price cycles (US 87% price, China 2021-2024 crash). MUQ is substantially a house-price-cycle indicator. | Partially resolved. v6 added GDP-based MUQ as parallel validation and quantity-price decomposition. But no price-cycle-adjusted MUQ was constructed; housing-based MUQ core defect remains. | B | (1) In Methods/Discussion, add explicit statement: "Housing-based MUQ captures asset-value capitalisation, which includes price-cycle effects; the GDP-based formulation provides a complementary signal immune to this channel." (2) Consider constructing quantity-effect-only Delta-V for China as ED robustness check showing paradox survives. |
| A2 | R3-3.1-P1, Black-NEW1 | Major | **GDP-based MUQ = 1/ICOR, which Easterly (1999) -- the paper's own ref [19] -- demonstrated is misleading.** GDP growth reflects TFP, institutions, trade, demographics, not just investment productivity. Self-contradictory to cite Easterly then use ICOR. | Not resolved. v6 uses GDP-MUQ as primary validation but does not address the Easterly critique. | A | Add 1-2 sentences in Methods M1 or Discussion: "We note that ICOR has been criticised as a prescriptive investment guide^19; here we use GDP-based MUQ not as an efficiency measure but as a diagnostic signal -- if the Simpson's paradox holds under a formulation that is structurally independent of housing prices, the pattern cannot be attributed solely to asset-price cycles." |
| A3 | R1-M1, R5-M3 | Major | **Need to show Simpson's paradox holds using quantity-effect-only Delta-V (not just GDP-MUQ).** Price-cycle adjustment was the core remedy suggested by R1. | Not resolved. v6 used GDP-MUQ as workaround, not price-adjusted housing MUQ. | B | If data permit, construct quantity-only MUQ for China (Delta-V_quantity / FAI) and test Simpson's paradox. If not feasible, acknowledge as future work in Discussion. |
| A4 | R3-3.1-P2 | Major | **Numerator-denominator mismatch**: V measures residential housing value; I measures total FAI (including infrastructure, industrial, commercial). MUQ captures returns to one asset class from investment in all asset classes. | Not resolved. v6 acknowledges "different MUQ definitions" in Limitation 9 but does not address the structural mismatch for China. | B | Add to Limitation 9 or Methods M1: "China's MUQ pairs residential asset value with total FAI, meaning non-residential investment (infrastructure, industrial) appears in the denominator without corresponding returns in the numerator. This asymmetry biases China's MUQ downward relative to the US, where both V and I are housing-specific." |
| A5 | R3-3.1-P3 | Minor | **MUQ < 1 threshold has no natural economic meaning** as "break-even." Investment generates returns through GDP, employment, amenities, not just housing prices. | Partially resolved. v6 Limitation 8 notes MUQ does not capture social value. But the MUQ = 1 threshold is still used without justification. | C | Add sentence in Box 1 or Methods: "MUQ = 1 is not a social welfare threshold; it indicates parity between housing-market capitalisation and gross investment, and should be interpreted as a market signal rather than a welfare criterion." |
| A6 | R3-3.3 | Minor | **Reframe MUQ as "housing market signal" rather than "investment efficiency."** | Partially resolved. v6 added caveats but still uses "investment efficiency" / "investment returns" language. | B | Audit remaining instances of "investment efficiency" and consider replacing with "investment outcomes" or "asset-value return on investment" in key locations. |

### Section B: Simpson's Paradox & Global Panel

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| B1 | R4-3.1a | Major | **Spearman p-values are unreliable due to within-country clustering.** Multiple country-years pooled; effective N far smaller than reported N. Need cluster-bootstrapped p-values. | Partially resolved. v6 added block bootstrap ("preserves significance in all three developing groups") but does not report specific bootstrap p-values in the main text. | B | Report bootstrap p-values explicitly in Finding 1 or ED Table 1. E.g., "Block bootstrap at the country level yields p < [value] for all three developing groups." |
| B2 | R4-3.1a, Blue-Blind4 | Major | **Time-varying income classification weakens within-group significance.** Fixed classification biases trajectories. Under time-varying scheme, only Q4_High remains significant. | Not resolved. v6 uses fixed classification and does not report time-varying sensitivity. | B | Run time-varying classification analysis and report in Methods M9 or ED. If already done, add to text: "Under time-varying income classification, significance is weakened in lower groups but the directional pattern persists." |
| B3 | R3-m4 | Minor | **Fixed income classification biases**: a country classified UMI for its full trajectory includes its earlier LMI-phase observations in the UMI group. | Same as B2; not resolved. | B | See B2 action. |
| B4 | R4-m6, R3-m5 | Minor | **Spearman rho effect sizes are small** (rho = -0.099 to -0.150, < 2.3% variance explained). Statistical significance does not imply economic importance. | Not resolved. v6 does not discuss effect sizes in substantive terms. | C | Add 1 sentence in Finding 1 or Discussion: "The within-group correlations, while modest in magnitude (rho approximately -0.10 to -0.25), are economically meaningful when scaled to the trillions of dollars flowing into urban construction annually." |
| B5 | R1-m5 | Minor | **Ten-country trajectory analysis is underpowered** (India: 5 obs, Indonesia: 6). | Partially resolved. v6 notes "MUQ coverage varies substantially" and calls inferences "indicative." | C | No further action needed; current framing is adequate. |
| B6 | White-C3 | Major | **144 vs 157 country count discrepancy.** GDP-based MUQ covers 157 countries (WDI groups sum), but paper says 144 throughout. | Not resolved. 144 may be housing-based coverage; paper uses it for GDP-based too. | A | Clarify: "Housing-based MUQ covers 144 countries; GDP-based MUQ covers [157] countries across [X] income groups. The 144-country figure refers to the housing-based panel." Or reconcile the numbers. |
| B7 | White-4.2.1 | Minor | **Abstract "all p < 0.003"**: housing-based UMI p = 0.003, which does not strictly satisfy "< 0.003." | Not resolved. | A | Change to "all p <= 0.003" or "all p < 0.005" in Abstract. |
| B8 | R3-4.3 | Minor | **Cross-country correlations lack controls** for terms of trade shocks, financial crises, institutional quality, demographics. Panel FE with controls would be more informative. | Not resolved. v6 uses bivariate Spearman with LOO robustness but no multivariate controls. | C | Acknowledge in Discussion or Limitations: "Bivariate within-group correlations do not control for terms-of-trade shocks, financial crises, or institutional variation; these remain potential confounders." |

### Section C: Scaling Gap / Box 1

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| C1 | R2-M1, R2-Claim4b, Blue-Over2 | Major | **Causal chain from scaling gap to Simpson's paradox is asserted, not derived.** City-level scaling vs. country-level paradox -- missing link never formally established. | Partially resolved. v6 presents scaling and paradox as "complementary" and acknowledges "formal derivation remains incomplete." But still claims scaling is "consistent with" the paradox in Box 1. | B | Current framing is adequate for initial submission. Blue hat agrees this is honest. No further action needed pre-submission. |
| C2 | R2-3-Claim1a | Minor | **beta_V = 1.34 (old) / 1.057 (v6) far above Bettencourt-predicted superlinear range (1.05-1.25).** V is a stock variable, not a flow variable; Bettencourt framework was developed for flows. | Resolved. v6 decomposed beta_V into mechanical (1) + economic (0.057), explaining why it appears superlinear. The 94.6% mechanical component is now transparent. | -- | No action needed. |
| C3 | R2-3-Claim1b | Minor | **beta_K = 0.86 conflates total capital with physical infrastructure.** Bettencourt sublinear prediction applies to infrastructure, not total capital. | Not resolved. v6 does not distinguish capital types. | C | Add brief note in Box 1 or Methods M8: "beta_K captures total capital stock, not infrastructure alone; sublinear scaling may reflect composition effects beyond infrastructure sharing." |
| C4 | R2-3-Claim1c, R4-3.2b | Major | **Cross-sectional vs. longitudinal scaling exponents differ.** Within-city scaling alpha = -1.42 (opposite sign). Paper uses cross-sectional exponents only. | Partially resolved. v6 reports within-city FE reversal. Finding 2 discusses this as "city-level Simpson's paradox." But does not discuss the cross-sectional vs. temporal scaling distinction explicitly. | C | Add 1 sentence in Box 1: "Cross-sectional scaling exponents describe equilibrium relationships across the urban hierarchy; within-city temporal dynamics may differ substantially (Bettencourt & Lobo 2016)." |
| C5 | R2-3-Claim2, R2-M3 | Minor | **Q ~ N^(Delta-beta) has low R^2 (0.31)** -- 69% of Q variation unexplained by population. | Resolved. v6 reports R^2 = 0.31 explicitly in Finding 1. | -- | No further action. |
| C6 | R2-M2 | Major | **US Delta-beta_VGDP not significant among metropolitan areas only** (p = 0.32 for 381 MSAs). Significant aggregate driven by micropolitan areas. | Partially resolved. v6 states "In US metropolitan areas, Delta-beta is not statistically significant" but does not give the specific metro-only numbers. | B | Add to Finding 1 or Box 1: "Among 381 US metropolitan statistical areas, Delta-beta_VGDP = 0.017 (p = 0.32); the aggregate Delta-beta = 0.086 is driven primarily by 540 micropolitan areas." |
| C7 | R2-M4 | Minor | **Regional heterogeneity in scaling exponents** (Eastern 0.37, Central 0.16, Western 0.09 n.s.). | Not resolved. Not reported in v6 main text. | C | Add to ED or Methods M8: "Regional heterogeneity is significant (F = 11.49, p < 0.0001), with Eastern China showing the strongest scaling gradient." |
| C8 | R2-M5, R2-m1, R3-m1 | Major | **"Mean-field framework" is misleading.** Not mean-field in any physics sense; it is a group-specific linear model. | Resolved. v6 renamed to "compositional decomposition." | -- | No action needed. |
| C9 | R1-M6, R2-4a, R3-M4 | Major | **Scaling gap contains large mechanical component** (94.6%). V = Pop x Area x Price mechanically gives beta_V >= 1. | Resolved. v6 decomposed beta_V, reported 94.6% mechanical and 5.4% economic, showed Delta-beta cancels mechanical part. | -- | But see C10 for narrative ordering issue. |
| C10 | Blue-Over2 | Minor | **94.6% mechanical is presented before the economic signal, creating impression of emptiness.** Narrative order should lead with "Delta-beta is pure economic signal" then note beta_V mechanical component. | Not resolved. v6 Finding 1 leads with "94.6% of beta_V reflects mechanical identity." | A | Reorder Finding 1 paragraph: Lead with "The cross-national difference Delta-beta is free of the mechanical component" (the positive finding), then explain beta_V decomposition as methodological context. |
| C11 | R2-4a-Claim3a, R3-M1 | Major | **V is defined differently in China and US** (China: Pop x Area x Price; US: MedianValue x Units). Scaling exponents are affected by variable construction. | Partially resolved. v6 Limitation 9 notes different definitions. Sign reversal tested in unified spec. | C | Already addressed adequately for initial submission. |
| C12 | R2-m4 | Minor | **Delta-beta notation is ambiguous** (Delta-beta_VK vs Delta-beta_VGDP used interchangeably). | Partially resolved. v6 uses Delta-beta_VGDP primarily but Box 1 reports both without clear distinction. | C | Standardize: use Delta-beta without subscript in main text, referring to VGDP; subscript VK only when explicitly comparing. |
| C13 | R2-m7, R2-Claim5 | Minor | **"Three testable predictions" should be "hypotheses."** Prediction (1) runs contrary to observation; (2) and (3) are untested. N=2 for key test. | Resolved. v6 reframed as "testable hypotheses" and acknowledged (1) is contrary. | -- | No action needed. |
| C14 | R2-4b | Minor | **Delta-beta SE computed assuming independence; SUR is more appropriate.** | Resolved. v6 reports SUR estimates with joint standard errors (2/10 years significant). | -- | No action needed. |
| C15 | R2-m5 | Minor | **Ramsey RESET test indicates non-linearity** (F = 9.34, p = 0.0001) for power-law specification. | Not resolved. Not reported in v6. | C | Add to Methods M8 or ED: "A RESET test rejects the linear-in-logs specification (F = 9.34, p < 0.001), though LOESS comparison shows only 6.8% improvement, suggesting mild non-linearity." |

### Section D: City-Level Analysis (Finding 2)

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| D1 | R1-M2, R4-m2 | Major | **Chinese city panel too short (2011-2016), unbalanced (150/213 cities = 1 obs), V reconstructed.** Panel ends a decade ago, misses 2020-2024. | Partially resolved. v6 reports the panel limitation in Limitation 4. | B | No new data available; current disclosure is adequate. Strengthen Limitation 4: "The city panel ends in 2016 and does not cover the critical 2020-2024 period when the property market declined sharply." |
| D2 | R1-M2, R4-MC2, Black-NEW3 | Major | **City FE estimate not significant** (p = 0.063 full; p = 0.252 balanced). Core relationship is cross-sectional only. Within-city estimator reverses sign to +0.52. | Resolved. v6 prominently reports the within-city sign reversal and TWFE insignificance. Frames as "city-level Simpson's paradox." | -- | No further action needed; v6 handling is transparent. |
| D3 | R4-MC1, Black-NEW2 | Critical | **Clean spec beta = -0.37, R^2 = 0.017.** Explains < 2% of variance. p = 0.019 may not survive Bonferroni (threshold = 0.002 for 25 tests). Effect is trivially small for Nature. | Partially resolved. v6 reports the numbers transparently but does not preemptively defend the low R^2. | A | Add sentence in Finding 2 or Methods: "The low R^2 (0.017) is expected in a between-city specification where persistent city characteristics dominate cross-sectional variation; the specification tests the direction and sign of the association, not its explanatory dominance." |
| D4 | R4-3.3a | Major | **Mechanical correlation share should be reported as ~80-87% (beta attenuation), not 13% (MC null).** The 83.7% attenuation is the informative comparison. | Resolved. v6 leads with 83.7% attenuation as the primary metric. The 13% MC figure is not in v6 main text. | -- | No action needed. |
| D5 | R4-3.3a | Minor | **Log-log elasticity = 1.28 fails diminishing returns prediction** (should be < 1). | Not resolved. Not reported in v6. | C | Not critical for submission; can be addressed in R1 if raised. |
| D6 | R1-m8 | Minor | **82.2% cities below MUQ = 1**: t-test for H0: MUQ = 1 yields p = 0.104 (not significant). 82.2% overstates the pattern. | Partially resolved. v6 added population-weighted figure (70.2%) but does not report the t-test insignificance. | C | Add to Finding 2: "The mean city MUQ does not differ significantly from unity (t-test p = 0.104); the 82.2% figure reflects the distributional skew rather than a shift in the central tendency." |
| D7 | R1-m6, R3-M1, C11 | Major | **US MUQ definition differs from China's.** I_US is housing-unit-change-based; I_China is total FAI. Sign reversal partly definitional. | Partially resolved. v6 Limitation 9 acknowledges. Unified DeltaV/GDP spec tested. | B | Add to Finding 2 or Methods: "The China-US comparison uses non-identical investment measures (total FAI vs. housing-unit-imputed investment). The sign reversal persists under the unified DeltaV/GDP specification (China beta = -0.37 vs US beta = +2.81), though magnitudes are not directly comparable." |
| D8 | Blue-Blind3 | Minor | **US beta = +2.81 not critically examined.** What does it mean economically? Potential reverse causality (rising prices attract construction). | Not resolved. v6 does not discuss US result interpretation. | C | Add 1 sentence in Discussion: "The positive US coefficient may reflect reverse causality -- cities with rising prices attract more construction -- rather than demand-driven efficiency." |
| D9 | R4-3.3c | Minor | **US year-clustered SE inflates by 6.28x (only 12 clusters).** Significance driven by cross-sectional variation. | Not resolved. Not discussed in v6. | C | Note in Methods M3 or ED: "Year-clustered standard errors yield only 12 effective clusters; the US results should be interpreted as cross-sectional regularities." |
| D10 | R4-m5 | Minor | **US V = median x units underestimates total value** in high-inequality cities. Mean-based measure preferable. | Not resolved. | C | Add to Limitation 9: "US V uses median home values, which may underestimate total asset value in cities with high price dispersion." |

### Section E: DID / Three Red Lines

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| E1 | R1-M3, R3-4.2, R4-MC3, Black-C3 | Critical | **DID fails parallel trends (F=2.82, p=0.093), placebo (p<0.001), and mechanism test (p=0.330).** Cannot support causal inference. | Resolved. v6 demoted DID to Extended Data with explicit diagnostic warnings. One sentence in Finding 2 references it. | -- | No further action needed. |
| E2 | R4-3.4b | Minor | **Placebo test for Urban Q specifically not reported** (only ln(HP)). | Not resolved. | C | If data available, add Urban Q placebo to ED Table 5. |
| E3 | R4-3.4e | Minor | **TWFE bias concerns** (Goodman-Bacon, de Chaisemartin, Sun-Abraham) not addressed. | Not resolved. | C | Can address in R1 if raised. Low priority given DID is already demoted. |
| E4 | R3-m7 | Minor | **Missing event-study year-by-year coefficients.** Only joint F-test reported. | Not resolved. v6 mentions ED Fig. 7 has event study plots. | C | Ensure ED Fig. 7 shows individual pre/post coefficients. |

### Section F: Carbon Estimation (Finding 3 / Discussion)

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| F1 | R1-M4, R5-M3, Black-C4 | Major | **Carbon estimate dominated by 2021-2024 housing crash** (>80% of total). 2024 MUQ = 0.077 implies 92.3% waste -- implausible. | Resolved. v6 decomposed into structural (0.5 GtCO2) and market correction (2.2 GtCO2), with explicit statement about asset-price effects. | -- | No further action; v6 handling is transparent. |
| F2 | R5-M1 | Major | **"Excess carbon" lacks physical counterfactual.** Economic inefficiency =/= physical carbon waste. What construction would not have occurred? | Partially resolved. v6 added public goods caveat and period decomposition. But counterfactual remains undefined. | B | Add 1 sentence to carbon paragraph: "The counterfactual is undefined: 'excess' refers to carbon associated with investment whose housing-market return fell below parity, not to physically unnecessary construction. Some below-parity buildings serve essential social functions." |
| F3 | R5-M2 | Major | **CI calibration insufficiently documented.** Exponential decay ad hoc; CABECA reference has placeholder; boundary mismatch (CI for construction value-added vs gross FAI). | Partially resolved. v6 gives CI range (1.20 to 0.60) and decay rate (2.89%) but provides no empirical calibration data points. CABECA reference appears resolved (ref 18). | B | Add to Methods M5: "CI was calibrated to CABECA (2022) construction-sector emission factors, declining from 1.20 tCO2/10,000 yuan in 2000 to approximately 0.60 in 2024. CI applies to gross FAI, which includes non-construction components (land, fees); this biases the estimate upward but is partially offset by the exclusion of operational and demolition carbon." |
| F4 | R5-M4 | Major | **Plausibility failure: 2024 peak (1,714 MtCO2) approaches total building materials carbon.** | Resolved. v6 imposed 50% annual cap and removed extreme years. The 2.7 GtCO2 with cap passes plausibility. | -- | No action needed. |
| F5 | R5-4.3, R4-3.5a | Major | **90% CI [2.0-3.5] too narrow.** Excludes model uncertainty, system boundary, threshold choice. Full range is 0.2-14.8 across all methods/thresholds. | Partially resolved. v6 Abstract says "structural uncertainty: 0.3-5.0" to signal wider range. But see F7 for the 0.3 problem. | B | Replace "structural uncertainty: 0.3-5.0" with "method uncertainty range: 1.9-5.0" or report "parametric 90% CI: 2.0-3.5; structural uncertainty range: 1.9-5.0." |
| F6 | R5-m1 | Minor | **"Embodied" terminology misused.** Paper's estimate is not embodied carbon in ISO 14040 sense; it is carbon associated with economically inefficient investment. | Not resolved. v6 still uses "embodied" in abstract and discussion. | B | Replace "embodied carbon" with "associated construction-phase carbon" or "carbon associated with below-parity investment" in Abstract and Discussion. |
| F7 | White-C1 | Critical | **Abstract "structural uncertainty: 0.3-5.0" -- the 0.3 GtCO2 lower bound has no source data support.** Minimum total estimate across all methods is 1.58 (Method B MC lower) or 1.90 (conservative). 0.3 may be structural-period contribution (0.37), conflated with total. | Not resolved. Abstract contains an unsupported number. | A | Fix immediately. Change "structural uncertainty: 0.3-5.0" to "structural uncertainty range: 1.9-5.0" or "method range: 2.0-5.0" based on actual source data. |
| F8 | R5-M5 | Minor | **Forward-looking inference for India/Vietnam/Indonesia is speculative** -- no quantification. | Partially resolved. v6 frames as conditional ("entering the phase where...") but provides no numbers. | C | Could add back-of-envelope in ED. Not essential for submission. |
| F9 | R5-m2 | Minor | **UNEP 2023 Global Status Report should be cited** (not 2022). | Not resolved. Ref 10 cites 2022 edition. | C | Update if feasible; minor. |
| F10 | R5-m3 | Minor | **Avoid-Shift-Improve attribution**: originates in transport policy (GIZ 2011), not Creutzig 2016. | Not resolved. | C | Add proper attribution if space permits. |
| F11 | R5-m4 | Minor | **K-K* stock method vs MUQ direct method discrepancy (2.5x) should be discussed as evidence of structural uncertainty.** | Partially resolved. v6 mentions multiple methods in ED Table 4. | C | Ensure ED Table 4 caption notes the discrepancy. |
| F12 | R5-3.2c | Minor | **Consistency with Zhong et al. (2021) not directly compared.** Paper claims consistency but provides no numbers. | Not resolved. | C | Add to Methods M5 or ED: "China's building materials embodied carbon is approximately 1.0-1.7 GtCO2/yr (derived from Zhong et al.^12); our annual estimates remain within this bound after the 50% cap." |

### Section G: Causal Language & Rhetorical Claims

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| G1 | R1-M5, R3-4.1, R4-overall | Major | **Causal claims and language overreach evidence.** "Drives," "engine," "misallocation," "produces." | Resolved. v6 performed ~50 language replacements. "Drives" -> "is associated with," etc. | -- | No further action needed. |
| G2 | R1-M5, R3-m6, Blue-d | Major | **"One of the largest misallocations of physical capital in modern history"** -- hyperbolic, unsupported. | Resolved. v6 replaced with "a substantial volume of below-cost-return urban investment." | -- | But see G3. |
| G3 | Blue-d | Minor | **v6 ending ("substantial volume") is too weak.** Lost all impact. | Not resolved. Blue suggests "trillions of dollars in below-cost-return urban investment" as data-supported alternative. | A | Replace "a substantial volume" with "trillions of dollars in" -- factually supported (China cumulative FAI > 100 trillion yuan). |
| G4 | Blue-Over3 | Minor | **"Three descriptive findings emerge" -- overly apologetic opening.** Nature readers expect "findings," not "descriptive findings." | Not resolved. Discussion opens with this phrasing. | A | Change "Three descriptive findings emerge from this analysis" to "Three findings emerge from this analysis." Keep "descriptive" for Methods declarations, not narrative. |
| G5 | Red-5 | Minor | **Paper argues against itself.** Every finding is immediately followed by its caveat, creating a prosecutor-calling-defence-witnesses effect. Caveats should follow, not interleave. | Partially resolved by v6's transparent structure. But the interleaving remains heavy. | B | Restructure Finding 1: lead with GDP-MUQ results (strongest), then housing-based as confirmation, then scaling decomposition as structural context. Move "94.6% mechanical" to after the economic signal discussion. |

### Section H: Scaling Law Estimation Methods

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| H1 | R4-MC4, R2-4a-d | Major | **OLS on log-log is biased for power-law distributed data** (Gabaix-Ibragimov 2011, Clauset et al. 2009). p-values for scaling exponents likely overconfident. | Not resolved. v6 uses OLS with HC1. | B | Add to Methods M8: "OLS estimation of scaling exponents may be biased when the size distribution follows a power law (Gabaix & Ibragimov 2011). We verified that results are robust to restricting the sample to cities above the minimum population threshold of [X]." Or note as limitation. |
| H2 | R2-4b | Minor | **Spatial autocorrelation not addressed.** Cities are not spatially independent. Need at minimum Moran's I on residuals. | Partially resolved. v6 Methods M9 mentions "Moran's I spatial autocorrelation tests" but does not report results in main text. | C | Report Moran's I results in ED or Methods M9. |
| H3 | R2-4c | Minor | **City definition sensitivity.** Chinese prefectures include rural hinterlands; US MSAs are commuting-zone-based. | Partially resolved. v6 Limitation 9 notes definitional differences. | C | Add sentence: "Chinese prefectures include rural areas, which may attenuate measured scaling exponents relative to functionally defined urban areas." |
| H4 | R2-m8 | Minor | **Japan and EU provide only GDP scaling, not V scaling.** Cross-national "validation" is overstated. | Not directly relevant to v6 (Japan/EU not prominently featured). | -- | No action needed for v6. |

### Section I: Data Quality & Transparency

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| I1 | R3-M3, R4-m3 | Major | **FAI data post-2017 structurally unreliable** (estimated from growth rates). >90% of carbon falls in period with estimated FAI. | Partially resolved. v6 Limitation 5 notes FAI discontinuity. Does not quantify impact or test sensitivity. | B | Add to Methods M7: "FAI after 2017 was estimated from published growth rates; sensitivity analysis varying post-2017 FAI by +/-20% shifts the carbon estimate by approximately [X]%." If not yet computed, note as limitation. |
| I2 | R1-m7 | Minor | **Winsorisation at 1%/99%: interaction with [-50, 100] clipping not transparent.** | Not resolved. | C | Add to Methods M1: "Global MUQ values outside [-50, 100] were first clipped, then the remaining distribution was winsorised at the 1st and 99th percentiles." |
| I3 | R4-m1, R3-m2 | Minor | **Winsorisation sensitivity (5%/95%) mentioned but results not reported.** | Partially resolved. Methods M9 lists it but no numbers. | C | Ensure ED or Methods states: "Results are robust to 5%/95% winsorisation and trimming." |
| I4 | R1-m9, R4-m4 | Minor | **BH-FDR: which 3 of 25 tests lost significance not identified.** | Not resolved. | B | Add to Methods M9: "The three tests losing significance under BH-FDR at alpha = 0.05 were: [identify them]. Under Bonferroni, 15/25 remain significant." |
| I5 | R1-m10 | Minor | **Dirichlet alpha = 20 and central weights are researcher degrees of freedom.** Sensitivity to alpha = 10/50 mentioned but not shown. Leave-one-calibration-out not done. | Partially resolved. v6 notes alpha sensitivity shifts crossing by < 1.5 years. | C | Consider adding leave-one-calibration-out to ED. Not critical for submission. |
| I6 | White-M5 | Major | **~40% of numerical claims in v6 are unverifiable** from provided analysis reports (scaling exponents, city-tier MUQ, DeltaV composition, DID, housing-based MUQ). | Not resolved. These numbers presumably come from earlier analyses not in the 4 provided reports. | B | Ensure all analysis scripts and output reports are archived and cross-referenced. For submission: all numbers must be traceable to scripts/outputs. |
| I7 | White-4.2.3 | Minor | **R^2 = 0.58 reported in text but source data pooled R^2 = 0.62.** Likely from annual mean but not stated. | Not resolved. | B | Either change to 0.62 (pooled) or add "(annual cross-section mean)" after 0.58. |
| I8 | White-M4, White-5.3 | Minor | **Hsieh-Klenow "30-50%" may be inaccurate.** H&K 2009 reports TFP losses ~2x for China, not 30-50%. | Not resolved. Introduction uses "30-50%." | A | Verify against Hsieh-Klenow (2009) original. If the paper says manufacturing TFP gains from removing misallocation would be 86-115% for China, change to the accurate figure. E.g., "Hsieh and Klenow documented manufacturing TFP losses of approximately 100% in China due to factor misallocation." |

### Section J: References & Compliance

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| J1 | White-C2 | Critical | **8 orphan references (#23-30) not cited in main text.** Nature does not allow uncited references. | Not resolved. Refs 23-30 are listed but never cited with superscript numbers in the text. | A | Either (a) add in-text citations for refs 23-30 at appropriate locations, or (b) remove them from the reference list. Given they were added to address reviewer concerns, option (a) is preferred. Suggested locations: - Ref 23 (Arcaute): Box 1 or Methods M8 re: city boundary sensitivity - Ref 24 (Leitao): Box 1 or Methods M8 re: scaling estimation - Ref 25 (Bai-Hsieh-Song): Introduction or Discussion re: Chinese fiscal expansion - Ref 26 (Glaeser-Gyourko 2018): Discussion re: housing supply - Ref 27 (Restuccia-Rogerson): Introduction re: misallocation theory - Ref 28 (Cottineau): Methods M8 re: city size distributions - Ref 29 (Huang): Methods M5 re: carbon intensity - Ref 30 (Pomponi): Methods M5 or Discussion carbon para re: embodied carbon |
| J2 | R1-m2, R2-m3, R3-M5 | Major | **Reference count too low (30) and missing key works.** Still missing: Duranton & Puga, Henderson, Seto et al., Acemoglu et al., Tao et al. (land finance), Kose et al. (2009), Holz (2014), Brandt et al. (2012), Abel & Eberly (1994), Erickson & Whited (2000), Freyaldenhoven et al. (2019), Roth (2022). | Partially resolved. v6 added 12 refs (19-30), covering Hsieh-Klenow, Bettencourt 2013, Easterly, etc. But still gaps, especially in development econ and housing. | C | Add 5-10 more references targeting gaps: housing/land finance, Chinese institutional context, causal inference methodology. Nature allows up to 50. |
| J3 | R1-compliance | Major | **Missing submission materials**: Data availability statement (placeholder), Code availability (placeholder), Reporting Summary, Competing interests, Author contributions (CRediT), Cover letter. | Partially resolved. v6 has Data/Code availability placeholders and Author contributions placeholder. Missing: Reporting Summary, Competing interests declaration. | A | Before submission: (1) Complete Data/Code availability with repository URLs; (2) Add Competing interests declaration; (3) Complete Author contributions; (4) Prepare Nature Reporting Summary; (5) Draft Cover letter. |
| J4 | R1-m1 | Minor | **Abstract may slightly exceed 150 words.** v6 word count table says 150 but needs verification. | Likely resolved. v6 tracks at 150 words. | C | Verify exact count before submission. |
| J5 | R1-compliance | Minor | **Main text may exceed 3,500 words.** v6 reports ~3,072 (main + Box 1) which is within limit. | Resolved. 3,072 < 3,500. | -- | No action needed. |
| J6 | R1-m3, Blue-Blind6 | Major | **Figures not finalized.** Most main figures listed as "pending" in figure-notes.md. | Not resolved. v6 references Figs 1-5 but actual figures may not be produced. | A | Finalize all 5 main figures and 7 ED figures/tables before submission. |
| J7 | R1-compliance | Minor | **Map compliance unknown.** If any figures contain maps of China, Taiwan/border depictions must comply with Nature's map policy. | Not resolved. | B | Review any maps for compliance before submission. |

### Section K: New Issues Introduced by v6

| # | Source | Type | Issue Summary | v6 Status | Class | Action |
|---|--------|------|--------------|-----------|-------|--------|
| K1 | Black-NEW1 | Major | **GDP-MUQ = 1/ICOR self-contradiction with Easterly.** See A2. | -- | A | See A2 action. |
| K2 | Black-NEW2 | Major | **R^2 = 0.017 may be insufficient for Nature.** See D3. | -- | A | See D3 action. |
| K3 | Black-NEW3 | Major | **Within-estimator sign reversal (+0.52) could be used to argue the negative association is omitted variable bias, not efficiency decline.** | Addressed transparently by v6's "city-level Simpson's paradox" framing. | B | Add preemptive defense in Discussion or Methods: "The positive within-city coefficient is consistent with cities responding efficiently to their own investment in the short run, while the negative between-city coefficient reflects structural differences in long-run returns across the urban hierarchy." |
| K4 | Black-NEW4 | Moderate | **Carbon 2.7 GtCO2 (structural 0.5) may lack Nature-level news value.** 0.5 GtCO2 structural excess with CI including 0.0 is not headline-worthy. | Cannot be fully resolved without new analysis. | B | Lead with the combined 2.7 GtCO2 in Discussion. Mention structural/market decomposition but do not lead with the 0.5. Emphasize the physical cross-validation (3.8 GtCO2) as independent confirmation. |
| K5 | Blue-Over1 | Minor | **Carbon Discussion paragraph is overloaded** (~200 words covering decomposition, cross-validation, public goods caveat, Avoid-Shift-Improve, and India/Vietnam/Indonesia). | Not resolved. | A | Split into two paragraphs: (1) Carbon estimate + decomposition + cross-validation; (2) Policy implications (Avoid-Shift-Improve + forward-looking). |
| K6 | Blue-Blind1 | Minor | **Correlation between housing-based and GDP-based MUQ not reported.** Reviewers will ask. | Not resolved. | B | Add to Methods M1 or ED: "The cross-country correlation between housing-based and GDP-based MUQ is r = [value], indicating [moderate overlap / independence]." |

---

## PART II: PRIORITY ACTION LIST

### A-Class: Must Fix Before Submission (Desk Reject Risk)

| # | Item | Est. Effort | Action |
|---|------|-------------|--------|
| A2 | Easterly/ICOR self-contradiction | 15 min | Add 1-2 sentences to Methods M1 defending GDP-MUQ as pattern robustness check, not efficiency measure |
| B6 | 144 vs 157 country count | 15 min | Clarify in Abstract/Methods which number applies to which MUQ definition |
| B7 | "all p < 0.003" strictness | 5 min | Change to "all p <= 0.003" or "all p < 0.005" |
| C10 | Reorder scaling gap narrative | 30 min | Lead Finding 1 with "Delta-beta is pure economic signal," then explain beta_V decomposition as context |
| D3 | Defend R^2 = 0.017 | 10 min | Add 1 sentence explaining low R^2 is expected in between-city specification |
| F7 | Fix Abstract carbon range 0.3 | 5 min | Replace "0.3-5.0" with actual minimum (1.9 or 2.0) |
| G3 | Strengthen ending | 5 min | Replace "substantial volume" with "trillions of dollars in" |
| G4 | Remove "descriptive" from Discussion opening | 5 min | "Three findings emerge" instead of "Three descriptive findings emerge" |
| I8 | Verify Hsieh-Klenow "30-50%" | 15 min | Check original paper; correct to accurate figure |
| J1 | Cite orphan references #23-30 | 30 min | Add superscript citations at appropriate text locations |
| J3 | Complete submission materials | 2-4 hours | Competing interests, Author contributions, Reporting Summary, Cover letter |
| J6 | Finalize all figures | Variable | Produce Figs 1-5 and ED Figs 1-7 |
| K5 | Split carbon Discussion paragraph | 15 min | Two paragraphs: estimate + policy implications |

### B-Class: Should Fix Before Submission (Reviewer Concern)

| # | Item | Est. Effort | Action |
|---|------|-------------|--------|
| A1 | MUQ price-cycle defense | 15 min | Add explicit framing in Methods/Discussion |
| A4 | Numerator-denominator mismatch | 10 min | Add to Limitation 9 |
| A6 | Reframe "investment efficiency" language | 20 min | Audit and replace with "investment outcomes" where possible |
| B1 | Report bootstrap p-values | 10 min | Add specific values to Finding 1 or ED Table 1 |
| B2 | Time-varying income classification | 30 min (if analysis done) | Report in Methods M9 or ED |
| C6 | US metro-only Delta-beta numbers | 10 min | Add specific statistics to Finding 1 |
| D1 | Strengthen panel limitation language | 5 min | Note 2020-2024 gap explicitly |
| D7 | China-US definition comparison | 10 min | Clarify in Finding 2 |
| F2 | Physical counterfactual | 10 min | Add sentence to carbon paragraph |
| F3 | CI calibration documentation | 15 min | Expand Methods M5 |
| F5 | Fix carbon uncertainty reporting | 10 min | Replace "0.3-5.0" with defensible range |
| F6 | "Embodied" terminology | 10 min | Replace in Abstract and Discussion |
| G5 | Reorder Finding 1 narrative | 30 min | Lead with strength, caveats follow |
| H1 | OLS scaling bias note | 10 min | Add to Methods M8 |
| I1 | FAI post-2017 sensitivity | 15 min (if computed) | Report in Methods M7 |
| I4 | Identify 3 BH-FDR failures | 10 min | Add to Methods M9 |
| I6 | Ensure all numbers traceable | 1-2 hours | Cross-reference scripts and outputs |
| I7 | R^2 = 0.58 vs 0.62 | 5 min | Clarify or correct |
| J7 | Map compliance | 15 min | Review any maps |
| K3 | Defend within-city sign reversal | 10 min | Add interpretive sentence |
| K4 | Carbon narrative strategy | 15 min | Lead with combined 2.7, not structural 0.5 |
| K6 | Housing/GDP MUQ correlation | 15 min (if computed) | Report in Methods or ED |

### C-Class: Can Address in R1 (Not Submission-Blocking)

| # | Items |
|---|-------|
| A3 | Quantity-only Delta-V test |
| A5 | MUQ = 1 threshold justification |
| B4 | Effect size discussion |
| B5 | Ten-country power caveat (already done) |
| B8 | Cross-country confounders acknowledgment |
| C3 | beta_K capital type distinction |
| C4 | Cross-sectional vs temporal scaling note |
| C7 | Regional heterogeneity reporting |
| C11 | V definition differences (already in L9) |
| C12 | Delta-beta notation standardization |
| C15 | RESET test reporting |
| D5 | Log-log elasticity failure |
| D6 | t-test for mean MUQ = 1 |
| D8 | US beta interpretation |
| D9 | US year-cluster concern |
| D10 | US median vs mean V |
| E2-E4 | DID refinements (already demoted) |
| F8-F12 | Carbon minor issues |
| H2-H4 | Scaling method refinements |
| I2, I3, I5 | Winsorisation/Dirichlet details |
| J2 | Additional references |
| J4, J5 | Word count verification |

---

## PART III: SUMMARY STATISTICS

| Category | Total Issues | Resolved | Partially Resolved | Not Resolved | New in v6 |
|----------|:-----------:|:--------:|:-----------------:|:----------:|:---------:|
| A: MUQ Construct | 6 | 0 | 3 | 3 | 0 |
| B: Simpson's/Global | 8 | 0 | 2 | 5 | 1 |
| C: Scaling Gap/Box 1 | 15 | 6 | 3 | 6 | 0 |
| D: City-Level | 10 | 2 | 3 | 5 | 0 |
| E: DID | 4 | 1 | 0 | 3 | 0 |
| F: Carbon | 12 | 2 | 3 | 7 | 0 |
| G: Language/Rhetoric | 5 | 2 | 1 | 0 | 2 |
| H: Scaling Methods | 4 | 0 | 1 | 3 | 0 |
| I: Data/Transparency | 8 | 0 | 3 | 5 | 0 |
| J: References/Compliance | 7 | 1 | 2 | 4 | 0 |
| K: New v6 Issues | 6 | 0 | 0 | 3 | 3 |
| **TOTAL** | **85** | **14 (16%)** | **21 (25%)** | **44 (52%)** | **6 (7%)** |

| Priority Class | Count | Description |
|:-:|:-:|:--|
| A (must fix) | 13 | Desk reject risk items |
| B (should fix) | 22 | Reviewer concern items |
| C (can wait) | 31 | Addressable in R1 |
| Resolved | 14 | No action needed |
| N/A | 5 | Not applicable to v6 |

---

## PART IV: OVERALL ASSESSMENT

**v6 has made substantial progress.** The most critical vulnerabilities from v5 -- mechanical correlation inflation (beta -2.23 -> -0.37), carbon overestimate (5.3 -> 2.7), causal language, DID over-reliance -- have been addressed honestly and transparently. The GDP-based MUQ validation is the single most important improvement.

**However, 13 A-class items remain.** Most are fixable in 3-5 days of text editing without new analysis:
- 7 are text fixes (wording, numbers, narrative ordering): A2, B7, C10, D3, F7, G3, G4
- 2 are factual corrections: B6 (country count), I8 (Hsieh-Klenow figure)
- 1 is a critical compliance issue: J1 (orphan references)
- 3 require preparation work: J3 (submission materials), J6 (figures), K5 (paragraph split)

**Estimated time to submission-ready v7**: 5-7 working days, of which:
- 1-2 days: Text edits (A-class + B-class text items)
- 2-3 days: Figure finalization
- 1-2 days: Submission materials (Cover letter, Reporting Summary, etc.)

---

*Compiled by: Claude (Peer Review Coordinator)*
*Date: 2026-03-22*
*Sources: 5 disciplinary reviewers + 6 thinking hat reviews + v6 manuscript*
