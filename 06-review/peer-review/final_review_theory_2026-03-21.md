# Final Pre-Submission Review: Theory and Evidence Completeness

**Paper**: "When building cities destroys value: a persistent regime shift in urban investment across nations"
**Target journal**: Nature (Article)
**Reviewer role**: Senior referee simulating Nature editorial + expert review (final gate)
**Review date**: 2026-03-21
**Version**: Post-revision (v4 outline + all 7 revision actions completed)
**Compared against**: review_v2_theory_2026-03-21.md (score 6.2/10)

---

## PART I: THREE-ROUND PROGRESSIVE REVIEW

---

### Round 1: Editorial 30-Second Screening

#### 1.1 Title Assessment

**"When building cities destroys value: a persistent regime shift in urban investment across nations"**

This is a significant improvement over the v2 title ("Irreversible regime shift in urban investment: when building cities stops creating value"). The new title leads with the accessible, arresting clause ("When building cities destroys value") and relegates the technical framing to the subtitle. "Persistent" replaces "irreversible," which is both more defensible and less likely to trigger reflexive scepticism from an editor with physics training. At 16 words it remains slightly long for Nature (ideal: 10-12), but the colon structure is conventional for the journal.

**Minor concern**: "across nations" is vague. The paper's strongest evidence is from China; the cross-national evidence is CPR-based, not Q-based. An editor may feel this oversells the generality. Consider: "...in urban investment from China to the world" -- though this is a stylistic preference, not a fatal issue.

**Score: 7.5/10** (up from 6/10)

#### 1.2 Abstract Design: Can MUQ + Carbon + EWS Secure Send-to-Review?

The proposed abstract structure -- opening with MUQ turning negative, then carbon cost, then EWS cross-national validation -- is well-calibrated for Nature's editorial sensibility in 2026. Three elements that would catch an editor's attention:

(a) **MUQ negative (p = 0.043)**: "Each additional yuan of investment now destroys value" is a sentence that could appear in Nature News & Views. It is concrete, counter-intuitive, and policy-relevant.

(b) **13.4 GtCO2**: This number immediately connects urban economics to climate policy, which is essential for broad-interest framing at Nature. Equivalent to "one full year of global building-sector carbon output" -- a comparison that any editor can grasp.

(c) **67.3% EWS (p = 0.009)**: This transforms the paper from a China case study into a cross-national pattern. The signal-detection framing ("critical slowing down") resonates with Nature's complexity science readership.

**Assessment**: This abstract design is substantially stronger than v2. The three hooks are distinct, escalating (China specifics -> global carbon -> universal dynamics), and each carries a p-value. An editor reading this in 30 seconds would likely conclude: "This is not just another China property paper."

**Score: 8/10** (up from 6.5/10)

#### 1.3 Desk Reject Probability

**Updated estimate: 40-50%**

This is a meaningful improvement from the previous 55-65% estimate. The key drivers of improvement:

- MUQ as headline (model-free, intuitive) eliminates the "clever repackaging" risk that was the primary desk-reject threat
- Carbon dimension crosses the disciplinary boundary that Nature editors value
- EWS cross-national evidence addresses the "is this just China?" concern

**Remaining desk-reject risks**:
- An editor who views this as "development economics + urban planning" rather than "general science" may still decline
- The V(t) measurement uncertainty (90% CI spanning 12 years for Q=1 crossing) remains a potential concern, though the MUQ-first framing partially bypasses this
- Competition from other submissions: if Nature has recently published on China property/overbuilding, the marginal novelty decreases

**What would push desk reject below 30%**: A fourth dimension -- either (a) a validated real-time policy application (e.g., a city government using OCR for investment decisions), or (b) a dramatic visual that is immediately Nature-cover-worthy (e.g., a global map of "years until Q=1" for every country). Neither is available at present.

---

### Round 2: Expert Deep Review

#### 2.1 Three Findings -- Evidence Chain Completeness

**Finding 1 (MUQ regime shift)**: The evidence chain is now the strongest in the paper. MUQ sign change (p = 0.043) -> seven-calibration ensemble Q decline -> Monte Carlo 98.8% below Q=1 -> Bai-Perron structural breaks (F = 30.1) -> EWS cross-national validation (35/52, p = 0.009). This is five layers of converging evidence with a clear logical progression from model-free to model-dependent. **Score: 8/10.**

**Finding 2 (OCR spatial-income gradients)**: Improved but remains the weakest link. M2 K* model is well-motivated (Cobb-Douglas not rejected, sign-consistent across Between/TWFE/RE, VIF resolved). However, the China OCR bootstrap CI of [0.25, 1709] spanning four orders of magnitude is devastating for any claim of quantitative precision. The revision plan's decision to use directional language rather than point estimates is correct but has not been fully implemented in the outline -- the text still refers to "median OCR ~ 1.4" for the northeast. The M1 vs M2 rank correlation (rho = 0.507) is moderate, not strong. **Score: 6/10.**

**Finding 3 (efficiency decline + carbon cost)**: The Simpson's paradox resolution is a genuine analytical contribution. The income-group stratification is clean: low/lower-middle/upper-middle income groups all show significant declining MUQ (rho = -0.10 to -0.15, all p < 0.01), while high-income countries show no trend. The carbon cost quantification (13.4 GtCO2) adds a new dimension. However, the carbon estimate is a simple multiplication (excess K times carbon intensity), and a climate scientist reviewer would question the use of a single carbon intensity coefficient (0.65 tCO2/10,000 yuan) applied uniformly across 25 years with no temporal variation. **Score: 7/10.**

**Weakest link**: Finding 2's OCR quantification. If a reviewer demands bootstrap CIs on OCR and sees the [0.25, 1709] range for China, the response that "direction is robust" may not satisfy. The 290-city OCR map is visually compelling but analytically fragile.

#### 2.2 Simpson's Paradox Treatment

The identification and resolution of Simpson's paradox is one of the most significant analytical improvements in v4. The diagnosis is correct: global aggregate MUQ shows a weak positive trend (rho = 0.036, p = 0.038) driven by compositional shifts (high-income countries dominate high-urbanisation strata and have structurally higher MUQ). The within-group declining trends are statistically significant and economically meaningful.

**Concern**: The upper-middle-income group's declining trend (rho = -0.099, p = 0.003) is statistically significant on the Spearman test but the Kruskal-Wallis across stages is not (H = 6.023, p = 0.110). This inconsistency should be acknowledged -- it suggests the decline in the upper-middle group is gradual and noisy, not as clean as in the lower-middle group.

**Overall**: Convincing. A reviewer would accept this treatment as methodologically sound. **Score: 7.5/10.**

#### 2.3 Carbon Emission Estimation Methodology

The carbon estimate (13.4 GtCO2) is based on:
- Overbuilding = K - K* (from the M2 model)
- Carbon intensity = 0.65 tCO2 per 10,000 yuan (China Building Energy Conservation Association, 2022)
- Applied uniformly across 2000-2024

**Methodological concerns**:

1. **K* uncertainty propagates directly to carbon estimates.** If K* is overestimated (which the wide bootstrap CIs suggest is possible), overbuilding is underestimated, and vice versa. The paper does not report a confidence interval on the 13.4 GtCO2 figure.

2. **Carbon intensity is not constant over 25 years.** China's construction sector carbon intensity has declined substantially since 2000 (cement production efficiency improvements, partial electrification). Using a 2022 figure for 2000-era construction likely underestimates early-period emissions but overestimates the rate of improvement. A time-varying intensity would be more defensible.

3. **The "overbuilding = all K above K*" assumption is strong.** K* is an equilibrium prediction, not a normative standard. Investment above K* may be suboptimal but not "wasted" -- it still creates some (diminished) value. Attributing all excess K's construction carbon to "avoidable waste" conflates economic suboptimality with physical waste.

4. **Global estimate (1,700 MtCO2/year) uses CPR > 1.5 as the overbuilding threshold**, which includes 128 of 143 countries. This means nearly every country is "overbuilt" by this criterion, which strains credibility. The threshold should be better justified or the estimate more carefully hedged.

**Verdict**: The carbon dimension is a strategically important addition that broadens the paper's appeal. But the estimates should be presented as order-of-magnitude illustrations, not precise accounting. The paper's current framing ("conservative lower-bound estimates") is appropriate for China but the global figure needs further qualification. A climate-focused reviewer would assign this section 5.5/10 on its own; as a discussion-section complement to the core economics, it is adequate. **Score: 6.5/10.**

#### 2.4 EWS 67.3% -- Statistical Power and Interpretation

The binomial test (35/52 countries with rising AR(1), p = 0.009 against H0 = 50%) is statistically significant and the analysis is straightforward. However:

1. **The 50% null is weak.** If there is any general trend toward rising autocorrelation in macroeconomic time series (e.g., due to increasing global integration or policy smoothing), the null should be higher than 50%. A more rigorous test would use a permutation-based null (shuffle each country's CPR time series and recompute AR(1) trends).

2. **"20% decline from peak" is an arbitrary threshold.** The results' sensitivity to this threshold should be reported. If 15% or 25% gives very different results, the finding is fragile.

3. **Rolling window of 8 years is short for AR(1) estimation.** With 8 observations, the sampling variability of AR(1) is high (SE approximately 1/sqrt(8) = 0.35). Many of the individual-country Kendall taus are not individually significant (only 15/52 = 28.8% have p < 0.1). The statistical significance comes from the aggregate binomial test, not from individual-country precision.

4. **The regional pattern is informative but uneven**: Sub-Saharan Africa 71%, Europe & Central Asia 72%, South Asia 100% (but n=2), East Asia & Pacific 50%, MENA 50%, North America 0% (n=1). The high rates in Sub-Saharan Africa and Europe may reflect very different dynamics (conflict/crisis vs structural maturation), undermining the claim of a unified "urban investment transition" mechanism.

**Verdict**: The EWS evidence is suggestive and adds genuine cross-national breadth, but it is not as strong as the p = 0.009 headline suggests. A complexity science reviewer familiar with EWS methodology would consider this preliminary rather than definitive. The paper's framing ("consistent with critical slowing down") is appropriately hedged. **Score: 6.5/10.**

#### 2.5 "Persistent and Self-Reinforcing" vs "Irreversible"

The terminology shift is well-executed. The new framing:
- Retains the three lock-in mechanisms (demographic saturation, sunk capital, institutional path dependence)
- Explicitly acknowledges that exogenous policy interventions could reverse the shift
- Notes that "no country in our 158-nation sample that crossed Q < 1 has returned to Q > 1 within the observation window"
- Draws correctly on Scheffer et al. (2009) for the conceptual vocabulary

This is substantially more defensible than "irreversible." A reviewer can no longer simply cite post-war reconstruction or post-GFC recovery as counter-examples, because the paper now explicitly scopes its claim to "endogenous dynamics."

**Remaining vulnerability**: The observation window is short. For most countries, the Q < 1 period may be only 5-15 years. Claiming "persistent" based on a window this short is weak. The strongest case remains Japan (Q declining since 1990, ~35 years without recovery), but even Japan's experience could be attributed to the specific "lost decades" rather than structural urban investment dynamics.

**Score: 7.5/10** (up from 6.5/10 for the irreversibility claim)

#### 2.6 alpha_N / alpha_R Decomposition

This decomposition remains theoretically elegant but empirically unestimated. The v4 materials do not present any new empirical evidence on alpha_N vs alpha_R. It appears only in ED Fig 6 as a "conceptual decomposition."

The core tension identified in the v2 review persists: **if alpha_R remains positive in mature cities, and if rational investors shift from I_N to I_R, then aggregate alpha should stabilise -- weakening the regime-shift narrative.** The paper's resolution (institutional inertia prevents timely shifting) is plausible for China but is not empirically demonstrated.

**New concern in v4**: The alpha decomposition is now listed as part of Finding 3's supporting evidence ("alpha_N declining vs alpha_R potentially stable"). Using an unestimated conceptual decomposition as "supporting evidence" for an empirical finding is a category error. It should be clearly labelled as a theoretical interpretation, not evidence.

**Score: 6/10** (unchanged from v2)

#### 2.7 Two China MUQ Series Reconciliation

This is the most important new methodological element in v4. The reconciliation is transparent and logically sound:

- **National-accounts MUQ** (NBS data, 1998-2024): turns negative in 2022-2024 (p = 0.043). Primary evidence for Finding 1.
- **Global-panel MUQ** (WB/PWT, PPP-adjusted, ending ~2018-2019): rising through S1-S3 (7.80 -> 12.86 -> 17.12). Used only for income-group stratification in Finding 3.

Three sources of divergence are identified: (a) accounting conventions (national currency vs PPP), (b) time horizon (national data extends to 2024; global panel ends before 2022), (c) different denominators (total FAI vs GFCF).

**Assessment**: This is handled competently. A reviewer would accept the explanation if it is presented clearly in the Methods section. The key is that the paper does not mix the two series in any single analysis.

**Remaining concern**: The global-panel China MUQ rising through S1-S3 directly contradicts the "efficiency decline" narrative. The paper explains this as "scale effects during rapid capital deepening," but this explanation is essentially saying "China's rising MUQ reflects genuine high returns during its construction boom" -- which undermines the claim that the decline is a structural inevitability. The paper should more explicitly address the temporal sequence: returns can be high during the boom phase and still collapse when the boom ends. This is not a contradiction; it is the definition of a regime shift.

**Score: 7/10.**

---

### Round 3: Reader Perspective

#### 3.1 Accessibility to Non-Economists

The paper has improved substantially in accessibility. The MUQ-first framing means the lead finding can be stated in plain language: "Since 2022, every yuan China puts into new urban construction destroys value rather than creating it." The carbon dimension (13.4 GtCO2) speaks directly to a climate audience. The EWS language ("early warning signals for critical transitions") is familiar to ecologists and complexity scientists.

**Remaining accessibility challenges**:
- The OCR concept requires understanding K*, which requires understanding Cobb-Douglas production functions. This will lose non-economists.
- The Simpson's paradox explanation, while correct, is inherently technical. The paper should use a concrete example ("globally, investment efficiency appears to rise because richer countries invest more efficiently and dominate the high-urbanisation group; within each income group, efficiency falls").
- The V(t) measurement discussion is necessarily technical but well-handled through the "seven calibrations, one direction" framing.

**Score: 7/10** (up from ~5.5/10 implicitly in v2)

#### 3.2 Abbreviation Density

The paper uses: Urban Q, OCR, MUQ, CPR, K*, EWS, AR(1), GFCF, CI/GDP, FAI, PWT, NBS, PPP, TWFE, CD, LOESS, ANOVA. This is approximately 17 abbreviations in the main text, which is high for Nature. Nature's style guide recommends minimising abbreviations and spelling out on each first use.

**Critical abbreviations to keep**: Urban Q (the paper's central concept), MUQ, OCR, CPR, EWS.
**Abbreviations to spell out consistently**: GFCF (gross fixed capital formation), FAI (fixed-asset investment), TWFE, CD.
**Abbreviations to eliminate from main text**: PWT, NBS (move to Methods/Data section only), CI/GDP (use "construction investment share").

**Score: 6/10** -- manageable but needs editorial attention.

#### 3.3 Cross-Disciplinary Reach via Carbon Dimension

The carbon dimension is the single most important strategic addition for Nature. It transforms the paper from "urban economics" into "urban economics + climate policy," which is precisely the kind of disciplinary bridging that Nature editors seek. The 13.4 GtCO2 figure, if defensible, would be cited by IPCC working groups and urban climate researchers.

**However**: The carbon estimates are methodologically thin compared to the core economics. A climate scientist on the review panel may view them as back-of-envelope calculations dressed up as findings. The paper's honest framing ("order-of-magnitude estimates") partially addresses this, but the numbers are prominently featured in the abstract and cover letter, where they carry implied precision.

**Score: 7/10** -- the strategic value is high, but the methodological depth must match the prominence.

---

## PART II: FATAL FLAW CHECK

### Previous Fatal 1: V(t) Measurement

**Status: Substantially mitigated, not fully resolved.**

The v4 paper addresses this through:
- V1_adj (age-adjusted valuation) with 1.0%/1.5%/2.0% depreciation sensitivity analysis
- Seven-calibration Monte Carlo framework (98.8% of paths below Q=1)
- MUQ as headline finding (model-free, does not depend on V(t) level)
- Explicit 90% CI for crossing year [2010.1, 2022.5]

The V1_adj analysis (china_q_adjusted_report) shows that age adjustment reduces V by 34-46% in recent years, which is within the expected range. The seven calibrations produce consistent directional results despite differing levels.

**Remaining vulnerability**: The V1_adj depreciation rate (1.5%) is assumed, not estimated from data. Different depreciation assumptions shift the Q=1 crossing year by several years. The paper should present the crossing year as a function of depreciation rate to show this sensitivity.

**Assessment: No longer fatal.** The MUQ-first strategy effectively bypasses the V(t) level problem. The regime shift direction is robust. The precise timing remains uncertain but the paper no longer claims a precise date. **Severity: Major issue, not fatal.**

### Previous Fatal 2: Irreversibility Claim

**Status: Resolved.**

The shift from "irreversible" to "persistent and self-reinforcing" eliminates the strongest theoretical objection. The paper now correctly scopes the claim to endogenous dynamics and acknowledges that exogenous interventions can reverse the shift. Counter-examples (post-war reconstruction, post-GFC recovery) are pre-empted by scope conditions.

**Assessment: No longer a flaw.** The revised framing is defensible and appropriately cautious. **Severity: Resolved.**

### New Concern: OCR Bootstrap CI

**Status: Potential new major issue.**

The China OCR bootstrap 95% CI of [0.25, 1709] was not prominently visible in v2 but is now exposed in the kstar_m2_report. If a reviewer requests uncertainty bounds on OCR and receives this answer, the quantitative content of Finding 2 collapses. The revision plan recommends directional language, but the paper outline v4 still contains quantitative OCR references ("median OCR ~ 1.4," "OCR ~ 1.0," "OCR ~ 0.9").

**Assessment: Major issue requiring attention before submission.** All point estimates of OCR must be removed from the main text and replaced with directional/ranking language, as the revision plan specified. The bootstrap CI should appear only in Extended Data with full context.

### New Concern: Carbon Estimate Precision

**Status: Moderate concern.**

The 13.4 GtCO2 figure is prominent in the abstract and cover letter but is computed from: (K - K*) times a single carbon intensity coefficient. Since K* itself has a bootstrap CI spanning four orders of magnitude, the carbon estimate's true uncertainty is enormous but unreported. The paper calls this a "conservative lower-bound estimate," but it may equally be an upper-bound estimate if K* is underestimated.

**Assessment: Not fatal, but needs explicit uncertainty quantification.** At minimum, report a range based on the K* bootstrap CIs. Alternatively, acknowledge in Methods that the carbon estimate inherits K* uncertainty and is therefore an order-of-magnitude illustration.

---

## PART III: COMPARISON WITH v2 REVIEW

### Improvements Since v2 (Score 6.2/10)

| Dimension | v2 Score | v4 Score | Change | Key Driver |
|-----------|:--------:|:--------:|:------:|------------|
| Title | 6.0 | 7.5 | +1.5 | Shorter, accessible, "persistent" replaces "irreversible" |
| Abstract/framing | 6.5 | 8.0 | +1.5 | MUQ headline, carbon hook, EWS breadth |
| Theoretical originality | 6.5 | 7.0 | +0.5 | Simpson's paradox, terminology refinement |
| Theoretical rigour | 6.0 | 6.5 | +0.5 | Dual MUQ reconciliation, but alpha decomposition still unestimated |
| Evidence convergence | 6.5 | 7.5 | +1.0 | EWS adds genuine new evidence line; carbon adds policy dimension |
| Literature dialogue | 5.5 | 6.0 | +0.5 | Scheffer connection strengthened via EWS; Bettencourt/Acemoglu still weak |
| **Desk reject probability** | **55-65%** | **40-50%** | **-15pp** | MUQ + carbon + EWS collectively strengthen the pitch |

### Issues That Persist from v2

1. **OCR empirical fragility**: The K* model's wide bootstrap CIs make OCR a qualitative rather than quantitative tool. This was M1 in v2 and is still a major issue.

2. **Insufficient engagement with competitive explanations**: Financial cycle, durable housing equilibrium (Glaeser-Gyourko), and Rogoff-Yang explanations are still not systematically addressed in v4's outline or theory responses. This was M2 in v2.

3. **OCR-Q mechanical correlation**: The shared K in the denominators of OCR (K/K*) and Q (V/K) still creates a mechanical negative correlation. Not addressed in v4. This was M3 in v2.

4. **Bettencourt scaling laws**: The cross-section vs time-series distinction for Q (larger cities have higher Q at a point in time, but Q declines over time for a given city) is still not addressed. This was E1 in v2.

5. **Acemoglu/institutional economics**: The land-finance institutional lock-in argument still lacks connection to the broader institutional economics literature. This was E3 in v2.

6. **City-level panel limited to 2010-2016 (7 years)**: No resolution possible without new data.

---

## PART IV: DIMENSION SCORES AND OVERALL ASSESSMENT

### Dimension Scores

| Dimension | Score | Weight | Weighted | Notes |
|-----------|:-----:|:------:|:--------:|-------|
| A. Editorial first impression | 7.5/10 | 15% | 1.125 | Title, abstract, hooks all improved |
| B. Theoretical originality | 7.0/10 | 20% | 1.400 | Simpson's paradox + terminology refinement |
| C. Theoretical rigour | 6.5/10 | 20% | 1.300 | Dual MUQ reconciliation good; alpha decomposition still unestimated |
| D. Evidence completeness | 7.0/10 | 20% | 1.400 | EWS adds breadth; OCR remains fragile |
| E. Methodological soundness | 6.5/10 | 15% | 0.975 | Carbon estimates thin; EWS null hypothesis weak |
| F. Literature and competitive explanations | 6.0/10 | 10% | 0.600 | Improved but gaps remain |
| **Weighted total** | | | **6.80/10** | |

### Desk Reject Probability: 40-50%

(Down from 55-65% in v2. The MUQ headline, carbon dimension, and EWS cross-national evidence collectively address the three main desk-reject risks identified previously.)

### Fatal Flaw Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| Former F1 | V(t) measurement | Major (not fatal) | Mitigated by MUQ-first strategy + Monte Carlo |
| Former F2 | Irreversibility claim | Resolved | "Persistent and self-reinforcing" is defensible |
| New | OCR bootstrap CI [0.25, 1709] | Major | Must remove point estimates from main text |
| New | Carbon estimate precision | Moderate | Must add uncertainty range or explicit caveats |

**No remaining fatal flaws.** Two major issues require attention before submission, but neither is structurally irresolvable.

---

## PART V: OVERALL ASSESSMENT

This paper has improved materially since the v2 review. The seven-action revision plan was well-designed and largely well-executed. The MUQ headline, Simpson's paradox resolution, EWS cross-national evidence, carbon dimension, "persistent and self-reinforcing" terminology, and dual MUQ reconciliation collectively address the most serious concerns from the previous review. The weighted score rises from 6.2 to 6.8, and the desk reject probability falls from 55-65% to 40-50%.

The paper now tells a coherent, three-layer story: (1) China's urban investment has crossed from value-creating to value-destroying, as shown by a model-free sign change in marginal returns; (2) overbuilding is spatially concentrated and follows clear income-group gradients; (3) the efficiency decline is a developing-country phenomenon masked by Simpson's paradox at the global level, with gigatonne-scale carbon implications. The EWS evidence adds cross-national breadth, and the carbon dimension bridges urban economics to planetary sustainability.

However, the paper still carries significant risks for Nature proper. Finding 2 (OCR) rests on a K* model whose bootstrap CIs span four orders of magnitude. The carbon estimates, while strategically important, are methodologically thin -- a single multiplication with no reported uncertainty. The literature engagement remains incomplete: Glaeser-Gyourko, Rogoff-Yang, Bettencourt, and Acemoglu are either absent or superficially treated. The EWS evidence, while statistically significant at the aggregate level, uses a weak null hypothesis and shows uneven regional patterns. These gaps would be exploited by expert reviewers.

The honest assessment is that this paper is a strong submission for a top specialty journal (Nature Cities, Nature Sustainability, or the Proceedings of the National Academy of Sciences) and a borderline submission for Nature proper. The core concept is Nature-worthy; the execution is approaching but has not yet reached Nature standard. The 40-50% desk reject estimate reflects this: the paper has a real chance of being sent out, but also a real chance of being redirected.

---

## PART VI: GO / NO-GO RECOMMENDATION

### **CONDITIONAL GO -- with three mandatory pre-submission actions**

The paper is close enough to Nature standard that submission is justified, provided the following three items are addressed in the final draft:

**Mandatory Action 1: Remove all OCR point estimates from main text.** Replace "median OCR ~ 1.4" and similar with directional language ("substantially above the model-predicted equilibrium," "top quartile among 126 countries"). Report the full bootstrap distribution only in Extended Data. The current outline still violates the revision plan's own recommendation on this point.

**Mandatory Action 2: Add uncertainty bounds to carbon estimates.** Either (a) propagate K* bootstrap uncertainty through the carbon calculation and report a range (e.g., "5-25 GtCO2" rather than "13.4 GtCO2"), or (b) explicitly label the figure as an "illustrative central estimate" in both the abstract and cover letter, with the caveat that it inherits the K* model's uncertainty. The current presentation implies false precision.

**Mandatory Action 3: Add a "competing explanations" paragraph to Discussion.** In ~150 words, address the financial-cycle explanation (Q decline reflects credit tightening, not structural overbuilding), the Glaeser-Gyourko durable housing explanation (Q < 1 can be an equilibrium for durable assets), and the Rogoff-Yang framework (already analysing China's property decline). This paragraph should explain why Urban Q adds analytical value beyond these existing frameworks. Its absence would be immediately noted by a specialist reviewer.

**If these three actions are completed**, the paper merits submission to Nature with a realistic (if not high) probability of surviving to review. If rejected at Nature, the paper would be a strong submission at Nature Cities or PNAS, where the measurement uncertainty and OCR fragility are less likely to be decisive.

**If these actions are not completed**, the desk reject probability rises to 55-60%, and the paper risks a review experience that creates more problems than it solves (reviewers identifying the OCR CI issue or carbon precision issue would require responses that may be difficult to construct after the fact).

---

### Summary Table

| Metric | v2 | v4 (current) | With 3 actions |
|--------|:--:|:------------:|:--------------:|
| Weighted score | 6.2/10 | 6.8/10 | 7.0-7.2/10 |
| Desk reject probability | 55-65% | 40-50% | 35-45% |
| If sent to review: accept probability | 25-35% | 35-45% | 40-50% |
| Overall acceptance probability | 10-15% | 18-25% | 22-30% |

---

*Final pre-submission review prepared by: Peer Reviewer Agent (simulating Nature senior referee)*
*Specialisation: Urban economics, complex systems, institutional economics, climate policy*
*Date: 2026-03-21*
*Confidence level: High (all core materials and previous reviews examined in detail)*
