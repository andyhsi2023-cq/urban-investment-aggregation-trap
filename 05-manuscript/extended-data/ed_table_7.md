# Extended Data Table 7 | Aggregation Trap theorem verification: cross-national and within-country tests

**Panel A. Cross-national verification (158 countries, housing-based MUQ)**

| Condition | Test | Result | Details |
|---|---|---|---|
| A1: Within-group decline | Spearman rho < 0 in all 4 income groups | **PASS** | Low: -0.150 (p = 0.002), LMI: -0.122 (p = 0.002), UMI: -0.099 (p = 0.003), High: -0.013 (p = 0.633) |
| A2: Compositional shift | Mass shifts toward higher-alpha groups | **PASS** | At u ~ 0.15: Low = 49%, High = 1%; at u ~ 0.85: Low = 0%, High = 83% |
| A3: Composition dominates within | \|Between\| > \|Within\| | **PASS** | \|0.114\| > \|0.076\|; ratio = 1.50x |
| **Verdict** | | **ALL SATISFIED** | Pooled rho = +0.038 despite all within-group rho < 0 |

**Panel B. Within-country verification (7 countries/regions)**

| Country | N obs | N regions | A1 (within decline) | A2 (comp. shift) | A3 (between > within) | All met? | Pooled rho |
|---|---:|---:|---|---|---|---|---:|
| China | 9,161 | 292 | PASS (4/4) | PASS (3/4) | FAIL | NO | -0.7712 |
| Japan | 2,256 | 47 | PASS (4/4) | FAIL (0/4) | FAIL | NO | -0.5846 |
| Korea | 592 | 17 | PASS (3/3) | FAIL (1/3) | FAIL | NO | -0.6175 |
| United States | 10,760 | 921 | FAIL (0/4) | PASS (3/4) | FAIL | NO | +0.2693 |
| Australia | 264 | 8 | FAIL (1/2) | PASS (2/2) | FAIL | NO | +0.0065 |
| South Africa | 270 | 9 | PASS (2/2) | PASS (2/2) | FAIL | NO | -0.1350 |
| Europe (NUTS-2) | 5,189 | 247 | FAIL (1/4) | FAIL (1/4) | FAIL | NO | +0.0730 |

**Panel C. Within/Between decomposition by country**

| Country | Pooled rho | Weighted within | Between component | Between/Within ratio |
|---|---:|---:|---:|---:|
| Cross-national (158 countries) | +0.038 | -0.076 | +0.114 | 1.50 |
| China | -0.771 | -0.772 | +0.001 | 0.001 |
| Japan | -0.585 | -0.592 | +0.008 | 0.013 |
| Korea | -0.618 | -0.623 | +0.006 | 0.009 |
| United States | +0.269 | +0.273 | -0.003 | 0.012 |
| Australia | +0.007 | +0.006 | +0.000 | 0.066 |
| South Africa | -0.135 | -0.135 | -0.000 | 0.003 |
| Europe (NUTS-2) | +0.073 | +0.074 | -0.001 | 0.007 |

**Panel D. Calibrated theorem parameters (cross-national, OLS with clustered SE)**

| Income Group | alpha_k | beta_k | SE(beta) | p(beta) | Spearman rho |
|---|---:|---:|---:|---:|---:|
| Low income | 7.095 | -8.013 | 4.084 | 0.050 | -0.150 |
| Lower-Middle income | 9.978 | -6.041 | 5.355 | 0.259 | -0.122 |
| Upper-Middle income | 10.034 | -3.771 | 2.131 | 0.077 | -0.099 |
| High income | 7.329 | +0.851 | 2.152 | 0.692 | -0.013 |

**Panel E. Monte Carlo theorem sharpness (two-group, 10,000 simulations)**

| Gap/gamma ratio | P(Paradox \| all within negative) |
|---:|---:|
| 0.00 | 0.000 |
| 0.25 | 0.002 |
| 0.50 | 0.196 |
| 0.75 | 0.974 |
| 1.00 | 1.000 |

---

**Notes.**
The Aggregation Trap theorem states that Simpson's Paradox arises necessarily when three conditions hold simultaneously: (A1) efficiency declines with urbanisation within every group; (A2) population composition shifts toward higher-baseline groups; (A3) the between-group composition effect exceeds the within-group decline. Cross-nationally, all three conditions are satisfied (Panel A), correctly predicting the observed positive pooled correlation despite uniformly negative within-group correlations. Within-country, condition A3 fails universally (Panel B): the between-region compositional effect is negligible relative to the dominant within-region trends. This is expected: within a single country, regions are more homogeneous than across income groups, so the "escalator" (compositional shift) is too weak to overcome the "treadmill" (within-group decline). The theorem's predictive power therefore operates at the cross-national level, where income-group heterogeneity is maximal. Monte Carlo validation (Panel E) confirms that the paradox transitions from impossible (Gap/gamma = 0) to certain (Gap/gamma >= 1.0) as the between-group efficiency gap grows relative to the common decline rate.
