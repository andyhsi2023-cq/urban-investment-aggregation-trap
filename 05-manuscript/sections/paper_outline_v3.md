# Paper Outline v3: 3-Finding Structure for Nature

**Version**: 3.0
**Date**: 2026-03-21
**Target journal**: Nature (Article format)
**Word budget**: ~3000-5000 words main text + Methods + Extended Data
**Basis**: optimization_plan_2026-03-21.md (Phase 2 corrections integrated)

---

## 1. Candidate Titles

**Option A (preferred)**:
> Irreversible regime shift in urban investment: when building cities stops creating value

**Option B**:
> The end of urban expansion: evidence for an irreversible investment regime shift across nations

**Option C**:
> When cities overbuild: quantifying the global transition from urban expansion to renewal

Design principles: avoids "phase transition" (insufficient physical rigour); foregrounds irreversibility, investment, and the global scope; accessible to Nature's broad readership.

---

## 2. Three Findings Structure

### Finding 1: China's Urban Q has undergone an irreversible regime shift

**Core claim** (2-3 sentences):
China's ratio of urban asset value to replacement cost (Urban Q) has been declining since the early 2000s and crossed the critical Q = 1 threshold around 2016.8 (90% CI [2010.1, 2022.5]). This crossing is structurally irreversible: 98.8% of Monte Carlo paths that incorporate measurement-calibre uncertainty fall below Q = 1 by 2024, and Bai-Perron structural break tests identify regime boundaries at 2004 and 2018 (F = 30.1, p < 0.0001). The marginal Urban Q (MUQ) -- the incremental value created per unit of new investment -- turned negative in 2022-2024 (p = 0.043), confirming that recent investment destroys rather than creates asset value.

**Supporting evidence**:
- Seven V/K calibrations (V1/K1 through V3/K2 plus V1_adj/K2), weighted ensemble
- Monte Carlo framework propagating calibre uncertainty: 98.8% of paths cross Q = 1
- Bai-Perron test: two structural breaks (2004, 2018), F = 30.1, p < 0.0001
- MUQ sign change: positive (2000-2021) to negative (2022-2024), two-sample t-test p = 0.043
- Phased efficiency decline: ANOVA across three development stages, F-test p = 0.004

**Main figure**: Fig 1 (see Section 4)
**Extended Data**: ED Fig 1 (individual calibrations), ED Fig 2 (Monte Carlo density + path plot), ED Table 1 (seven-calibre summary statistics)

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

### Finding 3: Investment efficiency declines systematically with development stage

**Core claim** (2-3 sentences):
The capacity of fixed-asset investment to generate urban value does not decline linearly but follows a staged pattern: high efficiency during early urbanisation, diminishing returns during the construction boom, and value destruction after overaccumulation. We document this through three independent lines of evidence -- MUQ time series, phased ANOVA, and non-parametric investment-efficiency curves -- none of which requires causal identification assumptions. Cross-nationally, countries with higher construction investment intensity (CI/GDP) exhibit systematically lower Urban Q trajectories, suggesting this pattern is not China-specific but a general feature of capital deepening.

**Supporting evidence**:
- MUQ time series for China (1998-2024): three-phase pattern visible without parametric assumptions
- Phased ANOVA: three development stages show significantly different mean MUQ (p = 0.004)
- Non-parametric (kernel/LOESS) regression of Delta V/V on I/GDP: reveals the shape of the efficiency curve without imposing quadratic functional form
- Cross-country CI/GDP vs Q correlation: four-country comparison + broader sample
- alpha(t) decomposition: alpha_N (new construction, declining) vs alpha_R (renewal, potentially stable) -- theoretical framework for why the aggregate pattern emerges

**Main figures**: Fig 4 + Fig 5 (see Section 4)
**Extended Data**: ED Fig 5 (OLS/IV/GMM comparison for inverted-U, reported for transparency), ED Fig 6 (alpha_N vs alpha_R conceptual decomposition), ED Table 4 (MUQ by phase, descriptive statistics)

---

## 3. Section-by-Section Outline

### Introduction (~800 words, 5 paragraphs)

**Para 1 -- Hook** (~150 words):
China invested more in fixed assets during 2010-2020 than any nation in history, yet its urban asset values have been declining in real terms since the mid-2010s. Open with a striking number: cumulative urban fixed-asset investment 2000-2023 in RMB and USD equivalent. The paradox: more building, less value.

**Para 2 -- Existing frameworks and their limits** (~200 words):
Solow growth model treats capital as homogeneous and predicts smooth convergence to steady state. Tobin's Q theory links investment decisions to asset valuation but has never been operationalised for the urban built environment at national scale. Urban economics literature documents housing bubbles and overbuilding episodically but lacks a unified, cross-national measurement framework. Three specific gaps:
1. No systematic measure of when urban investment crosses from value-creating to value-destroying
2. No benchmark for "how much should have been built" (optimal capital stock K*)
3. No cross-national comparison of urban investment efficiency trajectories

**Para 3 -- What this paper does** (~150 words):
We construct Urban Q (= V(t)/K(t)) for China across seven measurement calibrations and for three comparison countries (Japan, US, UK). We develop a theory-grounded optimal capital stock model (K*) to define the Overbuild Capital Ratio (OCR = K/K*). We document three findings: [one sentence per finding, previewing the structure].

**Para 4 -- Scope and distinctiveness** (~150 words):
Three ways this goes beyond Solow:
(a) We identify an irreversible structural break, not gradual convergence
(b) We distinguish new-build vs renewal investment (alpha_N vs alpha_R), not homogeneous capital
(c) We introduce population-industry-capital alignment (OCR), not a single capital aggregate

**Para 5 -- Roadmap** (~100 words):
Brief statement of paper structure. Close with: "Our findings imply that China -- and potentially other rapidly urbanising economies -- has entered a regime where the primary challenge is no longer building cities but managing, renewing, and right-sizing existing urban assets."

---

### Results (~1500 words)

#### Finding 1: Urban Q regime shift in China (~500 words)

**Para 1**: Present the seven-calibration ensemble result. Trend: Q declining from ~1.8 (early 2000s) to below 1.0 (mid-2010s). Weighted Q = 1 crossing at 2016.8. Reference Fig 1a.

**Para 2**: Monte Carlo uncertainty quantification. 10,000 draws with calibre-specific weights. 98.8% of paths cross Q = 1. 90% CI for crossing year: [2010.1, 2022.5]. Conclusion: the direction is robust even if the precise year is uncertain. Reference Fig 1b.

**Para 3**: Bai-Perron structural break test. Two breaks identified: 2004 (end of low-investment era, start of construction boom) and 2018 (Q enters sub-1 regime). F = 30.1, p < 0.0001. The breaks define three regimes: expansion (pre-2004), overaccumulation (2004-2018), contraction (post-2018). Reference Fig 1c.

**Para 4**: MUQ evidence. MUQ positive but declining 2000-2021, turns negative 2022-2024 (p = 0.043). This is a model-free confirmation: the latest investment cohort destroyed value. Reference Fig 1d.

**Para 5**: Four-country comparison. China and Japan: declining Q trajectories. US and UK: roughly stable Q > 1. The divergence correlates with construction investment intensity (CI/GDP): China ~45%, Japan ~25% at peak; US and UK ~15-20%. Reference Fig 1e or transition to Fig 2.

#### Finding 2: Overbuilding across cities and countries (~500 words)

**Para 1**: K* estimation via M2 model. Log-linear regression of capital stock on urban population and GDP per capita. Cobb-Douglas form not rejected (translog interaction terms insignificant). Elasticities: alpha_P ~ 1.0, alpha_D ~ 0.7. The model answers: "Given this city's population and economic output, how much capital stock is justified?" Reference Methods for details. Reference Fig 2a.

**Para 2**: OCR distribution across China's 290 cities. Map showing clear regional gradient. Northeast (old industrial base): median OCR ~ 1.4. Yangtze River Delta: median OCR ~ 1.0. Pearl River Delta: median OCR ~ 0.9. Resource-dependent cities in the west: highest OCR values. Reference Fig 2b.

**Para 3**: OCR as predictor. Cities with higher OCR in year t show lower GDP growth in t+3 to t+5 (coefficient -1.72, p < 0.001). This is consistent with the overbuilding hypothesis: excess capital stock becomes a drag on subsequent growth through maintenance burden, resource misallocation, and fiscal stress. Reference Fig 3.

**Para 4**: Global CPR patterns. Across 158 countries, CPR (= V2/K, a replacement-cost ratio) shows systematic differences by income group. Upper-middle-income countries (the "peak construction" cohort) show the steepest declines. High-income countries show stable or rising CPR. This is consistent with the regime shift being a feature of the rapid capital-deepening phase, not a permanent condition. Reference Fig 3b.

#### Finding 3: Staged efficiency decline (~500 words)

**Para 1**: MUQ phased analysis. Divide China's urban investment history into three stages based on Bai-Perron breaks: Stage I (pre-2004), Stage II (2004-2018), Stage III (post-2018). Mean MUQ declines monotonically: Stage I >> Stage II >> Stage III (ANOVA F-test p = 0.004). The decline is not gradual but accelerating. Reference Fig 4a.

**Para 2**: Non-parametric evidence. Kernel regression and LOESS of Delta V/V on I/GDP, using the city panel (290 cities, 2010-2016 real FAI window). The curve shows: efficiency peaks at moderate investment intensity, then declines. We report the shape without imposing a quadratic functional form. The theoretical inverted-U is consistent with the non-parametric shape, but we do not claim causal identification (see Methods for IV discussion). Reference Fig 4b.

**Para 3**: Cross-national investment intensity patterns. Countries that sustained high CI/GDP ratios longer (China, Japan) show steeper Q declines than those with moderate ratios (US, UK). Scatter plot of long-run average CI/GDP vs Q trajectory slope. Reference Fig 5a.

**Para 4**: Theoretical decomposition. The aggregate efficiency decline reflects two opposing forces: alpha_N (new-build efficiency) declining as urbanisation saturates, while alpha_R (renewal efficiency) can remain positive where quality gaps exist. China's problem: alpha_N collapsed but investment was not redirected toward renewal. Countries that shifted investment toward renewal earlier (UK post-1990s, Japan post-2000s) stabilised their Q trajectories. Reference Fig 5b.

**Para 5**: Implications. The staged decline pattern implies a predictable policy window: when MUQ approaches zero (detectable in real time), it signals the transition from "build more" to "build better." For China, this window closed around 2020.

---

### Discussion (~800 words)

**Para 1 -- Summary of contribution** (~100 words):
Restate the three findings in one sentence each. Emphasise what is new: first cross-national measurement of Urban Q; first operationalisation of urban overbuilding (OCR) with a theory-grounded benchmark; first documentation of staged investment efficiency decline with regime-shift evidence.

**Para 2 -- Beyond Solow** (~150 words):
Solow predicts diminishing returns but continuous convergence to steady state. Our evidence shows something qualitatively different: a structural break, not smooth adjustment. Three key distinctions:
(a) Irreversibility: no country in our sample that crossed Q < 1 has returned to Q > 1 within the observation window
(b) Heterogeneous capital: new-build vs renewal investment have fundamentally different value-creation properties (alpha_N vs alpha_R)
(c) Alignment matters: OCR captures the mismatch between what was built and what was needed, a dimension absent from aggregate production functions

**Para 3 -- Policy implications** (~200 words):
For China: the construction-led growth model has exhausted its value-creating potential. Policy should shift from quantity (new floor area) to quality (renewal, repurposing, right-sizing). Specific implications:
- Overbuilt cities (OCR >> 1): priority is asset absorption and repurposing, not additional construction
- Transition cities (OCR ~ 1, Q ~ 1): calibrated renewal with industry-matching assessment
- Still-growing cities (OCR < 1): continued but moderated new construction
For other rapidly urbanising economies (India, Southeast Asia, Africa): the Chinese/Japanese trajectory provides an early warning -- high CI/GDP ratios may create value now but embed overbuilding risks for the next decade.

**Para 4 -- Limitations** (~200 words):
1. V(t) measurement: market value of the urban built environment is inherently difficult to observe. Our seven-calibration approach with Monte Carlo uncertainty bounds the problem but does not resolve it. The Q = 1 crossing year has a ~12-year confidence interval.
2. Causal identification of the inverted-U: IV estimates contradict OLS, and we cannot resolve this with available instruments. We present the inverted-U as a theoretical prediction consistent with non-parametric evidence, not a causally identified relationship. Better natural experiments (e.g., quasi-random allocation of construction permits) are needed.
3. K* model: M2 is parsimonious but omits human capital as an independent predictor (collinear with GDP per capita). The direction of OCR rankings is robust across M1/M2, but precise OCR values carry substantial uncertainty. We report this as a diagnostic tool, not a precision instrument.
4. City-level panel: real FAI data window is limited to 2010-2016 (7 years). Longer panels with verified data would strengthen the city-level findings.
5. Urban asset stock: PIM assumptions (depreciation rates, initial stock) affect K(t) levels though not trends.

**Para 5 -- Future directions** (~100 words):
Three priorities: (1) city-level panel with longer verified data windows and market-based V(t) measures; (2) causal identification of the investment-efficiency relationship using natural experiments; (3) extension to other rapidly urbanising regions (India, Sub-Saharan Africa) as they approach the construction intensity levels where regime shifts may occur.

**Para 6 -- Closing** (~50 words):
Cities are humanity's largest physical asset class. Knowing when building more stops creating value -- and acting on that knowledge -- may be among the most consequential economic signals of the 21st century.

---

### Methods (~1500 words, not counted in main text)

#### M1. Urban Q construction (~400 words)
- V(t): three numerator approaches
  - V1: residential market capitalisation = average price per sqm * cumulative floor area (with V1_adj age-depreciated variant)
  - V2: PWT capital stock at current national prices (= nominal replacement cost, renamed CPR for global analysis)
  - V3: GDP capitalisation approach (GDP / cap rate)
- K(t): two denominator approaches
  - K1: cumulative residential investment (PIM, 2% depreciation)
  - K2: cumulative total fixed-asset investment (PIM, 3.5% depreciation)
- Seven calibrations: V1/K1, V1/K2, V1_adj/K2, V2/K1, V2/K2, V3/K1, V3/K2
- Recommended calibration: V1/K2 (conservative: residential market value / total construction cost), with V1_adj/K2 as lower bound
- Data sources: NBS Statistical Yearbooks (parsed from Excel), WB/PWT APIs, BIS residential property prices

#### M2. Monte Carlo calibre uncertainty framework (~200 words)
- 10,000 draws; each draw samples one calibration with Bayesian prior weights (based on theoretical fit)
- Within each calibration, parameter uncertainty (depreciation rate, initial stock) drawn from specified distributions
- Output: distribution of Q(t) for each year, distribution of Q = 1 crossing year
- Reporting: median + 90% CI for crossing year; percentage of paths below Q = 1 by 2024

#### M3. K* estimation and OCR (~300 words)
- M2 model (preferred): ln K_it = theta_i + alpha_P ln P_u,it + alpha_D ln(GDP_it/P_it) + epsilon_it
- Estimation: Between, TWFE, RE; Hausman test for model selection
- Translog specification test: add squared terms and interactions; F-test for Cobb-Douglas restriction
- Bootstrap: 1000 resamples for elasticity confidence intervals
- OCR_it = K_it / K*_it; values > 1 indicate overbuilding
- Global CPR: V2_it / K_PIM,it for 158 countries; descriptive analysis by income group (not claimed as Tobin's Q)

#### M4. Statistical tests (~300 words)
- Bai-Perron structural break test: applied to Q time series; up to 5 breaks allowed, BIC for model selection
- MUQ: defined as Delta V(t) / I(t); two-sample t-test for pre/post 2022 sign change; ANOVA across three stages
- Non-parametric efficiency curve: Nadaraya-Watson kernel regression and LOESS of Delta V/V on I/GDP
- IV analysis (reported in Extended Data for transparency): geographic instruments (terrain ruggedness, distance to coast); Hausman test rejects OLS; Sargan test rejects overidentification; conclusion: no credible causal estimate available with current instruments
- Four-country comparison: descriptive Q trajectories + correlation of CI/GDP with Q slope

#### M5. Data sources and ethics (~300 words)
- China national: NBS Statistical Yearbooks 2000-2023 (Excel, automated parsing)
- China city panel: Marc Data Urban Database v6.0, 58.com/Anjuke housing prices, municipal debt data; real FAI window 2010-2016
- International: WB WDI API, Penn World Table 10.01, BIS residential property prices, national statistical offices (e-Stat Japan, BEA US, ONS UK)
- Data availability statement
- No human subjects; publicly available aggregate data; no ethics approval required

---

## 4. Five Main Figures

### Fig 1: China's Urban Q regime shift
**Layout**: Multi-panel (a-d), full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Weighted Q time series (1998-2024) with 90% CI band from 7-calibration ensemble; horizontal line at Q = 1 | Trend crosses Q = 1 around 2016-2017 |
| **b** | Monte Carlo density of Q = 1 crossing year (histogram + kernel density); vertical line at median 2016.8 | 98.8% of paths cross; direction robust despite timing uncertainty |
| **c** | Bai-Perron regime identification: Q time series with vertical break lines at 2004, 2018; three regimes shaded differently | Three structural regimes, not gradual decline |
| **d** | MUQ time series (bar chart, positive = blue, negative = red); horizontal line at MUQ = 0 | Investment turned value-destroying post-2022 |

### Fig 2: Overbuilding across China's cities
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Choropleth map of OCR across 290 prefecture-level cities; diverging colour scale centred at OCR = 1 | Clear northeast-coast gradient; overbuilding concentrated in shrinking/resource cities |
| **b** | Histogram of OCR distribution with vertical lines at OCR = 1.0 and OCR = 1.5; labelled exemplar cities (Shenzhen OCR ~ 0.85, Hegang OCR ~ 1.8) | Most cities mildly overbuilt; long right tail |

### Fig 3: Global patterns of capital price and overbuilding
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Four-country Q time series (China, Japan, US, UK); different line styles; annotated with key events (Japan bubble burst, China stimulus) | China/Japan declining, US/UK stable; divergence tracks investment intensity |
| **b** | CPR (V2/K) trajectories by World Bank income group (4 groups, line plot with CI bands) | Upper-middle-income countries show steepest CPR decline; pattern is systematic |

### Fig 4: Staged decline of investment efficiency
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | MUQ by development stage (box plot or violin plot, three stages defined by Bai-Perron breaks); ANOVA p-value annotated | Monotonic decline across stages; statistically significant |
| **b** | Non-parametric (LOESS) curve of Delta V/V vs I/GDP from city panel (290 cities, 2010-2016); scatter plot with fitted curve and 95% CI | Efficiency peaks at moderate investment intensity then declines; shape consistent with inverted-U but reported model-free |

### Fig 5: From expansion to renewal -- the investment transition
**Layout**: Two panels, full page width

| Panel | Content | Key message |
|-------|---------|-------------|
| **a** | Scatter plot: long-run average CI/GDP vs Q trajectory slope (four countries + extended sample if available); labelled quadrants | High investment intensity predicts steeper Q decline |
| **b** | Conceptual diagram: alpha_N (new-build efficiency, declining curve) vs alpha_R (renewal efficiency, stable/rising); shaded area showing the gap; annotated with "policy window" where alpha_N approaches zero | Decomposition explains why aggregate efficiency declines; renewal offers an alternative path |

---

## 5. Extended Data Plan (up to 10 figures/tables)

| ID | Type | Content | Purpose |
|----|------|---------|---------|
| **ED Fig 1** | Figure | All 7 individual Q calibrations plotted separately (small multiples) | Transparency: show what each calibration looks like before ensembling |
| **ED Fig 2** | Figure | Monte Carlo spaghetti plot (200 random paths) + density at 2024 | Visualise the full uncertainty structure |
| **ED Table 1** | Table | Seven-calibration summary: V definition, K definition, Q at 2000/2010/2020/2024, crossing year, trend slope | Reference table for all calibrations |
| **ED Fig 3** | Figure | K* model comparison: M1 (full) vs M2 (parsimonious); Spearman rank correlation of city OCR between M1 and M2 | Robustness of OCR rankings to model choice |
| **ED Table 2** | Table | K* regression table: Between/TWFE/RE for both M1 and M2; translog test results; bootstrap CI for elasticities | Full statistical detail for K* estimation |
| **ED Fig 4** | Figure | OCR vs Q scatter plot across 290 cities with fitted line | Demonstrate the theorised negative OCR-Q relationship |
| **ED Table 3** | Table | Global CPR summary by income group: N countries, mean CPR, trend slope, 95% CI | Full descriptive statistics for the global pattern |
| **ED Fig 5** | Figure | Inverted-U analysis: OLS, IV, GMM side by side; coefficient table + diagnostic tests (Hausman, Sargan) | Transparent reporting of the causal identification challenge |
| **ED Fig 6** | Figure | UCI diagnostic: 4-quadrant plot (Q vs OCR) with 290 cities classified into expansion/renewal/rightsizing/crisis zones | Preview of the UCI framework (moved from main to Extended Data) |
| **ED Table 4** | Table | MUQ descriptive statistics by phase: N years, mean, SD, min, max, t-test results | Full statistical backup for Finding 3 |

---

## 6. Key Narrative Decisions

### What is IN the paper
- Urban Q as an empirical measurement (seven calibrations, uncertainty-bounded)
- OCR as a diagnostic tool (direction robust, precision limited)
- Staged efficiency decline (descriptive, model-free)
- Cross-national comparison (four countries + 158-country CPR)
- alpha_N vs alpha_R conceptual decomposition

### What is in Extended Data only
- UCI as a composite index (Q/OCR) -- promising but K* uncertainty too large for precise grading
- Inverted-U causal analysis (IV contradicts OLS; reported transparently, not as a main claim)
- City-level UCI classification and radar chart
- R-U relocation-utilisation policy framework (Discussion mention only)

### What is NOT in this paper (future work)
- Precise UCI thresholds for policy grading (needs better K* estimates)
- Causal identification of investment-efficiency relationship
- City-level panel beyond 2010-2016
- Extension to India, Africa, Southeast Asia

---

## 7. Writing Schedule (tentative)

| Section | Draft | Target date | Dependencies |
|---------|-------|-------------|--------------|
| Methods | First | After Phase 2 analysis complete | All data + analysis scripts |
| Results | First | 1 week after Methods | Finalised figures + statistics |
| Introduction | First | After Results draft | Literature review complete |
| Discussion | First | After Introduction draft | All other sections |
| Abstract | First | Last | Full draft complete |
| Full draft v1 | Assembly | ~2026-05-20 | All sections |
| Internal review | Peer-reviewer agent | ~2026-05-25 | Draft v1 |
| Revision + v2 | Final | ~2026-06-10 | Review feedback |
| Submission package | Cover letter + highlights | ~2026-06-25 | Draft v2 approved |

---

*Outline v3.0 -- 3-Finding structure*
*Manuscript Writer Agent*
*2026-03-21*
