# Extended Data Table 9 | Three Red Lines DID regression complete results with parallel trends and placebo tests

**Panel A. Main DID specifications**

| | (1) | (2) | (3) | (4) | (5) | (6) | (7) |
|---|---|---|---|---|---|---|---|
| | Base OLS | Prov FE + Ctrl | Prov FE + Ctrl | TWFE | TWFE | Binary DID | Binary DID |
| **Dependent variable** | **ln(HP)** | **ln(HP)** | **Urban Q** | **ln(HP)** | **Urban Q** | **ln(HP)** | **Urban Q** |
| | | | | | | | |
| Post x RE_dep_z | -0.0204\* | -0.0059 | -0.0632\*\* | -0.0217\*\* | -0.0890\*\*\* | | |
| | (0.0098) | (0.0146) | (0.0233) | (0.0075) | (0.0220) | | |
| | [p = 0.037] | [p = 0.684] | [p = 0.007] | [p = 0.004] | [p < 0.001] | | |
| | [-0.040, -0.001] | [-0.035, 0.023] | [-0.109, -0.018] | [-0.036, -0.007] | [-0.132, -0.046] | | |
| Post x High_dep | | | | | | -0.0238 | -0.0941\*\* |
| | | | | | | (0.0211) | (0.0354) |
| | | | | | | [p = 0.260] | [p = 0.008] |
| | | | | | | [-0.065, 0.018] | [-0.164, -0.025] |
| RE_dep_z | 0.2122\*\*\* | 0.0426 | 0.1008 | -- | -- | | |
| | (0.0263) | (0.0246) | (0.0683) | | | | |
| GDP growth | | 0.0710 | 0.6214\*\*\* | -0.1155\*\* | 0.1123\* | Yes | Yes |
| Fiscal self-sufficiency | | 0.8207\*\*\* | 0.0390 | 0.1293 | -0.1254 | Yes | Yes |
| Population growth | | 6.7523\*\*\* | 11.0256\*\* | -0.5080 | 0.1810 | Yes | Yes |
| Debt/GDP | | 0.1905\*\*\* | 0.0717 | 0.0047 | -0.0384 | Yes | Yes |
| | | | | | | | |
| Province FE | No | Yes | Yes | -- | -- | Yes | Yes |
| City FE | No | No | No | Yes | Yes | No | No |
| Year FE | No | Yes | Yes | Yes | Yes | Yes | Yes |
| Controls | No | Yes | Yes | Yes | Yes | Yes | Yes |
| N | 1,691 | 1,241 | 1,233 | 1,233 | 1,233 | 1,241 | 1,233 |
| R-squared | 0.177 | 0.765 | 0.518 | 0.032 | 0.130 | 0.767 | 0.519 |
| Clustering | None | Province | Province | City | City | Province | Province |

**Panel B. Dose-response analysis (Urban Q, reference = Q1 lowest RE dependence)**

| Quartile x Post | Coefficient | SE | p-value | 95% CI |
|---|---:|---:|---:|---|
| Q2 x Post | -0.0451 | 0.0403 | 0.263 | [-0.124, 0.034] |
| Q3 x Post | -0.0952 | 0.0396 | 0.016 | [-0.173, -0.018] |
| Q4 x Post | -0.1362 | 0.0483 | 0.005 | [-0.231, -0.042] |
| Linear trend (Q4-Q2) | F = 3.017 | | 0.082 | |

**Panel C. Parallel trends test**

| DV | Joint F-test (pre-treatment interactions) | p-value | Assessment |
|---|---:|---:|---|
| ln(HP) | F = 3.07 | 0.080 | Marginally significant -- caution warranted |
| Urban Q | F = 2.82 | 0.093 | Marginally significant -- caution warranted |

Pre-treatment interaction coefficients (2017, 2018 relative to 2019 baseline) are jointly tested. Both are marginally significant at the 10% level, indicating imperfect parallel trends. This limits causal interpretation.

**Panel D. Placebo test**

| DV | Pseudo-treatment year | Window | Coefficient | p-value | Assessment |
|---|---:|---|---:|---:|---|
| ln(HP) | 2016 | 2014--2015 vs 2017--2018 | 0.067 | <0.001 | **FAILS**: significant pre-existing differential trend |
| Urban Q | 2016 | 2014--2015 vs 2017--2018 | Not reported | | |

**Panel E. Diagnostic summary and interpretive caveats**

| Diagnostic | ln(HP) | Urban Q |
|---|---|---|
| Main effect (TWFE) | Significant (p = 0.004) | Significant (p < 0.001) |
| Parallel trends | Marginal (p = 0.080) | Marginal (p = 0.093) |
| Placebo test | FAILS (p < 0.001) | Not reported |
| Dose-response monotonicity | -- | Monotonic (Q2 < Q3 < Q4) |
| Causal interpretation | Conservative | More credible but with caveats |

---

**Notes.**
Sample: 297 Chinese cities, 2017--2023 (excluding 2020 as transition year). Treatment intensity RE_dep_z is the standardised real estate dependence ratio (RE investment / GDP, averaged 2017--2019, z-scored). Post = 1 for 2021--2023 (after Three Red Lines policy, August 2020). Models (1)--(3) use province fixed effects; models (4)--(5) use two-way (city + year) fixed effects. Models (6)--(7) use binary treatment (above/below median RE dependence). Controls: GDP growth rate, fiscal self-sufficiency ratio, population growth rate, local government debt/GDP ratio. Standard errors in parentheses (clustered as indicated); exact p-values in brackets; 95% confidence intervals below. Significance: \* p < 0.05, \*\* p < 0.01, \*\*\* p < 0.001.

**Interpretive caveats.** (1) The parallel trends test is marginally significant for both outcomes, meaning pre-treatment differential trends cannot be fully ruled out. (2) The placebo test for ln(HP) is significantly positive, suggesting that house prices in high-RE-dependence cities were already diverging before treatment -- the DID estimate for ln(HP) should therefore be interpreted as an upper bound on the policy effect. (3) The Urban Q results are more robust because Q incorporates both price and stock information, reducing sensitivity to pre-existing price trends. (4) The dose-response pattern (monotonically increasing effect across quartiles Q2-Q4) provides additional support for a genuine treatment gradient, even if the level effect is confounded. (5) The Three Red Lines policy was announced and implemented rapidly, but anticipation effects and concurrent macroeconomic shocks (COVID-19 aftermath) cannot be fully separated from the policy effect.
