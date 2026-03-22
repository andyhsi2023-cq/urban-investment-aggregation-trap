# Reviewer A: Urban Economics / Development Economics

## Manuscript: "A Simpson's paradox masks declining returns on urban investment worldwide"

## Target Journal: Nature
## Review Date: 2026-03-21

---

## 1. Overall Assessment

This paper introduces a "Marginal Urban Q" (MUQ) metric -- the incremental asset value per unit of investment, adapted from Tobin's Q -- and applies it across 158 countries, 455 Chinese city-year observations, and 10,760 US MSA-year observations to document three findings: (i) a Simpson's paradox in global investment efficiency; (ii) a sign reversal between China and the US consistent with supply-driven versus demand-driven investment regimes; and (iii) a carbon cost estimate of 5.3 GtCO2 for value-eroding investment in China. The ambition is admirable, and the Simpson's paradox finding is genuinely interesting. However, in its current form, the paper has several major conceptual and empirical weaknesses that prevent me from recommending acceptance at Nature. The MUQ metric conflates asset price changes with value creation in ways that undermine the central narrative; the V(t) measurement problem is more damaging than acknowledged; and the causal language -- though hedged -- still overreaches relative to the descriptive evidence presented.

**Recommendation: Major Revision** -- with significant reservations. The paper could potentially reach Nature standards, but only with substantial theoretical clarification and methodological strengthening. If the authors cannot resolve the V(t) measurement challenge more convincingly, the paper may be better suited for Nature Cities or a top economics journal (Review of Economics and Statistics, Journal of Urban Economics).

---

## 2. Principal Strengths

**S1. The Simpson's paradox is a genuine and important finding.** The demonstration that within-group declines in MUQ are masked by compositional shifts across income groups is clean, robust to leave-one-out analysis and exclusion of China, and has real implications for how policymakers interpret aggregate investment statistics. The within vs. between decomposition (within rho = -0.076, between = +0.114) is elegant.

**S2. The China-US sign reversal is striking and well-documented.** The contrast between beta = -2.23 (China) and beta = +2.75 (US) is robust to multiple specifications including two-way fixed effects, quantile regression, unified DeltaV/GDP metrics, and Monte Carlo mechanical-correlation tests. This is the strongest empirical contribution of the paper.

**S3. The paper is exceptionally well-written for a cross-disciplinary audience.** The prose is clear, precise, and appropriately hedged in most places. The word count is within Nature limits. The consistency check in the HTML comments (all key numbers verified) reflects commendable attention to detail.

**S4. The robustness architecture is impressive.** Seven MUQ calibration variants, Monte Carlo uncertainty propagation, Dirichlet-sampled ensemble weights, mechanical correlation tests, and multiple alternative specifications demonstrate genuine effort to stress-test the findings.

**S5. The carbon framing adds policy urgency.** Connecting investment misallocation to embodied carbon is novel and timely, linking urban economics to climate science in a way that broadens the paper's appeal.

---

## 3. Major Issues

### M1. MUQ conflates asset price changes with value creation -- this is a fundamental conceptual problem

**Problem description**: MUQ = DeltaV(t) / I(t), where DeltaV includes price appreciation of the existing stock. In the US, the paper itself acknowledges that "87% of DeltaV reflects price appreciation of the existing stock, with only 13% attributable to new construction." This means MUQ is overwhelmingly measuring house price changes, not investment efficiency. When US house prices rose during 2012-2022, MUQ was high; when Chinese house prices collapsed in 2022-2024, MUQ turned negative. But house price changes are not the same as value creation from new investment. A city where existing home values doubled due to a tech boom would show high MUQ even if the marginal investment (a new apartment building) was poorly designed and overpriced.

**Why this is major**: The entire interpretive framework rests on MUQ as a measure of "whether each additional unit of investment actually creates value." But as constructed, MUQ primarily reflects asset market dynamics rather than the productivity of marginal investment. The corporate Tobin's Q literature (Hayashi 1982) requires strong assumptions (constant returns to scale, competitive markets, no adjustment costs) even for firms where both market value and replacement cost are directly observable. Applying this logic to entire cities -- where neither V nor K is directly observed -- requires much stronger justification than currently provided.

**Suggested solution**: (a) Clearly separate the "price revaluation" and "new construction" components of DeltaV for China as well as the US. (b) Argue explicitly why price revaluation is informative about investment quality (e.g., if new investment triggers negative price spillovers on existing stock, that is a genuine signal). (c) Consider a "net-of-price" MUQ that strips out existing-stock revaluation, and show that core findings survive.

**Impact if unresolved**: If MUQ is primarily a house price index derivative, then the Simpson's paradox becomes a finding about house price dynamics across income groups, not about investment efficiency. This substantially reduces the novelty claim.

### M2. V(t) measurement uncertainty is so large that it threatens the key threshold claims

**Problem description**: The Q=1 crossing year has a 90% CI spanning approximately 12 years (2010.1-2022.5, per Methods M6). The seven calibrations use fundamentally different numerator definitions (V1: housing stock x commercial price; V1_adj: vintage-weighted with depreciation; V2, V3 from PWT). The fact that PWT-based MUQ for China shows rising values (S1: 7.80, S2: 12.86, S3: 17.12) while NBS-based MUQ shows decline means the directional finding itself depends on data source choice.

**Why this is major**: The paper's narrative hinges on several threshold claims -- 82.2% of cities have MUQ < 1 in 2016; national MUQ turned negative in 2022-2024; 5.3 GtCO2 of "excess" carbon. All of these depend on the absolute level of MUQ, which is precisely what the seven calibrations cannot agree on. The ensemble weighting (V1_adj/K2 = 0.30, V1/K2 = 0.25, etc.) is presented as methodologically principled but is ultimately subjective -- the Dirichlet concentration parameter alpha = 20 constrains the weights to stay close to the central weights, which were chosen by the authors. Different reasonable weight choices could shift the Q=1 crossing year by a decade.

**Suggested solution**: (a) De-emphasize threshold claims (MUQ < 1, MUQ < 0) and focus on directional findings that are robust across calibrations. (b) Report which specific findings are robust to all seven calibrations and which depend on calibration choice. (c) Consider presenting the 82.2% figure as calibration-specific rather than as a definitive finding.

**Impact if unresolved**: Reviewers at Nature will immediately question whether a 12-year confidence interval on the crossing year is compatible with the paper's strong policy claims. This is the most likely reason for a Major Revision rather than acceptance.

### M3. The "supply-driven vs. demand-driven" framework lacks independent testable predictions

**Problem description**: The paper attributes the China-US sign reversal to "supply-driven versus demand-driven investment regimes." But this is an ex post label applied to an observed pattern, not a falsifiable theoretical prediction. The paper offers one testable prediction: "countries transitioning from low-income to middle-income status should exhibit declining within-group MUQ." But this prediction follows from diminishing returns more generally and does not specifically test the supply-driven mechanism.

**Why this is major**: For Nature, a descriptive finding (the sign reversal) needs either (a) a compelling theoretical mechanism that generates unique predictions, or (b) a credible causal identification strategy. The paper has neither. The Three Red Lines DID is the closest thing to causal evidence, but the parallel trends are marginal (F = 2.82, p = 0.093), the placebo test fails (p < 0.001), and the mechanism channel test shows null results (FAI/GDP did not differentially decline in high-dependence cities, p = 0.33). These diagnostic failures are honestly reported but severely undermine the causal interpretation.

**Suggested solution**: (a) Develop the supply-driven framework into a simple formal model that generates predictions beyond what diminishing returns alone would produce. For example: in a supply-driven regime, MUQ should decline faster in cities with higher land-revenue dependence, controlling for demand fundamentals (population growth, income growth). (b) Test this prediction in the Chinese city panel. (c) Downgrade the Three Red Lines analysis from "quasi-natural experiment" to "suggestive descriptive evidence" given the failed diagnostic tests.

**Impact if unresolved**: Without a testable mechanism, the paper documents a pattern but does not explain it. Nature editors will ask: "What do we learn beyond 'China and the US are different'?"

### M4. China-US comparison uses non-comparable MUQ definitions

**Problem description**: Chinese MUQ uses FAI (total fixed-asset investment including infrastructure, equipment, real estate) as the denominator, while US MUQ uses housing unit growth x lagged median price. These measure fundamentally different things. FAI includes highway construction, factory equipment, and utility installation; the US measure captures residential construction only. The "unified DeltaV/GDP specification" partially addresses this, but the attenuated coefficient (China beta = -0.37 vs. -2.23 in the primary specification) suggests that much of the primary finding is driven by the specific variable construction.

**Why this is major**: The sign reversal is the paper's second headline finding, but comparing total fixed-asset investment efficiency in China to residential construction efficiency in the US is not a clean institutional comparison. The US also has public infrastructure investment, which is excluded from the analysis. If US public infrastructure MUQ were included, the sign reversal might attenuate or even disappear (US infrastructure investment in many cities is notoriously inefficient -- see Flyvbjerg 2003, Brooks and Liscow 2023).

**Suggested solution**: (a) Acknowledge this limitation more prominently -- currently buried in paragraph 6 of the Discussion. (b) Attempt a like-for-like comparison using residential investment only for both countries (China's real-estate development investment is available from NBS). (c) Alternatively, frame the comparison as revealing different relationships between total economic investment intensity and housing market outcomes, rather than as a direct efficiency comparison.

**Impact if unresolved**: A knowledgeable reviewer will view the sign reversal as potentially artifactual -- driven by comparing apples (total investment) to oranges (residential construction).

### M5. The carbon estimate conflates economic inefficiency with social waste

**Problem description**: The paper defines "excess" investment as I(t) x max(0, 1 - MUQ(t)), implying that any investment generating MUQ < 1 is wasteful. But much public investment (roads, schools, hospitals, water systems) generates returns that are not captured in housing asset values. A highway that reduces commute times by 30 minutes increases social welfare enormously but may not show up in MUQ if house prices do not fully capitalize the benefit. Similarly, schools and hospitals in fourth-tier Chinese cities have MUQ = 0.20, but the social return on these investments may be very high.

**Why this is major**: The 5.3 GtCO2 headline number is the paper's most media-friendly claim, but it rests on the assumption that MUQ < 1 implies waste. This assumption is unjustified for public goods with non-market returns. If even 30-40% of the "excess" investment represents socially valuable public goods, the carbon estimate drops to 3.2-3.7 GtCO2 and the narrative shifts from "massive waste" to "moderate inefficiency with significant measurement uncertainty."

**Suggested solution**: (a) Decompose FAI into real-estate development investment (where MUQ < 1 more plausibly indicates waste) and infrastructure investment (where non-market returns are important). NBS publishes this decomposition. (b) Present the carbon estimate as an upper bound on waste-associated emissions. (c) Discuss the public-goods externality issue explicitly.

**Impact if unresolved**: The carbon claim will attract criticism from development economists who will argue (correctly) that not all low-MUQ investment is wasteful. This risks undermining the paper's credibility on its strongest finding (the Simpson's paradox).

### M6. The Chinese city panel is narrow and the V reconstruction is fragile

**Problem description**: The city panel spans only 2010-2016 (7 years, 455 observations after filtering), with V reconstructed as population x median housing price x per-capita housing area. Coverage varies enormously: only 20 cities in 2011 but 213 in 2016. The 82.2% headline figure comes from the 2016 cross-section alone. The Mann-Kendall test for temporal trend is non-significant (p = 0.45), meaning there is no statistical evidence of MUQ declining over 2010-2016.

**Why this is major**: The paper's city-level claims rest on a thin, short, and unbalanced panel. The V reconstruction multiplies three noisy variables (population, price, area), each with its own measurement error. The fixed-effects regression yields a non-significant coefficient (beta = -1.96, p = 0.178 with TWFE; beta = -1.73, p = 0.063 with within estimator), meaning the negative relationship between FAI/GDP and MUQ is not robust to absorbing city-level heterogeneity. The pooled OLS result (beta = -2.23, p < 10^-6) may reflect between-city differences (rich coastal cities have low FAI/GDP and high MUQ) rather than within-city dynamics.

**Suggested solution**: (a) Extend the panel to 2023 using updated price data. (b) Report the TWFE and within-estimator results more prominently and discuss what the attenuation implies. (c) Consider an instrumental variables approach (e.g., using land-supply shocks as instruments for FAI/GDP).

**Impact if unresolved**: The city-level finding is the weakest link in the empirical chain. If the within-city effect is truly zero (as the TWFE p-value of 0.178 suggests), the negative association is entirely cross-sectional, which is harder to interpret causally.

### M7. The Simpson's paradox, while real, may be less surprising than claimed

**Problem description**: The paper presents the Simpson's paradox as "the first systematic documentation of this phenomenon in the urban investment literature." But the phenomenon -- that within-group trends differ from aggregate trends when group composition changes -- is extremely common in development economics. It is well known that aggregate investment efficiency metrics (ICOR, for instance) behave differently within and across income groups. Pritchett (2000), whom the authors cite, already documented that the relationship between public capital and growth varies enormously across income groups. The novelty claim needs to be more precisely stated.

**Why this is major**: For Nature, the novelty bar is extremely high. If a development economist reviewer says "this is just the well-known heterogeneity in investment efficiency across income groups, repackaged as a Simpson's paradox," the paper's headline contribution is diminished.

**Suggested solution**: (a) Explicitly address how this finding differs from the known heterogeneity documented by Pritchett (2000), Dabla-Norris et al. (2012), and the ICOR literature. (b) Argue that the specific mechanism (compositional shift producing sign reversal) has not been documented, even if heterogeneity per se is known. (c) Quantify the policy error that results from ignoring the paradox -- e.g., how much investment would be misallocated if policymakers relied on aggregate MUQ trends?

---

## 4. Minor Issues

### m1. Inconsistency in China MUQ direction
The global panel (PWT-based) shows China's MUQ rising across urbanisation stages (S1: 7.80, S2: 12.86, S3: 17.12), while the paper's narrative claims declining returns. The paper explains this as "three artefacts" (PPP adjustment, truncated time series, denominator effects), but the muq_real_correction_report reveals that even after real correction, China's MUQ is rising in the PWT data through 2018. The NBS-based decline only appears after 2021. This discrepancy deserves more transparent treatment.

### m2. One-tier city sample size
First-tier city MUQ = 7.46 is based on N = 3 (Beijing, Shanghai, Guangzhou or Shenzhen). This is too small for reliable inference. Report this caveat.

### m3. Quantile regression interpretation
The paper states that "cities with the highest marginal returns are most sensitive to over-investment" based on the steepening quantile regression gradient. But the 90th percentile of MUQ includes outlier cities with extreme positive values, and the larger coefficient may simply reflect greater variance rather than economic sensitivity.

### m4. "Largest misallocation of physical capital in modern economic history"
This claim in the final sentence of the Discussion is not supported by any comparative analysis. It requires benchmarking against other episodes (Soviet industrialisation, Japanese bubble, US subprime). Either substantiate or remove.

### m5. Missing key references
The paper does not cite Saiz (2010) on housing supply elasticity (critical for interpreting the US results), Hsieh and Moretti (2019) on spatial misallocation of housing, or Brandt et al. (2020) on capital misallocation in China. These are directly relevant.

### m6. Figure 1c
The within/between decomposition bar chart (within = -0.076, between = +0.114) is the most important panel for understanding the Simpson's paradox, but it is given very little visual real estate. Consider making it a more prominent element.

### m7. Carbon intensity decay rate
The 2.89% annual decay rate for carbon intensity is "calibrated to construction-sector emission factors" from one source (CBECA). Given the 25-year time span, even small errors in the decay rate compound substantially (sensitivity analysis shows range of 2.7-9.7 GtCO2). More sources for cross-validation would strengthen this.

### m8. References placeholder
The reference list is still a placeholder. Ensure all in-text citations are properly formatted before submission.

---

## 5. Specific Recommendations for Moving from Major Revision to Accept

If I were advising the authors on how to make this paper competitive for Nature, I would prioritize the following changes:

1. **Restructure the contribution hierarchy.** Lead with the Simpson's paradox as the primary finding (it is the most robust and novel). Reframe the China-US comparison as an illustration of the paradox's mechanism, not as a standalone finding. Downgrade the carbon estimate to Extended Data or a brief mention.

2. **Resolve the V(t) problem through transparency.** Present a "traffic light" table showing which findings are Green (robust to all calibrations), Yellow (sensitive to calibration choice), and Red (depend on specific calibrations). This turns a weakness into a strength by demonstrating intellectual honesty.

3. **Separate house price effects from investment efficiency.** Decompose DeltaV into existing-stock revaluation and new-construction value for both countries. If the Simpson's paradox survives in the new-construction component alone, the paper is dramatically strengthened.

4. **Drop or substantially qualify the Three Red Lines analysis.** Given the failed placebo test and marginal parallel trends, this analysis weakens rather than strengthens the paper. Either fix the identification (e.g., triple differences with a credible third dimension) or move it to Supplementary Information as "suggestive evidence."

5. **Formalize the supply-driven framework.** Even a two-page Supplementary model showing how fiscal incentives generate declining MUQ in equilibrium -- and how this model predicts the sign reversal -- would transform the paper from "interesting pattern" to "theoretical contribution."

---

## 6. Confidential Comments to the Editor

**Real competitiveness assessment**: This paper has a genuinely interesting core finding (the Simpson's paradox in global investment efficiency) that is currently buried under too many secondary claims of varying quality. The MUQ metric is creative but insufficiently validated; the China-US comparison is eye-catching but methodologically uneven; the carbon estimate is attention-grabbing but conceptually problematic. In its current form, I estimate this paper would be in the top 15-20% of Nature submissions in terms of ambition and relevance, but outside the top 8% in terms of execution.

**Recommendation on sending for review**: Yes, I recommend sending this for full review, conditional on the editor's judgment that the Simpson's paradox framing is sufficiently novel for Nature's audience. The paper addresses a genuinely important question (is global urban investment efficient?), and the cross-national scope is impressive. However, I would assign at least one reviewer from the capital misallocation literature (Hsieh-Klenow-Restucpo tradition) and one from the climate/carbon accounting community.

**Most appropriate journal**: In order of fit:

1. **Nature Cities** -- excellent fit for scope and audience; slightly relaxed novelty bar would accommodate the current evidence strength.
2. **Nature** -- possible if the authors can resolve M1 (price vs. value conflation) and M2 (V(t) uncertainty). The Simpson's paradox is the Nature-level finding; everything else is supporting evidence.
3. **Review of Economics and Statistics** -- if the authors want to lead with the economic methodology and add a formal model.
4. **Journal of Urban Economics** -- if the paper focuses on the China-US comparison with a formal theoretical framework.

The paper is clearly not a reject -- it is too ambitious, too well-executed in parts, and too policy-relevant for that. But it needs to decide what it is: a methodological paper about measuring urban investment efficiency (in which case, resolve M1 and M2); a development economics paper about investment regime differences (in which case, add a model and better identification); or a climate paper about embodied carbon waste (in which case, resolve M5). Currently, it tries to be all three and is fully convincing as none.

---

*Reviewer A*
*Expertise: Urban economics, development economics, Tobin's Q, housing markets, China's fiscal system*
*Conflicts of interest: None declared*
