# Urban investment efficiency declines worldwide: evidence from 1,567 cities and regions

## Abstract

Urban investment is central to economic growth, yet no cross-national framework tracks whether marginal investment still creates value as cities mature. Here we construct a marginal Urban Q (MUQ) across 157 countries and 1,567 subnational regions spanning eight countries across five continents. A Simpson's paradox conceals the decline: within every developing-economy income group, returns fall with urbanisation (all p < 0.001 under a GDP-based formulation immune to housing-price cycles), but compositional shifts produce an illusion of stability in pooled data. We prove that this aggregation trap is a mathematical necessity under three empirically verified conditions. At the city level, investment intensity is negatively associated with returns in China (beta = -0.37) but positively in the United States (+2.81) and Japan (+0.64). The China--Japan mirror is particularly instructive: at matched urbanisation rates, China's returns are 3.4 times lower alongside 1.8 times higher investment intensity (GFCF/GDP: China 44% versus Japan 25%), and China's MUQ decline rate is 2.7 times faster. Korea's V-shaped crisis recovery contrasts with Europe's L-shaped PIIGS stagnation, revealing three distinct institutional pathways. The cumulative below-parity investment in China totalled approximately US$18 trillion between 2000 and 2024, associated with an estimated 3.0 GtCO2 in excess embodied carbon -- equivalent to three years of global aviation emissions. As India, Indonesia, and Vietnam enter their peak construction decades, these patterns offer an early-warning diagnostic for cities worldwide.

---

## Introduction

Every developing economy that urbanises must answer a question it cannot easily measure: does each additional unit of urban investment still create more value than it costs? Aggregate statistics suggest the answer is reassuringly stable -- across 157 countries, the relationship between marginal investment returns and urbanisation is weakly positive. Yet this reassurance is a Simpson's paradox: within every developing-economy income group, marginal returns decline significantly, while compositional shifts across groups produce an illusion of resilience in pooled data.

The consequences of this hidden decline are already visible at street level. In Hegang, a northeastern Chinese city of 700,000, apartments sell for less than US$3,000 -- a price that implies negative marginal returns on every yuan of recent construction. In Detroit, entire blocks stand vacant after decades of federal investment. In Tama New Town on Tokyo's western fringe, 1970s apartment complexes face population decline and plummeting values despite Japan's continued urbanisation. These are not isolated failures; they are local manifestations of a pattern that aggregate statistics are structurally unable to detect.

This measurement vacuum is compounded by what we term the *aggregation trap*: pooled investment statistics, by combining heterogeneous trajectories, systematically conceal efficiency erosion within subgroups -- a manifestation of Simpson's paradox^31 untested in the urban investment context. We prove (Box 1) that under three empirically verifiable conditions -- within-group decline, endogenous group graduation, and compositional dominance -- the trap is a mathematical necessity, not a statistical curiosity. The phenomenon parallels known aggregation failures in development economics: Pritchett^7 demonstrated that cumulated investment effort bears little resemblance to productive capital; Hsieh and Klenow^20 documented how factor misallocation across heterogeneous firms substantially reduces aggregate TFP in China and India; Restuccia and Rogerson^27 formalised how policy distortions reduce aggregate productivity through factor misallocation across establishments. Easterly^19 showed that the financing-gap model fails empirically. Yet no cross-national framework measures whether marginal urban investment creates or destroys asset value, a gap that persists in the urban agglomeration literature^36,37,38. Tobin's Q -- the ratio of market value to replacement cost -- has guided corporate investment theory for half a century^3,4, yet has never been applied systematically to the urban built environment at multi-city, multi-country scale.

Here we construct a marginal Urban Q spanning 157 countries and 1,567 subnational regions across eight countries across five continents, validated in parallel with a GDP-based formulation immune to housing-price cycles. We document three principal findings. First, a Simpson's paradox: within every developing-economy income group, MUQ declines with urbanisation, reproduced in a unified panel of 1,567 regions (beta = -0.043, p < 0.001), and proved to be mathematically inevitable when three conditions hold (Box 1). Second, at the city and prefecture level, a multi-country comparison reveals divergent investment-return patterns -- negative in China, positive in the United States and Japan -- with Japan's 67-year prefectural record providing an unparalleled reference trajectory and the China--Japan--Korea comparison illuminating three distinct crisis-recovery archetypes. Third, the carbon footprint of overconstruction: excess embodied carbon associated with below-parity investment in China alone totals approximately 3.0 GtCO2 (90% CI: 2.0--3.5), cross-validated by independent physical estimation, positioning MUQ as a climate-relevant diagnostic tool.

Several scope limitations merit explicit statement. MUQ is a descriptive measure of investment outcomes, not an identification strategy for causal mechanisms. Cross-national comparisons indicate institutional correlates of efficiency divergence, not causes. The within-city estimator reverses the sign of the investment-return association, indicating that the negative pattern is a structural cross-sectional regularity rather than a within-city dynamic. We report these boundaries transparently throughout.

---

## Results

### Finding 1: Simpson's paradox in urban investment returns -- multi-scale verification and theorem confirmation

**GDP-based MUQ.** To test whether declining returns are robust to alternative metrics, we construct a GDP-based MUQ (= DeltaGDP / GFCF, the inverse of the incremental capital-output ratio) using World Bank constant-2015-USD data across 157 countries. The paradox is reproduced and strengthened: within low-income countries, rho = -0.116 (p < 0.001, N = 1,284); lower-middle-income, rho = -0.131 (p < 0.001, N = 1,681); upper-middle-income, rho = -0.248 (p < 0.001, N = 1,834). High-income countries show no significant trend (rho = -0.035, p = 0.080). Leave-one-out analysis within the upper-middle-income group confirms that all 40 countries yield negative, significant correlations. A parallel analysis using Penn World Table real GDP produces consistent results (all developing groups p < 0.001). Block bootstrap resampling at the country level preserves significance in all three developing groups (Extended Data Table 1). We note that Easterly^19 critiqued the use of ICOR as a normative planning tool; our use is distinct: we employ 1/ICOR as a diagnostic signal immune to housing-price cycles, testing whether the within-group decline pattern is robust to an entirely different operationalisation.

**Housing-based MUQ.** Under the original housing-market-based MUQ across 144 countries, the paradox also holds: low-income rho = -0.150 (p = 0.002); lower-middle rho = -0.122 (p = 0.002); upper-middle rho = -0.099 (p <= 0.003); high-income rho = -0.013 (p = 0.633). The within-group pattern is robust to excluding China (upper-middle rho = -0.095, p = 0.005).

**Unified regional panel.** To extend the paradox below the national level, we harmonise GDP-based MUQ across 1,567 subnational regions in eight countries (China 275 cities, Japan 47 prefectures, Korea 17 metropolitan/provincial units, United States 921 MSAs, Europe 265 NUTS-2 regions, Australia 8 states, South Africa 9 provinces; 30,098 observations). In a panel regression with country and year fixed effects, log GDP per capita is negatively associated with MUQ (beta = -0.043, SE = 0.013, p < 0.001, R^2 = 0.457, N = 28,492), confirming that the efficiency-development gradient persists at the subnational level.

**Within-between decomposition and theorem confirmation.** The paradox arises because countries that urbanise also graduate into higher income groups, which carry higher average MUQ. This between-group compositional uplift offsets within-group erosion, producing the aggregate illusion of stability -- the aggregation trap (Fig. 1). We formalise this mechanism in Box 1 and prove that when three conditions hold -- within-group decline, systematic compositional shift, and compositional dominance -- the paradox is mathematically inevitable. All three conditions are satisfied in the global panel (Box 1, empirical verification).

**Boundary condition: within-country paradox not detected.** Systematic testing across seven countries shows that the aggregation trap conditions (A1--A3) are satisfied at the cross-national level but not within any single country: 0 of 7 countries satisfy all three conditions at the regional level (Extended Data Table 7). In Japan, Korea, and China, within-group decline (A1) holds, but compositional dominance (A3) does not -- the between-group efficiency gap within a single country is too small to overwhelm within-group decline. The aggregation trap is a cross-development-stage phenomenon, not a within-country spatial pattern.

### Finding 2: City-level efficiency mapping -- multi-country comparison

**Sign reversal: China versus the United States.** A clean specification eliminating shared-denominator mechanical correlation (DeltaV/GDP regressed on investment intensity) shows a negative investment-return association in China (beta = -0.37, 95% CI [-0.67, -0.06], p = 0.019, N = 455 city-years) and a positive one in the United States (beta = +2.81, p < 10^-6, N = 10,760 MSA-years). The attenuation from the original MUQ specification (beta = -2.26) to the clean specification quantifies the mechanical-correlation share at 83.7%; the residual 16.3% represents the between-city association net of the shared-denominator artefact. The positive US association is consistent with demand-responsive housing supply^5,26.

**Japan: 67-year prefectural record.** Japan's 47 prefectures (3,149 observations, 1956--2022) provide the fullest available trajectory of urban investment efficiency (Fig. 3). The clean specification yields pooled beta = +0.638 (p < 10^-6); prefecture fixed effects beta = +0.813 (p < 10^-30); two-way fixed effects beta = +0.057 (p = 0.037). Period decomposition shows declining investment productivity: the high-growth era (1960--1973) coefficient of 0.127 falls to 0.073 during the recovery period (2003--2022). Bai-Perron structural break tests identify two breaks at 1980 and 1990, with mean MUQ collapsing from 0.403 (1956--1980) to 0.226 (1981--1990) to 0.034 (1991--2022).

Japanese prefectures exhibit a clear urban-hierarchy gradient. Capital-region prefectures (Tokyo, Kanagawa, Saitama, Chiba) show the steepest MUQ decline (-0.0087 per year) but retain the highest absolute levels (Tokyo MUQ = 0.25 in 2022). Kinki-region prefectures decline at -0.0080 per year; Chubu at -0.0080; local prefectures at -0.0072. This hierarchy gradient -- faster decline in more productive regions but from higher starting points -- mirrors the within-country pattern observed across Chinese city tiers.

**Korea: V-shaped crisis recovery.** Korea's 17 metropolitan/provincial units (592 observations, 1986--2022) offer a natural experiment in crisis resilience (Fig. 4). The 1997 Asian Financial Crisis triggered a sharp MUQ collapse: from 0.369 (pre-crisis mean) to 0.101 (crisis mean), followed by recovery to 0.289 (recovery-period mean). The recovery ratio of 0.78 indicates near-complete structural restoration. Kruskal-Wallis test confirms significance (H = 52.7, p < 10^-11). Critically, metropolitan and provincial regions recovered at similar rates (metro 0.75, province 0.74), suggesting that the institutional restructuring following the IMF programme operated at the national rather than local level. Bai-Perron tests identify structural breaks at 1995 and 2000. Korea's Seoul Capital Region maintains higher MUQ (mean 0.209) than non-capital regions (0.180, Mann-Whitney p < 0.001), and its GDP share has increased from 46% to 49% during 2000--2022 -- a modest compositional shift insufficient to generate Simpson's paradox within Korea (all three regions show declining MUQ trends).

**China--Japan mirror.** The comparison between China and Japan at equivalent urbanisation stages is the most striking pattern in the data (Fig. 5). At approximately 54% urbanisation, China's MUQ (0.144) is 29% of Japan's (0.494), alongside investment intensity (GFCF/GDP) 1.8 times higher (China 44% versus Japan 25%). China's MUQ decline rate (-0.0074 per year) is 2.7 times Japan's (-0.0027 per year). Japan did not cross below MUQ = 0.1 until urbanisation exceeded 80%; China crossed that threshold at 57%. The divergence is consistent with fundamentally different institutional models of capital allocation across the urban hierarchy.

The three-country trajectory comparison reveals three archetypal patterns: Korea's 'orderly exit' (MUQ declining gradually, stabilising near zero); China's 'cliff' (rapid descent from high MUQ under rapid urbanisation); and Japan's 'lost decades' (prolonged MUQ stagnation and negative territory after the bubble). These archetypes have predictive value: they suggest that the crisis-recovery pathway depends critically on the institutional response, not merely on the depth of the initial decline.

**Europe: PIIGS stagnation and convergence.** Europe's 265 NUTS-2 regions across 29 countries (5,893 observations, 2000--2024) provide the broadest geographic coverage (Fig. 6). The 2009 sovereign debt crisis produced differentiated recovery patterns among PIIGS countries: Ireland (V-shaped, recovery ratio 0.34/0.13 = 2.6x), Spain (U-shaped), Portugal (V-shaped), Italy (L-shaped), and Greece (L-shaped, with MUQ remaining negative through 2013). Non-PIIGS western Europe weathered the crisis more effectively (crisis-period mean MUQ 0.078 versus PIIGS -0.117).

Beta-convergence analysis across 249 European regions shows strong convergence (beta = -0.777, p < 10^-25, R^2 = 0.574): regions with higher initial MUQ experienced larger subsequent declines. Eastern European regions show declining MUQ dispersion (sigma-convergence slope = -0.011, p < 0.001), while western European regions show increasing dispersion (+0.009, p = 0.022) -- consistent with the EU accession catch-up dynamic operating alongside divergence within mature economies.

**China provincial panel.** Province fixed effects on 31 provinces (2011--2019) yield beta = -0.164 (p = 0.001, N = 249), reinforcing the city-level finding with higher-quality FAI data directly observed at the provincial level.

**Quantity versus price composition.** In China, 44% of asset value change reflects new physical construction versus 11% in the United States, where appreciation of existing housing dominates (87%). This 3.8-fold divergence means Chinese MUQ predominantly captures real construction-efficiency information.

**Within-city estimator and qualifications.** City fixed effects reverse the sign in China: beta_FE = +0.52 (clustered SE = 0.10, p < 0.001); two-way fixed effects yield beta = +0.16 (p = 0.47, not significant). The sign reversal is consistent with the interpretation that the negative association reflects cross-sectional capital-allocation patterns -- which cities receive investment -- rather than within-city investment dynamics.

### Finding 3: Carbon footprint of overconstruction

Below-parity urban investment carries physical consequences that extend beyond financial losses. When MUQ falls below unity, each unit of investment generates less than one unit of asset value -- but the concrete, steel, and cement have already been produced, and their embodied carbon is irreversible.

**Period decomposition.** Using a combined flow-stock estimation method (Methods M5), we estimate that China's overconstruction between 2000 and 2024 generated approximately 3.0 GtCO2 in excess embodied carbon (90% CI: 2.0--3.5 GtCO2; Fig. 7). Decomposing by period: the structural overcapitalisation component (2000--2020, based on five-year moving-average smoothed Q) accounts for 0.4 GtCO2 (0.0--1.1), while the market correction component (2021--2024) contributes 2.2 GtCO2 (1.8--2.7). Annual excess carbon is capped at 50% of China's total building embodied carbon (~1,400--1,900 MtCO2/yr) to ensure physical plausibility. The concentration of carbon in the 2021--2024 period (88%) reflects the sharp MUQ decline during China's property market correction; the structural-period component, though smaller, identifies chronic overcapitalisation that preceded the market downturn.

**Physical cross-validation.** An independent estimate based on excess per-capita housing area provides convergent evidence. China's urban residents occupy 42 m^2 per capita, compared with a benchmark of approximately 33 m^2 (Japan/Korea/Germany/France average). The excess 9 m^2 across 933 million urban residents yields 8.4 billion m^2 of surplus floor area. At a median carbon intensity of 0.45 tCO2/m^2 (Zheng et al. 2024), this implies 3.8 GtCO2 (range 2.5--5.0 depending on carbon intensity assumptions). The convergence between the MUQ-based estimate (3.0 GtCO2) and the physical estimate (3.8 GtCO2) -- within a factor of 1.3 -- provides mutual validation.

**Magnitude contextualisation.** The 3.0 GtCO2 estimate is equivalent to approximately three years of global aviation emissions, or 5% of China's total CO2 emissions over the same period. Within the IPCC Avoid-Shift-Improve framework^11,16, MUQ offers a quantitative tool for the "Avoid" layer: investment with MUQ < 1 can be identified and redirected *before* construction begins, preventing embodied carbon from entering the atmosphere. The economic value of avoided emissions, at US$50--100 per tonne, ranges from US$135 billion to US$270 billion.

---

## Box 1 | The Aggregation Trap Theorem

Urban investment statistics are simultaneously distorted by two distinct statistical artefacts. Part A identifies a mechanical--economic decomposition: the scaling gap between asset values and capital stocks contains a large mechanical component (94.6%) that cancels in cross-national comparison, leaving a pure economic signal. Part B identifies a compositional decomposition: the aggregation trap proves that within-group efficiency decline is mathematically guaranteed to be masked by between-group graduation under three conditions.

**Part A: The Scaling Gap.** Urban asset value decomposes as V = Population x PerCapitaArea x Price, yielding a scaling exponent beta_V = 1 + beta_A + beta_P, where the mechanical component (= 1) accounts for 94.6% of beta_V in China (pooled: beta_V = 1.057, beta_A = -0.256, beta_P = 0.313) and 88.4% in the United States (beta_V = 1.131). The cross-national difference Delta-beta is entirely economic: the mechanical component cancels exactly (1 - 1 = 0), leaving Delta-beta = 0.057 - 0.131 = -0.075 (SE = 0.054). Scaling exponents may vary with boundary definitions^23,24; meta-analytic evidence confirms substantial cross-system variation^28.

**Part B: The Aggregation Trap Theorem.** We formalise the compositional mechanism underlying the paradox. Let K groups have efficiency E_k(u) = alpha_k + beta_k * u, with weight function w_k(u) summing to unity. The aggregate E_agg(u) = Sum_k w_k(u) * E_k(u).

*Theorem.* Under three conditions -- (A1) within-group decline: beta_k <= 0 for all k; (A2) systematic compositional shift: Sum_k w_k'(u) * alpha_k > 0; (A3) composition dominates within: the compositional uplift exceeds the within-group drag at every u -- the aggregate slope is non-negative even though every within-group slope is non-positive. The Simpson's paradox is a mathematical necessity under three empirically verified conditions.

*Two-group simplification.* With two groups sharing decline rate gamma and baseline gap Delta-alpha = alpha_H - alpha_L, the paradox arises if and only if Delta-alpha >= gamma. The escalator of compositional shift outpaces the treadmill of within-group decline. This condition holds globally (between-component 0.114 versus within-component 0.076) but fails within any single country.

*Empirical verification (cross-national).* A1 holds (all four income groups show negative Spearman rho, three significant at p < 0.003). A2 holds (mass shifts from low-income toward upper-middle-income groups). A3 holds (between-group component 0.114 exceeds within-group component 0.076). All three conditions are satisfied.

*Boundary condition (within-country).* Testing across seven countries at the subnational level, 0 of 7 satisfy all three conditions. The aggregation trap is a cross-development-stage phenomenon that operates between countries at different income levels, not between regions within a single economy.

---

## Discussion

### Synthesis: what the aggregation trap reveals about urban investment

Aggregate investment statistics, as currently reported, are structurally unable to detect efficiency decline in urbanising economies -- and the theorem we prove is consistent with this failure. Within every developing-economy income group, marginal returns on urban investment decline significantly with urbanisation, confirmed independently under both housing-based and GDP-based formulations, robust to leave-one-out exclusion of all 40 upper-middle-income countries, and reproduced in a unified panel of 1,567 regions across eight countries across five continents. Yet in pooled data the trend is flat: a Simpson's paradox that is a mathematical necessity under three empirically verified conditions.

### The China--Japan--Korea triangle: three trajectories, three institutional lessons

The multi-country comparison yields its clearest insights through the China--Japan--Korea triangle. Japan's 67-year record indicates that China's efficiency at 54% urbanisation is already lower than Japan's was at equivalent stages -- alongside investment intensity more than twice as high. Japan's post-bubble experience -- a permanent structural downshift in MUQ from 0.40 to 0.03 -- shows that a comparable trajectory has not reversed in the Japanese case even as investment levels adjusted. The hierarchy gradient within Japan (Capital > Kinki > Chubu > Local in absolute MUQ, but steeper decline rates in more productive regions) mirrors China's city-tier structure, suggesting that intra-national divergence accompanies national-level decline.

Korea provides the counterpoint. The V-shaped recovery after 1997 (recovery ratio 0.78) is consistent with institutional restructuring being followed by restoration of investment efficiency. The near-identical recovery rates across metropolitan and provincial regions suggest that the critical variable was national-level policy reform -- specifically, corporate and financial sector restructuring under the IMF programme -- rather than local characteristics. Europe's PIIGS experience (recovery ratio 0.65, with Italy and Greece showing L-shaped stagnation) shows that below-parity returns have persisted for a decade in the absence of such restructuring.

Several mechanisms may underlie the China--Japan efficiency divergence, though their causal roles remain unidentified: China's land-revenue fiscal model, which incentivises local governments to expand construction regardless of demand signals^13,25; the hukou system, which constrains labour mobility and creates spatial mismatches between investment location and population demand^22; and GDP-target competition among prefectures, which rewards investment volume over returns. Korea's post-1997 success suggests that addressing such structural distortions can restore investment efficiency, but the window for reform may narrow as overcapitalisation deepens.

### The economic and carbon magnitude

The cumulative below-parity investment in China totalled approximately US$18 trillion (90% CI: 12--24) between 2000 and 2024, with 91% concentrated in the 2021--2024 market correction period. The associated excess embodied carbon of 3.0 GtCO2 (2.0--3.5) establishes a direct link between investment misallocation and climate outcomes. Within the IPCC Avoid-Shift-Improve framework, MUQ < 1 serves as a quantitative threshold for the "Avoid" layer: screening investment proposals against MUQ projections before construction begins could prevent carbon lock-in at the source. The convergence between the MUQ-based and physical cross-validation estimates (factor 1.4) strengthens confidence in the order of magnitude.

### Policy implications for cities at different stages

The findings suggest a differentiated policy framework calibrated to city-level MUQ:

**First-tier cities (MUQ > 0.5).** Investment retains substantial headroom. Policy priority: ensuring supply-side responsiveness to demand, as in the positive US pattern. Regulatory focus should be on preventing speculation-driven oversupply rather than restricting investment per se.

**Second- and third-tier cities (0 < MUQ < 0.5).** Returns are positive but declining. Policy priority: transitioning from greenfield construction to urban renewal and asset absorption. Japan's experience suggests that this transition is fiscally and politically difficult but essential. Korea's post-1997 example shows that institutional restructuring can arrest MUQ decline at this stage.

**Fourth-tier and below (MUQ approaching 0 or negative).** Investment is destroying value. Policy priority: managed contraction -- preventing further capital deployment, facilitating orderly market clearing, and redirecting investment to higher-MUQ locations. The European PIIGS experience warns that without proactive restructuring, stagnation can persist for a decade or more.

**For urbanising economies (India, Vietnam, Indonesia).** These countries are entering their peak construction decades at MUQ levels comparable to China circa 2005--2010. The aggregation trap guarantees that their national statistics will not detect efficiency decline as it occurs. Implementing city-level MUQ monitoring *before* the construction wave peaks could prevent the accumulation of below-parity investment that China has experienced.

### The aggregation trap as a general phenomenon

The theorem we prove (Box 1) extends beyond urban investment. The three requirements -- within-group deterioration, endogenous graduation between strata, and compositional dominance -- describe any system where units improve their categorical standing while the metric of interest erodes within categories. Parallel structures exist across domains: in medicine, treatments worsening outcomes within every stratum can appear beneficial in pooled data^31,32; in education, school quality may decline within types while aggregate scores rise through student migration; in infrastructure-gap estimation, the assumption of constant marginal returns^7,19 is precisely the aggregation trap in another guise. The boundary condition is equally diagnostic: within single countries, the between-group efficiency gap is too small to generate the paradox, suggesting that the trap operates specifically at the interface between developmental stages.

### Limitations

Five limitations warrant discussion. First, seven calibration variants bound but do not resolve uncertainty in the national MUQ trajectory (Q = 1 crossing year 90% CI spans approximately 12 years). Second, all core findings are descriptive; we do not identify why returns erode -- and MUQ measures asset market value, not social value, so investment with MUQ < 1 may generate positive externalities not captured by market prices. Third, the within-city estimator reverses the sign of the investment-return association, indicating that the negative effect is a cross-sectional between-city regularity, not a within-city causal dynamic. Fourth, the Chinese city panel spans only 2011--2016, with V reconstructed rather than directly observed; FAI series after 2017 are estimated from growth rates. Fifth, the carbon estimate is methodologically less rigorous than the investment-efficiency findings: 88% of excess carbon is attributed to the 2021--2024 market correction, which reflects asset-price adjustment rather than solely physical overbuilding, and the 50% annual cap is an ad hoc physical-plausibility bound.

The aggregation trap we prove is not confined to urban investment. As India, Vietnam, Indonesia, and a generation of urbanising economies commit to the next wave of construction, the question is not whether they will encounter diminishing returns -- the theorem guarantees that pooled statistics will fail to detect it -- but whether their measurement systems will see through the aggregation trap before the concrete is in the ground.

---

## Methods

### M1. Marginal Urban Q (MUQ) construction

We define the Marginal Urban Q as MUQ(t) = DeltaV(t) / I(t), where DeltaV(t) is the year-on-year change in urban asset value and I(t) is gross investment. MUQ < 1 indicates that marginal investment generates less than one unit of asset value per unit of cost.

**Housing-based MUQ.** *China national level*: V(t) was estimated using seven calibrations combining three numerator definitions and two denominator definitions, combined via a weighted ensemble with Dirichlet-sampled weights (concentration parameter alpha = 20). I(t) was total fixed-asset investment from NBS. Coverage: 1998--2024. *China city level*: for 213 prefecture-level cities (2011--2016), V was reconstructed as population x median housing price x per-capita housing area, and I was fixed-asset investment (FAI). After excluding observations with FAI < 100 million yuan and applying 1%/99% winsorisation, 455 city-year observations were retained. *China provincial level*: for 31 provinces (2011--2019), V was constructed from provincial housing stock, prices, and per-capita area; FAI was directly observed from NBS provincial statistics. After winsorisation, 249 observations were retained. *US metropolitan areas*: V = median home value x housing units from Census ACS 5-Year estimates; I was approximated as the change in housing units x lagged median price. Coverage: 921 MSAs, 2010--2022 (10,760 differenced observations after 1%/99% winsorisation).

**GDP-based MUQ.** To provide a formulation immune to housing-price cycles, we construct MUQ_GDP = DeltaGDP / GFCF (the inverse of the incremental capital-output ratio) using World Bank WDI constant-2015-USD GDP and gross fixed capital formation. Coverage: 157 countries across four World Bank income groups, 1960--2023. A parallel series uses Penn World Table real GDP (rgdpna).

**Unified regional panel.** GDP-based MUQ was harmonised across 1,567 subnational regions in eight countries: China (275 cities), Japan (47 prefectures, from Cabinet Office SNA), Korea (17 metropolitan/provincial units, from ECOS), United States (921 MSAs), Europe (265 NUTS-2 regions, 29 countries, with GFCF allocated proportionally from national totals), Australia (8 states/territories), and South Africa (9 provinces). For US MSAs, regional GFCF was not directly available; we estimated it as the national GFCF/GDP ratio (approximately 21%) applied uniformly. Cross-MSA MUQ variation therefore reflects GDP growth differences rather than investment allocation differences. Extreme MUQ values were winsorised at 1%/99% thresholds. Total: 30,098 valid MUQ observations.

**Global panel.** Housing-based MUQ = Delta(rnna x GDP_deflator) / GFCF, where rnna is real capital stock from PWT 10.01. Coverage: 144 countries, 3,329 observations.

### M2. Simpson's paradox identification and block bootstrap

Countries were stratified by World Bank income classification. Within each income group, Spearman rank correlations between MUQ and urbanisation rate were computed. Both housing-based and GDP-based MUQ were tested independently. Country-level block bootstrap resampling (2,000 iterations) preserving each country's full time series was used to assess significance.

### M3. City-level and prefecture-level clean specification

The original MUQ specification contains mechanical correlation because MUQ = DeltaV/FAI places FAI in both dependent and independent variables. The clean specification DeltaV/GDP ~ FAI/GDP eliminates the shared component. For Japan, the equivalent is DeltaGDP/GDP ~ GFCF/GDP. For Korea, DeltaGRDP/GRDP ~ GFCF/GRDP. Four estimators were applied: pooled OLS with HC1 standard errors; entity fixed effects with clustered standard errors; two-way fixed effects (entity + year); and period decomposition. For the US, DeltaV/GDP ~ housing-unit growth rate.

**Japan period decomposition.** The 67-year series was divided into five periods following Bai-Perron breakpoints and economic history: high growth (1960--1973), stable growth (1974--1985), bubble (1986--1991), lost decade (1992--2002), and recovery (2003--2022). Period-specific pooled OLS coefficients track the declining productivity of investment over Japan's development arc.

**Korea crisis analysis.** Three-period comparison (pre-crisis 1993--1996, crisis 1997--1998, recovery 1999--2003) with Kruskal-Wallis and pairwise Mann-Whitney U tests. Recovery ratios computed as post-crisis MUQ / pre-crisis MUQ for each of the 17 regions.

**European PIIGS analysis.** Three-period comparison (pre-crisis 2005--2008, crisis 2009--2013, recovery 2014--2019) for Portugal, Italy, Ireland, Greece, and Spain, with non-PIIGS western Europe as control. Beta-convergence estimated as cross-sectional OLS of MUQ change on initial MUQ level.

### M4. Three Red Lines difference-in-differences

China's "Three Red Lines" policy (August 2020) imposed borrowing caps on property developers. We exploited cross-city variation in pre-policy real-estate dependence as treatment intensity. Diagnostic limitations are substantial: the parallel-trends test yields a marginal F-statistic (F = 2.82, p = 0.093), and the placebo test is significant (p < 0.001). Results are reported in Extended Data only.

### M5. Carbon footprint estimation

Excess carbon was estimated using two complementary methods with period decomposition. **Method A (MUQ flow method)**: for each year, excess investment = I(t) x max(0, 1 - MUQ_MA5(t)), where MUQ_MA5 is the five-year moving average. Carbon(t) = excess_I(t) x CI(t), where CI(t) declines from 1.20 to 0.60 tCO2 per 10,000 yuan. Method A yields 2.48 GtCO2 (90% CI: 2.33--3.31). **Method B (Q stock method)**: when five-year moving-average Q falls below unity, excess capital = K - V; annual excess carbon = Delta(excess capital) x CI(t). Method B yields 3.46 GtCO2 (1.58--4.16). **Combined estimate (Method C)** averages A and B, yielding 2.97 GtCO2 (2.04--3.47). Annual excess carbon is capped at 50% of China's total building embodied carbon (~1,400--1,900 MtCO2/yr). Physical cross-validation: excess per-capita housing area (China 42 m^2 versus benchmark ~33 m^2) yields 3.78 GtCO2 (2.52--5.04). Uncertainty was propagated via Monte Carlo simulation (10,000 iterations). Following Pomponi and Moncaster^30, estimates cover construction-phase emissions only and do not constitute a full life-cycle assessment. We adopt the central estimate of 3.0 GtCO2 (Method C: 2.97, rounded) for reporting in the main text.

### M6. Monte Carlo calibration uncertainty

For the national Q trajectory, uncertainty was quantified by jointly sampling across calibration weights and within-calibration parameters in 10,000 iterations. Bai-Perron structural break tests^17 identified breaks at 2004 and 2018 in the Chinese national series.

### M7. Scaling gap estimation and beta_V decomposition

For each urban system, beta_V was estimated via OLS: ln(V) = a + beta_V x ln(Pop) + year FE + epsilon, with cluster-robust standard errors. The identity V = Pop x PerCapitaArea x Price implies beta_V = 1 + beta_A + beta_P. SUR estimation provides joint standard errors for the economic signal (beta_A + beta_P).

### M8. Robustness checks

Robustness checks included: (i) balanced sub-panels; (ii) Newey-West and cluster-robust standard errors; (iii) Benjamini-Hochberg FDR correction (22 of 25 tests remained significant); (iv) leave-one-out analysis (40/40 countries negative under GDP-based MUQ); (v) winsorisation sensitivity; (vi) spatial autocorrelation tests; (vii) Bai-Perron break tests on Japanese national MUQ (optimal breaks: 1980, 1990); (viii) Korea Bai-Perron breaks (1995, 2000); (ix) European beta-convergence and sigma-convergence tests.

### M9. Aggregation trap theorem verification

The theorem's three conditions were tested at both the cross-national level and within each of seven subnational systems. **Condition A1** (within-group decline): Spearman rho between MUQ and urbanisation/time was computed within each income group (cross-national) or GDP-per-capita quartile (within-country). **Condition A2** (compositional shift): Spearman rho between urbanisation quintile and group weight was computed. **Condition A3** (composition dominates within): the pooled Spearman rho was decomposed into within-group and between-group components. Verified as satisfied at the cross-national level and as not satisfied within any of the seven subnational systems.

### M10. Data sources

*China national statistics*: NBS China Statistical Yearbook (2001--2024 editions). *China city panel*: 213 prefecture-level cities from the China City Database; housing prices from 58.com/Anjuke. *China provincial panel*: 31 provinces from NBS provincial statistics. *Japan*: Cabinet Office System of National Accounts (1955--2022, prefectural accounts); Ministry of Internal Affairs population data. *Korea*: Bank of Korea ECOS regional accounts (17 metropolitan cities and provinces, 1985--2022). *Europe*: Eurostat regional GDP (NUTS-2, 2000--2024); national GFCF from World Bank allocated to regions proportionally. *Australia*: ABS state accounts (8 states/territories, 1990--2023). *South Africa*: Statistics South Africa provincial GDP (9 provinces, 1993--2023). *Global panel*: World Bank WDI; Penn World Table 10.01. *United States*: Census Bureau ACS (data.census.gov), BEA CAGDP1 county-level GDP. *Carbon intensity*: CABECA^18; IEA^15; Zheng et al. (2024).

All analyses were performed in Python 3.9. Random seeds were fixed for all stochastic procedures.

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
41. UN-Habitat. *World Cities Report 2022: Envisaging the Future of Cities* (UN-Habitat, 2022).
42. Acemoglu, D. & Robinson, J. A. Why nations fail: the origins of power, prosperity, and poverty. *Crown Business* (2012).
43. Zheng, Y. et al. Life cycle carbon emissions of residential buildings in China: a comparative study of three calculation methods. *J. Build. Eng.* **82**, 108318 (2024).
44. Angel, S. et al. *Atlas of Urban Expansion -- 2016 Edition* (Lincoln Institute of Land Policy, 2016).
45. Cervero, R. & Kockelman, K. Travel demand and the 3Ds: density, diversity, and design. *Transp. Res. D* **2**, 199--219 (1997).
46. Seto, K. C. et al. Human settlements, infrastructure and spatial planning. *In: Climate Change 2014: Mitigation of Climate Change* (Cambridge Univ. Press, 2014).
47. Eurostat. Regional GDP (NUTS-2, nama_10r_2gdp) (2024). https://ec.europa.eu/eurostat
48. Australian Bureau of Statistics. Australian National Accounts: State Accounts (2024). https://www.abs.gov.au
49. Statistics South Africa. Gross domestic product: Annual estimates per region (2024). https://www.statssa.gov.za
50. International Monetary Fund. *World Economic Outlook* (IMF, 2024).

---

## Data availability

All data used in this study are publicly available. China national statistics: National Bureau of Statistics (www.stats.gov.cn). China provincial statistics: NBS provincial yearbooks. Global panel: World Bank WDI (data.worldbank.org), Penn World Table 10.01 (www.rug.nl/ggdc/productivity/pwt). Japan: Cabinet Office SNA prefectural accounts (www.esri.cao.go.jp). Korea: Bank of Korea ECOS (ecos.bok.or.kr). Europe: Eurostat (ec.europa.eu/eurostat). Australia: ABS (www.abs.gov.au). South Africa: Statistics South Africa (www.statssa.gov.za). United States: Census Bureau ACS (data.census.gov), BEA Regional Accounts (www.bea.gov). The unified regional panel (1,567 regions, 30,098 observations) and all processed datasets are available at https://github.com/andyhsi2023-cq/urban-investment-aggregation-trap.

## Code availability

All analysis code (Python 3.9) is available at https://github.com/andyhsi2023-cq/urban-investment-aggregation-trap.

## Acknowledgements

The author thanks the open data providers whose publicly available datasets made this research possible: the World Bank, Penn World Table, Japan Cabinet Office, Bank of Korea, Eurostat, Australian Bureau of Statistics, Statistics South Africa, US Census Bureau, US Bureau of Economic Analysis, and China National Bureau of Statistics.

## Author contributions

H.X. conceived the study, collected and processed all data, developed the methodology, performed all analyses, proved the Aggregation Trap theorem, created all figures, and wrote the manuscript.

## Competing interests

The author declares no competing interests.

---

## Extended Data

| ID | Type | Content |
|----|------|---------|
| ED Fig. 1 | Figure | Simpson's paradox: GDP-based MUQ by income group and urbanisation stage (157 countries) |
| ED Fig. 2 | Figure | Unified panel: 1,567 regions MUQ versus log GDP per capita |
| ED Fig. 3 | Figure | Japan 47-prefecture MUQ trajectories by urban-hierarchy group |
| ED Fig. 4 | Figure | Korea 17-region crisis-recovery patterns (1997 and GFC) |
| ED Fig. 5 | Figure | Europe PIIGS vs non-PIIGS MUQ trajectories |
| ED Fig. 6 | Figure | European beta-convergence and sigma-convergence |
| ED Fig. 7 | Figure | beta_V decomposition: mechanical vs. economic components |
| ED Fig. 8 | Figure | DeltaV decomposition: price effect vs. quantity effect (China by tier, US) |
| ED Fig. 9 | Figure | City-tier MUQ gradient with population-weighted statistics |
| ED Fig. 10 | Figure | Aggregation trap theorem: schematic and empirical verification |
| ED Table 1 | Table | Full Simpson's paradox statistics: housing-based and GDP-based MUQ, block bootstrap p-values |
| ED Table 2 | Table | Unified panel regression: MUQ ~ ln(GDP_pc) + Country FE + Year FE |
| ED Table 3 | Table | Cross-country clean specification summary: China, Japan, US, Korea (beta, SE, R^2) |
| ED Table 4 | Table | Japan period decomposition: five-era coefficients and MUQ statistics |
| ED Table 5 | Table | Korea three-period MUQ comparison and recovery ratios by region |
| ED Table 6 | Table | Europe PIIGS crisis analysis with country-level recovery patterns |
| ED Table 7 | Table | Aggregation trap C1/C2/C3 verification: cross-national (PASS) and within-country (7/7 FAIL) |
| ED Table 8 | Table | Carbon estimates: Method A, B, C with period decomposition and physical cross-validation |
| ED Table 9 | Table | DID regression table (with diagnostic warnings) |
| ED Table 10 | Table | SUR estimates of Delta-beta by year |

---

## Main Figures (proposed)

| Fig. | Content | Nature Cities rationale |
|------|---------|----------------------|
| Fig. 1 | Simpson's paradox: four income groups x two MUQ formulations | Core finding -- identical to Nature version |
| Fig. 2 | Aggregation trap theorem schematic + empirical verification | Theoretical contribution |
| Fig. 3 | Japan 67-year MUQ trajectory with structural breaks and hierarchy gradient | Key reference trajectory for urban science |
| Fig. 4 | Three crisis-recovery archetypes: Japan (L-shaped), Korea (V-shaped), PIIGS (mixed) | Multi-country institutional comparison |
| Fig. 5 | China--Japan mirror: MUQ aligned by urbanisation rate with investment intensity overlay | Central comparative finding |
| Fig. 6 | Europe 265 NUTS-2: East-West MUQ dynamics and convergence | Geographic breadth |
| Fig. 7 | Carbon period decomposition + physical cross-validation | Restored finding (NC-specific) |
| Fig. 8 | Policy framework: city-tier MUQ gradient with intervention thresholds | Policy translation (NC-specific) |

---

## Word Count

| Section | Words (est.) |
|---------|:------------:|
| Abstract | ~220 |
| Introduction | ~780 |
| Finding 1 | ~560 |
| Finding 2 | ~1,050 |
| Finding 3 | ~470 |
| Box 1 | ~470 |
| Discussion | ~1,100 |
| **Main text + Box 1** | **~4,650** |
| Methods (M1--M10) | ~1,450 |
| **Full text (Main + Box 1 + Methods)** | **~6,100** |
| References | 50 |

---

<!-- CHANGELOG: Nature Cities version (2026-03-22)

## Key differences from Nature v7.2 submission version:

### Structure
1. Three Findings (vs two in Nature): Finding 3 restores carbon as formal finding
2. Main figures: 8 (vs 5-6 in Nature)
3. References: 50 (vs 40 in Nature)

### Content expansions
1. **Abstract**: ~220 words (vs ~155), includes carbon + policy forward-look
2. **Introduction**: ~780 words (vs ~600), adds Tama New Town example, deeper urban science framing, three findings preview
3. **Finding 2**: ~1,050 words (vs ~560), fully expanded:
   - Japan hierarchy gradient (Capital > Kinki > Chubu > Local decline rates)
   - Korea V-shaped recovery with regional detail + IMF restructuring interpretation
   - China-Japan-Korea triangle narrative with three archetypes
   - Europe PIIGS detailed country-level patterns
   - European beta-convergence and sigma-convergence
4. **Finding 3**: ~470 words (new), carbon restored as formal finding:
   - Period decomposition with structural vs market-correction
   - Physical cross-validation (excess housing area)
   - IPCC Avoid-Shift-Improve framework positioning
   - Magnitude contextualisation (aviation emissions equivalent)
5. **Discussion**: ~1,100 words (vs ~810), expanded:
   - China-Japan-Korea triangle framing
   - Differentiated policy framework by city MUQ tier
   - Urbanising economies forward-look (India, Vietnam, Indonesia)
   - Carbon magnitude and policy link
6. **Methods**: ~1,450 words (vs ~1,260), added:
   - M3 expanded: Japan period decomposition, Korea crisis analysis, European PIIGS analysis
   - M5 carbon methods promoted from ED to main Methods
   - M8 expanded: Korea and Europe robustness checks
   - M10 expanded data sources

### Content preserved unchanged
- Finding 1 (Simpson's paradox): identical to Nature version
- Box 1 (Aggregation Trap theorem): identical except minor compression
- Clean specification methodology: identical
- Within-city estimator and qualifications: identical

### Tone adjustments
- More specific policy recommendations (city-tier framework)
- More detailed institutional interpretation (IMF, hukou, land-revenue)
- Carbon framed as policy-relevant finding, not just data point
- Forward-looking framing for urbanising economies
-->
