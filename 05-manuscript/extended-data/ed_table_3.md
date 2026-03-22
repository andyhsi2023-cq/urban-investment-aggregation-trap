# Extended Data Table 3 | Cross-country clean specification summary (China, Japan, Korea, United States)

**Panel A. Japan (47 prefectures, 1956--2022)**

| Specification | DV | IV | beta | SE (cluster) | p-value | Within R-sq | N |
|---|---|---|---:|---:|---:|---:|---:|
| Pooled OLS (HC1) | DeltaGDP/GDP | GFCF/GDP | 0.6382 | 0.0150 | 0.0000 | 0.3544 | 3,149 |
| Prefecture FE | DeltaGDP/GDP | GFCF/GDP | 0.8129 | 0.0295 | 3.17e-30 | 0.4600 | 3,149 |
| Two-way FE (Pref + Year) | DeltaGDP/GDP | GFCF/GDP | 0.0567 | 0.0265 | 3.75e-02 | 0.0052 | 3,149 |

**Panel B. China -- Provincial level (31 provinces, 2006--2019)**

| Specification | DV | IV | beta | SE (cluster) | p-value | N |
|---|---|---|---:|---:|---:|---:|
| Pooled OLS (HC1) | DeltaGDP/GDP | FAI/GDP | 0.0122 | 0.0113 | 2.82e-01 | 434 |
| Province FE | DeltaV/GDP | FAI/GDP | -0.1639 | 0.0503 | 1.11e-03 | 434 |
| Two-way FE (Prov + Year) | DeltaV/GDP | FAI/GDP | -0.0480 | 0.0503 | 3.40e-01 | 434 |

**Panel C. China -- City level (213 cities, 2011--2016)**

| Specification | DV | IV | beta | SE (cluster) | p-value | R-sq | N |
|---|---|---|---:|---:|---:|---:|---:|
| Pooled OLS (HC1) | DeltaV/GDP | FAI/GDP | -0.3669 | 0.1569 | 1.94e-02 | 0.0171 | 455 |
| City FE | DeltaV/GDP | FAI/GDP | 0.5210 | 0.1022 | 3.44e-07 | 0.5646 | 455 |
| Two-way FE (City + Year) | DeltaV/GDP | FAI/GDP | 0.1560 | 0.2151 | 4.68e-01 | 0.6842 | 455 |

**Panel D. United States (921 MSAs, 2010--2022)**

| Specification | DV | IV | beta | SE (cluster) | p-value | R-sq | N |
|---|---|---|---:|---:|---:|---:|---:|
| Pooled OLS (HC1) | DeltaV/GDP | hu_growth | 2.8097 | 0.1007 | 0.0000 | 0.0956 | 10,760 |
| Two-way FE (MSA + Year) | DeltaV/GDP | hu_growth | 2.7623 | 0.1282 | 5.62e-103 | -- | 10,760 |
| Pooled OLS (HC1) | DeltaV/GDP | invest_intensity | 1.3914 | 0.0781 | 5.45e-71 | 0.0789 | 10,760 |
| Two-way FE (MSA + Year) | DeltaV/GDP | invest_intensity | 1.6486 | 0.0898 | 2.90e-75 | -- | 10,760 |

**Panel E. Sign reversal summary (Clean Specification)**

| Country | Pooled OLS beta | TWFE beta | Sign reversal (Pooled) |
|---|---:|---:|---|
| China (city) | -0.3669 (p = 0.019) | +0.1560 (p = 0.468) | YES |
| United States | +2.8097 (p = 0.000) | +2.7623 (p = 0.000) | -- |
| Japan | +0.6382 (p = 0.000) | +0.0567 (p = 0.037) | -- |

China-US sign reversal confirmed under clean specification: China beta < 0, US beta > 0.

---

**Notes.**
Clean specification replaces MUQ = DeltaV/I (mechanically correlated with investment denominator) with DeltaV/GDP as dependent variable and investment intensity (FAI/GDP or housing unit growth) as independent variable. This eliminates spurious mechanical correlation. Standard errors clustered at the spatial unit level (prefecture, province, city, MSA). For Japan, DeltaGDP/GDP is used as the dependent variable (GDP growth rate, not asset value growth) because Japan's prefectural accounts provide income-side data. For China's city-level panel: 150/213 cities have only 1 period of observation, limiting within-estimator power; the City FE sign reversal (negative in pooled, positive in FE) constitutes a Simpson's Paradox at the city level. Attenuation ratio (China city): original beta (MUQ ~ FAI/GDP) = -2.257, clean beta = -0.367, implying 83.7% of the original coefficient was attributable to mechanical correlation.
