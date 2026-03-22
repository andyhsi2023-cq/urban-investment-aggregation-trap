# Revision Strategy v1: Response to Five-Reviewer Internal Assessment

**Paper**: Simpson's paradox masks declining returns on urban investment worldwide
**Target**: Nature (main journal)
**PI Decision Date**: 2026-03-21
**Estimated Revision Period**: 45--55 working days

---

## Part 1: Strategic Decisions

### Q1: MUQ Reconstruction Strategy

**Decision: Option D (A+B+C), with C as primary and A+B as robustness architecture**

#### Analysis of Options

| Option | Pros | Cons | Data availability | Work (days) |
|--------|------|------|-------------------|:-----------:|
| A: Quantity-effect-only MUQ | Cleanly removes price cycle contamination; directly addresses R1-M1 and R5-M3 | Only feasible for China (DeltaV decomposition available) and US (price/quantity separable); global panel cannot be decomposed | China: available (script 85 already decomposes). US: available. Global: **not feasible** | 5--7 |
| B: GDP-based MUQ (1/ICOR) | Addresses R3's concern about housing-only numerator; GDP is a flow measure immune to asset price cycles; globally constructible | ICOR has well-known problems (Easterly 1999); loses the Tobin's Q framing; may not show Simpson's paradox (untested) | WDI has Delta-GDP and GFCF for all 144 countries | 4--5 |
| C: Reposition original MUQ as "housing market capitalization signal" | Minimal rework; honest about what the metric captures; preserves existing results | Loses some rhetorical force; "housing market signal" sounds less important than "investment efficiency" | Already done | 1--2 |
| D: All three | Convergent evidence architecture that Nature values; each addresses different reviewer concerns | Total workload; risk of paper becoming too methods-heavy | See above | 10--14 |

**Rationale for D**: The core strategic insight is that the Simpson's paradox must survive multiple MUQ definitions to be credible. R1, R3, and R4 all independently question whether the paradox is an artifact of price cycles. If we show it holds under (i) original MUQ, (ii) quantity-effect-only MUQ (China/US), and (iii) GDP-based MUQ (global), the finding becomes nearly unassailable. This is the "evidence convergence" approach Nature rewards.

**Implementation priority**:
- **Main text**: Reposition original MUQ per Option C. Explicitly call it "a housing-market-capitalization signal that captures, but does not disentangle, investment efficiency and asset price dynamics."
- **Finding 1 robustness**: Run GDP-based MUQ (Option B) for the global Simpson's paradox. If it holds, this becomes a headline robustness check in the main text (one sentence + Extended Data figure). If it fails, we have a critical interpretive issue to address.
- **Finding 2 robustness**: Run quantity-effect-only MUQ (Option A) for China city-level analysis. This directly addresses R1-M1.
- **Finding 3**: Decompose carbon estimate into pre-2021 (structural) and 2021--2024 (market-crash-contaminated) periods.

**Impact on core findings**: If Simpson's paradox survives GDP-based MUQ, the paper's central finding is dramatically strengthened -- it means declining returns are not an artifact of housing prices. If it fails, we must honestly reframe the paper as documenting a housing-market phenomenon rather than an investment-efficiency phenomenon. **We must run this test before committing to the full revision.**

**Kill criterion**: If GDP-based MUQ shows no within-group decline in any income group, the paper's claim to measure "investment efficiency" collapses. In that scenario, we pivot to Nature Cities with a more modest framing.

---

### Q2: City-Level Analysis Reconstruction

**Decision: Lead with clean specification; reframe cross-sectional pattern; abandon causal interpretation**

#### The damage assessment

The situation is worse than any single reviewer states. Let me lay it out:

1. **Headline beta = -2.23 is indefensible as a primary result.** R4 is correct: the 83% attenuation to beta = -0.37 when eliminating the shared I denominator means the headline number is mostly mechanical. We cannot lead with it.

2. **Within-estimator null (p = 0.063--0.252) is the real finding.** It means: *within the same city over time, more investment does not predict lower returns.* The entire negative association is cross-sectional -- i.e., cities that invest more are different from cities that invest less, but it is not the case that a given city's returns decline when it invests more. This destroys any quasi-causal narrative.

3. **The sign reversal survives in clean specification** (China: -0.37, p = 0.019; US: +1.78, p < 10^-6). This is the salvageable finding. But -0.37 is barely significant and the effect size is tiny.

4. **US metro-only Delta-beta is not significant** (R2-M2). This means the scaling gap in the US is driven by small towns, not big cities. This contradicts the agglomeration narrative.

#### Reconstruction plan

**New Finding 2 narrative**: "City-level mapping reveals that the aggregate efficiency decline operates through cross-sectional composition, not within-city dynamics."

Specific changes:
- **Lead with DeltaV/GDP ~ FAI/GDP** as the primary specification. Report beta = -0.37 honestly.
- **Report within-estimator null** in the main text, not buried in robustness checks. Frame it as informative: "The null within-estimator indicates that the efficiency gradient is a structural feature of the urban hierarchy -- a sorting phenomenon -- rather than a within-city dynamic of diminishing returns."
- **Report mechanical correlation share as ~80%** (ratio of clean to original beta), not 13% (MC null comparison). The 13% figure is technically defensible but misleading in context.
- **Sign reversal**: Keep, but present in the clean specification. The contrast (-0.37 vs. +1.78) is still significant and interpretable, just smaller.
- **82.2% statistic**: Downgrade. Add population-weighted version. Note that t-test for mean = 1 yields p = 0.104 (R4-m8).
- **Tier gradient**: Retain as descriptive cross-sectional mapping. Remove any implication of causality.

**New instrument variable**: Not feasible within the revision timeline. The most natural IV (lagged land auction revenue, fiscal transfer dependence) requires data collection that would take 20+ days and is not guaranteed to produce a valid first stage. Instead, frame the cross-sectional pattern honestly and identify IV estimation as future work.

**China-US sign reversal in clean spec**: beta_China = -0.37 (p = 0.019) vs. beta_US = +1.78 (p < 10^-6). This is sufficient to establish "directionally different associations." The sign reversal is not as dramatic as -2.23 vs. +2.75, but it is real and interpretable.

---

### Q3: Carbon Estimation

**Decision: Option B (decompose) + elements of A and D**

#### Analysis of Options

| Option | Pros | Cons |
|--------|------|------|
| A: Truncate at 2020 | Eliminates the most vulnerable period; remaining estimate (~0.5 GtCO2) is defensible | Loses 90%+ of the carbon estimate; "0.5 GtCO2" is not a Nature-worthy number |
| B: Decompose into physical overbuilding + market revaluation | Intellectually honest; shows both components; lets readers interpret | Requires vacancy/physical-excess data that may not exist at national level |
| C: Demote to Discussion paragraph | Removes the most attackable Finding; simplifies paper | 5.3 GtCO2 is the paper's most media-friendly number; losing it reduces broad appeal |
| D: Replace MUQ with physical indicators | Uses vacancy rates, demolition rates as carbon basis | Vacancy data for China is notoriously unreliable (Rogoff & Yang 2021) |

**Decision rationale**: The 5.3 GtCO2 number is simultaneously the paper's greatest asset and greatest liability. R5's plausibility check is devastating: the 2024 peak of 1,714 MtCO2 essentially claims all of China's building carbon was wasted that year. This cannot stand.

**Implementation**:

1. **Split the estimate into two periods**:
   - **2000--2020 (structural period)**: Estimate using smoothed MUQ (5-year moving average) to filter price volatility. Expected: ~0.5--1.5 GtCO2. This is the defensible number.
   - **2021--2024 (market-crash period)**: Estimate separately. Clearly label as "market-value-adjusted" rather than physical waste. Expected: ~3.5--5.0 GtCO2.

2. **Add annual plausibility cap**: Following R5-M4, cap annual "excess carbon" at 50% of estimated total building embodied carbon for that year. This prevents the 2024 absurdity.

3. **Introduce physical cross-check**: Use floor-area-based excess metric. China's per-capita housing floor area (~42 m2 in 2023) substantially exceeds Japan (~33 m2) and EU average (~35 m2) at comparable development stages. The physical excess can be estimated as (actual per-capita area - reference per-capita area) x population x carbon intensity per m2. This grounds the carbon number in physical reality.

4. **Reframe in main text**: Lead with the 2000--2020 structural estimate. Present the 2021--2024 component as "an additional market-adjustment component that reflects asset price declines and may partially reverse if prices recover."

5. **Widen uncertainty**: Report parametric CI [4.3, 6.3] alongside structural uncertainty range [1.3, 8.0] (from Method C). Make it clear which is which.

6. **Replace "embodied" with "associated with"** throughout (R5-m1).

**Impact**: The headline number will change from "5.3 GtCO2" to something like "0.8--1.2 GtCO2 in structural excess, with an additional 3--5 GtCO2 in market-adjustment losses." Less dramatic, but defensible. The "1.5 years of global building embodied emissions" comparison must be dropped or heavily qualified.

**Risk**: Losing the punchy 5.3 GtCO2 number reduces media appeal. But keeping a number that fails R5's plausibility check would be fatal in review.

---

### Q4: Scaling Gap Theoretical Positioning

**Decision: Downgrade to "structural observation" with a formal derivation sketch in Supplementary**

#### The problem

R2 is correct on all counts:
- The causal chain from city-level scaling gap to country-level Simpson's paradox is asserted, not derived (R2-M1).
- The "mean-field" label is misleading (R2-m1).
- Q ~ N^(Delta-beta) has R2 = 0.31 -- 69% noise (R2-M3).
- US metro-only Delta-beta is not significant (R2-M2).
- Regional heterogeneity is large (R2-M4).

A full formal derivation (city-size distribution -> investment allocation -> country-level MUQ) is feasible in principle but would require 15--20 days of theoretical work and would expand Box 1 beyond Nature's format constraints. The derivation would need:
- A Pareto/Zipf city-size distribution assumption
- An investment allocation rule (proportional to GDP? to population? to political weight?)
- Integration of city-level Q ~ N^(Delta-beta) over the city-size distribution to get country-level MUQ
- Demonstration that the integral produces the observed MUQ ~ urbanization relationship

This is a paper in itself. It would strengthen the theoretical framework enormously but is not achievable within a 45-day revision window.

**Implementation**:

1. **Rename**: "mean-field framework" -> "group-specific linear decomposition" (R2-m1).

2. **Honest framing in Box 1**: "The scaling gap and the Simpson's paradox are two empirical regularities that we document independently. We hypothesize that the scaling gap is a micro-level mechanism that contributes to the macro-level paradox, but we do not formally derive this connection. The formal derivation -- which would require assumptions about city-size distributions and investment allocation rules -- is a priority for future theoretical work."

3. **Report US metro-only Delta-beta** in main text (R2-M2): "Among US metropolitan areas only (N = 381), Delta-beta_VGDP = 0.017 (p = 0.32); the aggregate significance is driven by micropolitan areas, suggesting the scaling gap in the US is primarily a small-city phenomenon."

4. **Report Q ~ N^(Delta-beta) R2 = 0.31** (R2-M3) and regional heterogeneity.

5. **Decompose beta_V** into mechanical (population term) and economic (price + area scaling) components, following R2's suggestion. For China: beta_V = 1 + beta_A + beta_P. The "real" agglomeration signal is beta_P + beta_A - not the full 1.34.

6. **Standardize Delta-beta notation**: Use Delta-beta_VGDP as the primary metric throughout; subscript all variants.

7. **Sketch formal derivation in Supplementary Note**: Even a partial derivation (showing that under Zipf's law and proportional investment, Q ~ N^(Delta-beta) aggregates to a declining MUQ-urbanization relationship) would satisfy R2 partially. Estimated work: 5--7 days.

---

### Q5: Overall Paper Repositioning

**Decision: Hybrid -- "Discovery paper with a measurement innovation," leading with the Simpson's paradox, not the carbon estimate**

#### Analysis

| Positioning | Nature appeal | Risk | Reviewers' implicit preference |
|-------------|:------------:|:----:|-------------------------------|
| Discovery paper ("we found a hidden pattern") | HIGH -- Nature loves "X was hiding in plain sight" | Must demonstrate pattern is real, not artifact | R1, R5 lean this way |
| Methods/framework paper ("we built a new tool") | MODERATE -- better for Nature Cities | Feels incremental for Nature main | R3 leans this way |
| Hybrid ("new tool reveals hidden pattern") | HIGH -- if balanced correctly | Must avoid overclaiming on both fronts | Best fit for the evidence |

**Rationale**: The Simpson's paradox is the paper's most defensible and most Nature-worthy finding. It is:
- Statistically robust (LOO 47/47; survives multiple corrections)
- Conceptually crisp (one-sentence explanation to a non-specialist)
- Broadly relevant (aggregation traps exist everywhere)
- Surprising (the conventional wisdom is wrong)

The scaling gap is intellectually interesting but empirically weaker (R2 = 0.31, US metro-only not significant). The carbon estimate is attention-grabbing but methodologically vulnerable. The sign reversal is informative but descriptive.

**New hierarchy**:
1. **Lead finding**: Simpson's paradox (currently Finding 1) -- STRENGTHEN
2. **Supporting finding**: Cross-sectional efficiency mapping and sign reversal (currently Finding 2) -- REFRAME with honest limitations
3. **Policy implication**: Carbon cost (currently Finding 3) -- DEMOTE from "finding" to "policy dimension" in Discussion
4. **Theoretical framework**: Scaling gap (currently Box 1) -- RETAIN but downgrade from "engine" to "structural observation"

**Title options**:
- Keep current: "Simpson's paradox masks declining returns on urban investment worldwide" -- Still works, and "Simpson's paradox" in the title is attention-grabbing.
- Alternative: "An aggregation trap conceals declining returns on urban investment worldwide" -- Stronger claim to novelty ("aggregation trap" is our coinage) but less immediately recognizable.
- **Decision**: Keep current title. "Simpson's paradox" is a known concept that immediately signals the finding's structure. The word "masks" is appropriately non-causal.

---

## Part 2: Detailed Revision Plan

### 1. Revised Paper Structure

```
TITLE: Simpson's paradox masks declining returns on urban investment worldwide
       [unchanged]

ABSTRACT: ~150 words [tighten from ~155]
  - Lead with Simpson's paradox
  - Replace beta=-2.23 with clean-spec beta=-0.37
  - Replace "drives" with "is associated with"
  - Replace "embodied approximately 5.3 GtCO2" with
    "is associated with an estimated 0.8--1.2 GtCO2 in structural excess
    construction carbon (structural uncertainty range: 1.3--8.0)"
  - Remove "one of the largest misallocations" framing

INTRODUCTION: ~600 words [trim from ~700]
  - Paragraph 1: The measurement gap (keep)
  - Paragraph 2: Aggregation trap concept + literature positioning (expand refs)
  - Paragraph 3: Three findings, with recalibrated language
  - Paragraph 4: Scope limitations (keep but tighten)

FINDING 1: Simpson's paradox [STRENGTHEN]
  - Scaling gap as structural observation (not engine)
  - Simpson's paradox: original MUQ + GDP-based MUQ robustness
  - Ten-country trajectories (with data-sparsity caveat for India/Indonesia)
  - Report US metro-only Delta-beta non-significance
  - Report Q~N^(Delta-beta) R2 = 0.31
  - Report regional heterogeneity

FINDING 2: City-level efficiency mapping [REFRAME]
  - Lead with DeltaV/GDP ~ FAI/GDP specification
  - Report within-estimator null prominently
  - Report mechanical correlation share as ~80%
  - Sign reversal in clean specification (-0.37 vs +1.78)
  - DeltaV decomposition (quantity vs price effect)
  - Tier gradient as cross-sectional description
  - DID: one sentence referencing Extended Data, flagging diagnostic failures

BOX 1: The Scaling Gap [RESTRUCTURE]
  - Rename: no "mean-field"
  - Decompose beta_V into mechanical + economic components
  - Honest statement about missing formal derivation
  - Reframe "three testable predictions" as "three hypotheses"

DISCUSSION: ~800 words
  - Para 1: Summary of findings with recalibrated language
  - Para 2: Policy implications -- "invest differently" message (keep)
  - Para 3: Carbon dimension [NEWLY POSITIONED HERE]
    - 2000-2020 structural estimate as primary number
    - 2021-2024 as market-adjustment component, separately labeled
    - Structural uncertainty range [1.3, 8.0]
    - Annual plausibility capping
    - Avoid-Shift-Improve framing (retain)
  - Para 4: Limitations (7 -> 9, adding within-estimator null + price cycle sensitivity)
  - Para 5: Future directions -- causal identification, formal scaling-paradox derivation
  - Para 6: Closing -- REMOVE "one of the largest misallocations" hyperbole
    Replace with measured statement about aggregation traps

METHODS: M1-M9 [UPDATE per specific changes below]

REFERENCES: Expand from 18 to 35-40
```

### 2. Finding-by-Finding Modification Details

#### Finding 1: Simpson's Paradox (STRENGTHEN)

**Keep unchanged**:
- Spearman correlations within income groups
- LOO robustness (47/47)
- Within/between decomposition
- Ten-country trajectories (with stronger caveats for data-sparse countries)

**Modify**:
- Add cluster-bootstrapped p-values for Spearman rho (clustering by country) [R4-3.1a]
- Add time-varying income classification sensitivity -- acknowledge it weakens significance [R4-3.1a]
- Add GDP-based MUQ (1/ICOR) as parallel validation of Simpson's paradox [R3-3.3]
- Add 5-year moving average smoothed MUQ to filter price cycles [R3-M2]
- Report Delta-beta_VGDP R2 = 0.31 and discuss [R2-M3]
- Report US metro-only Delta-beta = 0.017 (p = 0.32) [R2-M2]
- Report regional heterogeneity in scaling exponents [R2-M4]
- Replace "the scaling gap is the engine" with "the scaling gap is a structural feature consistent with the observed efficiency gradients"
- Rename "mean-field framework" -> "group-specific linear decomposition" [R2-m1]
- Standardize Delta-beta subscripts throughout [R2-m4]

**Add**:
- Decomposition of beta_V = 1 + beta_A + beta_P (mechanical vs economic) [R2-4a, R3-M4]
- RESET test result (F = 9.34, p = 0.0001) with discussion of power-law approximation quality [R2-m5]
- Formal test of Delta-beta_China vs Delta-beta_US difference (z ~ 4.1) [R2-3.60c]

#### Finding 2: City-Level Efficiency Mapping (REFRAME)

**Major changes**:
- Primary specification: DeltaV/GDP ~ FAI/GDP (beta = -0.37, p = 0.019, R2 = 0.017)
- Report original MUQ ~ FAI/GDP specification as secondary with explicit mechanical correlation warning
- Mechanical correlation: report as ~80% beta attenuation (not 13% MC null)
- Within-estimator null: main text, framed as "the efficiency gradient is cross-sectional -- a sorting phenomenon across the urban hierarchy"
- 82.2% statistic: add population-weighted version; note t-test p = 0.104
- Sign reversal: present in clean spec (-0.37 vs +1.78)
- DID: one sentence in Finding 2 ("A quasi-experiment using China's 2020 Three Red Lines policy is presented in Extended Data; diagnostic tests do not meet standard identification requirements [see Methods M4]"). Full results remain in ED.

**Remove from main text**:
- beta = -2.23 as headline number (move to ED as original specification)
- "investment intensity predicts lower returns" language
- "supply-driven vs demand-driven regimes" as causal distinction (replace with "differing institutional associations")
- log-log elasticity result (it contradicts the narrative; R4-3.3a)

#### Finding 3: Carbon -> Discussion Paragraph (DEMOTE)

**Move from standalone Finding to Discussion paragraph 3**:
- Lead with 2000--2020 structural estimate (expected: 0.8--1.2 GtCO2)
- Present 2021--2024 separately as "market-adjustment component"
- Report parametric CI alongside structural uncertainty range [1.3, 8.0]
- Add annual plausibility cap (max 50% of total building carbon)
- Replace "embodied" with "associated with" throughout
- Add physical cross-check using per-capita floor area excess
- Retain Avoid-Shift-Improve framing but qualify
- Remove "1.5 years of global building embodied emissions" comparison (or heavily qualify)
- Forward-looking claims for India/Vietnam/Indonesia: add back-of-envelope scenario [R5-M5]

#### Box 1: Scaling Gap (RESTRUCTURE)

**Revised structure**:
1. Scaling exponents with decomposition (beta_V = 1 + beta_A + beta_P)
2. Scaling gap definition with R2 and regional heterogeneity
3. Group-specific linear decomposition (not "mean-field")
4. Three hypotheses (not "confirmed predictions")
5. Honest acknowledgment of missing formal derivation

### 3. New Analysis Checklist

| # | Analysis | Script name | Data needed | Status | Days |
|---|----------|-------------|-------------|--------|:----:|
| N1 | GDP-based MUQ (1/ICOR) for global Simpson's paradox | `n01_gdp_muq_simpson.py` | WDI: Delta-GDP, GFCF (already downloaded) | New | 3 |
| N2 | Cluster-bootstrapped Spearman p-values | `n02_clustered_spearman.py` | Existing global panel | New | 2 |
| N3 | Time-varying income classification sensitivity | `n03_timevar_income.py` | WDI historical classifications (download) | New | 2 |
| N4 | Quantity-effect-only MUQ for China cities | `n04_quantity_muq_china.py` | Existing city panel | New | 2 |
| N5 | 5-year MA smoothed MUQ for China national | `n05_smoothed_muq.py` | Existing national data | New | 1 |
| N6 | beta_V decomposition (beta_A + beta_P + 1) | `n06_betav_decomposition.py` | Existing city cross-section | New | 2 |
| N7 | SUR estimation of Delta-beta | `n07_sur_deltabeta.py` | Existing scaling data | New | 2 |
| N8 | Gabaix-Ibragimov corrected scaling exponents | `n08_gi_correction.py` | Existing scaling data | New | 2 |
| N9 | Carbon estimate split (2000-2020 vs 2021-2024) | `n09_carbon_split.py` | Existing carbon data | New | 2 |
| N10 | Carbon annual plausibility cap | `n10_carbon_cap.py` | CABECA total building carbon data (collect) | New | 2 |
| N11 | Physical floor-area excess carbon cross-check | `n11_floor_area_carbon.py` | Per-capita floor area by country (WDI/UN-Habitat) | New | 3 |
| N12 | Back-of-envelope India/Vietnam/Indonesia scenario | `n12_forward_scenario.py` | WDI + IEA investment data | New | 2 |
| N13 | Moran's I spatial autocorrelation test on scaling residuals | `n13_morans_i.py` | City coordinates (existing) | New | 1 |
| N14 | RESET test reporting | already computed in script 80 | Existing | Report only | 0.5 |
| N15 | Population-weighted 82.2% statistic | `n15_weighted_below_unity.py` | Existing city panel | New | 0.5 |
| N16 | Language audit -- systematic causal->associational replacement | manual | Full manuscript | New | 2 |
| N17 | CI calibration data points from CABECA/IEA | data collection | CABECA 2022 report, IEA reports | New | 2 |
| N18 | Alternative CI functional form (piecewise linear) | `n18_ci_piecewise.py` | Same as N17 | New | 1 |
| **Total** | | | | | **~30** |

### 4. Content to Delete or Demote

| Content | Current location | Action | Rationale |
|---------|-----------------|--------|-----------|
| beta = -2.23 as headline | Abstract, Finding 2, Discussion | **Demote** to ED as "original specification" | Mechanically inflated (R4-MC1) |
| "one of the largest misallocations" | Discussion final para | **Delete** | Overclaim (R1-M5, R3-m6) |
| "the scaling gap provides the theoretical engine" | Discussion para 1 | **Replace** with "structural observation consistent with" | Causal overclaim (R2-M1) |
| "supply-driven vs demand-driven regimes" | Finding 2, Discussion | **Replace** with "differing institutional contexts" | Causal overclaim (R1-M5, R3-4.1) |
| "drives these efficiency gradients" | Abstract | **Replace** with "is associated with" | Causal language (R1-M5) |
| "flows against the scaling gradient, producing below-cost returns" | Box 1 | **Rewrite** | Causal mechanism asserted not demonstrated (R2-M5) |
| DID in main text | Finding 2 | **Demote** to one sentence + ED | Failed diagnostics (R1-M3, R3-4.2, R4-MC3) |
| "5.3 GtCO2" as headline | Abstract, Finding 3 | **Split** into structural + market-adjustment | Plausibility failure in 2022-2024 (R5-M4) |
| "1.5 years of global building embodied emissions" | Finding 3, Discussion | **Remove or heavily qualify** | Temporal incommensurability (R5-3.4a) |
| 13% mechanical correlation claim | Finding 2 | **Replace** with ~80% attenuation framing | Misleading metric (R4-MC1) |
| "confirmed" for Prediction 1 | Box 1 | **Replace** with "consistent with" (N=2) | N=2 is not confirmation (R2-Claim 5) |
| Ten-country forward inference for India (N=5) | Finding 1 | **Demote** to ED with strong caveats | Underpowered (R1-m5) |

### 5. Narrative Adjustment Summary

#### Language audit rules (systematic find-and-replace)

| Current language | Replacement | Instances (est.) |
|-----------------|-------------|:----------------:|
| "drives" / "driving" | "is associated with" / "accompanies" | 8--10 |
| "engine" | "structural pattern" | 2--3 |
| "produces" / "producing" | "is accompanied by" / "co-occurs with" | 4--5 |
| "predicts" (in causal sense) | "is cross-sectionally associated with" | 3--4 |
| "supply-driven regime" | "supply-oriented institutional context" | 5--6 |
| "demand-driven regime" | "demand-responsive institutional context" | 5--6 |
| "misallocation" | "below-cost-return investment" | 2--3 |
| "embodied X GtCO2" | "associated with an estimated X GtCO2" | 3--4 |
| "excess construction carbon" | "carbon associated with below-unity-return investment" | 5--6 |
| "mean-field framework" | "group-specific linear decomposition" | 3--4 |
| "confirmed" (re: predictions) | "consistent with" | 2 |
| "investment efficiency" (standalone) | "investment-return metric" or "housing-market-capitalization signal" | 10+ |

#### Key narrative shifts

1. **From "we discovered a misallocation" to "we revealed a measurement trap"**. The paper's strongest contribution is showing that aggregate statistics mislead. That is a measurement/methodology insight. The "misallocation" framing requires causal evidence we do not have.

2. **From "the scaling gap explains the paradox" to "the scaling gap and the paradox are complementary findings"**. Until formal derivation connects them, they are parallel observations, not a causal chain.

3. **From "5.3 GtCO2 of wasted carbon" to "0.8--1.2 GtCO2 in structural excess, with larger but less certain market-adjusted estimates"**. Honest, defensible, still impactful.

4. **From "China vs US proves institutional divergence" to "China and US exhibit opposite cross-sectional associations, consistent with different institutional contexts"**. Same information, appropriate epistemic modesty.

### 6. Work Schedule and Resource Allocation

| Phase | Tasks | Days | Dependencies |
|-------|-------|:----:|-------------|
| **Phase 0: Kill test** | N1 (GDP-based MUQ Simpson's paradox) | 3 | None -- **do this first** |
| **Phase 1: Core analyses** | N2, N4, N5, N6, N7, N8, N9 | 10 | After Phase 0 passes |
| **Phase 2: Carbon rebuild** | N10, N11, N12, N17, N18 | 7 | N9 complete |
| **Phase 3: Robustness** | N3, N13, N14, N15 | 4 | After Phase 1 |
| **Phase 4: Writing** | Language audit (N16), rewrite all sections | 12 | After Phases 1-3 |
| **Phase 5: Figures** | All 5 main figures + 7 ED figures | 8 | After Phase 4 |
| **Phase 6: References** | Expand from 18 to 35--40 | 3 | Parallel with Phase 4 |
| **Phase 7: Internal review** | Full re-read, compliance check, cover letter | 5 | After all above |
| **Buffer** | Unexpected issues, iteration | 5 | -- |
| **TOTAL** | | **52--57** | |

**Critical path**: Phase 0 (3 days) -> Phase 1 (10 days) -> Phase 4 (12 days) -> Phase 5 (8 days) -> Phase 7 (5 days) = **38 days minimum**

**Target completion**: ~2026-05-15 (assuming start 2026-03-24)

### 7. Expected Post-Revision Assessment

#### Predicted reviewer scores after revision

| Dimension | Current | Post-revision (est.) | Change driver |
|-----------|:-------:|:-------------------:|---------------|
| R1 Novelty | 7.5 | 7.5 | Unchanged -- novelty is inherent |
| R1 Rigour | 5.5 | 7.0 | Clean spec, within-estimator honesty, carbon decomposition |
| R1 Significance | 7.0 | 7.0 | Reduced claims offset by stronger evidence base |
| R1 Clarity | 7.0 | 7.5 | Tighter structure, no overreach |
| R2 Theoretical rigour | 5.0 | 6.0 | beta_V decomposition, R2 reporting, honest framing |
| R2 Empirical rigour | 6.0 | 7.0 | GI correction, SUR, metro-only reporting |
| R3 Identification | 4.0 | 5.5 | Honest descriptive framing + GDP-based MUQ convergence |
| R3 Data quality | 5.0 | 5.5 | Additional cross-checks; fundamental data issues unresolvable |
| R4 Statistical rigour | 6.0 | 7.5 | Clean spec as primary, clustered bootstrap, carbon CI widened |
| R4 Identification | 4.5 | 5.0 | DID demoted; honest descriptive framing |
| R5 Methodology | 5.5 | 6.5 | CI data points, plausibility cap, physical cross-check |
| R5 Uncertainty | 6.0 | 7.5 | Structural uncertainty range reported prominently |

#### Desk reject risk

| Scenario | Current | Post-revision |
|----------|:-------:|:------------:|
| R1's estimate | 40--50% | 15--20% |
| If GDP-based MUQ confirms Simpson's paradox | -- | 10--15% |
| If GDP-based MUQ fails | -- | 60%+ (pivot to Nature Cities) |

#### Remaining vulnerabilities (post-revision)

1. **MUQ is still fundamentally a housing price signal.** No revision can fully disentangle asset price cycles from investment efficiency. The GDP-based MUQ robustness check is our best defense, but if a reviewer insists on a clean identification strategy, we cannot provide one.

2. **The scaling gap R2 = 0.31 is low.** We can report it honestly, but we cannot make it higher. A reviewer who demands R2 > 0.5 for a "scaling law" will not be satisfied.

3. **City panel is short (2010--2016) and old.** We cannot extend it without substantial new data collection. This is a known weakness we must live with.

4. **China FAI data post-2017 are estimated.** This is an inherent data quality issue in Chinese statistics. We can flag it but cannot resolve it.

5. **The paper is dense for Nature's format.** Even after demoting Finding 3, the paper covers scaling laws + Simpson's paradox + city-level mapping + carbon, which is a lot for ~3,500 words. The revision may push us to 3,800+ words, requiring tight editing.

### 8. References to Add (Priority List)

**Must-add (addressing reviewer gaps)**:
1. Hsieh, C.-T. & Klenow, P. J. Misallocation and manufacturing TFP in China and India. *QJE* 124, 1403--1448 (2009). [R3-M5]
2. Hsieh, C.-T. & Moretti, E. Housing constraints and spatial misallocation. *AEJ: Macro.* 11, 1--39 (2019). [R3-M5]
3. Bettencourt, L. M. A. The origins of scaling in cities. *Science* 340, 1438--1441 (2013). [R2-m2]
4. Arcaute, E. et al. Constructing cities, deconstructing scaling laws. *J. R. Soc. Interface* 12, 20140745 (2015). [R2-m3]
5. Leitao, J. C. et al. Is this scaling nonlinear? *R. Soc. Open Sci.* 3, 150649 (2016). [R2-m3]
6. Easterly, W. The ghost of financing gap. *J. Dev. Econ.* 60, 423--438 (1999). [R3-M5]
7. Glaeser, E. L. & Gyourko, J. The economic implications of housing supply. *JEP* 32, 3--30 (2018). [R3-M5]
8. Bai, C.-E., Hsieh, C.-T. & Song, Z. M. The long shadow of a fiscal expansion. *Brookings Pap. Econ. Act.* 2016, 129--181 (2016). [R3-M5]
9. Huang, L. et al. Carbon emission of global construction sector. *Renew. Sustain. Energy Rev.* 81, 1906--1916 (2018). [R5-m6]
10. Pomponi, F. & Moncaster, A. Scrutinising embodied carbon in buildings. *Renew. Sustain. Energy Rev.* 71, 307--316 (2017). [R5-m6]
11. Gabaix, X. & Ibragimov, R. Rank-1/2: a simple way to improve the OLS estimation of tail exponents. *J. Bus. Econ. Stat.* 29, 24--39 (2011). [R4-MC4]
12. Goodman-Bacon, A. Difference-in-differences with variation in treatment timing. *J. Econom.* 225, 254--277 (2021). [R4-3.4e]
13. Duranton, G. & Puga, D. Micro-origins of urban agglomeration economies. *Handbook of Regional and Urban Economics* 4, 2063--2117 (2004). [R1-m2]

**Should-add (strengthening literature engagement)**:
14. Henderson, J. V. Urbanization and development. *Am. Econ. Rev.* 95, 1517--1533 (2005).
15. Seto, K. C. et al. Human settlements, infrastructure and spatial planning. *IPCC AR5 WG3* Ch. 12 (2014).
16. Restuccia, D. & Rogerson, R. Policy distortions and aggregate productivity. *Rev. Econ. Stud.* 75, 707--731 (2008).
17. Brandt, L., Van Biesebroeck, J. & Zhang, Y. Creative accounting or creative destruction? *Am. Econ. Rev.* 102, 3088--3120 (2012).
18. Cottineau, C. MetaZipf. *PLoS ONE* 12, e0183919 (2017).
19. Louf, R. & Barthelemy, M. Scaling: lost in the smog. *Environ. Plan. B* 41, 767--769 (2014).
20. Abel, A. B. & Eberly, J. C. A unified model of investment under uncertainty. *Am. Econ. Rev.* 84, 1369--1384 (1994).

### 9. Compliance Items (Nature Articles)

| Requirement | Current status | Action needed |
|-------------|:-------------:|---------------|
| Abstract <= 150 words | ~155 | Trim 5+ words |
| Main text <= 3,500 words | ~3,800--4,000 | Trim by demoting Finding 3 to Discussion |
| Main figures <= 6 | 5 planned, 1 complete | Complete all 5 figures |
| Extended Data <= 10 items | At limit (10) | May need to consolidate if new ED items added |
| References <= 50 | 18 -> target 35--40 | Add per list above |
| Data availability | Missing | Write; specify Zenodo DOI |
| Code availability | Missing | Write; specify GitHub repo |
| Reporting Summary | Missing | Complete Nature checklist |
| Competing interests | Missing | Write (presumably none) |
| Author contributions (CRediT) | Missing | Write |
| Cover letter | Not written | Write; lead with Simpson's paradox |
| Map compliance | Unknown | Check any China maps for Taiwan/border policy |

---

## Summary Decision Matrix

| Issue | Decision | Expected impact on reviewers |
|-------|----------|------------------------------|
| MUQ construct | Reposition + GDP-based validation | Addresses R1-M1, R3-M1, R4-3.3a |
| City-level beta | Lead with clean spec (-0.37) | Addresses R4-MC1, R1-M2 |
| Within-estimator null | Report prominently | Addresses R4-MC2 |
| Scaling gap theory | Downgrade to structural observation | Addresses R2-M1, R2-M5 |
| DID | Demote to ED with failure disclosure | Addresses R1-M3, R3-4.2, R4-MC3 |
| Carbon estimate | Split + cap + widen CI | Addresses R5-M1--M4, R1-M4 |
| Causal language | Systematic audit | Addresses R1-M5, R3-4.1, R4 throughout |
| US metro-only | Report in main text | Addresses R2-M2 |
| References | 18 -> 35--40 | Addresses R1-m2, R2-m2/m3, R3-M5, R5-m6 |
| "Largest misallocation" | Delete | Addresses R1-M5, R3-m6 |

**Bottom line**: This revision preserves the paper's genuine contributions (Simpson's paradox, measurement framework, cross-national dataset) while honestly confronting its weaknesses (MUQ is partly a price signal, city-level evidence is cross-sectional, carbon estimate is model-dependent). The revised paper will be less dramatic but substantially more credible. If the GDP-based MUQ validation succeeds, the paper has a strong shot at Nature. If it fails, we pivot gracefully to Nature Cities.

---

*Strategy drafted by: PI (Claude, research-director agent)*
*Date: 2026-03-21*
*Next action: Execute Phase 0 kill test (GDP-based MUQ Simpson's paradox)*
