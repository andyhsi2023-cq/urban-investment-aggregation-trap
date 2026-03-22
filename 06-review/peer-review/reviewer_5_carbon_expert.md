# Reviewer 5: Carbon Accounting & Climate Science Expert Review

## Manuscript: "Simpson's paradox masks declining returns on urban investment worldwide"
## Target Journal: Nature (main journal)
## Review Date: 2026-03-21
## Reviewer Expertise: Building lifecycle carbon accounting, embodied carbon, emission inventories, IPCC AR6 WG3, LCA standards (ISO 14040/14044, EN 15978)

---

## 1. Overall Assessment

This manuscript introduces a novel "Marginal Urban Q" (MUQ) framework to diagnose investment efficiency decline across countries, and as a secondary contribution, estimates the carbon cost of below-unity MUQ investment in China at approximately 5.3 GtCO2 (90% CI: 4.3--6.3). From a climate science and carbon accounting perspective, the carbon dimension is conceptually innovative -- linking investment efficiency metrics to embodied carbon is a genuinely new contribution that could bridge urban economics and climate mitigation literatures. However, the carbon estimation methodology, while improved over earlier versions (the shift from a constant-CI K-K* stock method to an MUQ-based direct method with time-varying carbon intensity was a significant upgrade), contains several methodological issues that range from moderate to potentially serious. The core concern is that this is not a lifecycle carbon assessment in any conventional sense; it is an economic efficiency metric re-expressed in carbon units, and the manuscript does not sufficiently distinguish between the two.

The 5.3 GtCO2 headline number is striking and policy-relevant, but it conflates "carbon associated with economically inefficient investment" with "physically excess carbon emissions." These are not the same thing: a building that generates below-cost asset returns still provides shelter, still stores materials, and still displaces alternative housing that would have been built elsewhere. The counterfactual is underspecified. This is not a fatal flaw -- the paper explicitly states limitations (MUQ measures asset market value, not social value; below-MUQ-1 investment may generate positive externalities) -- but the framing in the Abstract and Discussion ("embodied approximately 5.3 GtCO2") needs to be much more carefully hedged than it currently is.

**Competitiveness for Nature**: The carbon accounting component, as a supporting finding within a broader economics paper, is adequate for Nature if the methodological caveats are made explicit. As a standalone carbon estimate, it would not survive peer review at Nature Climate Change or ES&T without substantially more rigorous lifecycle boundary definition and counterfactual analysis.

---

## 2. Scoring (0--10)

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| **Methodological soundness** | 5.5 | The MUQ-based direct method is a reasonable first-order approach, but lacks lifecycle boundary coherence, counterfactual specification, and process-based validation. The exponential decay CI model is ad hoc. |
| **Uncertainty quantification** | 6.0 | Monte Carlo with 10,000 iterations covers parametric uncertainty well. However, structural uncertainty (model choice, system boundary, counterfactual) is not propagated and likely dominates. The 90% CI [4.3, 6.3] is almost certainly too narrow. |
| **Policy relevance** | 7.5 | The "Avoid" tier framing within Avoid-Shift-Improve is compelling and original. MUQ as an ex ante screening tool for carbon-wasteful construction is a genuinely useful policy concept. |
| **Novelty** | 8.0 | No prior work has linked investment efficiency metrics to embodied carbon at this scale. The conceptual bridge between Tobin's Q and carbon accounting is new. |

---

## 3. Carbon Accounting Method Review -- Step by Step

### 3.1 Definition of "Excess Construction Carbon"

**Method**: excess_I(t) = I(t) * max(0, 1 - MUQ(t)); carbon(t) = excess_I(t) * CI(t)

**Assessment**: This definition equates "economically inefficient investment" with "carbon waste." The logic is: when MUQ < 1, each yuan of investment generates less than one yuan of asset value, so the fraction (1 - MUQ) is "wasted." The carbon associated with this wasted fraction is then deemed excess.

**Problems**:

(a) **Missing counterfactual**: If China had not built those "excess" structures, what would have happened? The carbon is not truly "excess" unless the counterfactual is zero construction. In practice, some fraction of below-MUQ-1 construction serves real housing demand, replaces informal or substandard housing, or provides public infrastructure (schools, hospitals, transit). The paper acknowledges this in the limitations paragraph but the headline number does not reflect it.

(b) **MUQ < 1 does not mean MUQ = 0**: The formula treats (1 - MUQ) as a waste fraction, but this implies a linear relationship between economic inefficiency and physical carbon waste. A building with MUQ = 0.8 generates 80% of its cost in asset value -- is 20% of its carbon truly "wasted"? The building still exists, still provides services, still stores embodied carbon in its materials. The conceptual leap from "below-cost return" to "excess carbon" needs much more justification.

(c) **Temporal concentration problem**: The report shows >90% of the 5.3 GtCO2 falls in 2021--2024, when MUQ collapsed (reaching 0.232 in 2022 and 0.077 in 2024). This period coincides with China's property market downturn and asset price crash. The MUQ decline in 2022--2024 is substantially driven by falling asset prices (Delta-V denominator), not by physical overbuilding. The carbon was physically emitted at the time of construction, but MUQ is computed ex post based on market valuations. A building constructed in 2022 at MUQ = 0.23 embodied its carbon regardless of what happens to housing prices in 2023. The paper's approach assigns carbon "waste" based on realized market outcomes, which introduces a circular dependency: if housing prices recover, the "excess" carbon retrospectively shrinks.

### 3.2 Carbon Intensity (CI) Model

**Model**: CI(t) = 1.20 * exp(-0.0289 * (t - 2000)), declining from 1.20 to 0.60 tCO2/10,000 yuan over 2000--2024.

**Assessment**:

(a) **Boundary mismatch**: The CI parameter is described as "tCO2 per 10,000 yuan of fixed-asset investment" (construction-sector emission factor). Fixed-asset investment in China (FAI) includes land acquisition costs, developer margins, financing costs, and fees -- none of which have direct carbon content. The physically carbon-intensive component is materials and on-site energy, which is a subset of FAI. The CABECA emission factors likely refer to construction activity value-added, not gross FAI. If CI is calibrated to construction value-added but applied to gross FAI, the result will overestimate carbon by a factor that depends on the value-added-to-FAI ratio (typically 0.3--0.5 in China). **This is a potentially serious error** -- though it is partially offset by the claim that the estimate is a "conservative lower bound."

(b) **Exponential decay justification**: The 1.20-to-0.60 range and 2.89% annual decay are described as "calibrated to construction-sector emission factors from CABECA." However, no empirical data points are provided to validate the exponential functional form. IEA data show that China's construction carbon intensity has declined, but the trajectory is not smooth: there were periods of stagnation (2010--2015) and acceleration (post-2020 due to cement decarbonization). A piecewise linear or step-function model would be more defensible.

(c) **Consistency with Zhong et al. (2021)**: The manuscript claims consistency with Zhong et al. but does not provide a direct comparison. Zhong et al. report embodied carbon in building materials (scope: cradle-to-gate for steel, cement, aluminum, glass, etc.) at approximately 2.5--3.5 GtCO2/yr globally for all buildings. China accounts for roughly 40--50% of global cement and steel production, suggesting Chinese building materials embodied carbon of ~1.0--1.7 GtCO2/yr. The manuscript's peak year (2024) shows 1,714 MtCO2 in "excess" construction carbon alone, which would imply that nearly all of China's building materials carbon is "excess." This fails a basic plausibility test.

(d) **The 0.65 tCO2/10,000 yuan constant used in the initial script (37_carbon_dimension.py) versus the 0.60--1.20 range in the revised script (93_carbon_uncertainty.py)**: The initial script using a constant 0.65 yielded 13.4 GtCO2 -- 2.5x the revised estimate. This discrepancy itself reveals the sensitivity to CI assumptions and underscores the importance of getting CI right.

### 3.3 System Boundary

**Stated scope**: "Construction-phase embodied carbon only."

**Assessment**:

(a) The paper correctly notes this is a lower bound excluding operational carbon, demolition, and material extraction. However, in standard lifecycle assessment terminology (ISO 14040/14044; EN 15978), "construction-phase embodied carbon" corresponds to modules A1--A5 (product stage + construction process). The paper's CI appears to capture only a subset of this -- likely A1--A3 (cradle-to-gate materials) based on CABECA factors, excluding A4 (transport to site) and A5 (construction installation). This should be stated explicitly.

(b) The exclusion of B1--B7 (operational energy, maintenance, refurbishment) and C1--C4 (demolition, waste processing) is standard for embodied carbon estimates but means the "5.3 GtCO2" figure understates the full lifecycle carbon of excess construction. If operational carbon is included, the figure could be 2--3x larger (IEA estimates operational carbon is approximately 2x embodied carbon for buildings in China). The paper mentions this is a "conservative lower bound" but should quantify the magnitude of what is excluded.

(c) **No distinction between building types**: Residential, commercial, and infrastructure construction have very different carbon intensities (kg CO2/m2 ranges from ~200 for low-rise residential to ~800 for high-rise commercial in China, per Huang et al. 2018). FAI includes all types. The uniform CI assumption introduces heterogeneity bias.

### 3.4 The "1.5 Years of Global Building Embodied Carbon" Comparison

**Claim**: 5.3 GtCO2 "corresponds to approximately 1.5 years of global building embodied emissions."

**Assessment**: The reference baseline is "3.5--4.0 GtCO2 annually" from UNEP GlobalABC (2022) and IPCC (2022). Several issues:

(a) The UNEP 2022 Global Status Report cites approximately 3.6 GtCO2 for building construction industry (direct + indirect) in 2021. This figure includes both embodied carbon and construction-process energy, and covers the global total, not just new construction. The 5.3 GtCO2 figure is a 25-year cumulative for one country versus an annual global figure -- the "1.5 years" framing is arithmetically correct but potentially misleading because the temporal scales are incommensurable. A more informative comparison would be: "5.3 GtCO2 over 25 years represents approximately X% of China's total building-sector embodied emissions over the same period."

(b) The IPCC AR6 WG3 Chapter 9 (Buildings) reports embodied carbon from building materials at approximately 3.5 GtCO2-eq/yr (including process emissions from cement and steel). However, this is CO2-equivalent including non-CO2 GHGs, while the paper's estimate appears to be CO2-only. The comparison should note this unit difference.

---

## 4. Uncertainty Review

### 4.1 What Is Covered

The Monte Carlo framework samples from three uncertainty sources:
1. MUQ ensemble weights (via Q's MC distribution, propagated through a log-normal approximation)
2. CI base level (normal, SD = 0.15)
3. CI decay rate (normal, mean = 0.0289, SD = 0.005)

This is competent parametric uncertainty propagation. The 10,000 iterations are sufficient for convergence at the 90% level.

### 4.2 What Is Missing

**Structural/model uncertainty** -- the dominant source -- is not propagated through MC:

(a) **Counterfactual uncertainty**: The choice of MUQ = 1 as the threshold between "efficient" and "excess" is one of infinitely many possible thresholds. The sensitivity analysis varies this from 0 to 1.2 (yielding 0.2--7.4 GtCO2), which is informative, but this is a discrete scenario analysis, not a probabilistic uncertainty propagation. The "true" threshold depends on the counterfactual, which is undefined.

(b) **MUQ definition uncertainty**: The paper uses seven calibration variants for Q, combined via Dirichlet-weighted ensemble. But all seven share the same fundamental approach (V/K). Alternative definitions of "investment efficiency" (e.g., social return on investment, cost-benefit ratio including externalities, physical occupancy-based metrics) could yield very different "excess" fractions.

(c) **System boundary uncertainty**: The difference between the K-K* stock method (13.4 GtCO2) and the MUQ direct method (5.3 GtCO2) is a factor of 2.5x. This is a structural choice, not a parametric variation, and it is not reflected in the 90% CI.

(d) **CI functional form uncertainty**: Exponential decay is one assumption; linear, logistic, or data-driven trajectories could yield different cumulative carbon. The decay rate sensitivity analysis (2.7--9.7 GtCO2 range) shows this is the most influential parameter class, yet the 90% CI (4.3--6.3) does not span this range.

### 4.3 Is the 90% CI [4.3, 6.3] Too Narrow?

**Yes, almost certainly.** The full range of defensible estimates spans at least 1.3--8.0 GtCO2 (Method C's 90% CI), and the scenario range is 0.2--14.8 GtCO2. The reported 90% CI of [4.3, 6.3] reflects parametric uncertainty conditional on the MUQ direct method with a fixed functional form for CI, a fixed system boundary, and a fixed threshold definition. It does not capture the structural uncertainty that dominates.

**Recommendation**: Report the MC CI as the primary uncertainty bound for the MUQ-based estimate, but add a clearly labeled "structural uncertainty range" or "method uncertainty range" that spans at least [1.3, 8.0] GtCO2 (from Method C). Ideally, present the full scenario range (0.2--14.8 GtCO2) as the outer bound, with the 5.3 GtCO2 [4.3, 6.3] as the central estimate under preferred assumptions.

### 4.4 Independence Assumption

The paper states that MUQ, CI level, and CI decay rate are sampled independently, acknowledging that "in practice, MUQ and carbon intensity may co-vary through construction-sector activity levels." This is correct: during construction booms (high I, potentially low MUQ), carbon intensity may actually increase due to rushed construction, lower quality control, and increased demand for carbon-intensive materials like cement. Conversely, during downturns, only higher-quality (lower-CI) projects may proceed. The direction of the bias from independent sampling is ambiguous, and the claim that independent sampling is "conservative" is not substantiated.

---

## 5. Major Concerns

### M1. The "Excess Carbon" Concept Lacks a Physical Counterfactual

**Problem**: The paper defines "excess construction carbon" as carbon associated with below-MUQ-1 investment. This is an economic definition, not a physical one. In carbon accounting, "excess emissions" requires a counterfactual baseline (ISO 14064-2; GHG Protocol). What would emissions have been in the absence of the "excess" investment? If the counterfactual is zero construction, then 100% of below-MUQ-1 investment carbon is excess. If the counterfactual is efficient construction (same floor area at optimal cost), then only the cost overrun fraction is excess. If the counterfactual is reduced construction volume (fewer buildings), then excess carbon equals the difference. The paper does not specify.

**Literature**: The GHG Protocol's Project Quantification Standard requires explicit baseline scenarios for claiming emission reductions or excess emissions. The concept of "avoided emissions" in IPCC AR6 WG3 Chapter 12 similarly requires counterfactual specification.

**Recommendation**: Define explicitly what "excess" means in physical terms. At minimum, distinguish between (a) carbon from buildings that should never have been built (true waste -- vacant, uninhabitable, demolished within 5 years) and (b) carbon from buildings that were built inefficiently (overbuilt but occupied). If data on vacancy rates, demolition rates, or occupancy are available, use them to calibrate the counterfactual. Without this, the 5.3 GtCO2 is an upper bound on economic inefficiency re-expressed in carbon units, not a measure of physically wasted carbon.

### M2. Carbon Intensity Calibration Is Insufficiently Documented

**Problem**: The CI model (1.20 to 0.60 tCO2/10,000 yuan, exponential decay) is attributed to CABECA (2022) and described as "consistent with" IEA and Zhong et al. (2021), but no empirical calibration data are provided. The manuscript reference for CABECA (Ref 18) has an unresolved placeholder ("[reference]" in Methods M5). The exponential functional form is assumed without empirical justification.

**Literature**: Huang et al. (2018, *Applied Energy* 238: 442-452) provide process-based carbon intensity data for Chinese building construction by type and year. Hong et al. (2015, *Energy* 87: 116-125) provide lifecycle carbon intensity for Chinese residential buildings. These data show non-monotonic trends.

**Recommendation**: (a) Provide the actual data points used to calibrate the CI model (at minimum: CI values for 2000, 2005, 2010, 2015, 2020, 2024 from CABECA or comparable sources). (b) Test at least one alternative functional form (piecewise linear, logistic). (c) Clarify whether CI applies to gross FAI or construction value-added, and adjust accordingly.

### M3. The 2021--2024 Carbon Spike Is Dominated by Asset Price Effects, Not Physical Overbuilding

**Problem**: The uncertainty report shows that >90% of the 5.3 GtCO2 falls in 2021--2024. In 2022, MUQ = 0.232, implying 76.8% of investment was "wasted." In 2024, MUQ = 0.077, implying 92.3% waste. These extreme values coincide with China's property market crash, where Delta-V turned sharply negative due to falling housing prices. The physical construction volume in 2022--2024 actually declined (floor area completions fell ~20--30% from the 2020 peak). The "excess carbon" in 2022--2024 is therefore largely driven by asset revaluation losses, not by physical overbuilding.

**Implication**: If housing prices recover (even partially), the cumulative "excess carbon" would retrospectively shrink. This means the 5.3 GtCO2 is not a physical quantity -- it is a market-contingent calculation. From a climate science perspective, CO2 emissions are a physical stock in the atmosphere that does not change when housing prices recover. The conceptual mismatch is fundamental.

**Recommendation**: (a) Decompose the 5.3 GtCO2 into a "physical overbuilding" component (based on vacancy rates, demolition, or physical excess relative to demographic need) and a "market revaluation" component (based on asset price changes). (b) At minimum, present a variant that caps MUQ at some floor (e.g., MUQ >= 0) to prevent negative MUQ from driving the estimate, or use a lagged/smoothed MUQ to filter out short-term price volatility.

### M4. Plausibility Check: Peak Year Exceeds Total Building Materials Carbon

**Problem**: The 2024 peak of 1,714 MtCO2 in "excess" carbon implies that 92.3% of China's construction investment in 2024 was carbon-wasteful. China's total building construction industry direct emissions are approximately 500--800 MtCO2/yr (CABECA 2022; IEA 2023), and embodied carbon in building materials (cement, steel, aluminum) is approximately 1,500--2,000 MtCO2/yr (derived from Zhong et al. 2021 and IPCC AR6). If 1,714 MtCO2 is "excess" from below-MUQ-1 investment alone, this would consume nearly all of China's building materials embodied carbon -- implying essentially zero efficient construction in 2024. This fails a basic plausibility test.

**Root cause**: The MUQ in 2024 (0.077) is an outlier driven by the property market crash. Using it as a physical efficiency metric produces implausible carbon numbers.

**Recommendation**: Either (a) cap the analysis at 2021 (before the asset price crash dominates), (b) use a physically-grounded efficiency metric (vacancy rate, utilization rate) rather than MUQ for the carbon calculation, or (c) clearly state that the 2022--2024 estimates are "market-value-adjusted" figures that should not be interpreted as physical carbon waste.

### M5. Forward-Looking Inference for India/Vietnam/Indonesia Is Speculative

**Problem**: The manuscript states: "India, Vietnam, and Indonesia, with combined population exceeding 1.8 billion and urbanisation rates of 35--58%, are in the phase where the scaling gap predicts accelerating efficiency divergence. Whether they accumulate comparable carbon debts depends on the same supply-versus-demand distinction." This is framed as a conditional prediction, which is appropriate, but lacks even order-of-magnitude scenario analysis.

**Recommendation**: At minimum, provide a back-of-envelope calculation: "If India's construction investment reaches X trillion USD/yr and MUQ follows China's trajectory with a Y-year lag, the implied carbon accumulation would be Z GtCO2 over 2025--2050." Without this, the forward-looking claim is rhetorical rather than analytical.

---

## 6. Minor Concerns

### m1. "Embodied" Terminology

The paper uses "embodied approximately 5.3 GtCO2" in the Abstract and Introduction. In LCA terminology, "embodied carbon" has a specific meaning (A1--A5 or A1--A3 lifecycle stages). The paper's estimate is not really "embodied carbon" in this sense -- it is "carbon associated with economically inefficient investment." Suggest using "associated with" or "attributable to" rather than "embodied."

### m2. Comparison with UNEP GlobalABC

The manuscript cites the UNEP 2022 Global Status Report. The 2023 edition (published November 2023) provides updated figures and should be cited as the most recent available data.

### m3. Creutzig et al. (2016) Citation

The "Avoid-Shift-Improve" framework is attributed to Creutzig et al. (2016). While Creutzig's work discusses demand-side mitigation, the Avoid-Shift-Improve hierarchy originates in transport policy (GIZ 2011; Dalkmann & Brannigan 2007). In the buildings context, the more relevant framing may be from IEA (2019) or the IPCC AR6 WG3 Chapter 9 SPM contribution. Suggest verifying the attribution.

### m4. The K-K* Stock Method vs. MUQ Direct Method Discrepancy

The initial analysis (script 37) using constant CI and K-K* stock method yields 13.4 GtCO2. The revised MUQ-based analysis yields 5.3 GtCO2. The manuscript correctly uses the revised estimate, but the 2.5x discrepancy between methods should be discussed more prominently as evidence of structural uncertainty. Currently, this appears only in Extended Data.

### m5. Monte Carlo Seed and Reproducibility

The MC seed is set to 20260321 (a future date). This is cosmetic but unusual. More importantly, the code uses `np.random.seed()` (legacy API) rather than `np.random.default_rng()` (recommended since NumPy 1.17). This does not affect results but may affect reproducibility across NumPy versions.

### m6. Missing References

The carbon accounting section would benefit from citing:

- Huang, L. et al. Carbon emission of global construction sector. *Renewable and Sustainable Energy Reviews* 81, 1906--1916 (2018). [Process-based CI data for China]
- Pomponi, F. & Moncaster, A. Scrutinising embodied carbon in buildings: The next performance gap made manifest. *Renewable and Sustainable Energy Reviews* 71, 307--316 (2017). [System boundary issues]
- Roebbel, N., et al. Health & Energy Efficiency in Buildings. WHO, 2023. [Health co-benefits of avoiding excess construction]

---

## 7. Summary Evaluation Table

| Aspect | Rating | Comment |
|--------|--------|---------|
| Conceptual innovation | Strong | Linking investment efficiency to carbon accounting is genuinely new |
| CI calibration | Weak | Insufficiently documented, ad hoc functional form, potential boundary mismatch |
| Counterfactual specification | Absent | No physical counterfactual defined |
| System boundary definition | Moderate | Stated as construction-phase only, but not mapped to ISO/EN modules |
| Parametric uncertainty | Adequate | MC with 10,000 iterations covers CI and MUQ parametric variation |
| Structural uncertainty | Inadequate | Model choice, boundary, and threshold uncertainty not propagated; 90% CI too narrow |
| Plausibility of headline number | Questionable for 2022--2024 | 2024 peak (1,714 Mt) exceeds total building materials carbon; driven by market crash |
| Policy relevance | Strong | MUQ as Avoid-tier screening tool is a useful concept |
| Forward-looking analysis | Speculative | India/Vietnam/Indonesia claims lack even order-of-magnitude quantification |

---

## 8. Recommended Decision

**Major Revision** -- with the following conditions:

The carbon dimension is a valuable supporting finding that strengthens the paper's policy relevance. However, in its current form, the carbon estimate risks being misinterpreted as a physical LCA result rather than what it is: an economic efficiency metric re-expressed in carbon units. The following revisions are necessary before the carbon findings can withstand scrutiny from the climate science community:

1. **Define the physical counterfactual** (M1): What construction would not have occurred under an efficient investment regime? Use vacancy data, demolition rates, or demographic need to anchor the counterfactual.

2. **Decompose the 2021--2024 spike** (M3): Separate asset-price-driven MUQ decline from physical overbuilding. Present at minimum a variant that smooths or caps MUQ to filter market volatility.

3. **Document CI calibration** (M2): Provide empirical data points, clarify whether CI applies to gross FAI or construction value-added, and test an alternative functional form.

4. **Widen the reported uncertainty** (Section 4.3): The 90% CI should reflect structural uncertainty, not just parametric uncertainty. Report a "method uncertainty range" alongside the MC CI.

5. **Conduct a plausibility check** (M4): Compare the implied carbon against independent estimates of China's total building embodied carbon to verify that the numbers are physically possible year by year.

6. **Soften the "embodied" language** (m1): Use "associated with" rather than "embodied" to avoid implying ISO-standard LCA methodology.

If these revisions are made, the carbon component would be a credible and impactful supporting analysis. Without them, it is the most vulnerable section of an otherwise strong paper.

---

*Reviewer disclosure: No conflicts of interest. This review focuses exclusively on the carbon accounting and climate science dimensions (Finding 3, Methods M5, Discussion paragraphs on carbon). I defer to other reviewers on the investment economics, Simpson's paradox methodology, and city-level efficiency analysis.*
