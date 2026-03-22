# Simpson's paradox masks declining returns on urban investment worldwide

## Abstract

Aggregate statistics suggest returns on urban investment remain stable as economies urbanise. This stability is a Simpson's paradox. We construct a marginal Urban Q across 157 countries and 1,567 subnational regions spanning eight countries and six continents. Within every developing-economy income group, returns decline with urbanisation (all p < 0.001 under a GDP-based formulation immune to housing-price cycles), but compositional shifts conceal the decline. We prove this aggregation trap is a mathematical necessity under three empirically verified conditions -- and that it extends to any domain where heterogeneous units are evaluated on pooled metrics. At the city level, investment intensity is negatively associated with returns in China (beta = -0.37) but positively in the United States (+2.81) and Japan (+0.64). Japan's 67-year prefectural record shows that at matched urbanisation rates, China's returns are 3.4 times lower alongside 2.3 times higher investment intensity. The cumulative below-parity investment in China alone totalled approximately US$18 trillion (90% CI: 12--24) between 2000 and 2024.

---

## Introduction

Every developing economy that urbanises must answer a question it cannot easily measure: does each additional unit of urban investment still create more value than it costs? Aggregate statistics suggest the answer is reassuringly stable -- across 157 countries, the relationship between marginal investment returns and urbanisation is weakly positive. Yet this reassurance is a Simpson's paradox: within every developing-economy income group, marginal returns decline significantly, while compositional shifts across groups produce an illusion of resilience in pooled data. The consequences of this hidden decline are already visible at street level. In Hegang, a northeastern Chinese city of 700,000, apartments sell for less than US$3,000 -- a price that implies negative marginal returns on every yuan of recent construction. In Detroit, entire blocks stand vacant after decades of federal investment. These are not isolated failures; they are local manifestations of a pattern that aggregate statistics are structurally unable to detect.

This measurement vacuum is compounded by what we term the *aggregation trap*: pooled investment statistics, by combining heterogeneous trajectories, systematically conceal efficiency erosion within subgroups -- a manifestation of Simpson's paradox untested in the urban investment context. We prove (Box 1) that under three empirically verifiable conditions -- within-group decline, endogenous group graduation, and compositional dominance -- the trap is a mathematical necessity (under conditions stated in Box 1), not a statistical curiosity. The phenomenon parallels known aggregation failures in development economics: Pritchett^7 demonstrated that cumulated investment effort bears little resemblance to productive capital; Hsieh and Klenow^20 documented how factor misallocation across heterogeneous firms substantially reduces aggregate TFP in China and India; Restuccia and Rogerson^27 formalised how policy distortions reduce aggregate productivity through factor misallocation across establishments. Easterly^19 showed that the financing-gap model fails empirically. Yet no cross-national framework measures whether marginal urban investment creates or destroys asset value, a gap that persists in the urban agglomeration literature^36,37,38. Tobin's Q -- the ratio of market value to replacement cost -- has guided corporate investment theory for half a century^3,4, yet has never been applied to the urban built environment.

Here we construct a marginal Urban Q (MUQ) spanning 157 countries and 1,567 subnational regions across eight countries and six continents, validated in parallel with a GDP-based formulation that is immune to housing-price cycles. We document two principal findings. First, a Simpson's paradox: within every developing-economy income group, MUQ declines with urbanisation, but the aggregate trend is flat or positive -- a pattern confirmed under both housing-based and GDP-based definitions, reproduced in a unified panel of 1,567 regions (beta = -0.043, p < 0.001), and proved to be mathematically inevitable when three conditions hold (Box 1). Second, at the city and prefecture level, a clean specification removing mechanical correlation shows a negative investment-return association in China (beta = -0.37, p = 0.019) but a positive one in the United States (beta = +2.81, p < 10^-6) and Japan (pooled beta = +0.64, p < 10^-6; TWFE beta = +0.057, p = 0.037), a pattern consistent with divergent institutional contexts. Japan's 67-year prefectural record provides the fullest available trajectory of urban investment efficiency, indicating that China at 54% urbanisation exhibits MUQ levels that Japan did not reach until urbanisation exceeded 90%.

Several scope limitations merit explicit statement. MUQ is a descriptive measure of investment outcomes, not an identification strategy for causal mechanisms. Cross-national comparisons indicate institutional correlates of efficiency divergence, not causes. The within-city estimator reverses the sign of the investment-return association, indicating that the negative pattern is a structural cross-sectional regularity rather than a within-city dynamic. The aggregation trap theorem's conditions hold across countries (three-fold verification) but are not satisfied within single countries, indicating that the paradox is a cross-development-stage phenomenon. We report these boundaries transparently throughout.

## Results

### Finding 1: Simpson's paradox in urban investment returns -- multi-scale verification and theorem confirmation

**GDP-based MUQ.** To test whether declining returns are robust to alternative metrics, we construct a GDP-based MUQ (= DeltaGDP / GFCF, the inverse of the incremental capital-output ratio) using World Bank constant-2015-USD data across 157 countries. The paradox is reproduced and strengthened: within low-income countries, rho = -0.116 (p < 0.001, N = 1,284); lower-middle-income, rho = -0.131 (p < 0.001, N = 1,681); upper-middle-income, rho = -0.248 (p < 0.001, N = 1,834). High-income countries show no significant trend (rho = -0.035, p = 0.080). Leave-one-out analysis within the upper-middle-income group confirms that all 40 countries yield negative, significant correlations. A parallel analysis using Penn World Table real GDP produces consistent results (all developing groups p < 0.001). Block bootstrap resampling at the country level preserves significance in all three developing groups (Extended Data Table 1). We note that Easterly^19 critiqued the use of ICOR as a normative planning tool for projecting investment requirements. Our use is distinct: we employ 1/ICOR not as an efficiency metric but as a diagnostic signal immune to housing-price cycles, testing whether the within-group decline pattern is robust to an entirely different operationalisation. The convergence of housing-based and GDP-based results strengthens both.

**Housing-based MUQ.** Under the original housing-market-based MUQ across 144 countries, the paradox also holds: low-income rho = -0.150 (p = 0.002); lower-middle rho = -0.122 (p = 0.002); upper-middle rho = -0.099 (p <= 0.003); high-income rho = -0.013 (p = 0.633). The within-group pattern is robust to excluding China (upper-middle rho = -0.095, p = 0.005).

**Unified regional panel.** To extend the paradox below the national level, we harmonise GDP-based MUQ across 1,567 subnational regions in eight countries (China 275 cities, Japan 47 prefectures, Korea 17 metropolitan/provincial units, United States 921 MSAs, Europe 265 NUTS-2 regions, Australia 8 states, South Africa 9 provinces; 30,098 observations). In a panel regression with country and year fixed effects, log GDP per capita is negatively associated with MUQ (beta = -0.043, SE = 0.013, p < 0.001, R^2 = 0.457, N = 28,492), confirming that the efficiency-development gradient persists at the subnational level.

**Within-between decomposition and theorem confirmation.** The paradox arises because countries that urbanise also graduate into higher income groups, which carry higher average MUQ. This between-group compositional uplift offsets within-group erosion, producing the aggregate illusion of stability -- the aggregation trap (Fig. 1). We formalise this mechanism in Box 1 and prove that when three conditions hold -- within-group decline, systematic compositional shift, and compositional dominance -- the paradox is not merely empirically observed but mathematically inevitable. All three conditions are satisfied in the global panel (Box 1, empirical verification). The balance is inherently temporary: graduation potential is bounded, but urbanisation continues.

**Boundary condition: within-country paradox not detected.** Systematic testing across seven countries shows that the aggregation trap conditions (A1--A3) are satisfied at the cross-national level (Section 7 of the theorem verification) but not within any single country: 0 of 7 countries satisfy all three conditions at the regional level. In Japan, Korea, and China, within-group decline (A1) holds, but compositional dominance (A3) does not -- the between-group efficiency gap within a single country is too small to overwhelm within-group decline. The aggregation trap is a cross-development-stage phenomenon, not a within-country spatial pattern.

### Finding 2: City-level efficiency mapping -- multi-country comparison

**Sign reversal: China versus the United States.** A clean specification eliminating shared-denominator mechanical correlation (DeltaV/GDP regressed on investment intensity) shows a negative investment-return association in China (beta = -0.37, 95% CI [-0.67, -0.06], p = 0.019, N = 455 city-years) and a positive one in the United States (beta = +2.81, p < 10^-6, N = 10,760 MSA-years). The attenuation from the original MUQ specification (beta = -2.26) to the clean specification quantifies the mechanical-correlation share at 83.7%; the residual 16.3% represents the between-city association net of the shared-denominator artefact. Investment intensity explains less than 2% of cross-city variance in value growth (R^2 = 0.017) -- expected in a between-city specification where persistent city characteristics dominate; the specification tests sign and direction, not explanatory power. The positive US association is consistent with demand-responsive housing supply^5,26.

**Japan: 67-year prefectural record.** Japan's 47 prefectures (3,149 observations, 1956--2022) provide the fullest available trajectory. The clean specification yields pooled beta = +0.638 (p < 10^-6); prefecture fixed effects beta = +0.813 (p < 10^-30); two-way fixed effects beta = +0.057 (p = 0.037). Period decomposition shows declining investment productivity: the high-growth era (1960--1973) coefficient of 0.127 falls to 0.073 during the recovery period (2003--2022). Bai-Perron structural break tests identify two breaks at 1980 and 1990, with mean MUQ collapsing from 0.403 (1956--1980) to 0.226 (1981--1990) to 0.034 (1991--2022).

**China--Japan mirror.** The comparison between China and Japan at equivalent urbanisation stages is the most striking pattern in the data. At approximately 54% urbanisation, China's MUQ (0.144) is 29% of Japan's (0.494), alongside investment intensity (GFCF/GDP) 2.3 times higher (China 44% versus Japan 31%). China's MUQ decline rate (-0.0074 per year) is 2.7 times Japan's (-0.0027 per year). Japan did not cross below MUQ = 0.1 until urbanisation exceeded 80%; China crossed that threshold at 57%. The divergence is consistent with fundamentally different institutional models of capital allocation across the urban hierarchy.

**Crisis-recovery patterns.** Japan's post-bubble trajectory (permanent structural downshift, MUQ mean 0.034 after 1991), Korea's 1997 V-shaped recovery (recovery ratio 0.78), and Europe's PIIGS L-shaped stagnation (recovery ratio 0.65) indicate that MUQ decline is trend-structural but annual recovery is possible. All 47 Japanese prefectures experienced MUQ < 0 at some point; all 47 subsequently recovered above 0.1 -- falsifying any claim of strict irreversibility.

**China provincial panel.** Province fixed effects on 31 provinces (2011--2019) yield beta = -0.164 (p = 0.001, N = 249), reinforcing the city-level finding with higher-quality FAI data directly observed at the provincial level rather than estimated.

**Quantity versus price composition.** In China, 44% of asset value change reflects new physical construction versus 11% in the United States, where appreciation of existing housing dominates (87%). This 3.8-fold divergence means Chinese MUQ predominantly captures real construction-efficiency information.

**Within-city estimator and qualifications.** City fixed effects reverse the sign in China: beta_FE = +0.52 (clustered SE = 0.10, p < 0.001); two-way fixed effects yield beta = +0.16 (p = 0.47, not significant). The panel structure constrains interpretation: 150 of 213 cities contribute only one observation, limiting within-city variation. The sign reversal is consistent with the interpretation that the negative association reflects cross-sectional capital-allocation patterns -- which cities receive investment -- rather than within-city investment dynamics. A difference-in-differences analysis^39 exploiting China's 2020 Three Red Lines credit-tightening policy is reported in Extended Data; diagnostic limitations preclude definitive causal interpretation.

---

## Box 1 | The Aggregation Trap Theorem

Urban investment statistics are simultaneously distorted by two distinct statistical artefacts. Part A identifies a mechanical--economic decomposition: the scaling gap between asset values and capital stocks contains a large mechanical component (94.6%) that cancels in cross-national comparison, leaving a pure economic signal. Part B identifies a compositional decomposition: the aggregation trap proves that within-group efficiency decline is mathematically guaranteed to be masked by between-group graduation under three conditions.

**Part A: The Scaling Gap.** Urban asset value decomposes as V = Population x PerCapitaArea x Price, yielding a scaling exponent beta_V = 1 + beta_A + beta_P, where the mechanical component (= 1) accounts for 94.6% of beta_V in China (pooled: beta_V = 1.057, beta_A = -0.256, beta_P = 0.313) and 88.4% in the United States (beta_V = 1.131). Crucially, the cross-national difference Delta-beta is entirely economic: the mechanical component cancels exactly (1 - 1 = 0), leaving Delta-beta = 0.057 - 0.131 = -0.075 (SE = 0.054). SUR estimation shows this difference is significant in 2 of 10 overlapping years (p < 0.05), underscoring that the scaling gap is a structural observation requiring cautious interpretation. Scaling exponents may vary with boundary definitions^23,24; meta-analytic evidence confirms substantial cross-system variation^28.

**Part B: The Aggregation Trap Theorem.** We formalise the compositional mechanism underlying the paradox. Let K groups have efficiency E_k(u) = alpha_k + beta_k * u, with weight function w_k(u) summing to unity. The aggregate E_agg(u) = Sum_k w_k(u) * E_k(u).

*Theorem.* Under three conditions -- (A1) within-group decline: beta_k <= 0 for all k; (A2) systematic compositional shift: Sum_k w_k'(u) * alpha_k > 0; (A3) composition dominates within: the compositional uplift exceeds the within-group drag at every u -- the aggregate slope is non-negative even though every within-group slope is non-positive. The Simpson's paradox is a mathematical necessity under three empirically verified conditions.

*Two-group simplification.* With two groups sharing decline rate gamma and baseline gap Delta-alpha = alpha_H - alpha_L, the paradox arises if and only if Delta-alpha >= gamma. The escalator of compositional shift outpaces the treadmill of within-group decline. This condition has a natural interpretation: the efficiency gap between developmental stages must exceed the rate at which efficiency erodes within any single stage -- a condition that holds globally (between-component 0.114 versus within-component 0.076) but fails within any single country, where the between-region efficiency gap is too narrow.

*Empirical verification (cross-national).* In the global panel: A1 holds (all four income groups show negative Spearman rho, three significant at p < 0.003). A2 holds (mass shifts from low-income toward upper-middle-income groups as urbanisation increases). A3 holds (between-group component 0.114 exceeds within-group component 0.076; ratio 1.5x). All three conditions are satisfied; the theorem correctly predicts the observed paradox.

*Boundary condition (within-country).* Testing across seven countries at the subnational level, 0 of 7 satisfy all three conditions. Within-group decline (A1) holds in China, Japan, Korea, and South Africa, but compositional dominance (A3) fails in every case: the efficiency gap between subnational regions within a single country is insufficient to overwhelm within-group decline. The aggregation trap is a cross-development-stage phenomenon that operates between countries at different income levels, not between regions within a single economy.

---

## Discussion

Aggregate investment statistics, as currently reported, are structurally unable to detect efficiency decline in urbanising economies -- and the theorem we prove is consistent with this failure. Within every developing-economy income group, marginal returns on urban investment decline significantly with urbanisation, confirmed independently under both housing-based and GDP-based formulations, robust to leave-one-out exclusion of all 40 upper-middle-income countries, and reproduced in a unified panel of 1,567 regions across eight countries and six continents. Yet in pooled data the trend is flat: a Simpson's paradox that is a mathematical necessity under three empirically verified conditions. At the city and prefecture level, the investment-return relationship reverses sign between China (beta = -0.37) and the United States (beta = +2.81) under a clean specification that eliminates mechanical correlation, while Japan's 67-year record indicates that China's efficiency at 54% urbanisation is already lower than Japan's was at equivalent stages -- alongside investment intensity more than twice as high. These findings are descriptive: they document patterns, not causes. But the patterns carry an urgent implication.

**China--Japan mirror, mechanisms, and policy implications.** The policy message is not "invest less" but "invest differently as urbanisation advances." The China--Japan comparison quantifies the stakes: at matched urbanisation rates, China's marginal return on investment is less than one-third of Japan's, and the gap is widening 2.7 times faster. Japan's post-bubble experience -- a permanent structural downshift in MUQ from 0.40 to 0.03 -- shows that a comparable trajectory has not reversed in the Japanese case even as investment levels adjusted. Korea's V-shaped recovery after 1997 (recovery ratio 0.78) is consistent with institutional restructuring being followed by restoration of investment efficiency, while Europe's PIIGS L-shaped stagnation (recovery ratio 0.65) shows that below-parity returns have persisted for a decade in the absence of such restructuring. First-tier Chinese cities retain substantial headroom; lower-tier cities require asset absorption rather than greenfield construction, consistent with the long-term fiscal consequences of China's stimulus-era investment^25.

Several mechanisms may underlie the China--Japan efficiency divergence, though their causal roles remain unidentified: China's land-revenue fiscal model, which incentivises local governments to expand construction regardless of demand signals^13,25; the hukou system, which constrains labour mobility and creates spatial mismatches between investment location and population demand^22; and GDP-target competition among prefectures, which rewards investment volume over returns. These remain hypotheses for future causal investigation using instrumental variable or regression discontinuity designs.

**The economic magnitude.** The cumulative below-parity investment -- computed as Sum(FAI x max(0, 1 - MUQ)) across all years -- totalled approximately US$18 trillion (90% CI: 12--24) in China between 2000 and 2024, with 91% concentrated in the 2021--2024 market correction period. The unified panel suggests that the efficiency-development gradient operates similarly across all three developing-economy income groups. The dollar magnitude provides the most methodologically grounded measure of the aggregation trap's economic consequences, requiring no auxiliary assumptions beyond MUQ itself.

**The aggregation trap as a general phenomenon.** The theorem we prove (Box 1) is the central theoretical contribution of this paper. It identifies sufficient conditions under which pooled statistics *must* mask within-group decline -- conditions that are not specific to urban investment. The three requirements -- within-group deterioration, endogenous graduation between strata, and compositional dominance -- describe any system where units improve their categorical standing while the metric of interest erodes within categories. The structure is isomorphic to Simpson's paradox^31, but the theorem specifies *when* the paradox is guaranteed rather than merely possible. Parallel structures exist across domains: in medicine, treatments worsening outcomes within every stratum can appear beneficial in pooled data^31,32; in education, school quality may decline within types while aggregate scores rise through student migration; in infrastructure-gap estimation, the assumption of constant marginal returns^7,19 is precisely the aggregation trap in another guise; and in international finance, aggregate risk-sharing metrics may mask heterogeneous country-level exposures^40. The boundary condition is equally diagnostic: within single countries, the between-group efficiency gap is too small to generate the paradox (0 of 7 countries satisfy A3), suggesting that the trap operates specifically at the interface between developmental stages. This scope condition -- cross-development-stage but not within-country -- may itself serve as a diagnostic for identifying other domains where compositional masking is consequential.

**Limitations.** Five limitations warrant discussion. First, seven calibration variants bound but do not resolve uncertainty in the national MUQ trajectory (Q = 1 crossing year 90% CI spans approximately 12 years). Second, all core findings are descriptive; we do not identify why returns erode, only that they do -- and MUQ measures asset market value, not social value, so investment with MUQ < 1 may generate positive externalities not captured by market prices. Third, the within-city estimator reverses the sign of the investment-return association, indicating that the negative effect is a cross-sectional between-city regularity, not a within-city causal dynamic. Fourth, the Chinese city panel spans only 2011--2016, with V reconstructed rather than directly observed; the panel is severely unbalanced (150 of 213 cities contribute one observation), and FAI series after 2017 are estimated from growth rates due to statistical discontinuation. Fifth, the aggregation trap theorem's three conditions hold at the cross-national level but not within single countries, limiting the paradox to a cross-development-stage phenomenon.

The aggregation trap we prove is not confined to urban investment. It is a mathematical property of any system in which heterogeneous units are evaluated on pooled metrics while graduating between categories -- and the conditions for its inevitability are empirically common: within-group decline is the norm in maturing systems, graduation between strata is the aspiration of development policy, and the efficiency gap between strata need only exceed the within-group erosion rate. In the domain we examine, the consequences are already staggering: approximately eighteen trillion dollars in below-parity urban investment in a single country, concealed by the very statistical conventions designed to measure it. As India, Vietnam, Indonesia, and a generation of urbanising economies commit to the next wave of construction, the question is not whether they will encounter diminishing returns -- the theorem guarantees that pooled statistics will fail to detect it -- but whether their measurement systems will see through the aggregation trap before the concrete is in the ground.

---

## Methods

### M1. Marginal Urban Q (MUQ) construction

We define the Marginal Urban Q as MUQ(t) = DeltaV(t) / I(t), where DeltaV(t) is the year-on-year change in urban asset value and I(t) is gross investment. MUQ < 1 indicates that marginal investment generates less than one unit of asset value per unit of cost.

**Housing-based MUQ.** *China national level*: V(t) was estimated using seven calibrations combining three numerator definitions and two denominator definitions, combined via a weighted ensemble with Dirichlet-sampled weights (concentration parameter alpha = 20). I(t) was total fixed-asset investment from NBS. Coverage: 1998--2024. *China city level*: for 213 prefecture-level cities (2011--2016), V was reconstructed as population x median housing price x per-capita housing area, and I was fixed-asset investment (FAI). After excluding observations with FAI < 100 million yuan and applying 1%/99% winsorisation, 455 city-year observations were retained. *China provincial level*: for 31 provinces (2011--2019), V was constructed from provincial housing stock, prices, and per-capita area; FAI was directly observed from NBS provincial statistics. After winsorisation, 249 observations were retained. *US metropolitan areas*: V = median home value x housing units from Census ACS 5-Year estimates; I was approximated as the change in housing units x lagged median price. Coverage: 921 MSAs, 2010--2022 (10,760 differenced observations after 1%/99% winsorisation).

**GDP-based MUQ.** To provide a formulation immune to housing-price cycles, we construct MUQ_GDP = DeltaGDP / GFCF (the inverse of the incremental capital-output ratio) using World Bank WDI constant-2015-USD GDP and gross fixed capital formation. Coverage: 157 countries across four World Bank income groups, 1960--2023. A parallel series uses Penn World Table real GDP (rgdpna). The GDP-based MUQ captures whether marginal investment generates proportional output growth, complementing the housing-based MUQ that captures asset-value capitalisation.

**Unified regional panel.** GDP-based MUQ was harmonised across 1,567 subnational regions in eight countries: China (275 cities), Japan (47 prefectures, from Cabinet Office SNA), Korea (17 metropolitan/provincial units, from ECOS), United States (921 MSAs), Europe (265 NUTS-2 regions, 29 countries, with GFCF allocated proportionally from national totals), Australia (8 states/territories), and South Africa (9 provinces). For US MSAs, regional GFCF was not directly available; we estimated it as the national GFCF/GDP ratio (approximately 21%) applied uniformly. Cross-MSA MUQ variation therefore reflects GDP growth differences rather than investment allocation differences. This limitation means the US panel tests output-side efficiency rather than input-side allocation. Extreme MUQ values were winsorised at 1%/99% thresholds. Total: 30,098 valid MUQ observations.

**Global panel.** Housing-based MUQ = Delta(rnna x GDP_deflator) / GFCF, where rnna is real capital stock from PWT 10.01. Coverage: 144 countries, 3,329 observations. Extreme values (MUQ outside [-50, 100]) were winsorised.

### M2. Simpson's paradox identification and block bootstrap

Countries were stratified by World Bank income classification. Within each income group, Spearman rank correlations between MUQ and urbanisation rate were computed. Both housing-based and GDP-based MUQ were tested independently. Country-level block bootstrap resampling (2,000 iterations) preserving each country's full time series was used to assess significance.

### M3. City-level and prefecture-level clean specification

The original MUQ specification contains mechanical correlation because MUQ = DeltaV/FAI places FAI in both dependent and independent variables. The clean specification DeltaV/GDP ~ FAI/GDP eliminates the shared component. For Japan, the equivalent is DeltaGDP/GDP ~ GFCF/GDP. Four estimators were applied: pooled OLS with HC1 standard errors; entity fixed effects with clustered standard errors; two-way fixed effects (entity + year); and quantile regression. For the US, DeltaV/GDP ~ housing-unit growth rate. For China provinces, DeltaV/GDP ~ FAI/GDP with province and year fixed effects.

### M4. Three Red Lines difference-in-differences

China's "Three Red Lines" policy (August 2020) imposed borrowing caps on property developers. We exploited cross-city variation in pre-policy real-estate dependence as treatment intensity. Diagnostic limitations are substantial: the parallel-trends test yields a marginal F-statistic (F = 2.82, p = 0.093), and the placebo test is significant (p < 0.001). Results are reported in Extended Data only. We note that recent advances in difference-in-differences methodology with staggered treatment timing^39 highlight the importance of diagnostic rigour in such designs.

### M5. Monte Carlo calibration uncertainty

For the national Q trajectory, uncertainty was quantified by jointly sampling across calibration weights and within-calibration parameters in 10,000 iterations. Bai-Perron structural break tests^17 identified breaks at 2004 and 2018 in the Chinese national series.

### M6. Data sources

*China national statistics*: NBS China Statistical Yearbook (2001--2024 editions). FAI after 2017 was estimated from published growth rates. *China city panel*: 213 prefecture-level cities from the China City Database; housing prices from 58.com/Anjuke. *China provincial panel*: 31 provinces from NBS provincial statistics. *Japan*: Cabinet Office System of National Accounts (1955--2022, prefectural accounts); Ministry of Internal Affairs population data. *Korea*: Bank of Korea ECOS regional accounts (17 metropolitan cities and provinces, 1985--2022). *Europe*: Eurostat regional GDP (NUTS-2, 2000--2024); national GFCF from World Bank allocated to regions proportionally. *Australia*: ABS state accounts (8 states/territories, 1990--2023). *South Africa*: Statistics South Africa provincial GDP (9 provinces, 1993--2023). *Global panel*: World Bank WDI; Penn World Table 10.01. *United States*: Census Bureau ACS (data.census.gov), BEA CAGDP1 county-level GDP. *Carbon intensity*: CABECA^18; IEA^15.

### M7. Scaling gap estimation and beta_V decomposition

For each urban system, beta_V was estimated via OLS: ln(V) = a + beta_V x ln(Pop) + year FE + epsilon, with cluster-robust standard errors. The identity V = Pop x PerCapitaArea x Price implies beta_V = 1 + beta_A + beta_P. SUR estimation provides joint standard errors for the economic signal (beta_A + beta_P), enabling inference on the cross-national difference Delta-beta, in which the mechanical component (= 1) cancels exactly.

### M8. Robustness checks

Robustness checks included: (i) balanced sub-panels; (ii) Newey-West and cluster-robust standard errors; (iii) Benjamini-Hochberg FDR correction (22 of 25 tests remained significant); (iv) leave-one-out analysis (40/40 countries negative under GDP-based MUQ); (v) winsorisation sensitivity; (vi) spatial autocorrelation tests; (vii) Bai-Perron break tests on Japanese national MUQ (optimal breaks: 1980, 1990).

### M9. Aggregation trap theorem verification

The theorem's three conditions were tested at both the cross-national level and within each of seven subnational systems. **Condition A1** (within-group decline): Spearman rho between MUQ and urbanisation/time was computed within each income group (cross-national) or GDP-per-capita quartile (within-country). **Condition A2** (compositional shift): Spearman rho between urbanisation quintile and group weight was computed. **Condition A3** (composition dominates within): the pooled Spearman rho was decomposed into within-group and between-group components using the total-correlation identity. The theorem was verified as satisfied at the cross-national level (A1: 4/4 groups negative; A2: mass shifts toward higher-baseline groups; A3: between-component 0.114 > within-component 0.076) and as not satisfied within any of the seven subnational systems (0/7 satisfy all three conditions; A3 fails in every case).

All analyses were performed in Python 3.9. Random seeds were fixed for all stochastic procedures (seed = 42 for city-level analyses; seed = 20260322 for unified panel; seed = 20260321 for Monte Carlo simulations).

---

## Extended Data Methods

### ED-M1. Carbon cost estimation

Excess carbon was estimated using two complementary methods with period decomposition. **Method A (MUQ flow method)**: for each year, excess investment = I(t) x max(0, 1 - MUQ_MA5(t)), where MUQ_MA5 is the five-year moving average. Carbon(t) = excess_I(t) x CI(t), where CI(t) declines from 1.20 to 0.60 tCO2 per 10,000 yuan. **Method B (Q stock method)**: when five-year moving-average Q falls below unity, excess capital = K - V; annual excess carbon = Delta(excess capital) x CI(t). **Combined estimate (Method C)** averages A and B. Annual excess carbon is capped at 50% of China's total building embodied carbon. Period decomposition distinguishes the structural period (2000--2020) from the market correction period (2021--2024). Physical cross-validation: excess per-capita housing area (China 42 m^2 versus benchmark ~33 m^2) yields 2.5--5.0 GtCO2. Uncertainty was propagated via Monte Carlo simulation (10,000 iterations). Carbon intensity values are calibrated to process-based estimates^18,29. Following Pomponi and Moncaster^30, estimates cover construction-phase emissions only and do not constitute a full life-cycle assessment.

---

## References

1. National Bureau of Statistics of China. *China Statistical Yearbook 2024* (China Statistics Press, 2024).

2. World Bank. World Development Indicators (2024). https://data.worldbank.org

3. Tobin, J. A general equilibrium approach to monetary theory. *J. Money Credit Bank.* **1**, 15--29 (1969).

4. Hayashi, F. Tobin's marginal q and average q: A neoclassical interpretation. *Econometrica* **50**, 213--224 (1982).

5. Glaeser, E. L. & Gyourko, J. Urban decline and durable housing. *J. Polit. Econ.* **113**, 345--375 (2005).

6. Rogoff, K. & Yang, Y. Has China's housing production peaked? *China World Econ.* **29**, 1--31 (2021).

7. Pritchett, L. The tyranny of concepts: CUDIE (cumulated, depreciated, investment effort) is not capital. *J. Econ. Growth* **5**, 361--384 (2000).

8. Dabla-Norris, E., Brumby, J., Kyobe, A., Mills, Z. & Papageorgiou, C. Investing in public investment: an index of public investment efficiency. *J. Econ. Growth* **17**, 235--266 (2012).

9. Bettencourt, L. M. A., Lobo, J., Helbing, D., Kuhnert, C. & West, G. B. Growth, innovation, scaling, and the pace of life in cities. *Proc. Natl Acad. Sci. USA* **104**, 7301--7306 (2007).

10. United Nations Environment Programme. *2022 Global Status Report for Buildings and Construction* (UNEP, 2022).

11. IPCC. *Climate Change 2022: Mitigation of Climate Change. Contribution of Working Group III to the Sixth Assessment Report* (Cambridge Univ. Press, 2022).

12. Zhong, X. et al. Global greenhouse gas emissions from residential and commercial building materials and mitigation strategies to 2060. *Nat. Commun.* **12**, 6126 (2021).

13. Xu, C. The fundamental institutions of China's reforms and development. *J. Econ. Lit.* **49**, 1076--1151 (2011).

14. Song, Z., Storesletten, K. & Zilibotti, F. Growing like China. *Am. Econ. Rev.* **101**, 196--233 (2011).

15. International Energy Agency. *Buildings* (IEA, Paris, 2023). https://www.iea.org/energy-system/buildings

16. Creutzig, F. et al. Beyond technology: demand-side solutions for climate change mitigation. *Annu. Rev. Environ. Resour.* **41**, 173--198 (2016).

17. Bai, J. & Perron, P. Computation and analysis of multiple structural change models. *J. Appl. Econom.* **18**, 1--22 (2003).

18. China Building Energy Conservation Association. *China Building Energy Consumption and Carbon Emission Research Report 2022* (CABECA, 2022).

19. Easterly, W. The ghost of financing gap: testing the growth model used in the international financial institutions. *J. Dev. Econ.* **60**, 423--438 (1999).

20. Hsieh, C.-T. & Klenow, P. J. Misallocation and manufacturing TFP in China and India. *Q. J. Econ.* **124**, 1403--1448 (2009).

21. Bettencourt, L. M. A. The origins of scaling in cities. *Science* **340**, 1438--1441 (2013).

22. Hsieh, C.-T. & Moretti, E. Housing constraints and spatial misallocation. *Am. Econ. J. Macroecon.* **11**, 1--39 (2019).

23. Arcaute, E. et al. Constructing cities, deconstructing scaling laws. *J. R. Soc. Interface* **12**, 20140745 (2015).

24. Leitao, J. C. et al. Is this scaling nonlinear? *R. Soc. Open Sci.* **3**, 150649 (2016).

25. Bai, C.-E., Hsieh, C.-T. & Song, Z. M. The long shadow of a fiscal expansion. *Brookings Pap. Econ. Act.* **2016**, 129--181 (2016).

26. Glaeser, E. L. & Gyourko, J. The economic implications of housing supply. *J. Econ. Perspect.* **32**, 3--30 (2018).

27. Restuccia, D. & Rogerson, R. Policy distortions and aggregate productivity with heterogeneous establishments. *Rev. Econ. Stud.* **75**, 707--731 (2008).

28. Cottineau, C. MetaZipf. A dynamic meta-analysis of city size distributions. *PLoS ONE* **12**, e0183919 (2017).

29. Huang, L. et al. Carbon emission of global construction sector. *Renew. Sustain. Energy Rev.* **81**, 1906--1916 (2018).

30. Pomponi, F. & Moncaster, A. Scrutinising embodied carbon in buildings: the next performance gap made manifest. *Renew. Sustain. Energy Rev.* **71**, 307--316 (2017).

31. Simpson, E. H. The interpretation of interaction in contingency tables. *J. R. Stat. Soc. B* **13**, 238--241 (1951).

32. Robinson, W. S. Ecological correlations and the behavior of individuals. *Am. Sociol. Rev.* **15**, 351--357 (1950).

33. Feenstra, R. C., Inklaar, R. & Timmer, M. P. The next generation of the Penn World Table. *Am. Econ. Rev.* **105**, 3150--3182 (2015).

34. Japan Cabinet Office. *System of National Accounts (prefectural accounts)* (various years). https://www.esri.cao.go.jp

35. Bank of Korea. *Economic Statistics System (ECOS)* (2024). https://ecos.bok.or.kr

36. Duranton, G. & Puga, D. Micro-origins of urban agglomeration economies. *Handbook of Regional and Urban Economics* **5**, 2063--2117 (2015).

37. Henderson, J. V. The urbanization process and economic growth: the so-what question. *J. Econ. Growth* **8**, 47--71 (2003).

38. Combes, P.-P. & Gobillon, L. The empirics of agglomeration economies. *Handbook of Regional and Urban Economics* **5**, 247--348 (2015).

39. Goodman-Bacon, A. Difference-in-differences with variation in treatment timing. *J. Econometrics* **225**, 254--277 (2021).

40. Kose, M. A., Prasad, E. S. & Terrones, M. E. Does financial globalization promote risk sharing? *J. Dev. Econ.* **89**, 258--270 (2009).

---

## Data availability

All data used in this study are publicly available. China national statistics: National Bureau of Statistics (www.stats.gov.cn). China provincial statistics: NBS provincial yearbooks. Global panel: World Bank WDI (data.worldbank.org), Penn World Table 10.01 (www.rug.nl/ggdc/productivity/pwt). Japan: Cabinet Office SNA prefectural accounts (www.esri.cao.go.jp). Korea: Bank of Korea ECOS (ecos.bok.or.kr). Europe: Eurostat (ec.europa.eu/eurostat). Australia: ABS (www.abs.gov.au). South Africa: Statistics South Africa (www.statssa.gov.za). United States: Census Bureau ACS (data.census.gov), BEA Regional Accounts (www.bea.gov). The unified regional panel (1,567 regions, 30,098 observations) and all processed datasets are available at [repository URL upon acceptance].

## Code availability

All analysis code (Python 3.9) is available at [repository URL upon acceptance].

## Acknowledgements

[placeholder]

## Author contributions

[placeholder]

---

## Extended Data

| ID | Type | Content |
|----|------|---------|
| ED Fig. 1 | Figure | Simpson's paradox: GDP-based MUQ by income group and urbanisation stage (157 countries) |
| ED Fig. 2 | Figure | Unified panel: 1,567 regions MUQ versus log GDP per capita (coloured by country income group) |
| ED Fig. 3 | Figure | China--Japan mirror: MUQ trajectories aligned by urbanisation rate |
| ED Fig. 4 | Figure | Three crisis-recovery patterns: Japan bubble, Korea 1997, Europe PIIGS |
| ED Fig. 5 | Figure | beta_V decomposition: mechanical vs. economic components (China and US) |
| ED Fig. 6 | Figure | DeltaV decomposition: price effect vs. quantity effect (China by tier, US) |
| ED Fig. 7 | Figure | City-tier MUQ gradient with population-weighted statistics |
| ED Fig. 8 | Figure | Aggregation trap theorem: four-group schematic and empirical verification |
| ED Fig. 9 | Figure | Ten-country MUQ trajectories with data-coverage annotation |
| ED Fig. 10 | Figure | DID event study plots for ln(HP) and Q (with diagnostic warnings) |
| ED Table 1 | Table | Full Simpson's paradox statistics: housing-based and GDP-based MUQ, block bootstrap p-values |
| ED Table 2 | Table | Unified panel regression: MUQ ~ ln(GDP_pc) + Country FE + Year FE |
| ED Table 3 | Table | Cross-country clean specification summary: China, Japan, US, Korea (beta, SE, R^2) |
| ED Table 4 | Table | SUR estimates of Delta-beta by year, with joint standard errors |
| ED Table 5 | Table | City-level regression table: original, clean, FE, TWFE, quantile specifications |
| ED Table 6 | Table | Carbon estimates: Method A, B, C with period decomposition and annual cap |
| ED Table 7 | Table | Aggregation trap C1/C2/C3 verification: cross-national (PASS) and within-country (7/7 FAIL) |
| ED Table 8 | Table | Japan Bai-Perron structural breaks and period MUQ statistics |
| ED Table 9 | Table | DID regression table, all specifications (with parallel-trends and placebo results) |
| ED Note 1 | Note | Carbon cost estimation: methodology, results, and caveats (see ED-M1) |

---

## Word Count

| Section | Words (v7.1) | Words (v7.2) |
|---------|:------------:|:------------:|
| Abstract | ~155 | ~155 |
| Introduction | ~590 | ~600 |
| Finding 1 | ~560 | ~555 |
| Finding 2 | ~620 | ~560 |
| Box 1 | ~530 | ~590 |
| Discussion | ~790 | ~810 |
| **Main text + Box 1** | **~3,245** | **~3,270** |
| Methods (M1--M9) | ~1,200 | ~1,260 |
| ED Methods (ED-M1) | ~160 | ~160 |
| **Full text (Main + Box 1 + Methods)** | **~4,605** | **~4,690** |

---

<!-- CHANGELOG v7.1 -> v7.2 (2026-03-22)

## P0-2: 全文因果语言审查

### 逐项修改清单:

1. **Abstract, line "3.4 times lower despite 2.3 times higher"**
   - OLD: "China's returns are 3.4 times lower despite 2.3 times higher investment intensity"
   - NEW: "China's returns are 3.4 times lower alongside 2.3 times higher investment intensity"
   - 理由: "despite" 暗示高投资应带来高回报（因果假设）

2. **Introduction Para 2, "Despite trillions at stake"**
   - OLD: "Despite trillions at stake, no cross-national framework measures..."
   - NEW: "Yet no cross-national framework measures..., a gap that persists in the urban agglomeration literature^36,37,38."
   - 理由: "Despite" 开头暗示因果关系；重构为 "Yet" 表示转折而非因果

3. **Introduction Para 3, "reveals that China at 54%"**
   - OLD: "revealing that China at 54% urbanisation exhibits MUQ levels"
   - NEW: "indicating that China at 54% urbanisation exhibits MUQ levels"
   - 理由: "reveals" 暗示揭示因果真相；"indicates" 为描述性语言

4. **Finding 2, China-Japan mirror, "despite investment intensity"**
   - OLD: "despite investment intensity (GFCF/GDP) 2.3 times higher"
   - NEW: "alongside investment intensity (GFCF/GDP) 2.3 times higher"
   - 理由: 同 #1

5. **Finding 2, China-Japan mirror, "reveals the most striking pattern"**
   - OLD: "reveals the most striking pattern in the data"
   - NEW: "is the most striking pattern in the data"
   - 理由: "reveals" 暗示因果发现

6. **Finding 2, Japan 67-year, "reveals declining investment productivity"**
   - OLD: "Period decomposition reveals declining investment productivity"
   - NEW: "Period decomposition shows declining investment productivity"
   - 理由: "reveals" → "shows"

7. **Discussion opening, "the theorem we prove explains why"**
   - OLD: "and the theorem we prove explains why"
   - NEW: "and the theorem we prove is consistent with this failure"
   - 理由: "explains why" 暗示因果解释

8. **Discussion, China-Japan mirror, "may be difficult to reverse"**
   - OLD: "suggests that the current trajectory, once established, may be difficult to reverse even if investment levels adjust"
   - NEW: "shows that a comparable trajectory has not reversed in the Japanese case even as investment levels adjusted"
   - 理由: 将因果暗示改为对日本经验的描述性陈述

9. **Discussion, "can restore investment efficiency" (Korea)**
   - OLD: "demonstrates that institutional restructuring can restore investment efficiency"
   - NEW: "is consistent with institutional restructuring being followed by restoration of investment efficiency"
   - 理由: "can restore" 是因果声明

10. **Discussion, "can persist for a decade" (Europe)**
    - OLD: "shows that without such restructuring, below-parity returns can persist for a decade"
    - NEW: "shows that below-parity returns have persisted for a decade in the absence of such restructuring"
    - 理由: "can persist" 是因果预测；改为已观测事实

11. **Discussion opening, "reveals that China's efficiency"**
    - OLD: "Japan's 67-year record reveals that China's efficiency"
    - NEW: "Japan's 67-year record indicates that China's efficiency"
    - 理由: "reveals" → "indicates"

12. **Discussion opening, "despite...investment intensity"**
    - OLD: "despite investment intensity more than twice as high" (implicit in v7.1 closing summary)
    - NEW: "alongside investment intensity more than twice as high"
    - 理由: 同 #1

13. **Introduction Para 1, "despite decades of federal investment"**
    - OLD: "entire blocks stand vacant despite decades of federal investment"
    - NEW: "entire blocks stand vacant after decades of federal investment"
    - 理由: "despite" 暗示联邦投资应阻止空置（因果假设）

14. **Finding 1, boundary condition, "reveals that"**
    - OLD: "Systematic testing across seven countries reveals that"
    - NEW: "Systematic testing across seven countries shows that"
    - 理由: "reveals" → "shows"

## P0-3: "mathematical necessity" 加限定

1. **Abstract**: 已含 "under three empirically verified conditions"，保留不变
2. **Introduction Para 2**: 改为 "the trap is a mathematical necessity (under conditions stated in Box 1)"
3. **Box 1 Part B Theorem**: 改为 "The Simpson's paradox is a mathematical necessity under three empirically verified conditions"
4. **Discussion opening**: 改为 "a mathematical necessity under three empirically verified conditions"
5. **Discussion closing**: 未使用 "mathematical necessity" 一词，无需修改

## P0-4: 美国 GFCF 透明报告

- 在 Methods M1 Unified regional panel 段落，美国条目后增加:
  "For US MSAs, regional GFCF was not directly available; we estimated it as the national GFCF/GDP ratio (approximately 21%) applied uniformly. Cross-MSA MUQ variation therefore reflects GDP growth differences rather than investment allocation differences. This limitation means the US panel tests output-side efficiency rather than input-side allocation."

## P0-5: Cover Letter MUQ vs ICOR 区分

- 在 Cover Letter "Core contributions" 段落后增加新段落，明确区分 MUQ 与 ICOR

## P1-6: Discussion 增加 mechanisms 段落

- 在 China-Japan mirror 段落后增加 mechanisms 假说段落（2-3句），列举:
  · land-revenue fiscal model (^13,25)
  · hukou system (^22)
  · GDP-target competition
- 明确标注 "hypotheses for future causal investigation"

## P1-7: Box 1 两部分逻辑衔接

- 在 Box 1 开头（Part A 之前）增加衔接段落，说明 Part A (mechanical-economic) 和 Part B (within-between) 共同揭示两种统计假象

## P1-8: 补充参考文献

新增 5 条参考文献 (#36-40):
- 36: Duranton & Puga (2015) — 引用于 Introduction Para 2（城市集聚经济文献空白）
- 37: Henderson (2003) — 引用于 Introduction Para 2（城市化与经济增长）
- 38: Combes & Gobillon (2015) — 引用于 Introduction Para 2（城市集聚经验研究）
- 39: Goodman-Bacon (2021) — 引用于 Finding 2 DID 段落和 M4
- 40: Kose, Prasad & Terrones (2009) — 引用于 Discussion 跨领域泛化段落（金融全球化风险共担中的类似聚合问题）
总引用数: 35 → 40

## P1-9: Finding 2 后半段精简

- "Three crisis-recovery patterns" 段落从约 95 词压缩至约 50 词
- 保留核心数字: Japan permanent downshift (0.034), Korea V-shaped (0.78), PIIGS L-shaped (0.65)
- 删除: 详细国别讨论（"with Greece and Italy failing to return to pre-crisis levels"）、"falsifying any claim of strict point-of-no-return irreversibility" 改为 "falsifying any claim of strict irreversibility"
- 释放约 45 词

## P1-10: Limitations 压缩

从 8 条压缩为 5 条:
- 保留 #1: 校准不确定性（不变）
- 保留 #2: 描述性非因果 + 合并原 #7（MUQ 不含社会价值）
- 保留 #3: within-estimator 翻正（不变）
- 保留 #4: 中国城市面板短 + 合并原 #5（FAI 断裂）
- 保留 #8→#5: 定理条件限制（不变）
- 删除原 #6: scaling gap 信号弱（已在 Box 1 Part A 充分讨论）

## 其他文本调整

- Discussion 段落标题 "China-Japan mirror and policy implications" 改为 "China-Japan mirror, mechanisms, and policy implications" 以反映新增 mechanisms 内容
- 美元数字改为占位符 [US$X trillion]，等待数据分析师计算 continuous measure 结果
- Abstract 最后一句时间范围从 "2019 and 2024" 改为 "2003 and 2024"（配合新的 continuous measure 计算，将覆盖更长时间跨度）

-->
