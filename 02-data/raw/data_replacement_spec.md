# 数据替换规格说明书 (Data Replacement Specification)

> 编制日期: 2026-03-21
> 目的: 为 5 个脚本中的硬编码代理数据替换为官方来源数据提供精确的变量映射和数据源规格

---

## 1. 脚本 40 -- 中国国家级 (`40_china_real_data.py`)

### 1.1 硬编码数据位置

函数 `build_yearbook_data()` (约第 193-366 行) 包含 5 个 Python 字典:

| 变量名 | 字典名 | 时间范围 | 单位 | 声称来源 |
|--------|--------|----------|------|----------|
| GDP 总量 | `gdp_data['gdp_100m']` | 1990-2023 (34年) | 亿元(当年价) | 统计年鉴2024, 表3-1 |
| 第一产业增加值 | `gdp_data['primary_gdp_100m']` | 1990-2023 | 亿元 | 同上 |
| 第二产业增加值 | `gdp_data['secondary_gdp_100m']` | 1990-2023 | 亿元 | 同上 |
| 第三产业增加值 | `gdp_data['tertiary_gdp_100m']` | 1990-2023 | 亿元 | 同上 |
| 总人口 | `pop_data['total_pop_10k']` | 1990,1995,2000-2023 (26点) | 万人 | 统计年鉴2024, 表2-1 |
| 城镇人口 | `pop_data['urban_pop_10k']` | 同上 | 万人 | 同上 |
| 城镇化率 | `pop_data['urbanization_rate']` | 同上 | % | 同上 |
| 固定资产投资 | `inv_data['fai_total_100m']` | 2000-2023 (24年) | 亿元 | 统计年鉴2024, 表5-1; 统计公报 |
| 房地产开发投资 | `inv_data['re_inv_100m']` | 2000-2023 | 亿元 | 统计年鉴2024, 表5-35 |
| 商品房销售额 | `sales_data['sales_value_100m']` | 2000-2023 | 亿元 | 统计年鉴2024, 表5-40 |
| 商品房销售面积 | `sales_data['sales_area_10k_m2']` | 2000-2023 | 万平方米 | 同上 |
| 住宅竣工面积 | `completion_data['residential_completed_10k_m2']` | 2000-2023 | 万平方米 | 统计年鉴2024, 表5-33 |

### 1.2 推荐官方数据源

| 变量 | 首选数据源 | 具体位置 |
|------|-----------|---------|
| GDP 及三产 | NBS 国家数据云 | https://data.stats.gov.cn -> 年度数据 -> 国民经济核算 -> 国内生产总值 (指标码 A0201) |
| 人口与城镇化 | NBS 国家数据云 | 年度数据 -> 人口 -> 人口数及构成 (指标码 A0301) |
| 固定资产投资 | NBS 国家数据云 | 年度数据 -> 固定资产投资 -> 固定资产投资(不含农户) (指标码 A0501) |
| 房地产开发投资 | NBS 国家数据云 | 年度数据 -> 房地产 -> 房地产开发投资完成额 (指标码 A0503) |
| 商品房销售 | NBS 国家数据云 | 年度数据 -> 房地产 -> 商品房销售面积及销售额 (指标码 A0506) |
| 住宅竣工面积 | NBS 国家数据云 | 年度数据 -> 房地产 -> 房屋竣工面积 |
| 备用: World Bank | World Bank Open Data | SP.URB.TOTL.IN.ZS (城镇化率), NV.SRV.TOTL.ZS (服务业占比) |

### 1.3 输出 CSV 列名清单

输出文件: `02-data/raw/china_national_real_data.csv`

优先列顺序 (`priority_cols`):
```
year, country, country_code, data_source,
gdp_100m, primary_gdp_100m, secondary_gdp_100m, tertiary_gdp_100m,
primary_pct, secondary_pct, tertiary_pct,
total_pop_10k, urban_pop_10k, urbanization_rate,
fai_total_100m, re_inv_100m, re_inv_share_pct,
sales_value_100m, sales_area_10k_m2, avg_price_yuan_m2,
residential_completed_10k_m2, housing_stock_10k_m2,
housing_value_100m, capital_stock_100m, re_capital_stock_100m,
urban_q, marginal_urban_q, real_estate_q
```

注意: 实际输出还包含 World Bank 合并列 (wb_gdp_current_usd, wb_urban_pct 等), 列名在 `other_cols` 中动态捕获。

---

## 2. 脚本 41 -- 中国省级 (`41_china_provincial_data.py`)

### 2.1 硬编码数据位置

函数 `build_yearbook_data()` (约第 158-434 行) 包含 4 个嵌套字典, 每个字典的外层键为年份, 内层键为 31 个省名:

| 变量名 | 字典名 | 关键年份 | 单位 | 声称来源 |
|--------|--------|----------|------|----------|
| 地区生产总值 | `gdp_data` | 2005, 2010, 2015, 2019, 2023 | 亿元(当年价) | 统计年鉴各年版 |
| 城镇化率 | `urbanization_rate` | 2005, 2010, 2015, 2019, 2023 | % | 统计年鉴/七普 |
| 第三产业占比 | `tertiary_share` | 2005, 2010, 2015, 2019, 2023 | % | 统计年鉴各年版 |
| 固定资产投资 | `fai_data` | 2005, 2010, 2015, 2019 (无2023) | 亿元 | 统计年鉴各年版 |

**5 个关键年份各变量覆盖情况:**

| 年份 | GDP | 城镇化率 | 三产占比 | 固定资产投资 |
|------|-----|---------|---------|------------|
| 2005 | Yes | Yes | Yes | Yes |
| 2010 | Yes | Yes | Yes | Yes |
| 2015 | Yes | Yes | Yes | Yes |
| 2019 | Yes | Yes | Yes | Yes |
| 2023 | Yes | Yes | Yes | **No** (统计局不再公布绝对值) |

### 2.2 推荐官方数据源

| 变量 | 首选数据源 | 具体位置 |
|------|-----------|---------|
| 分省 GDP | NBS 国家数据云 | https://data.stats.gov.cn -> 分省年度数据 (dbcode=fsnd) -> 地区生产总值 (指标码 A0201-A0204) |
| 分省城镇化率 | NBS 国家数据云 | 分省年度数据 -> 人口 (A0305) |
| 分省固定资产投资 | NBS 国家数据云 | 分省年度数据 -> 固定资产投资 (A0501) |
| 备用: 各省统计年鉴 | 各省统计局官网 | 逐省查询 |

### 2.3 输出 CSV 列名清单

输出文件: `02-data/raw/china_provincial_real_data.csv`

```
province, province_en, year, data_type,
gdp_billion_yuan, urbanization_rate_pct, tertiary_share_pct,
fai_billion_yuan, fai_gdp_ratio, source
```

注意:
- `data_type` = "actual" | "interpolated"
- 中间年份 (如 2006-2009) 通过线性插值生成
- 2020-2023 年 `fai_billion_yuan` 和 `fai_gdp_ratio` 强制设为 NaN

---

## 3. 脚本 03 -- 日本 (`03_japan_urban_q.py`)

### 3.1 硬编码数据位置

脚本开头 (第 49-150 行) 包含 7 个顶层 Python 字典:

| 变量名 | 字典名 | 时间范围 | 数据点数 | 单位 | 声称来源 |
|--------|--------|----------|---------|------|----------|
| 城镇化率 | `urbanization_data` | 1950-2023 | 16点 | % | World Bank (SP.URB.TOTL.IN.ZS) |
| 建设投资(名义) | `construction_investment_data` | 1960-2023 | 48点 | 万亿日元 | MLIT 建设投资见通し/建设统计 |
| GDP(名义) | `gdp_data` | 1955-2023 | 35点 | 万亿日元 | 内阁府 SNA / World Bank |
| 住宅着工件数 | `housing_starts_data` | 1960-2023 | 48点 | 万户 | MLIT 建筑着工统计 |
| 地价指数 | `land_price_index_data` | 1960-2023 | 38点 | 1983=100 | JREI 市街地価格指数 |
| 三产GDP占比 | `tertiary_share_data` | 1960-2023 | 14点 | % | World Bank / 内阁府 SNA |
| 新建 vs 维修 | `new_vs_repair_data` | 1970-2023 | 14点 | (万亿日元, 万亿日元) | MLIT 建设统计 |

### 3.2 推荐官方数据源

| 变量 | 首选数据源 | 具体 URL / 表号 |
|------|-----------|----------------|
| 城镇化率 | World Bank Open Data | https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS?locations=JP |
| 建设投资 | MLIT 建设投资見通し | https://www.mlit.go.jp/sogoseisaku/jouhouka/sosei_jouhouka_tk_000014.html (建設投資見通し PDF/Excel) |
| GDP | 内阁府 国民経済計算 | https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/tables/2023/ (93SNA/08SNA 长期时间序列) |
| 住宅着工 | MLIT 建築着工統計 | https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00600120 (e-Stat: 建築着工統計調査) |
| 地価指数 | JREI 市街地価格指数 | https://www.reinet.or.jp/?page_id=13968 (不動産研究所, 需注册) |
| 三产占比 | World Bank / e-Stat | World Bank NV.SRV.TOTL.ZS 或内阁府 SNA 产业别 GDP |
| 新建/修缮比 | MLIT 建設総合統計 | https://www.mlit.go.jp/statistics/details/kensetsu_list.html (建設総合統計年度報) |

### 3.3 输出 CSV 列名清单

**Raw 输出** (`02-data/raw/japan_urban_q_data.csv`):
```
year, urbanization_rate, construction_investment_trillion_yen,
gdp_trillion_yen, housing_starts_10k, land_price_index_1983eq100,
tertiary_share_pct, new_construction_trillion, maintenance_repair_trillion,
urbanization_interpolated, ci_interpolated
```

**Results 输出** (`03-analysis/models/japan_urban_q_timeseries.csv`):
```
year, urbanization_rate, construction_investment_trillion_yen,
gdp_trillion_yen, capital_stock_K, asset_value_V,
urban_Q, MUQ, ci_gdp_ratio, housing_starts_10k,
land_price_index_1983eq100, tertiary_share_pct,
new_construction_trillion, maintenance_repair_trillion,
new_repair_ratio
```

---

## 4. 脚本 04 -- 美国 (`04_us_urban_q.py`)

### 4.1 硬编码数据位置

脚本开头 (第 56-161 行) 包含 7 个顶层字典 + 1 个辅助字典:

| 变量名 | 字典名 | 时间范围 | 数据点数 | 单位 | 声称来源 |
|--------|--------|----------|---------|------|----------|
| 名义 GDP | `gdp_data` | 1970-2024 | 41点 | 万亿美元 | BEA NIPA / World Bank |
| 建设投资/GDP 比率 | `ci_gdp_ratio_data` | 1970-2024 | 41点 | 小数 | BEA NIPA Table 5.4.5 + 5.8.5 |
| 住房价格指数 | `hpi_data` | 1970-2024 | 41点 | 1970=100 | Case-Shiller / FHFA HPI |
| 城镇化率 | `urbanization_data` | 1970-2024 | 12点 | % | World Bank / Census Bureau |
| 三产占比 | `tertiary_share_data` | 1970-2024 | 12点 | % | World Bank / BEA |
| 人口 | `population_data` | 1970-2024 | 12点 | 百万 | Census Bureau / World Bank |
| 新建 vs 改善比例 | `new_vs_improvement_share` | 1970-2024 | 11点 | (份额, 份额) | Census Bureau C30 |
| 住宅市值/GDP 比率 | `res_value_gdp_ratio` | 1970-2024 | 27点 | 小数 | Fed Z.1 / BEA Fixed Assets |
| 非住宅/住宅价值比 | `nonres_ratio_data` | 1970-2024 | 10点 | 小数 | BEA Fixed Assets Table 1.1 |

### 4.2 推荐官方数据源

| 变量 | 首选数据源 | 具体 URL / 表号 |
|------|-----------|----------------|
| GDP | BEA NIPA | https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey (Table 1.1.5 GDP) |
| 建设投资 | BEA NIPA | Table 5.4.5 (Private Fixed Investment by Type) + Table 5.8.5 (Gov Fixed Investment) |
| HPI | FHFA HPI | https://www.fhfa.gov/data/hpi (All-Transactions HPI, quarterly, 国家级) |
| 城镇化率 | World Bank | SP.URB.TOTL.IN.ZS?locations=US |
| 三产占比 | World Bank / BEA | NV.SRV.TOTL.ZS 或 BEA GDP by Industry |
| 人口 | Census Bureau | https://www.census.gov/programs-surveys/popest.html |
| C30 (新建/改善) | Census Bureau | https://www.census.gov/construction/c30/c30index.html (Value of Construction Put in Place) |
| 住宅市值 | Fed Z.1 | https://www.federalreserve.gov/releases/z1/ -> Table B.101 (Balance Sheet of Households, line 4 Real Estate) |
| 非住宅存量 | BEA Fixed Assets | https://apps.bea.gov/iTable/?reqid=10&step=2&isuri=1 (Table 1.1 Current-Cost Net Stock) |

### 4.3 输出 CSV 列名清单

输出文件: `03-analysis/models/us_urban_q_timeseries.csv`

```
year, urbanization_rate, gdp_trillion_usd,
construction_investment_trillion, ci_gdp_ratio,
hpi_1970eq100, tertiary_share_pct, population_million,
capital_stock_K, V_residential, V_nonresidential, V_total,
V_gdp_ratio, urban_Q, Q_residential, MUQ, MUQ_residential,
new_construction_trillion, improvement_trillion,
new_improvement_ratio, new_construction_share
```

---

## 5. 脚本 05 -- 英国 (`05_uk_urban_q.py`)

### 5.1 硬编码数据位置

脚本开头 (第 56-191 行) 包含 8 个顶层字典:

| 变量名 | 字典名 | 时间范围 | 数据点数 | 单位 | 声称来源 |
|--------|--------|----------|---------|------|----------|
| 名义 GDP | `gdp_data` | 1970-2024 | 41点 | 万亿英镑 | ONS Blue Book / World Bank |
| 建设投资/GDP 比率 | `ci_gdp_ratio_data` | 1970-2024 | 42点 | 小数 | ONS GFCF by asset type / OECD |
| 住房价格指数 | `hpi_data` | 1970-2024 | 55点 | 1970=100 | Nationwide HPI / ONS HPI |
| 城镇化率 | `urbanization_data` | 1970-2024 | 12点 | % | World Bank / ONS |
| 三产占比 | `tertiary_share_data` | 1970-2024 | 12点 | % | World Bank / ONS |
| 人口 | `population_data` | 1970-2024 | 12点 | 百万 | ONS / World Bank |
| 住宅市值/GDP 比率 | `res_value_gdp_ratio` | 1970-2024 | 34点 | 小数 | BoE FSR / Savills / ONS NBS |
| 新建 vs 维修比例 | `new_vs_repair_share` | 1970-2024 | 11点 | (份额, 份额) | ONS Output in Construction / RICS |
| 非住宅/住宅价值比 | `nonres_ratio_data` | 1970-2024 | 10点 | 小数 | ONS NBS Table 10.1 |

### 5.2 推荐官方数据源

| 变量 | 首选数据源 | 具体 URL / 表号 |
|------|-----------|----------------|
| GDP | ONS | https://www.ons.gov.uk/economy/grossdomesticproductgdp/timeseries/abmi/pn2 (GDP at current prices) |
| 建设投资 | ONS GFCF | https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/grossfixedcapitalformation (GFCF by asset) |
| HPI | ONS UK HPI | https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/housepriceindexmonthlyquarterlytables (Table 1) |
| HPI (备用) | Nationwide | https://www.nationwidehousepriceindex.co.uk/download (季度/年度长序列) |
| 城镇化率 | World Bank | SP.URB.TOTL.IN.ZS?locations=GB |
| 三产占比 | World Bank / ONS | NV.SRV.TOTL.ZS 或 ONS GDP by industry |
| 人口 | ONS | https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates |
| 住宅市值 | ONS National Balance Sheet | https://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts/datasets/thenationalbalancesheetestimates (Table 10.1) |
| 建设产出(新建/修缮) | ONS | https://www.ons.gov.uk/businessindustryandtrade/constructionindustry/datasets/outputintheconstructionindustry (Table 1) |

### 5.3 输出 CSV 列名清单

输出文件: `03-analysis/models/uk_urban_q_timeseries.csv`

```
year, urbanization_rate, gdp_trillion_gbp,
construction_investment_trillion, ci_gdp_ratio,
hpi_1970eq100, tertiary_share_pct, population_million,
capital_stock_K, V_residential, V_nonresidential, V_total,
V_gdp_ratio, res_value_gdp_ratio,
urban_Q, Q_residential, MUQ, MUQ_residential,
new_construction_trillion, repair_trillion,
new_repair_ratio, new_construction_share
```

---

## 6. 汇总: 替换优先级与工作量估计

### 6.1 按脚本分的变量总数

| 脚本 | 硬编码字典数 | 总数据点(估) | 替换难度 |
|------|------------|-------------|---------|
| 40_china_real_data | 5 个字典 (12个变量) | ~300 | 中 -- NBS API 已有尝试, 可能需要手动CSV |
| 41_china_provincial | 4 个字典 (4变量x31省x5年) | ~620 | 高 -- 数据量大, 需逐省核对 |
| 03_japan_urban_q | 7 个字典 (8个变量) | ~250 | 高 -- e-Stat 接口复杂, 日语界面 |
| 04_us_urban_q | 9 个字典 (9个变量) | ~250 | 中 -- BEA/Fed 数据可机读下载 |
| 05_uk_urban_q | 9 个字典 (9个变量) | ~270 | 中 -- ONS 数据有 API 和 CSV 下载 |

### 6.2 跨脚本共享变量

以下变量可以从单一来源获取后分发:

| 变量 | 涉及脚本 | 统一来源 |
|------|---------|---------|
| 城镇化率 | 03, 04, 05 | World Bank SP.URB.TOTL.IN.ZS (已在 WB 面板中) |
| 三产占比 | 03, 04, 05 | World Bank NV.SRV.TOTL.ZS (已在 WB 面板中) |
| 人口 | 04, 05 | World Bank SP.POP.TOTL (已在 WB 面板中) |

### 6.3 下游兼容性关键约束

替换数据后,必须确保以下列名和格式不变,否则下游脚本 (06_cross_country_comparison.py 等) 将报错:

1. **日本**: `urban_Q`, `MUQ`, `ci_gdp_ratio`, `new_repair_ratio` -- 用于跨国比较图
2. **美国**: `urban_Q`, `Q_residential`, `MUQ`, `V_gdp_ratio` -- 同上
3. **英国**: `urban_Q`, `Q_residential`, `MUQ`, `V_gdp_ratio` -- 同上
4. **中国国家级**: `urban_q`, `marginal_urban_q`, `real_estate_q` -- 注意小写命名
5. **中国省级**: `gdp_billion_yuan`, `urbanization_rate_pct`, `tertiary_share_pct` -- 用于省级分析

### 6.4 建议替换策略

1. **Phase 1**: 先替换可从 World Bank 面板直接获取的变量 (城镇化率, 三产占比, GDP, 人口)
2. **Phase 2**: 替换各国专属统计机构的核心变量 (建设投资, 房价指数)
3. **Phase 3**: 替换需要特殊处理的变量 (新建/修缮比例, 住宅市值/GDP 比率, 非住宅比率)
4. **每次替换后**: 运行对应脚本, 比较 Urban Q 曲线形态是否合理; 如偏差超过 10%, 需检查数据单位和口径
