# Data Availability Statement

## For Nature Submission

### Statement (to be included in the manuscript)

The data that support the findings of this study are available from the following sources. **Public international datasets** are freely accessible: World Bank World Development Indicators (https://databank.worldbank.org/source/world-development-indicators), Penn World Table version 10.01 (https://www.rug.nl/ggdc/productivity/pwt/), Bank for International Settlements residential property price statistics (https://www.bis.org/statistics/pp.htm), and United Nations World Population Prospects (https://population.un.org/wpp/). **Chinese national statistics** are available from the National Bureau of Statistics of China (NBS) annual statistical communiques (https://www.stats.gov.cn/) and the Ministry of Finance fiscal revenue and expenditure reports (https://www.mof.gov.cn/). **Chinese city-level panel data** were compiled from the *China City Statistical Yearbook* (2001--2024 editions), published by NBS and available through the China National Knowledge Infrastructure (CNKI, https://www.cnki.net/) and university libraries. Supplementary city-level housing transaction data were obtained from commercial platforms (58.com/Anjuke) and are subject to the data providers' terms of use; aggregated indicators derived from these data are included in the supplementary materials. All **derived indicators** constructed in this study---including Urban Q, the Overcapacity Ratio (OCR), and the Urban Capital Imbalance index (UCI)---together with the analysis code, are available at [GitHub repository URL to be inserted upon acceptance]. Source data for all figures are provided with this paper.

---

## Detailed Data Inventory

### 1. Public International Datasets (openly accessible)

| Dataset | Provider | Coverage | Access URL | Files in This Project |
|---------|----------|----------|------------|----------------------|
| World Development Indicators | World Bank | 217 countries, 1960--2023 | https://databank.worldbank.org/source/world-development-indicators | `02-data/raw/world_bank_all_countries.csv` |
| Penn World Table 10.01 | Groningen Growth and Development Centre | 183 countries, 1950--2019 | https://www.rug.nl/ggdc/productivity/pwt/ | `02-data/raw/penn_world_table.csv` |
| Residential Property Prices | Bank for International Settlements (BIS) | 51 economies, 1956--2025 | https://www.bis.org/statistics/pp.htm | `02-data/raw/bis_property_prices.csv` |
| World Population Prospects | United Nations DESA | 200+ countries, 1950--2100 | https://population.un.org/wpp/ | `02-data/raw/un_population.csv` |

**Key indicators extracted**: GDP (constant 2015 US$), gross capital formation (% of GDP), urban population (%), total population, human capital index, capital stock at current PPPs, real GDP at constant national prices, residential property price indices.

### 2. Chinese Government Statistics (publicly available)

| Dataset | Provider | Coverage | Access |
|---------|----------|----------|--------|
| Annual Statistical Communiques | NBS | 1978--2024 | https://www.stats.gov.cn/sj/tjgb/ |
| China Statistical Yearbook | NBS | Annual editions | https://www.stats.gov.cn/sj/ndsj/ |
| China City Statistical Yearbook | NBS | 2001--2024 editions | University libraries / CNKI |
| Fiscal Revenue & Expenditure Reports | Ministry of Finance | 1999--2024 | https://www.mof.gov.cn/ |

**Key indicators**: GDP and industrial structure (Table 3-1), population and urbanization rate (Table 2-1), fixed asset investment (Table 5-1), real estate development investment (Table 5-35), commercial housing sales (Table 5-40), housing completions (Table 5-33), land transfer revenue.

**Note on 2024 data**: Values for 2024 are preliminary estimates based on NBS releases as of January 2025. These will be updated upon publication of the official 2024 Statistical Communique.

### 3. Commercial and Restricted-Access Data

| Dataset | Provider | Coverage | Access Pathway |
|---------|----------|----------|----------------|
| China City Database | Marker Database (马克数据网) | 275 prefecture-level cities, 2000--2023 | https://www.marcdata.cn/ (subscription required) |
| Housing transaction prices | 58.com / Anjuke (安居客) | Major cities, 2010--2024 | https://www.anjuke.com/ (commercial platform; terms of use apply) |

**Replication note**: Researchers seeking to replicate the city-level analysis may obtain equivalent data from the *China City Statistical Yearbook* (available at Chinese university libraries and CNKI) or the CEIC China Premium Database.

### 4. Derived Datasets (to be deposited upon publication)

The following derived datasets, constructed from the sources above, will be deposited in a public repository (Figshare or Zenodo) upon acceptance:

| Derived Dataset | Description | Key Variables | File |
|-----------------|-------------|---------------|------|
| Global Urban Q Panel | 158-country annual panel | `urban_q`, `delta_V_ratio`, `ci_gdp_ratio`, `urban_pct` | `02-data/processed/global_q_revised_panel.csv` |
| Global K*/OCR/UCI Panel | Cross-country overcapacity and imbalance indicators | `Q`, `OCR`, `UCI`, `kstar`, `dV_V` | `02-data/processed/global_kstar_m2_panel.csv` |
| China National Q Series | National-level Urban Q time series (1990--2024) | `Q_V1K2`, `V_t`, `K_t`, `OCR`, `UCI` | `03-analysis/models/china_q_adjusted.csv` |
| China City Panel | 275 prefecture-level cities | `urban_q`, `ocr`, `uci`, city-level controls | `02-data/processed/china_city_ocr_uci.csv` |
| Monte Carlo CI | Uncertainty quantification for China Q | `Q_mean`, `Q_lo`, `Q_hi` | `03-analysis/models/monte_carlo_q_ci.csv` |

### 5. Code Availability

All analysis scripts (Python) are available at [GitHub URL]. The repository includes:
- `requirements.txt` --- Python dependencies with pinned versions
- `master_pipeline.py` --- Reproducible analysis pipeline with dependency checks
- `03-analysis/scripts/` --- All analysis scripts (numbered 01--70)

The pipeline can be executed with:
```bash
pip install -r requirements.txt
python master_pipeline.py
```

---

## Formatting Notes for Submission

- The **Data Availability Statement** (first section above) should be placed after the Methods section, before the References, per *Nature* formatting guidelines.
- The **Code Availability** statement should be a separate paragraph immediately following the Data Availability Statement.
- The detailed inventory (sections 1--5) is for internal reference and reviewer response; it should not be included in the main manuscript but may be provided as a Supplementary Note if requested.
