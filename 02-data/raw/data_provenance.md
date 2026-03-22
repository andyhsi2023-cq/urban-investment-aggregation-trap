# Urban Q 项目数据溯源文档

> 生成日期：2026-03-21
> 数据来源项目：`six-curves-urban-transition/02-data/raw/`
> 本文档记录 Urban Q 模型所依赖的全部 CSV 原始数据文件的来源、结构与验证信息。

---

## 1. 文件清单总览

| # | 文件名 | 时间范围 | 观测数 | 主要来源 |
|---|--------|----------|--------|----------|
| 1 | `background_gdp_NBS_1978-2024.csv` | 1978--2024 | 47 | 国家统计局历年统计公报 |
| 2 | `c1_urbanization_rate_NBS_1949-2024.csv` | 1949--2024 | 76 | 国家统计局历年统计公报 |
| 3 | `c3_new_construction_starts_NBS_1985-2024.csv` | 1985--2024 | 40 | 国家统计局历年统计公报 |
| 4 | `c5_residential_price_NBS_1998-2024.csv` | 1998--2024 | 27 | 国家统计局历年统计公报 |
| 5 | `c5_land_transfer_revenue_MOF_1999-2024.csv` | 1999--2024 | 26 | 财政部历年财政收支情况 |
| 6 | `c6_real_estate_investment_NBS_1987-2024.csv` | 1987--2024 | 38 | 国家统计局历年统计公报 |
| 7 | `c6_infrastructure_investment_NBS_1990-2024.csv` | 1990--2024 | 35 | 国家统计局历年统计公报 |

注：观测数 = 数据行数（不含表头行）。

---

## 2. 逐文件详细信息

### 2.1 background_gdp_NBS_1978-2024.csv

- **列名**: `year`, `gdp_100m_current`, `gdp_growth_pct`, `gdp_per_capita_yuan`, `urban_disposable_income_yuan`, `source_note`
- **时间范围**: 1978--2024（47 个年度观测）
- **单位**: GDP 为当年价（亿元）；人均 GDP（元）；城镇居民人均可支配收入（元）
- **数据来源** (source_note 摘录):
  - 1978--2022：国家统计局对应年份统计公报
  - 2023：国家统计局2024年统计公报
  - 2024：国家统计局2025年初步数据（估算）
- **注意**: 2024 年数据标注为"估算"，待2025年统计公报正式发布后需核实更新。

### 2.2 c1_urbanization_rate_NBS_1949-2024.csv

- **列名**: `year`, `urbanization_rate_pct`, `urban_population_10k`, `total_population_10k`, `source_note`
- **时间范围**: 1949--2024（76 个年度观测）
- **单位**: 城镇化率（%）；城镇人口、总人口（万人）
- **数据来源** (source_note 摘录):
  - 1949--2022：国家统计局对应年份统计公报
  - 2023：国家统计局2024年统计公报
  - 2024：国家统计局2025年初步统计数据（估算）
- **注意**: 2024 年数据标注为"估算"。

### 2.3 c3_new_construction_starts_NBS_1985-2024.csv

- **列名**: `year`, `new_starts_10k_m2`, `completion_10k_m2`, `commercial_starts_10k_m2`, `commercial_completion_10k_m2`, `source_note`
- **时间范围**: 1985--2024（40 个年度观测）
- **单位**: 万平方米
- **数据来源** (source_note 摘录):
  - 1985--2022：国家统计局对应年份统计公报
  - 2023：国家统计局2024年统计公报
  - 2024：国家统计局2025年1月《2024年全国房地产市场基本情况》
- **注意**: 2024 年的新开工面积 (74,492 万平方米) 已由官方数据修正（原估算值 78,000）；竣工面积及商品房分项仍为估算。

### 2.4 c5_residential_price_NBS_1998-2024.csv

- **列名**: `year`, `commercial_housing_avg_price_yuan_m2`, `residential_avg_price_yuan_m2`, `commercial_housing_sales_area_10k_m2`, `commercial_housing_sales_amount_100m`, `yoy_price_growth_pct`, `source_note`
- **时间范围**: 1998--2024（27 个年度观测）
- **单位**: 均价（元/平方米）；销售面积（万平方米）；销售额（亿元）
- **数据来源** (source_note 摘录):
  - 1998--2022：国家统计局对应年份统计公报
  - 2023：国家统计局2024年统计公报
  - 2024：国家统计局2025年初步数据（估算）
- **注意**: 2024 年房价及增速为估算值。

### 2.5 c5_land_transfer_revenue_MOF_1999-2024.csv

- **列名**: `year`, `land_transfer_revenue_100m`, `land_transfer_area_10k_ha`, `residential_land_price_yuan_m2`, `commercial_land_price_yuan_m2`, `industrial_land_price_yuan_m2`, `comprehensive_land_price_yuan_m2`, `yoy_revenue_growth_pct`, `source_note`
- **时间范围**: 1999--2024（26 个年度观测）
- **单位**: 土地出让收入（亿元）；出让面积（万公顷）；地价（元/平方米）
- **数据来源** (source_note 摘录):
  - 主要来源为财政部历年财政收支情况发布
  - 2022：财政部2022年财政收支情况
  - 2023：财政部2023年财政收支情况
  - 2024：财政部2024年财政数据（初步数据，估算）
- **注意**: 2022 年之后的分项地价数据（住宅、商业、工业、综合）缺失。2024 年收入为估算值。

### 2.6 c6_real_estate_investment_NBS_1987-2024.csv

- **列名**: `year`, `real_estate_investment_100m`, `yoy_growth_pct`, `source_note`
- **时间范围**: 1987--2024（38 个年度观测）
- **单位**: 亿元
- **数据来源** (source_note 摘录):
  - 1987--2022：国家统计局对应年份统计公报
  - 2023：国家统计局2024年统计公报
  - 2024：国家统计局2025年1月《2024年全国房地产市场基本情况》
- **注意**: 2024 年数据已由官方数据修正（原估算值 97,794 亿元/-11.8% 已更正为 100,280 亿元/-10.6%）。

### 2.7 c6_infrastructure_investment_NBS_1990-2024.csv

- **列名**: `year`, `infra_investment_100m`, `transport_investment_100m`, `utility_investment_100m`, `source_note`
- **时间范围**: 1990--2024（35 个年度观测）
- **单位**: 亿元
- **数据来源** (source_note 摘录):
  - 1990--2022：国家统计局对应年份统计公报
  - 2023：国家统计局2024年统计公报
  - 2024：国家统计局2025年1月数据，基于 2023 年 198,936 亿元乘以增速 5.3% 估算（原估算值 206,000 已修正）
- **注意**: 2024 年为估算值，交通和公用事业分项投资缺失；官方精确值待统计公报确认。2022--2024 年交通和公用事业分项投资数据均缺失。

---

## 3. 抽查验证

选取 3 个关键数据点，与公开权威数据比对：

| 指标 | 数据年份 | 文件中的值 | 官方公开值 | 来源文件 | 验证结果 |
|------|----------|-----------|-----------|----------|----------|
| GDP (亿元) | 2023 | 1,260,582.0 | 1,260,582 | 国家统计局《2023年国民经济和社会发展统计公报》(2024-02-29) | **一致** |
| 城镇化率 (%) | 2023 | 66.16 | 66.16 | 国家统计局《2023年国民经济和社会发展统计公报》(2024-02-29) | **一致** |
| 房地产投资 (亿元) | 2024 | 100,280.0 | 100,280 | 国家统计局《2024年全国房地产市场基本情况》(2025-01-17) | **一致** |

验证说明：
- 2023 年 GDP 126.06 万亿元、增速 5.2%，与统计公报完全一致。
- 2023 年城镇化率 66.16%，与统计公报完全一致。
- 2024 年房地产投资 100,280 亿元、同比 -10.6%，与 NBS 2025 年 1 月发布数据一致（文件中已标注从原估算值修正）。

**结论**: 抽查的 3 个关键数据点均与官方公开数据一致，数据可信度高。

---

## 4. 数据质量说明

### 4.1 已知的估算值

以下数据点标注为"估算"，在分析中需注意：

| 文件 | 年份 | 估算字段 | 说明 |
|------|------|---------|------|
| background_gdp | 2024 | 全部字段 | 2025年初步数据 |
| c1_urbanization_rate | 2024 | 全部字段 | 2025年初步统计 |
| c3_new_construction_starts | 2024 | 竣工面积、商品房分项 | 新开工已修正为官方值 |
| c5_residential_price | 2024 | 全部字段 | 2025年初步数据 |
| c5_land_transfer_revenue | 2024 | 收入总额 | 初步数据 |
| c6_real_estate_investment | 2024 | -- | 已修正为官方值 |
| c6_infrastructure_investment | 2024 | 全部字段 | 基于增速估算 |

**建议**: 待 2025 年国家统计局正式统计公报发布后（通常为 2 月底至 3 月），统一核实并更新全部 2024 年数据。

### 4.2 缺失值

- `c5_land_transfer_revenue`: 2022--2024 年分项地价数据（住宅、商业、工业、综合）全部缺失。
- `c6_infrastructure_investment`: 2022--2024 年交通投资和公用事业投资分项缺失。

---

## 5. 论文引用建议

### 5.1 中文论文引用格式

数据来源统一在方法部分或数据说明注脚中标注：

> 本研究使用的宏观经济数据来源于国家统计局历年《国民经济和社会发展统计公报》(1978--2024)；土地出让收入数据来源于财政部历年《全国财政收支情况》(1999--2024)；2024年房地产相关数据来源于国家统计局《2024年全国房地产市场基本情况》(2025年1月发布)。

### 5.2 英文论文引用格式 (APA 7th)

在正文中引用：

> ... data were obtained from the National Bureau of Statistics of China (NBS) annual statistical communiques (1978--2024) and the Ministry of Finance (MOF) fiscal revenue and expenditure reports (1999--2024).

参考文献条目：

> National Bureau of Statistics of China. (1979--2025). *Statistical communique of the People's Republic of China on the [year] national economic and social development* [年度统计公报]. https://www.stats.gov.cn/
>
> Ministry of Finance of the People's Republic of China. (2000--2025). *National fiscal revenue and expenditure report* [全国财政收支情况]. https://www.mof.gov.cn/

### 5.3 图表脚注建议

图表中建议统一使用以下脚注格式：

> Source: NBS Statistical Communiques (1978--2024); MOF Fiscal Reports (1999--2024). Note: 2024 values marked with * are preliminary estimates.

---

## 6. 文件路径映射

所有原始数据文件存储于 six-curves 项目中，Urban Q 项目通过引用访问：

```
源路径: six-curves-urban-transition/02-data/raw/
  background_gdp_NBS_1978-2024.csv
  c1_urbanization_rate_NBS_1949-2024.csv
  c3_new_construction_starts_NBS_1985-2024.csv
  c5_residential_price_NBS_1998-2024.csv
  c5_land_transfer_revenue_MOF_1999-2024.csv
  c6_real_estate_investment_NBS_1987-2024.csv
  c6_infrastructure_investment_NBS_1990-2024.csv
```

如需在 Urban Q 分析脚本中引用，建议使用相对路径或在脚本开头定义 `DATA_ROOT` 变量指向 six-curves 项目的 raw 目录，避免数据重复存储。
