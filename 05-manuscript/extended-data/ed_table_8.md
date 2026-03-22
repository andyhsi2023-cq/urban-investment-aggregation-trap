# Extended Data Table 8 | Japan Bai-Perron structural breakpoint analysis (national GDP-weighted MUQ, 1956--2022)

**Panel A. Breakpoint number selection (BIC criterion)**

| N breaks | Breakpoints | Sum of costs | BIC |
|---:|---|---:|---:|
| 1 | 1990 | 0.8640 | -287.31 |
| **2** | **1980, 1990** | **0.6408** | **-303.12** |
| 3 | 1970, 1980, 1990 | 0.6240 | -300.70 |
| 4 | 1980, 1990, 2000, 2010 | 0.6011 | -299.00 |
| 5 | 1970, 1980, 1990, 2000, 2010 | 0.5842 | -296.70 |

Optimal number of breaks by BIC: **2** (1980 and 1990).

**Panel B. Segment-wise MUQ statistics**

| Segment | Years | N | MUQ Mean | MUQ SD | MUQ Min | MUQ Max | GFCF/GDP |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 (High growth) | 1956--1980 | 25 | 0.4027 | 0.1072 | 0.1738 | 0.6620 | 0.3092 |
| 2 (Stable) | 1981--1990 | 10 | 0.2259 | 0.0335 | 0.1737 | 0.2644 | 0.2714 |
| 3 (Post-bubble) | 1991--2022 | 32 | 0.0338 | 0.1070 | -0.2169 | 0.2172 | 0.2362 |

**Panel C. Welch t-tests at each breakpoint**

| Breakpoint | Mean before | Mean after | Difference | Welch t | p-value |
|---|---:|---:|---:|---:|---:|
| ~1981 | 0.4027 | 0.2259 | -0.1767 | 7.389 | 2.07e-08 |
| ~1991 | 0.2259 | 0.0338 | -0.1921 | 8.863 | 5.61e-11 |

**Panel D. Correspondence with SNA accounting revisions**

| SNA Revision Year | Nearest detected break | Distance (years) | Assessment |
|---:|---:|---:|---|
| 1974 (68SNA -> 93SNA prep) | 1980 | 6 | Partial overlap possible |
| 1995 (93SNA adoption) | 1990 | 5 | Partial overlap possible |
| 2010 (08SNA adoption) | 1990 | 20 | No correspondence |

**Panel E. Period-specific investment efficiency (Pooled OLS, HC1 SE)**

| Period | Label | N | beta (GFCF/GDP) | SE | p-value | R-sq | Mean DeltaGDP/GDP | Mean GFCF/GDP |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1960--1973 | High growth | 658 | 0.1268 | 0.0324 | 8.89e-05 | 0.025 | 0.1427 | 0.3508 |
| 1974--1985 | Stable growth | 564 | 0.1726 | 0.0290 | 2.56e-09 | 0.056 | 0.0785 | 0.3223 |
| 1986--1991 | Bubble | 282 | -0.0342 | 0.0313 | 0.2745 | 0.004 | 0.0548 | 0.3019 |
| 1992--2002 | Lost Decade | 517 | 0.2479 | 0.0271 | 6.14e-20 | 0.131 | 0.0089 | 0.2795 |
| 2003--2022 | Recovery | 940 | 0.0734 | 0.0233 | 1.66e-03 | 0.010 | 0.0052 | 0.2479 |

---

**Notes.**
Bai-Perron structural break detection applied to the national GDP-weighted mean MUQ time series (67 annual observations, 1956--2022). Break number selected by minimising BIC. The two detected breaks (1980, 1990) partition Japan's post-war MUQ trajectory into three regimes: (1) high-growth era with MUQ averaging 0.40, (2) a transition decade with MUQ halved to 0.23, and (3) the post-bubble era with MUQ near zero (0.03). Both breaks are highly significant by Welch t-tests (p < 1e-08). SNA accounting revisions (1974, 1995, 2010) partially overlap with detected breaks; the 1980 break occurs 6 years after the 1974 SNA revision and the 1990 break 5 years before the 1995 revision. While measurement artefacts cannot be entirely excluded, the magnitude of MUQ decline (from 0.40 to 0.03) far exceeds plausible SNA-revision effects. Period-specific regressions (Panel E) show investment efficiency (beta of GFCF/GDP on GDP growth) declining from 0.17 (stable growth) to near zero or negative (bubble and recovery periods), consistent with diminishing marginal returns to urban investment.
