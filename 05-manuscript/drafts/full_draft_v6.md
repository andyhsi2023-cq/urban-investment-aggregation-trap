# Simpson's paradox masks declining returns on urban investment worldwide

## Abstract

As developing economies commit trillions annually to urban construction, aggregate statistics suggest returns remain stable. This stability is a Simpson's paradox. We construct a marginal Urban Q -- incremental asset value per unit of investment -- across 144 countries, 275 Chinese cities, and 921 US metropolitan areas. Within every developing-economy income group, returns decline with urbanisation (all p < 0.003), but compositional shifts conceal the decline. A GDP-based formulation immune to housing-price cycles confirms the paradox (all developing groups p < 0.001). At city level, a clean specification removing mechanical correlation yields beta = -0.37 (p = 0.019) in China but beta = +2.81 (p < 10^-6) in the United States, a sign reversal consistent with divergent institutional contexts. Below-parity investment in China is associated with an estimated 2.7 GtCO2 in excess embodied carbon (structural uncertainty: 0.3--5.0). Aggregate investment metrics may systematically mask efficiency decline in any rapidly urbanising economy.

---

## Introduction

Every developing economy that urbanises must answer a question it cannot easily measure: does each additional unit of urban investment still create more value than it costs? Aggregate statistics suggest the answer is reassuringly stable -- across 144 countries, the relationship between marginal investment returns and urbanisation is weakly positive. Yet this reassurance is a Simpson's paradox: within every developing-economy income group, marginal returns decline significantly, while compositional shifts across groups produce an illusion of resilience in pooled data. The consequences of this hidden decline are already visible at street level. In Hegang, a northeastern Chinese city of 700,000, apartments sell for less than US$3,000 -- a price that implies negative marginal returns on every yuan of recent construction. In Detroit, entire blocks stand vacant despite decades of federal investment. These are not isolated failures; they are local manifestations of a global pattern that aggregate statistics are structurally unable to detect.

This measurement vacuum is compounded by what we term the *aggregation trap*: aggregate investment statistics, by pooling heterogeneous trajectories, systematically conceal efficiency erosion within subgroups -- a manifestation of Simpson's paradox untested in the urban investment context. The phenomenon parallels known aggregation failures in development economics: Pritchett^7 demonstrated that cumulated investment effort bears little resemblance to productive capital; Easterly^19 showed that the "financing gap" model -- which implicitly assumes constant returns to capital accumulation -- fails empirically; and Hsieh and Klenow^20 documented how factor misallocation across heterogeneous firms reduces aggregate TFP by 30--50% in China and India. Despite trillions at stake, no cross-national framework measures whether marginal urban investment creates or destroys asset value. Tobin's Q -- the ratio of market value to replacement cost -- has guided corporate investment theory for half a century^3,4, yet has never been applied to the urban built environment. Filling this gap is urgent: infrastructure needs grow with city size following well-documented scaling laws^9,21, yet whether this scaling reflects productive deepening or diminishing returns remains open.

Here we construct a marginal Urban Q (MUQ) spanning 144 countries, 275 Chinese cities, and 921 US metropolitan areas, validated in parallel with a GDP-based formulation (1/ICOR) that is immune to housing-price cycles. We document two principal findings. First, a Simpson's paradox: within low-income, lower-middle-income, and upper-middle-income country groups, MUQ declines with urbanisation (all p < 0.003), but the aggregate trend is flat -- a pattern confirmed under both housing-based and GDP-based MUQ definitions. A scaling gap -- a structural pattern in which asset values outpace economic output with city size -- is cross-sectionally associated with these efficiency gradients (Box 1). Second, at the city level, a clean specification that removes mechanical correlation between investment and returns reveals a negative investment-return association in China (beta = -0.37, p = 0.019) but a positive one in the United States (beta = +2.81, p < 10^-6), a sign reversal consistent with divergent institutional contexts governing how capital is allocated across the urban hierarchy.

Several scope limitations merit explicit statement. MUQ is a descriptive measure of investment outcomes, not an identification strategy for causal mechanisms. The China--US comparison reveals institutional correlates of efficiency divergence, not causes. The within-city estimator yields a sign reversal relative to the between-city pattern (Methods), indicating that the negative association is a structural cross-sectional regularity rather than a within-city dynamic. We report these boundaries transparently throughout and identify the causal architecture behind the efficiency decline as a priority for future work.

## Results

### Finding 1: Simpson's paradox in urban investment returns

Urban asset values, physical capital, and economic output each scale with city population, but at different rates, generating a structural gradient in investment returns across the urban hierarchy. Across 275 Chinese cities, asset value scales superlinearly with population (V ~ N^1.06, R^2 = 0.58), economic output scales approximately linearly (GDP ~ N^1.04, R^2 = 0.69), and capital stock scales sublinearly (K ~ N^0.86, R^2 = 0.63). Because Tobin's Q = V/K, the scaling gap Delta-beta governs how Q co-varies with city size: Q ~ N^(Delta-beta). The scaling gap is a structural observation rather than a causal claim: 94.6% of the V--population exponent (beta_V = 1.057) reflects the mechanical identity V = Population x PerCapitaArea x Price, with the economic signal -- the sum of per-capita-area scaling (beta_A = -0.256) and price scaling (beta_P = 0.313) -- accounting for 5.4% (Box 1). Crucially, when computing the cross-national difference Delta-beta = beta_V(China) - beta_V(US), the mechanical component (1 - 1 = 0) cancels exactly, leaving the economic signal intact: Delta-beta = 0.057 - 0.131 = -0.075 (SE = 0.054). The Q--population relationship explains 31% of cross-city variance (R^2 = 0.31). In US metropolitan areas, Delta-beta is not statistically significant, consistent with a mature economy where asset prices track fundamentals more tightly.

**GDP-based MUQ validation.** To verify that the Simpson's paradox is not an artefact of housing-price cycles, we construct a GDP-based MUQ (= DeltaGDP / GFCF, the inverse of the incremental capital-output ratio) using World Bank constant-2015-USD data. The paradox is reproduced and strengthened: within low-income countries, rho = -0.116 (p < 0.001, N = 1,284); lower-middle-income, rho = -0.131 (p < 0.001, N = 1,681); upper-middle-income, rho = -0.248 (p < 0.001, N = 1,834). High-income countries show no significant trend (rho = -0.035, p = 0.080). Leave-one-out analysis within the upper-middle-income group confirms that all 40 countries yield negative, significant Spearman correlations. A parallel analysis using Penn World Table real GDP (rgdpna) produces consistent results (all developing groups p < 0.001). Block bootstrap resampling at the country level preserves significance in all three developing groups (Extended Data Table 1).

**Housing-based MUQ.** Under the original housing-market-based MUQ, the paradox also holds: low-income rho = -0.150 (p = 0.002); lower-middle rho = -0.122 (p = 0.002); upper-middle rho = -0.099 (p = 0.003); high-income rho = -0.013 (p = 0.633). The within-group pattern is robust to excluding China (upper-middle rho = -0.095, p = 0.005).

**Within-between decomposition.** The paradox arises because countries that urbanise also graduate into higher income groups, which carry higher average MUQ. This between-group compositional uplift offsets within-group erosion, producing the aggregate illusion of stability -- the aggregation trap (Fig. 1). A compositional decomposition framework connects scaling to paradox (Box 1): within each income group, MUQ declines with urbanisation; as countries cross income thresholds, they enter higher-baseline groups; the aggregate stands still while every component declines. This balance is inherently temporary: graduation potential is bounded, but urbanisation continues.

**Ten-country trajectories.** Country-level MUQ trajectories confirm that the pattern extends beyond the cross-section (Fig. 5). Early-stage economies (Rwanda, India) maintain MUQ well above unity, consistent with urbanisation phases where investment headroom remains large. Upper-middle-income countries with advanced urbanisation (Turkey, Brazil) show late-period declines. China's trajectory is distinctive in speed rather than direction: MUQ reached unity in the mid-2010s and turned negative by 2022. Six of ten countries have experienced at least one year with MUQ below unity. We note that MUQ coverage varies substantially (China: 44 observations; India: 5; Indonesia: 6), and forward-looking inferences for data-sparse economies should be treated as indicative.

### Finding 2: City-level efficiency mapping reveals institutional divergence

**Primary specification.** To address mechanical correlation between MUQ (= DeltaV/I) and investment intensity (FAI/GDP), where investment (I) appears in both numerator and denominator, we adopt a clean specification: DeltaV/GDP regressed on FAI/GDP. This eliminates the shared FAI component. Across 455 city-year observations (213 prefecture-level cities, 2011--2016), the clean specification yields beta = -0.37 (95% CI [-0.67, -0.06], p = 0.019, R^2 = 0.017). The attenuation relative to the original MUQ specification (beta = -2.26) is 83.7%, quantifying the share attributable to mechanical correlation. The residual 16.3% represents the between-city association net of the shared-denominator artefact.

**Within-city estimator.** City fixed effects reverse the sign: beta_FE = +0.52 (clustered SE = 0.10, p < 0.001). This sign reversal constitutes a second, city-level Simpson's paradox: between cities, higher investment intensity is associated with lower value growth; within the same city over time, the association is positive. Two-way fixed effects (city + year) yield beta = +0.16 (p = 0.47, not significant). We interpret the clean-specification result as a structural between-city regularity -- cities with persistently high investment-to-GDP ratios tend to generate less incremental value per unit of GDP -- rather than a within-city dynamic. The panel structure reinforces this interpretation: 150 of 213 cities contribute only one observation, limiting within-city variation.

**Sign reversal across institutional contexts.** The United States presents the opposite pattern. Across 10,760 MSA-year observations (921 MSAs, 2011--2022), DeltaV/GDP is positively associated with housing-unit growth (beta = +2.81, p < 10^-6) and with investment intensity (beta = +1.39, p < 10^-6). Two-way fixed effects preserve the positive sign (beta = +2.76, p < 10^-6). The China--US sign reversal survives the clean specification: China beta = -0.37 versus US beta = +2.81 (Fig. 3).

**Quantity versus price composition.** A decomposition of asset value change reveals fundamentally different return compositions. In China, 44% of DeltaV reflects new physical construction (quantity effect) versus 11% in the United States, where appreciation of existing housing dominates (87% price effect). This 3.8-fold divergence in quantity-effect share means that Chinese MUQ captures real construction-efficiency information, not merely price cycles. By city tier, first-tier Chinese cities approach the American pattern, while lower-tier cities are quantity-dominated (Extended Data Fig. 3).

**City-tier gradient.** In the 2016 cross-section (N = 213), 82.2% of cities exhibit MUQ below unity (70.2% when population-weighted). The urban hierarchy maps onto a steep efficiency gradient: first-tier cities average MUQ = 7.46, new first-tier 2.84, second-tier 1.00, third-tier 0.52, and fourth-to-fifth-tier 0.20 (Fig. 2). These are cross-sectional regularities reflecting persistent city characteristics (location, institutional capacity, market depth), not within-city causal effects. Regional disparities are significant (Kruskal-Wallis H = 16.60, p = 0.0002), with eastern cities outperforming central and western counterparts.

**Quantile regression.** The investment-return gradient steepens in the upper tail: in the clean specification, beta is insignificant at the median (tau = 0.50: beta = -0.05, p = 0.53) but significant and negative at the 75th percentile (beta = -0.27, p = 0.024) and 90th percentile (beta = -0.89, p = 0.016), indicating that the negative association is concentrated among cities with high value growth.

**Three Red Lines quasi-experiment.** A difference-in-differences analysis exploiting China's 2020 credit-tightening policy is reported in Extended Data; diagnostic limitations (marginal parallel-trends F = 2.82, p = 0.093; significant placebo test) preclude definitive causal interpretation.

---

## Box 1 | The Scaling Gap: a compositional decomposition of urban investment gradients

**Urban outputs scale superlinearly with population, but the components of asset value -- quantity and price -- scale at different rates.** In the Bettencourt scaling framework^9,21, city output Y relates to population N as Y ~ N^beta. We decompose the urban balance sheet identity V = Population x PerCapitaArea x Price, yielding beta_V = 1 + beta_A + beta_P, where beta_A is the population elasticity of per-capita floor area and beta_P is the population elasticity of price. Across 275 Chinese cities (pooled 2005--2019 with year fixed effects and city-clustered standard errors): beta_V = 1.057 (SE = 0.060), beta_A = -0.256 (SE = 0.044), beta_P = 0.313 (SE = 0.025). The mechanical component (= 1) accounts for 94.6% of beta_V; the economic signal (beta_A + beta_P = 0.057) accounts for 5.4%. Across 921 US MSAs (2010--2022): beta_V = 1.131 (SE = 0.011), with a larger economic signal of 0.131.

**The cross-national difference Delta-beta is free of the mechanical component.** Because the identity contributes exactly 1 to both countries, Delta-beta(mechanical) = 1 - 1 = 0. The entire cross-national difference is economic: Delta-beta = 0.057 - 0.131 = -0.075. SUR estimation with joint standard errors shows this difference is not robustly significant in most years (2 of 10 overlapping years at p < 0.05), underscoring that the scaling gap is a structural observation requiring cautious interpretation. The economic signal decomposes further: China's negative per-capita-area scaling (beta_A = -0.256, indicating crowding in large cities) is partially offset by stronger price scaling (beta_P = 0.313); the US shows near-zero area scaling (beta_A = -0.025) and moderate price scaling (beta_P = 0.156).

**A compositional decomposition connects scaling to Simpson's paradox.** Within income group k, MUQ declines with urbanisation u at rate gamma: MUQ_k = mu_k - gamma . u_k + epsilon, where mu_k is a group-specific baseline. The aggregate MUQ = Sum_k [w_k . MUQ_k]. A Simpson's paradox arises when compositional uplift from income-group graduation offsets within-group erosion. This balance is temporary: graduation potential is bounded, while urbanisation continues.

**Three testable hypotheses follow.** (1) The economic component of beta_V should be larger in rapidly urbanising economies than in mature ones (observed: China 0.057 versus US 0.131 -- contrary to expectation, the US signal is larger; the formal city-to-country derivation remains incomplete). (2) Within-group erosion rate gamma should co-vary positively with institutional investment intensity. (3) Recently graduated countries should exhibit above-average MUQ within their new income group. These remain open empirical questions; the data presented here are consistent with (2) and (3) but do not constitute definitive tests.

---

## Discussion

Three descriptive findings emerge from this analysis. Within every developing-economy income group, marginal returns on urban investment decline with urbanisation, yet compositional shifts across groups conceal the decline in pooled data -- a Simpson's paradox confirmed under both housing-based and GDP-based MUQ formulations and robust to block bootstrap resampling. City-level mapping across 213 Chinese and 921 US metropolitan units reveals a sign reversal in the investment-return association -- negative in China, positive in the United States -- that survives a clean specification removing mechanical correlation, though the effect is a between-city regularity that reverses within cities. A scaling gap in which asset values outpace economic output with city size provides a structural pattern consistent with the paradox, but the formal derivation linking city-level scaling to country-level Simpson's paradox remains incomplete.

The policy implication is not "invest less" but "invest differently as urbanisation advances." First-tier Chinese cities (MUQ = 7.46) retain substantial headroom; fourth-to-fifth-tier cities (MUQ = 0.20) require asset absorption rather than greenfield construction. The aggregation trap may extend beyond urban investment: any domain where units graduate between categories while being evaluated on aggregate metrics -- including the infrastructure-gap estimates that assume constant marginal returns^7,19 -- could conceal within-group deterioration through the same compositional mechanism. Hsieh and Moretti^22 document an analogous pattern in US housing markets, where spatial misallocation of labour driven by housing supply constraints reduces aggregate GDP by 36%; the MUQ framework suggests that misallocation of physical capital across the urban hierarchy may impose comparable costs in developing economies.

**Carbon dimension.** Applying time-varying carbon intensity with period decomposition and a 50% annual cap on building-sector embodied carbon, we estimate that China's below-parity investment (2000--2024) is associated with approximately 2.7 GtCO2 in excess embodied carbon (90% CI: 2.0--3.5 GtCO2). Decomposing by period: the structural overcapitalisation component (2000--2020, based on five-year moving-average smoothed Q) accounts for 0.5 GtCO2 (0.0--1.1), while the market correction component (2021--2024, when housing prices declined sharply) contributes 2.2 GtCO2 (1.8--2.7). The concentration in 2021--2024 means that much of the estimated carbon reflects asset-price adjustment rather than purely physical overbuilding. An independent physical cross-validation based on excess per-capita housing area (China: 42 m^2 versus Japan/Korea/Europe benchmark: ~33 m^2) yields 3.8 GtCO2 (2.5--5.0), consistent in order of magnitude. An important caveat: MUQ does not capture the social value of public goods (transport, hospitals, schools) whose returns are not capitalised into housing prices; below-parity MUQ does not necessarily indicate socially wasteful investment. Within the Avoid-Shift-Improve mitigation hierarchy^11,15,16, MUQ could serve as an ex ante screening tool for the "Avoid" tier, flagging construction whose expected return is insufficient to justify its embodied carbon. India, Vietnam, and Indonesia -- with combined population exceeding 1.8 billion and urbanisation rates of 35--58% -- are entering the phase where the scaling gradient is associated with accelerating efficiency divergence.

**Limitations.** Nine limitations warrant discussion. First, seven calibration variants bound but do not resolve uncertainty in the national MUQ trajectory (Q = 1 crossing year 90% CI spans ~12 years). Second, all core findings are descriptive; we do not identify why returns erode, only that they do. Third, the within-city estimator reverses the sign of the investment-return association, indicating that the negative effect is a cross-sectional between-city regularity, not a within-city causal dynamic. Fourth, the Chinese city panel spans only 2011--2016, with V reconstructed rather than directly observed; the panel is severely unbalanced (150 of 213 cities contribute one observation). Fifth, FAI series after 2017 are estimated from growth rates due to statistical discontinuation. Sixth, carbon estimates cover construction-phase embodied carbon only and are sensitive to housing-price cycles, particularly in 2021--2024. Seventh, the scaling gap contains a large mechanical component (94.6%), and while the Delta-beta is free of this component, it is not robustly significant across years. Eighth, MUQ measures asset market value, not social value; investment with MUQ < 1 may generate positive externalities. Ninth, the China--US comparison uses different MUQ definitions; the sign reversal is robust in a unified specification, but coefficient magnitudes are not directly comparable.

Identifying the causal mechanisms behind these patterns -- through instrumental variable strategies, spatial regression discontinuity designs, or structural estimation -- is a priority for future work. Equally important is the formal derivation linking city-level scaling to the country-level Simpson's paradox, a step that requires analytical treatment of within-group and between-group dynamics under endogenous income-group transition.

The aggregation trap we document suggests that a substantial volume of below-cost-return urban investment has been concealed by the very statistical conventions designed to measure it. As a generation of developing economies commits trillions to urban construction, the question is not whether they will encounter diminishing returns, but whether their measurement systems will detect the decline before the concrete is in the ground.

---

## Methods

### M1. Marginal Urban Q (MUQ) construction

We define the Marginal Urban Q as MUQ(t) = DeltaV(t) / I(t), where DeltaV(t) is the year-on-year change in urban asset value and I(t) is gross investment. MUQ < 1 indicates that marginal investment generates less than one unit of asset value per unit of cost.

**Housing-based MUQ.** *China national level*: V(t) was estimated using seven calibrations combining three numerator definitions (V1: housing stock x commercial housing price; V1_adj: vintage-weighted valuation with 1.5% annual depreciation; V2 and V3 from Penn World Table capital accounts) and two denominator definitions (K1: perpetual inventory method at 5% depreciation; K2: PWT capital stock at current PPPs). The seven calibrations were combined via a weighted ensemble with Dirichlet-sampled weights (concentration parameter alpha = 20). I(t) was total fixed-asset investment from NBS. Coverage: 1998--2024. *China city level*: for 213 prefecture-level cities (2011--2016), V was reconstructed as population x median housing price x per-capita housing area, and I was fixed-asset investment (FAI). After excluding observations with FAI < 100 million yuan and applying 1%/99% winsorisation, 455 city-year observations were retained. *US metropolitan areas*: V = median home value x housing units from Census ACS 5-Year estimates; I was approximated as the change in housing units x lagged median price. Coverage: 921 MSAs, 2010--2022 (10,760 differenced observations after 1%/99% winsorisation).

**GDP-based MUQ.** To provide a formulation immune to housing-price cycles, we construct MUQ_GDP = DeltaGDP / GFCF (the inverse of the incremental capital-output ratio) using World Bank WDI constant-2015-USD GDP and gross fixed capital formation. Coverage: 144 countries, 1960--2023. A parallel series uses Penn World Table real GDP (rgdpna). The GDP-based MUQ captures whether marginal investment generates proportional output growth, complementing the housing-based MUQ that captures asset-value capitalisation.

**Global panel.** Housing-based MUQ = Delta(rnna x GDP_deflator) / GFCF, where rnna is real capital stock from PWT 10.01. Coverage: 144 countries (from a panel of 158), 3,329 real-MUQ observations. Extreme values (MUQ outside [-50, 100]) were winsorised.

### M2. Simpson's paradox identification

Countries were stratified by World Bank income classification. Within each income group, we computed Spearman rank correlations between MUQ and urbanisation rate. The paradox was identified by comparing the direction of the aggregate correlation (all countries pooled) against within-group correlations. Both housing-based and GDP-based MUQ were tested independently.

**Block bootstrap.** To account for within-country serial correlation, we implemented country-level block bootstrap resampling (2,000 iterations). In each iteration, countries were resampled with replacement (preserving each country's full time series), and within-group Spearman correlations were recomputed. Significance was assessed from the bootstrap distribution of rho values.

### M3. City-level clean specification

The original MUQ specification (MUQ ~ FAI/GDP) contains mechanical correlation because MUQ = DeltaV/FAI, placing FAI in both the dependent variable denominator and the independent variable numerator. To address this, we adopt a clean specification: DeltaV/GDP ~ FAI/GDP, which eliminates the shared FAI component. The attenuation ratio 1 - (beta_clean / beta_original) quantifies the share of the original coefficient attributable to mechanical correlation.

Four estimators were applied: (i) pooled OLS with HC1 standard errors; (ii) city fixed effects with city-clustered standard errors; (iii) two-way fixed effects (city + year); (iv) quantile regression at tau = 0.10, 0.25, 0.50, 0.75, 0.90. For US MSAs, the equivalent clean specification is DeltaV/GDP ~ housing-unit growth rate, estimated under the same four approaches.

### M4. Three Red Lines difference-in-differences

China's "Three Red Lines" policy (August 2020) imposed borrowing caps on property developers. We exploited cross-city variation in pre-policy real-estate dependence as treatment intensity. The coefficient of interest is the Post x RE_dependence interaction. Diagnostic limitations are substantial: the parallel-trends test yields a marginal F-statistic (F = 2.82, p = 0.093), and the placebo test is significant (p < 0.001). Results are reported in Extended Data only, as suggestive evidence.

### M5. Carbon cost estimation

Excess carbon was estimated using two complementary methods with period decomposition.

**Method A (MUQ flow method).** For each year t, excess investment = I(t) x max(0, 1 - MUQ_MA5(t)), where MUQ_MA5 is the five-year moving average of MUQ, smoothing financial-cycle fluctuations. Carbon(t) = excess_I(t) x CI(t), where CI(t) declines from 1.20 to 0.60 tCO2 per 10,000 yuan (2.89% annual decay rate), calibrated to CABECA construction-sector emission factors^18.

**Method B (Q stock method).** When the five-year moving-average Q falls below unity, excess capital = K - V. Annual excess carbon = Delta(excess capital) x CI(t).

**Combined estimate.** Method C averages Methods A and B. Annual excess carbon is capped at 50% of China's total building embodied carbon (~1,400--1,900 MtCO2/yr) to ensure physical plausibility.

**Period decomposition.** We distinguish the structural period (2000--2020), when five-year moving-average MUQ remained above unity, from the market correction period (2021--2024), when housing-price declines sharply reduced MUQ.

**Physical cross-validation.** China's urban per-capita housing area (42 m^2, 2023) exceeds the Japan/Korea/Germany/France benchmark (~33 m^2) by 9 m^2. Multiplied by urban population (933 million) and carbon intensity (0.3--0.6 tCO2/m^2), this yields 2.5--5.0 GtCO2 in cumulative excess embodied carbon.

Uncertainty was propagated via Monte Carlo simulation (10,000 iterations) sampling from MUQ ensemble weights, CI level, and CI decay rate. Results are reported as medians with 90% credible intervals.

### M6. Monte Carlo calibration uncertainty

For the national Q trajectory, uncertainty was quantified by jointly sampling across calibration weights and within-calibration parameters in 10,000 iterations. The concentration parameter alpha = 20 was chosen to balance calibration diversity against prior beliefs; sensitivity checks with alpha = 10 and alpha = 50 confirm that the Q = 1 crossing year CI shifts by less than 1.5 years. Bai-Perron structural break tests^17 identified breaks at 2004 and 2018.

### M7. Data sources

*China national statistics*: NBS China Statistical Yearbook (2001--2024 editions). FAI after 2017 was estimated from published growth rates due to discontinuation of the total-society series. *China city panel*: 213 prefecture-level cities from the China City Database (Marker Database, version 6.0); housing prices supplemented from 58.com/Anjuke. *Global panel*: World Bank WDI (GDP, GFCF, urbanisation, income classification); Penn World Table 10.01 (rnna, rgdpna). *United States*: Census Bureau ACS 5-Year estimates (median home value, housing units, population; 2010--2022); BEA CAGDP1 county-level GDP aggregated to MSAs. *Carbon intensity*: CABECA^18; IEA^15.

### M8. Scaling gap estimation and beta_V decomposition

For each urban system, we estimated beta_V via OLS: ln(V) = a + beta_V x ln(Pop) + year FE + epsilon, with cluster-robust standard errors at the city/MSA level. The identity V = Pop x PerCapitaArea x Price implies beta_V = 1 + beta_A + beta_P, where beta_A and beta_P are estimated from parallel regressions of ln(PerCapitaArea) and ln(Price) on ln(Pop). SUR estimation provides joint standard errors for beta_A + beta_P, enabling inference on the economic signal. The mechanical component (= 1) cancels in the cross-national difference Delta-beta. Cross-national validation used China (275 cities, 2005--2019) and US (921 MSAs, 2010--2022).

### M9. Robustness checks

Robustness checks included: (i) re-estimation on balanced sub-panels (2015--2016, N = 51 cities); (ii) Newey-West and cluster-robust standard errors for US regressions; (iii) Benjamini-Hochberg FDR correction across all hypothesis tests (22 of 25 remained significant); (iv) leave-one-out analysis for the upper-middle-income Simpson's paradox (40/40 countries negative and significant under GDP-based MUQ); (v) winsorisation sensitivity (5%/95% and no winsorisation); (vi) Moran's I spatial autocorrelation tests.

All analyses were performed in Python 3.9. Random seeds were fixed for all stochastic procedures (seed = 42 for city-level analyses; seed = 20260321 for Monte Carlo simulations).

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

---

## Data availability

All data used in this study are publicly available. China national statistics: National Bureau of Statistics (www.stats.gov.cn). Global panel: World Bank WDI (data.worldbank.org), Penn World Table 10.01 (www.rug.nl/ggdc/productivity/pwt). United States: Census Bureau ACS (data.census.gov), BEA Regional Accounts (www.bea.gov). Processed datasets and analysis code are available at [repository URL upon acceptance].

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
| ED Fig. 1 | Figure | Simpson's paradox: GDP-based MUQ by income group and urbanisation stage |
| ED Table 1 | Table | Full Simpson's paradox statistics: housing-based and GDP-based MUQ, block bootstrap p-values |
| ED Fig. 2 | Figure | beta_V decomposition: mechanical vs. economic components (China and US) |
| ED Table 2 | Table | SUR estimates of Delta-beta by year, with joint standard errors |
| ED Fig. 3 | Figure | DeltaV decomposition: price effect vs. quantity effect (China by tier, US) |
| ED Table 3 | Table | City-level regression table: original, clean, FE, TWFE, quantile specifications |
| ED Fig. 4 | Figure | City-tier MUQ gradient with population-weighted statistics |
| ED Fig. 5 | Figure | Ten-country MUQ trajectories with data-coverage annotation |
| ED Table 4 | Table | Carbon estimates: Method A, B, C with period decomposition and annual cap |
| ED Fig. 6 | Figure | Carbon method comparison: flow method, stock method, physical cross-validation |
| ED Fig. 7 | Figure | DID event study plots for ln(HP) and Q (with diagnostic warnings) |
| ED Table 5 | Table | DID regression table, all specifications (with parallel-trends and placebo results) |

---

## Word Count

| Section | Words (v6) |
|---------|:----------:|
| Abstract | 150 |
| Introduction | ~565 |
| Finding 1 | ~597 |
| Finding 2 | ~547 |
| Box 1 | ~432 |
| Discussion | ~781 |
| **Main text + Box 1** | **~3,072** |
| Methods (M1--M9) | ~1,216 |
| **Full text (Main + Box 1 + Methods)** | **~4,288** |

---

<!-- REVISION LOG v5 -> v6 (2026-03-21)

STRATEGIC CHANGES:

1. GDP-based MUQ promoted to primary validation (Finding 1):
   - Phase 0 results: all 3 developing groups significant (p < 0.001)
   - LOO: 40/40 upper-middle-income countries negative and significant
   - Presented before housing-based MUQ as primary evidence

2. Clean specification as primary city-level result (Finding 2):
   - DeltaV/GDP ~ FAI/GDP: beta = -0.37 (p = 0.019), replacing beta = -2.23
   - Attenuation ratio 83.7% reported transparently
   - Within-estimator sign reversal (+0.52) reported as city-level Simpson's Paradox
   - Framed as "between-city structural regularity, not within-city dynamic"

3. Carbon estimate downgraded to Discussion paragraph:
   - 5.3 GtCO2 replaced by 2.7 GtCO2 (comprehensive method C)
   - Period decomposition: structural 0.5 + market correction 2.2
   - Physical cross-validation: 3.8 GtCO2 (order-of-magnitude consistent)
   - 50% annual cap on building-sector embodied carbon
   - Public goods caveat added

4. Scaling Gap downgraded to "structural observation":
   - beta_V decomposition: 94.6% mechanical, 5.4% economic signal
   - Delta-beta: mechanical component cancels, 100% economic signal
   - SUR significance: only 2/10 years at p < 0.05
   - "Confirmed predictions" -> "testable hypotheses"
   - "Mean-field framework" -> "compositional decomposition"
   - "Engine" -> "structural pattern"
   - City-to-country derivation gap acknowledged

5. Systematic language calibration (~50 replacements):
   - "drives" -> "is associated with" / "co-occurs with"
   - "engine" -> "structural pattern"
   - "supply-driven regime" -> "supply-oriented institutional context"
   - "demand-driven regime" -> "demand-responsive institutional context"
   - "misallocation" -> "below-cost-return investment"
   - "confirmed" -> "consistent with" / "observed"
   - "produces" -> "is accompanied by"
   - All causal language replaced with associational language

6. Limitations expanded from 7 to 9:
   - Added: within-estimator null (sign reversal)
   - Added: FAI post-2017 discontinuity
   - Added: panel imbalance (150/213 cities = 1 obs)

7. References expanded from 18 to 30:
   - Added: Hsieh-Klenow (2009), Bettencourt (2013), Easterly (1999)
   - Added: Hsieh-Moretti (2019), Arcaute (2015), Leitao (2016)
   - Added: Bai-Hsieh-Song (2016), Glaeser-Gyourko (2018)
   - Added: Restuccia-Rogerson (2008), Cottineau (2017)
   - Added: Huang et al. (2018), Pomponi-Moncaster (2017)

8. Structure change: Finding 3 (carbon) removed from Results, moved to Discussion para 3

9. Box 1 restructured:
   - beta_V = 1 + beta_A + beta_P identity introduced
   - SUR significance caveat added
   - Three "predictions" reframed as "testable hypotheses"
   - Acknowledged hypothesis (1) runs contrary to expectation

10. Population-weighted statistic added: 82.2% -> 70.2% when weighted

NUMBERS UPDATED:
- beta: -2.23 -> -0.37 (clean spec, primary)
- US beta: +2.75 -> +2.81 (clean spec: DeltaV/GDP ~ hu_growth)
- Carbon: 5.3 GtCO2 -> 2.7 GtCO2 (structural uncertainty 0.3-5.0)
- Cities: 300 -> 213 (clean spec panel)
- City-years: 455 (unchanged)
- Years: 2010-2016 -> 2011-2016 (clean spec)
- Countries: 275 cities (scaling), unchanged 144 countries (global)

-->
