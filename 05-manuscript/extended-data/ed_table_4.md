# Extended Data Table 4 | SUR Delta-beta year-by-year estimates (China vs United States, 2010--2019)

**Panel A. Annual Delta-beta and decomposition**

| Year | Delta-beta | SE | t | p-value | Delta(beta_A) | Delta(beta_P) |
|---:|---:|---:|---:|---:|---:|---:|
| 2010 | -0.1377 | 0.0540 | -2.548 | 0.0108 | -0.2482 | +0.1105 |
| 2011 | -0.1124 | 0.0545 | -2.064 | 0.0390 | -0.2454 | +0.1330 |
| 2012 | -0.0868 | 0.0551 | -1.576 | 0.1150 | -0.2426 | +0.1558 |
| 2013 | -0.0494 | 0.0560 | -0.882 | 0.3778 | -0.2355 | +0.1861 |
| 2014 | -0.0349 | 0.0568 | -0.614 | 0.5391 | -0.2308 | +0.1960 |
| 2015 | -0.0219 | 0.0571 | -0.384 | 0.7010 | -0.2275 | +0.2055 |
| 2016 | -0.0121 | 0.0574 | -0.211 | 0.8329 | -0.2227 | +0.2106 |
| 2017 | -0.0037 | 0.0575 | -0.064 | 0.9486 | -0.2180 | +0.2143 |
| 2018 | +0.0040 | 0.0578 | +0.070 | 0.9443 | -0.2161 | +0.2201 |
| 2019 | +0.0085 | 0.0581 | +0.146 | 0.8840 | -0.2136 | +0.2221 |
| **Mean** | **-0.0446** | | | | **-0.2300** | **+0.1854** |
| **SD** | **0.0512** | | | | **0.0125** | **0.0399** |

Significant years (p < 0.05): 2/10 (2010, 2011).

**Panel B. Decomposition interpretation**

| Component | Pooled estimate | Interpretation |
|---|---:|---|
| Delta-beta(total) | -0.0746 | CN beta_V - US beta_V (pooled OLS) |
| Delta-beta(mechanical) | 0.0000 | Cancels exactly (1 - 1 = 0) |
| Delta-beta(economic) | -0.0746 | 100% economic signal |
| Delta(beta_A) | -0.2314 | Area scaling: CN more negative (crowding) |
| Delta(beta_P) | +0.1568 | Price scaling: CN stronger agglomeration premium |
| Area contribution | 310.2% | Dominates total Delta-beta |
| Price contribution | -210.2% | Partially offsets area effect |

**Panel C. Underlying country-level SUR estimates (pooled OLS with year FE, clustered SE)**

| Country | beta_V | beta_A | beta_P | Econ signal | Mechanical % | N |
|---|---:|---:|---:|---:|---:|---:|
| China (275 cities, 2005--2019) | 1.0567 | -0.2563 | +0.3129 | +0.0567 | 94.6% | 4,125 |
| United States (921 MSAs, 2010--2022) | 1.1313 | -0.0249 | +0.1561 | +0.1313 | 88.4% | 11,681 |

**Panel D. Bootstrap validation (2019 cross-section, 2,000 resamples)**

| Statistic | China beta_V | China econ | US beta_V | US econ | Delta-beta |
|---|---:|---:|---:|---:|---:|
| Point estimate | 1.1352 | 0.1352 | 1.1267 | 0.1267 | +0.0085 |
| Bootstrap mean | 1.1343 | 0.1362 | 1.1269 | 0.1264 | +0.0074 |
| Bootstrap 95% CI | [1.004, 1.256] | [0.028, 0.238] | [1.104, 1.150] | [0.105, 0.148] | [-0.124, 0.129] |

---

**Notes.**
SUR (Seemingly Unrelated Regression) estimates two independent equations per country-year: ln(PCA) ~ ln(Pop) and ln(Price) ~ ln(Pop), where PCA = per capita area (China) or per capita housing units (US). The identity ln(V) = ln(Pop) + ln(PCA) + ln(Price) implies beta_V = 1 + beta_A + beta_P deterministically; hence beta_V need not be estimated separately. The mechanical component (= 1) cancels in the cross-country difference: Delta-beta = (1 + econ_CN) - (1 + econ_US) = econ_CN - econ_US. Delta(beta_A) = beta_A(CN) - beta_A(US) captures the difference in area scaling (crowding effect). Delta(beta_P) = beta_P(CN) - beta_P(US) captures the difference in price scaling (agglomeration premium). The convergence of Delta-beta toward zero over 2010--2019 reflects China's rising price premium (beta_P increasing) partially closing the gap with the US.
