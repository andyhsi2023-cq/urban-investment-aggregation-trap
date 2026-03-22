# Extended Data Table 1 | Simpson's Paradox complete statistics: Housing-based and GDP-based MUQ

**Panel A. Housing-based MUQ by income group and urbanisation stage**

| Income Group | Urbanisation Stage | N | MUQ Median | MUQ/CPR Median | Spearman rho | p-value |
|---|---|---:|---:|---:|---:|---:|
| Low income | S1: <30% | 258 | 4.709 | 2.39 | | |
| Low income | S2: 30--50% | 173 | 2.332 | 1.18 | | |
| Low income | S3: 50--70% | 12 | 3.755 | 0.87 | | |
| Low income | S4: >70% | 0 | -- | -- | | |
| **Low income** | **All** | **443** | | | **-0.150** | **0.002** |
| Lower middle income | S1: <30% | 142 | 9.879 | 2.50 | | |
| Lower middle income | S2: 30--50% | 301 | 7.163 | 2.07 | | |
| Lower middle income | S3: 50--70% | 129 | 8.188 | 2.09 | | |
| Lower middle income | S4: >70% | 64 | 1.149 | 1.54 | | |
| **Lower middle income** | **All** | **636** | | | **-0.122** | **0.002** |
| Upper middle income | S1: <30% | 95 | 9.085 | 2.44 | | |
| Upper middle income | S2: 30--50% | 247 | 8.887 | 2.43 | | |
| Upper middle income | S3: 50--70% | 379 | 7.836 | 2.26 | | |
| Upper middle income | S4: >70% | 198 | 7.477 | 2.23 | | |
| **Upper middle income** | **All** | **919** | | | **-0.099** | **0.003** |
| High income | S1: <30% | 2 | 1.111 | 0.45 | | |
| High income | S2: 30--50% | 85 | 6.011 | 2.51 | | |
| High income | S3: 50--70% | 408 | 8.021 | 2.44 | | |
| High income | S4: >70% | 836 | 8.144 | 3.67 | | |
| **High income** | **All** | **1,331** | | | **-0.013** | **0.633** |

**Panel B. GDP-based MUQ by income group (Phase 0 Kill Test)**

| Income Group | Method | N | Countries | Spearman rho | p-value |
|---|---|---:|---:|---:|---:|
| Low income | WDI (constant 2015 USD) | 1,284 | 29 | -0.1160 | 0.0000 |
| Lower middle income | WDI | 1,681 | 37 | -0.1306 | 0.0000 |
| Upper middle income | WDI | 1,834 | 40 | -0.2475 | 0.0000 |
| High income | WDI | 2,494 | 51 | -0.0351 | 0.0795 |
| **Pooled** | **WDI** | **7,293** | **157** | **-0.2104** | **0.0000** |
| Low income | PWT (rgdpna) | 1,168 | 28 | -0.1248 | 0.0000 |
| Lower middle income | PWT | 1,425 | 33 | -0.2038 | 0.0000 |
| Upper middle income | PWT | 1,566 | 36 | -0.2228 | 0.0000 |
| High income | PWT | 2,198 | 48 | -0.0148 | 0.4876 |
| **Pooled** | **PWT** | **6,357** | **145** | **-0.2358** | **0.0000** |

**Panel C. Within/Between decomposition**

| Component | Housing-based rho | GDP-based rho (WDI) |
|---|---:|---:|
| Pooled (all countries) | +0.038 (p = 0.030, N = 3,329) | -0.2104 (p = 0.0000, N = 7,293) |
| Weighted within-group | -0.076 | All 4 groups negative |
| Between-group component | +0.114 | Composition effect |

**Panel D. Block bootstrap and leave-one-out robustness**

| Test | Housing-based | GDP-based |
|---|---|---|
| UMI LOO: all iterations negative | 47/47 (100%) | 40/40 (100%) |
| UMI LOO: significant at p < 0.05 | 46/47 (97.9%) | 40/40 (100%) |
| UMI LOO: rho range | [-0.126, -0.064] | All negative and significant |

**Panel E. Robustness to excluding large countries**

| Specification | Spearman rho | p-value | N |
|---|---:|---:|---:|
| Pooled, excl. China | +0.042 | 0.017 | 3,286 |
| UMI group, excl. China | -0.095 | 0.005 | 876 |
| UMI group, excl. Brazil | -0.105 | 0.002 | 894 |
| UMI group, excl. Mexico | -0.125 | <0.001 | 890 |
| UMI group, excl. Turkey | -0.098 | 0.003 | 897 |
| UMI group, excl. Russia | -0.099 | 0.003 | 903 |
| UMI group, excl. all 5 | -0.132 | <0.001 | 784 |

---

**Notes.**
Housing-based MUQ is measured in constant 2015 USD using PWT 10.01 capital stock (rnna) and GDP deflator (158 countries, 1960--2019). GDP-based MUQ uses WDI constant 2015 USD GDP and PWT rgdpna as alternative measures. Urbanisation stages follow World Bank thresholds: S1 (<30%), S2 (30--50%), S3 (50--70%), S4 (>70%). Income groups use World Bank classification. MUQ/CPR = MUQ normalised by country-period mean. Spearman rho tests the monotonic association between MUQ and urbanisation rate within each group. The within/between decomposition shows that the between-group compositional shift drives the positive pooled correlation for housing-based MUQ, while within each income group MUQ declines with urbanisation. The GDP-based MUQ shows consistent within-group decline across both WDI and PWT methods, confirming robustness to the choice of capital stock measure. Leave-one-out (LOO) robustness: for UMI group, removing any single country preserves the negative within-group correlation (Housing: 47/47 negative, 46/47 significant; GDP: 40/40 negative, 40/40 significant).
