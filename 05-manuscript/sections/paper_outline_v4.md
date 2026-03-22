# Paper Outline v4: Integrating Wave-1 Empirical Findings

**Version**: 4.0
**Date**: 2026-03-21
**Basis**: paper_outline_v3.md + muq_real_correction_report + carbon_dimension_report + predictions_ews_report + revision_plan_v2
**Target journal**: Nature (Article format)
**Word budget**: ~3000-5000 words main text + Methods + Extended Data

---

## Changelog v3 -> v4

1. **MUQ 头条化**: 摘要和 Finding 1 均以 MUQ 转负为首要发现
2. **"irreversible" -> "persistent and self-reinforcing"**: 全文术语调整
3. **Finding 3 微调**: "效率递减"叙事修正为"发展中国家效率递减 + 碳成本"，整合 Simpson's paradox 解释
4. **EWS 跨国验证纳入**: 35/52 国家在 CPR 下降前展现 AR(1) 上升（p = 0.009），作为 Finding 1 的加强证据
5. **碳排放维度纳入 Discussion**: 中国 13.4 GtCO2 累计过度建设碳排放，全球 ~1,700 MtCO2/年
6. **前瞻预测纳入 Discussion**: 印度/越南/印尼条件性预测
7. **5 张主图更新**: 匹配 figure-designer 新设计方案
8. **区分两个"中国 MUQ"**: 国家级 MUQ（six-curves 数据，转负）vs 全球面板中国 MUQ（WB/PWT 数据，递增），口径差异在 Methods 中说明

---

## 1. Candidate Titles

**Option A (preferred)**:
> When building cities destroys value: a persistent regime shift in urban investment across nations

**Option B**:
> The end of urban expansion: evidence for a persistent investment regime shift across 158 countries

**Option C**:
> When cities overbuild: quantifying the global transition from urban expansion to renewal

Design principles: "persistent" replaces "irreversible" (reviewer concern); foregrounds value destruction (MUQ headline); accessible to Nature's broad readership.

---

## 2. Three Findings Structure

### Finding 1: China's Urban Q has undergone a persistent regime shift, with investment now destroying value

**Core claim** (2-3 sentences):
Since 2022, each additional yuan invested in China's urban built environment has destroyed rather than created asset value: the marginal Urban Q (MUQ) turned negative (p = 0.043), a model-free result that does not depend on the absolute calibration of the asset stock. This sign change is embedded in a broader structural shift: China's ratio of urban asset value to replacement cost (Urban Q) has been declining since the early 2000s, crossing the critical Q = 1 threshold around 2016.8 (90% CI [2010.1, 2022.5]). Across 10,000 Monte Carlo paths incorporating measurement-calibre uncertainty, 98.8% fall below Q = 1 by 2024, and Bai-Perron structural break tests identify regime boundaries at 2004 and 2018 (F = 30.1, p < 0.0001). The transition is persistent and self-reinforcing: three lock-in mechanisms -- demographic saturation, sunk capital with accelerating maintenance costs, and institutional path dependence in land-finance systems -- resist endogenous reversal.

**Supporting evidence**:
- MUQ sign change: positive (2000-2021) to negative (2022-2024), two-sample t-test p = 0.043 [HEADLINE]
- Seven V/K calibrations (V1/K1 through V3/K2 plus V1_adj/K2), weighted ensemble
- Monte Carlo framework propagating calibre uncertainty: 98.8% of paths cross Q = 1
- Bai-Perron test: two structural breaks (2004, 2018), F = 30.1, p < 0.0001
- Phased efficiency decline: ANOVA across three development stages, F-test p = 0.004
- **NEW -- EWS cross-national validation**: among 52 countries whose CPR declined >20% from peak, 67.3% (35/52) exhibited rising AR(1) coefficients in the decade before decline onset (binomial test p = 0.009), consistent with critical slowing down preceding urban investment regime shifts

**Main figure**: Fig 1 (see Section 4)
**Extended Data**: ED Fig 1 (individual calibrations), ED Fig 2 (Monte Carlo density + path plot), ED Table 1 (seven-calibre summary statistics), ED Fig 7 (EWS global scan)

---

### Finding 2: Overbuilding is quantifiable and displays clear spatial-income gradients

**Core claim** (2-3 sentences):
We estimate a theory-grounded optimal capital stock K* using a parsimonious model (urban population and GDP per capita as predictors, Cobb-Douglas form not rejected by translog test) and define the Overbuild Capital Ratio OCR = K/K*. China's 290 prefecture-level cities show a pronounced regional gradient: northeastern and western resource cities exhibit OCR >> 1 while coastal megacities cluster near OCR ~ 1. Globally, the Capital Price Ratio (CPR = V2/K, a replacement-cost analogue across 158 countries) displays systematic income-group differences, with upper-middle-income countries -- the cohort undergoing the fastest capital deepening -- showing the steepest CPR declines.

**Supporting evidence**:
- M2 model for K*: ln K = theta + alpha_P ln P_u + alpha_D ln(GDP/P), elasticities sign-consistent across Between/TWFE/RE; translog does not reject Cobb-Douglas
- China 290-city OCR distribution: spatial map + histogram
- OCR as predictor of subsequent economic performance: coefficient -1.72*** in growth regressions
- Global 158-country CPR by World Bank income group: systematic level and trend differences
- Four-country Q trends: China and Japan declining, US and UK stable; negative correlation with construction investment intensity (CI/GDP)

**Main figures**: Fig 2 + Fig 3 (see Section 4)
**Extended Data**: ED Fig 3 (M1 vs M2 comparison, rank correlation), ED Table 2 (K* regression table, full specifications), ED Fig 4 (OCR-Q scatter plot across cities), ED Table 3 (global CPR summary by income group)

---

### Finding 3: Investment efficiency declines systematically in developing economies, with mounting carbon costs

**Core claim** (2-3 sentences):
The capacity of fixed-asset investment to generate urban value does not decline uniformly across all countries but follows a development-stage-dependent pattern masked by Simpson's paradox in global aggregates. In low-income, lower-middle-income, and upper-middle-income countries, real MUQ declines significantly with urbanisation (Spearman rho = -0.10 to -0.15, all p < 0.01), while high-income countries show no significant trend. This efficiency decline carries a substantial carbon cost: China's cumulative overbuilding (K - K*) accounts for an estimated 13.4 GtCO2 in embodied construction emissions (2000-2024), with annual peaks reaching 11.8% of national total emissions; globally, overbuilding-attributable construction emissions total approximately 1,700 MtCO2 per year, or 12.3% of building-sector carbon output.

**Supporting evidence**:
- **Real MUQ by income group** (Simpson's paradox resolved):
  - Low income: declining (4.71 -> 3.76), rho = -0.150, p = 0.002
  - Lower middle income: declining (9.88 -> 1.15), rho = -0.122, p = 0.002
  - Upper middle income: declining (9.09 -> 7.48), rho = -0.099, p = 0.003
  - High income: no trend (rho = -0.013, p = 0.633)
- MUQ phased analysis for China: three stages, ANOVA F-test p = 0.004
- Non-parametric (kernel/LOESS) regression of Delta V/V on I/GDP from city panel
- **NEW -- Carbon dimension**: China cumulative overbuilding emissions 13.4 GtCO2; peak year 2022 at 1,287 MtCO2 (11.8% of national total); global overbuilding ~1,700 MtCO2/yr (12.3% of building-sector emissions)
- Cross-country CI/GDP vs Q correlation: four-country comparison + broader sample
- alpha(t) decomposition: alpha_N (new construction, declining) vs alpha_R (renewal, potentially stable)

**Main figures**: Fig 4 + Fig 5 (see Section 4)
**Extended Data**: ED Fig 5 (OLS/IV/GMM comparison), ED Fig 6 (alpha_N vs alpha_R decomposition), ED Table 4 (MUQ by phase and income group), ED Fig 8 (carbon cost map and time series)

---

## 3. Section-by-Section Outline

### Introduction (~800 words, 5 paragraphs)

**Para 1 -- Hook** (~150 words):
China invested more in fixed assets during 2010-2020 than any nation in history, yet since 2022, each additional yuan of urban investment has destroyed rather than created asset value. Open with MUQ turning negative -- the most accessible, model-free finding. The paradox: more building, less value.

**Para 2 -- Existing frameworks and their limits** (~200 words):
Solow growth model treats capital as homogeneous and predicts smooth convergence to steady state. Tobin's Q theory links investment decisions to asset valuation but has never been operationalised for the urban built environment at national scale. Urban economics literature documents housing bubbles and overbuilding episodically but lacks a unified, cross-national measurement framework. Three specific gaps:
1. No systematic measure of when urban investment crosses from value-creating to value-destroying
2. No benchmark for "how much should have been built" (optimal capital stock K*)
3. No cross-national comparison of urban investment efficiency trajectories

**Para 3 -- What this paper does** (~150 words):
We construct Urban Q (= V(t)/K(t)) for China across seven measurement calibrations and for 158 countries globally. We develop a theory-grounded optimal capital stock model (K*) to define the Overbuild Capital Ratio (OCR = K/K*). We document three findings: (1) China's MUQ has turned negative, confirming a persistent regime shift; (2) overbuilding shows clear spatial and income-group gradients; (3) investment efficiency declines systematically in developing economies, with mounting carbon costs that compound the misallocation.

**Para 4 -- Scope and distinctiveness** (~150 words):
Three ways this goes beyond Solow:
(a) We identify a persistent, self-reinforcing structural break, not gradual convergence
(b) We distinguish new-build vs renewal investment (alpha_N vs alpha_R), not homogeneous capital
(c) We introduce population-industry-capital alignment (OCR), not a single capital aggregate

**Para 5 -- Roadmap** (~100 words):
Brief statement of paper structure. Close with: "Our findings imply that China -- and potentially other rapidly urbanising economies -- has entered a regime where the primary challenge is no longer building cities but managing, renewing, and right-sizing existing urban assets. The carbon cost of delayed recognition may be measured in gigatonnes."

---

### Results (~1500 words)

#### Finding 1: Urban Q regime shift in China (~600 words)

**Para 1 [HEADLINE]**: MUQ evidence. Since 2022, China's marginal Urban Q has been negative (p = 0.043): each additional unit of investment reduces rather than increases the total value of the urban asset stock. This is a model-free finding -- it depends only on the year-over-year change in V(t) relative to annual investment, not on the absolute calibration of the asset stock. Reference Fig 1a (MUQ bar chart).

**Para 2**: Present the seven-calibration ensemble result. Trend: Q declining from ~1.8 (early 2000s) to below 1.0 (mid-2010s). Weighted Q = 1 crossing at 2016.8. Reference Fig 1b.

**Para 3**: Monte Carlo uncertainty quantification. 10,000 draws with calibre-specific weights. 98.8% of paths cross Q = 1. 90% CI for crossing year: [2010.1, 2022.5]. Conclusion: the direction is robust even if the precise year is uncertain. Reference Fig 1c.

**Para 4**: Bai-Perron structural break test. Two breaks identified: 2004 (end of low-investment era, start of construction boom) and 2018 (Q enters sub-1 regime). F = 30.1, p < 0.0001. The breaks define three regimes: expansion (pre-2004), overaccumulation (2004-2018), contraction (post-2018). Annotated on Fig 1b.

**Para 5**: Four-country comparison. China and Japan: declining Q trajectories. US and UK: roughly stable Q > 1. The divergence correlates with construction investment intensity (CI/GDP). Reference Fig 2a.

**Para 6 [NEW]**: EWS cross-national validation. Among 52 countries whose CPR declined more than 20% from peak, 35 (67.3%) exhibited rising first-order autocorrelation in the decade before decline onset, significantly above the 50% null expectation (binomial test p = 0.009). This pattern -- consistent with critical slowing down -- suggests that the regime shift documented in China reflects a more general dynamical signature of urban investment transitions, not a China-specific anomaly. Reference Fig 1d or ED Fig 7.

#### Finding 2: Overbuilding across cities and countries (~500 words)

**Para 1**: K* estimation via M2 model. Log-linear regression of capital stock on urban population and GDP per capita. Cobb-Douglas form not rejected (translog interaction terms insignificant). Elasticities: alpha_P ~ 1.0, alpha_D ~ 0.7. Reference Methods for details. Reference Fig 3a.

**Para 2**: OCR distribution across China's 290 cities. Map showing clear regional gradient. Northeast (old industrial base): median OCR ~ 1.4. Yangtze River Delta: median OCR ~ 1.0. Pearl River Delta: median OCR ~ 0.9. Resource-dependent cities in the west: highest OCR values. Reference Fig 3b.

**Para 3**: OCR as predictor. Cities with higher OCR in year t show lower GDP growth in t+3 to t+5 (coefficient -1.72, p < 0.001). This is consistent with the overbuilding hypothesis: excess capital stock becomes a drag on subsequent growth through maintenance burden, resource misallocation, and fiscal stress.

**Para 4**: Global CPR patterns. Across 158 countries, CPR shows systematic differences by income group. Upper-middle-income countries (the "peak construction" cohort) show the steepest declines. High-income countries show stable or rising CPR. Reference Fig 2b.

#### Finding 3: Staged efficiency decline with carbon costs (~500 words)

**Para 1 [Simpson's paradox]**: At the global aggregate level, real MUQ shows a weak positive trend with urbanisation (Spearman rho = 0.036, p = 0.038). However, this masks a classic Simpson's paradox: within each income group except high-income countries, MUQ declines significantly with urbanisation stage. The strongest decline occurs in lower-middle-income countries (median MUQ from 9.88 in Stage 1 to 1.15 in Stage 4, rho = -0.122, p = 0.002). High-income countries show no significant trend, consistent with a mature-economy baseline where marginal investment maintains but does not expand the stock. Reference Fig 4a.

**Para 2**: MUQ phased analysis for China. Based on six-curves national data, China's MUQ shows three-stage decline with ANOVA F-test p = 0.004. Note: China's position in the global panel (WB/PWT data, covering S1-S3 urbanisation stages) shows rising MUQ due to scale effects of rapid capital deepening. The sign difference reflects data-source differences (national accounts vs international PPP-adjusted data) and the fact that China has not yet entered S4 in the global panel timeframe. The national-data MUQ turning negative in 2022-2024 captures the most recent transition that the global panel cannot yet observe. Reference Methods for reconciliation.

**Para 3**: Non-parametric evidence. Kernel regression and LOESS of Delta V/V on I/GDP from the city panel (290 cities, 2010-2016). The curve shows efficiency peaking at moderate investment intensity, then declining. Reference Fig 4b.

**Para 4 [NEW -- Carbon cost]**: The efficiency decline carries a substantial environmental externality. Using China's construction-sector carbon intensity (0.65 tCO2 per 10,000 yuan of construction investment; China Building Energy Conservation Association, 2022), we estimate that cumulative overbuilding (K - K*, the capital stock exceeding model-predicted equilibrium) has generated 13.4 GtCO2 in embodied construction emissions over 2000-2024. Annual overbuilding-related emissions peaked at 1,287 MtCO2 in 2022, representing 11.8% of China's total carbon output. Globally, overbuilding-attributable construction emissions across countries with CPR > 1.5 total approximately 1,700 MtCO2 per year, or 12.3% of the building sector's annual carbon output. These are conservative lower-bound estimates covering only construction-phase emissions, excluding operational carbon from excess building stock. Reference Fig 5 or ED Fig 8.

**Para 5**: Theoretical decomposition. The aggregate efficiency decline reflects two opposing forces: alpha_N (new-build efficiency) declining as urbanisation saturates, while alpha_R (renewal efficiency) can remain positive where quality gaps exist. China's problem: alpha_N collapsed but investment was not redirected toward renewal. Countries that shifted investment toward renewal earlier (UK post-1990s, Japan post-2000s) stabilised their Q trajectories.

---

### Discussion (~900 words)

**Para 1 -- Summary of contribution** (~100 words):
Restate the three findings in one sentence each. Emphasise what is new: first cross-national measurement of Urban Q; first operationalisation of urban overbuilding (OCR) with a theory-grounded benchmark; first documentation of income-group-stratified investment efficiency decline with regime-shift evidence; first quantification of overbuilding's embodied carbon cost.

**Para 2 -- Beyond Solow** (~150 words):
Solow predicts diminishing returns but continuous convergence to steady state. Our evidence shows something qualitatively different: a structural break, not smooth adjustment. Three key distinctions:
(a) Persistence: no country in our sample that crossed Q < 1 has returned to Q > 1 within the observation window; three lock-in mechanisms (demographic saturation, sunk capital, institutional path dependence) make the transition self-reinforcing, though not physically irreversible in the strict sense
(b) Heterogeneous capital: new-build vs renewal investment have fundamentally different value-creation properties (alpha_N vs alpha_R)
(c) Alignment matters: OCR captures the mismatch between what was built and what was needed, a dimension absent from aggregate production functions

**Para 3 -- Policy implications** (~200 words):
For China: the construction-led growth model has exhausted its value-creating potential. Policy should shift from quantity (new floor area) to quality (renewal, repurposing, right-sizing). Specific implications:
- Overbuilt cities (OCR >> 1): priority is asset absorption and repurposing, not additional construction
- Transition cities (OCR ~ 1, Q ~ 1): calibrated renewal with industry-matching assessment
- Still-growing cities (OCR < 1): continued but moderated new construction
For other rapidly urbanising economies: the Chinese/Japanese trajectory provides an early warning -- high CI/GDP ratios may create value now but embed overbuilding risks for the next decade.

**Para 4 [NEW -- Carbon and climate implications]** (~120 words):
The carbon dimension transforms this from an economic efficiency problem into a planetary sustainability challenge. China's 13.4 GtCO2 of overbuilding-related construction emissions -- equivalent to one full year of the global building sector's carbon output -- represents perhaps the largest single category of "wasted" embodied carbon in human history. Because construction-phase emissions are irreversible (the CO2 is already in the atmosphere regardless of whether the buildings create value), the Urban Q framework provides a novel lens for climate accounting: emissions associated with investment that destroys rather than creates value should be counted as avoidable carbon waste. For rapidly urbanising economies, early detection of the Q = 1 threshold is therefore a climate imperative as well as an economic one.

**Para 5 [NEW -- Forward-looking predictions]** (~100 words):
The framework generates testable conditional predictions. If India (current urbanisation rate 34%, GFCF/GDP 28.5%) follows China's historical trajectory, its CPR may peak within approximately 13 years (2027-2037). Vietnam (urbanisation 35%, GFCF/GDP 30.4%) faces a similar timeline (2026-2036). Indonesia (urbanisation 56%) has already passed the urbanisation stage at which China's CPR peaked, and its CPR is indeed declining. These are conditional projections -- actual trajectories will depend on institutional responses -- but they demonstrate that the framework provides actionable early warning for the next wave of rapidly urbanising economies.

**Para 6 -- Limitations** (~200 words):
1. V(t) measurement: market value of the urban built environment is inherently difficult to observe. Our seven-calibration approach with Monte Carlo uncertainty bounds the problem but does not resolve it. The Q = 1 crossing year has a ~12-year confidence interval.
2. MUQ data-source reconciliation: China's national-data MUQ (turning negative) and global-panel MUQ (still positive in S1-S3) reflect different data sources and time horizons. We report both transparently and note that the national data captures recent dynamics the global panel cannot yet observe.
3. Causal identification of the inverted-U: IV estimates contradict OLS, and we cannot resolve this with available instruments. We present the shape as a theoretical prediction consistent with non-parametric evidence, not a causally identified relationship.
4. K* model: M2 is parsimonious but OCR values carry substantial uncertainty. We report OCR as a diagnostic tool with robust directional rankings, not a precision instrument.
5. City-level panel: real FAI data window is limited to 2010-2016 (7 years).
6. Carbon estimates: construction-phase only; operational carbon from excess stock would increase the total substantially.

**Para 7 -- Future directions** (~100 words):
Three priorities: (1) city-level panel with longer verified data windows and market-based V(t) measures; (2) causal identification of the investment-efficiency relationship using natural experiments; (3) real-time early warning system based on AR(1) monitoring for countries approaching the construction intensity threshold, potentially integrated with national carbon accounting frameworks.

**Para 8 -- Closing** (~50 words):
Cities are humanity's largest physical asset class and a major source of carbon emissions. Knowing when building more stops creating value -- and acting on that knowledge before the carbon is emitted -- may be among the most consequential economic and environmental signals of the 21st century.

---

### Methods (~1500 words, not counted in main text)

#### M1. Urban Q construction (~400 words)
- V(t): three numerator approaches (V1, V1_adj, V2, V3) -- unchanged from v3
- K(t): two denominator approaches (K1, K2) -- unchanged from v3
- Seven calibrations: V1/K1, V1/K2, V1_adj/K2, V2/K1, V2/K2, V3/K1, V3/K2
- Data sources: NBS Statistical Yearbooks, WB/PWT APIs, BIS residential property prices

#### M2. Monte Carlo calibre uncertainty framework (~200 words)
- 10,000 draws; each draw samples one calibration with Bayesian prior weights
- Within each calibration, parameter uncertainty drawn from specified distributions
- Output: distribution of Q(t) for each year, distribution of Q = 1 crossing year
- Reporting: median + 90% CI for crossing year; percentage of paths below Q = 1 by 2024

#### M3. K* estimation and OCR (~300 words)
- M2 model (preferred): ln K_it = theta_i + alpha_P ln P_u,it + alpha_D ln(GDP_it/P_it) + epsilon_it
- Estimation: Between, TWFE, RE; Hausman test for model selection
- Translog specification test
- OCR_it = K_it / K*_it
- Global CPR: V2_it / K_PIM,it for 158 countries

#### M4. Statistical tests (~350 words)
- Bai-Perron structural break test
- MUQ: defined as Delta V(t) / I(t); two-sample t-test for pre/post 2022 sign change; ANOVA across three stages
- Non-parametric efficiency curve: Nadaraya-Watson kernel regression and LOESS
- IV analysis (reported in Extended Data for transparency)
- Four-country comparison

**NEW -- M4.6 Simpson's paradox and real MUQ** (~50 words):
The global aggregate MUQ trend (weakly positive with urbanisation, rho = 0.036) masks divergent within-group patterns, a classic Simpson's paradox. We report all MUQ results stratified by World Bank income group using real (constant 2017 PPP USD) values, deflated by the GDP deflator from PWT 10.01. The aggregate trend is reported for transparency but not interpreted as evidence against efficiency decline.

**NEW -- M4.7 Early warning signal (EWS) analysis** (~80 words):
We compute rolling-window (8-year) first-order autocorrelation (AR(1)) of CPR time series for all countries with sufficient data. For the 52 countries whose CPR declined more than 20% from peak, we test whether AR(1) increased in the decade before the decline onset, consistent with the critical-slowing-down hypothesis (Scheffer et al., 2009). We report the proportion of countries showing rising AR(1) (Kendall tau > 0) and test against the 50% null with a binomial test.

#### M5. Carbon cost estimation (~150 words)
**NEW**: Overbuilding carbon cost = (K - K*) * carbon intensity of construction investment. For China, we use 0.65 tCO2 per 10,000 yuan (China Building Energy Conservation Association, 2022; consistent with IEA and UNEP estimates). For global estimates, we apply country-specific GFCF and the CPR-implied overbuilding fraction, with a uniform carbon intensity as a first-order approximation. All estimates cover construction-phase embodied carbon only; operational carbon from excess stock is excluded. We report these as order-of-magnitude estimates, not precise accounting.

#### M6. Data sources and ethics (~300 words)
- Unchanged from v3, with the addition of carbon intensity data sources

---

## 4. Five Main Figures (Updated)

### Fig 1: The headline -- investment turns value-destroying
**Layout**: Multi-panel (a-d), full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Four-country Q time series (China, Japan, US, UK); different line styles; China/Japan declining vs US/UK stable | Global context: divergence tracks investment intensity |
| **b** | China weighted Q time series (1998-2024) with 90% CI band; Q = 1 line labelled "value destruction threshold"; Bai-Perron break years annotated directly on curve | Q crosses 1 around 2016-2017; three structural regimes visible |
| **c** | MUQ bar chart (positive = blue, negative = orange); 2022-2024 prominently labelled; horizontal line at MUQ = 0 | Investment turned value-destroying post-2022 (p = 0.043) |
| **d** | EWS global scan: histogram or dot plot of AR(1) Kendall tau for 52 countries; binomial test result annotated | 67% show rising AR(1) before CPR decline; p = 0.009 |

### Fig 2: Global patterns of capital price and investment efficiency
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Monte Carlo density of Q = 1 crossing year (histogram + kernel density); vertical line at median 2016.8; 98.8% annotation | Direction robust despite timing uncertainty |
| **b** | CPR (V2/K) trajectories by World Bank income group (4 groups, line plot with CI bands); key countries labelled | Upper-middle-income countries show steepest CPR decline |

### Fig 3: Overbuilding across China's cities
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Choropleth map of OCR across 290 prefecture-level cities; diverging blue-white-red scale centred at OCR = 1 | Clear northeast-coast gradient; overbuilding concentrated in shrinking/resource cities |
| **b** | City-tier boxplot (4 tiers) of OCR; individual points overlaid; OCR = 1 reference line | Tier-3-and-below cities: 70.4% overbuilt; tier-1 cities all below 1 |

### Fig 4: Investment efficiency declines in developing economies (Simpson's paradox resolved)
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Real MUQ by income group and urbanisation stage (grouped boxplot or faceted violin); Spearman rho and p-values annotated per group | Low/middle-income groups: significant decline; high-income: flat |
| **b** | Non-parametric (LOESS) curve of Delta V/V vs I/GDP from city panel (290 cities, 2010-2016); scatter plot with fitted curve and 95% CI | Efficiency peaks at moderate investment intensity then declines |

### Fig 5: Carbon cost of overbuilding and forward-looking predictions
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | China overbuilding carbon emissions time series (stacked area: within-threshold vs over-threshold investment); right axis: % of national total emissions; annotation at 13.4 GtCO2 cumulative | Overbuilding carbon cost peaked at 11.8% of national emissions |
| **b** | Conditional predictions: CPR trajectories for India, Vietnam, Indonesia mapped against China's historical path; shaded uncertainty bands | India/Vietnam ~12-13 years from CPR peak; Indonesia already past peak |

---

## 5. Extended Data Plan (up to 10 figures/tables)

| ID | Type | Content | Purpose |
|----|------|---------|---------|
| **ED Fig 1** | Figure | All 7 individual Q calibrations plotted separately (small multiples) | Transparency |
| **ED Fig 2** | Figure | Monte Carlo spaghetti plot (200 random paths) + density at 2024 | Full uncertainty structure |
| **ED Table 1** | Table | Seven-calibration summary statistics | Reference table |
| **ED Fig 3** | Figure | K* model comparison: M1 vs M2; Spearman rank correlation | OCR robustness |
| **ED Table 2** | Table | K* regression table (all specifications) | Statistical detail |
| **ED Fig 4** | Figure | OCR vs Q scatter plot across 290 cities | OCR-Q relationship |
| **ED Table 3** | Table | Global CPR summary by income group | Full descriptives |
| **ED Fig 5** | Figure | Inverted-U: OLS/IV/GMM comparison | Transparent causal ID challenge |
| **ED Fig 6** | Figure | alpha_N vs alpha_R conceptual decomposition | Theoretical framework |
| **ED Table 4** | Table | MUQ by phase and income group, with Simpson's paradox decomposition | Statistical backup |
| **ED Fig 7** | Figure | EWS global scan: country-level AR(1) Kendall tau with 95% CI; regional breakdown | Cross-national EWS evidence |
| **ED Fig 8** | Figure | Carbon cost: 290-city overbuilding carbon map + global overbuilding carbon by country | Environmental dimension |

---

## 6. Key Narrative Decisions (Updated)

### What is IN the paper
- MUQ turning negative as HEADLINE finding (model-free, p = 0.043)
- Urban Q as an empirical measurement (seven calibrations, uncertainty-bounded)
- OCR as a diagnostic tool (direction robust, precision limited)
- Income-group-stratified efficiency decline (Simpson's paradox explicitly addressed)
- EWS cross-national validation (35/52, p = 0.009)
- Carbon cost of overbuilding (Discussion + one figure panel)
- Forward-looking conditional predictions (Discussion)
- "Persistent and self-reinforcing" framing (NOT "irreversible")
- alpha_N vs alpha_R conceptual decomposition

### What is in Extended Data only
- UCI as a composite index
- Inverted-U causal analysis (IV contradicts OLS)
- City-level UCI classification
- Global aggregate MUQ trend (reported for transparency, not as main evidence)
- Full EWS country-by-country results

### What is NOT in this paper (future work)
- Precise UCI thresholds for policy grading
- Causal identification of investment-efficiency relationship
- City-level panel beyond 2010-2016
- Operational carbon from excess building stock
- Real-time EWS monitoring system design

### Key data-source distinction (NEW)
- **China national MUQ** (from six-curves framework, NBS data, 1998-2024): turns negative in 2022-2024 (p = 0.043). This is the paper's headline finding.
- **China in global panel** (from WB/PWT data, PPP-adjusted, covering S1-S3 urbanisation stages): MUQ rising (7.80 -> 12.86 -> 17.12). This reflects (a) different data sources and accounting conventions, (b) the fact that China's global-panel observations end before the 2022 transition, and (c) scale effects during rapid capital deepening.
- **Resolution**: Both are reported. The Methods section explains the data-source differences. The national-data MUQ is the primary evidence for Finding 1; the global-panel MUQ is used only within the income-group stratification of Finding 3.

---

## 7. Writing Schedule (Updated)

| Section | Draft | Target date | Dependencies |
|---------|-------|-------------|--------------|
| Methods | First | 2026-04-05 | All data + analysis scripts finalized |
| Results | First | 2026-04-15 | Finalized figures + statistics |
| Introduction | First | 2026-04-25 | Literature review complete |
| Discussion | First | 2026-05-05 | All other sections |
| Abstract | First | 2026-05-10 | Full draft complete |
| Full draft v1 | Assembly | 2026-05-15 | All sections |
| Internal review | Peer-reviewer agent | 2026-05-25 | Draft v1 |
| Revision + v2 | Final | 2026-06-15 | Review feedback |
| Submission package | Cover letter + highlights | 2026-06-30 | Draft v2 approved |
| **Submission** | | **~2026-08-15** | Final checks |

---

*Outline v4.0 -- Wave-1 findings integrated*
*Manuscript Writer Agent*
*2026-03-21*
