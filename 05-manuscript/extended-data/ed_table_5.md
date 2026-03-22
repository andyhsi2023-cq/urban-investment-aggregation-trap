# Extended Data Table 5 | City-level regression complete table (China 213 cities and US 921 MSAs)

**Panel A. China city-level regressions (213 cities, 2011--2016)**

| Row | Specification | DV | IV | beta | SE | p-value | 95% CI | R-sq | N |
|---|---|---|---|---:|---:|---:|---|---:|---:|
| (a) | Original Pooled OLS | MUQ | FAI/GDP | -2.2571 | 0.4198 | 7.58e-08 | [-3.080, -1.434] | 0.123 | 455 |
| (b) | Clean Pooled OLS | DeltaV/GDP | FAI/GDP | -0.3669 | 0.1569 | 1.94e-02 | [-0.674, -0.059] | 0.017 | 455 |
| (c) | City FE (cluster) | DeltaV/GDP | FAI/GDP | +0.5210 | 0.1022 | 3.44e-07 | [+0.321, +0.721] | 0.565 | 455 |
| (d) | TWFE City+Year (cluster) | DeltaV/GDP | FAI/GDP | +0.1560 | 0.2151 | 4.68e-01 | [-0.266, +0.578] | 0.684 | 455 |
| (e1) | Quantile tau = 0.10 | DeltaV/GDP | FAI/GDP | -0.0190 | 0.1592 | 9.05e-01 | [-0.332, +0.294] | -- | 455 |
| (e2) | Quantile tau = 0.25 | DeltaV/GDP | FAI/GDP | +0.0256 | 0.0708 | 7.18e-01 | [-0.114, +0.165] | -- | 455 |
| (e3) | Quantile tau = 0.50 | DeltaV/GDP | FAI/GDP | -0.0464 | 0.0737 | 5.29e-01 | [-0.191, +0.099] | -- | 455 |
| (e4) | Quantile tau = 0.75 | DeltaV/GDP | FAI/GDP | -0.2715 | 0.1199 | 2.40e-02 | [-0.507, -0.036] | -- | 455 |
| (e5) | Quantile tau = 0.90 | DeltaV/GDP | FAI/GDP | -0.8908 | 0.3672 | 1.57e-02 | [-1.613, -0.169] | -- | 455 |

**Panel B. United States MSA-level regressions (921 MSAs, 2010--2022)**

| Row | Specification | DV | IV | beta | SE | p-value | 95% CI | R-sq | N |
|---|---|---|---|---:|---:|---:|---|---:|---:|
| (f) | Original Pooled OLS | MUQ | hu_growth | -638.49 | 34.97 | 1.78e-74 | [-707.0, -569.9] | 0.030 | 8,607 |
| (g) | Clean Pooled OLS | DeltaV/GDP | hu_growth | +2.8097 | 0.1007 | 0.0000 | [+2.612, +3.007] | 0.096 | 10,760 |
| (g2) | Clean Pooled OLS | DeltaV/GDP | invest_int | +1.3914 | 0.0781 | 5.45e-71 | [+1.238, +1.545] | 0.079 | 10,760 |
| (h) | TWFE MSA+Year (cluster) | DeltaV/GDP | hu_growth | +2.7623 | 0.1282 | 5.62e-103 | [+2.511, +3.014] | -- | 10,760 |
| (h2) | TWFE MSA+Year (cluster) | DeltaV/GDP | invest_int | +1.6486 | 0.0898 | 2.90e-75 | [+1.473, +1.825] | -- | 10,760 |

**Panel C. Mechanical correlation quantification**

| Metric | Value | Interpretation |
|---|---:|---|
| Original beta (MUQ ~ FAI/GDP) | -2.2571 | Contains mechanical + true effect |
| Clean beta (DeltaV/GDP ~ FAI/GDP) | -0.3669 | True effect only |
| Attenuation ratio | 83.7% | Share attributable to mechanical correlation |
| City FE beta | +0.5210 | Sign reversal: within-city effect is positive |
| TWFE beta | +0.1560 | Not significant after absorbing city + year FE |
| Total attenuation (Original to TWFE) | 106.9% | >100% implies full sign reversal |

**Panel D. Simpson's Paradox at city level (China)**

| Dimension | Correlation | Direction |
|---|---:|---|
| Between cities (city means) | -0.0886 (p = 0.198) | Negative |
| Within cities (demeaned) | +0.0653 (p = 0.164) | Positive |
| Pooled OLS | -0.3669 (p = 0.019) | Negative |

Panel structure diagnostic: 150/213 cities (70.4%) have only 1 period of observation. Cities with >= 3 periods: 61/213 (28.6%).

---

**Notes.**
Panel A: China city-level MUQ reconstructed from urban asset value (V) and fixed-asset investment (FAI). Original specification (row a) uses MUQ = DeltaV/FAI as dependent variable, which is mechanically correlated with FAI/GDP through shared denominators. Clean specification (rows b--e) uses DeltaV/GDP to eliminate this mechanical correlation. The attenuation ratio of 83.7% indicates that the vast majority of the original negative coefficient was an artefact of ratio construction. The sign reversal from pooled OLS (negative) to City FE (positive) constitutes a Simpson's Paradox: cities with chronically high FAI/GDP have lower DeltaV/GDP (between-city, negative), but within the same city, years with higher FAI/GDP tend to have higher DeltaV/GDP (within-city, positive). Panel B: US MSA-level data from Zillow (house prices) and Census (housing units). The positive and robust coefficient across all specifications confirms that housing investment generates commensurate value in the US context. Quantile regression (Panel A, rows e1--e5) shows the negative effect in China intensifies at higher quantiles (tau = 0.75, 0.90), suggesting overinvestment damage is concentrated in cities with already higher DeltaV/GDP.
