# Urban Investment Efficiency Declines Worldwide

**Evidence from 1,567 cities and regions**

Hongyang Xi | Chongqing Survey Institute Co., Ltd., Chongqing, China

[![SSRN](https://img.shields.io/badge/SSRN-6453159-blue)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6453159)

---

## Summary

Aggregate statistics suggest returns on urban investment remain stable as economies urbanise. This stability is a Simpson's paradox. We construct a marginal Urban Q (MUQ) across 157 countries and 1,567 subnational regions spanning eight countries across five continents (30,098 observations). Within every developing-economy income group, returns decline with urbanisation, but compositional shifts conceal the decline. We prove this aggregation trap is a mathematical necessity under three empirically verified conditions.

## Data

| Source | Coverage | Directory |
|--------|----------|-----------|
| World Bank WDI | 157 countries, 1960-2023 | `02-data/raw/` |
| Penn World Table 10.01 | 183 countries, 1950-2019 | `02-data/raw/` |
| Japan Cabinet Office SNA | 47 prefectures, 1955-2022 | `02-data/raw/` |
| Bank of Korea ECOS | 17 metro/provinces, 1985-2022 | `02-data/raw/` |
| Eurostat | 265 NUTS-2 regions, 2000-2024 | `02-data/raw/` |
| ABS (Australia) | 8 states, 1990-2023 | `02-data/raw/` |
| Stats SA (South Africa) | 9 provinces, 1993-2023 | `02-data/raw/` |
| US Census + BEA | 921 MSAs, 2010-2022 | `02-data/raw/` |
| China NBS | 275 cities + 31 provinces | `02-data/raw/` |

## Repository Structure

```
02-data/
  raw/              # Original data files
  processed/        # Cleaned panels (unified_regional_panel.csv)
03-analysis/
  scripts/          # All Python analysis scripts
  models/           # Statistical output and reports
04-figures/
  final/            # Publication-quality figures
  source-data/      # Figure source data
05-manuscript/
  drafts/           # Manuscript (Markdown)
  extended-data/    # Extended Data figures and tables
```

## Requirements

Python 3.9+ with: numpy, pandas, scipy, statsmodels, matplotlib, seaborn

## Citation

Xi, H. (2026). Urban investment efficiency declines worldwide: evidence from 1,567 cities and regions. SSRN preprint. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6453159

## License

MIT
