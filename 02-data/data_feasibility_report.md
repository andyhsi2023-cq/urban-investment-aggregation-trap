# Urban Q 国际数据可行性报告

**项目**: urban-q-phase-transition
**撰写日期**: 2026-03-19
**撰写人**: data-analyst
**目标期刊**: Nature

---

## 一、概述

本报告评估计算 Urban Q = V(t) / K(t) 所需的国际可比数据的可得性。Urban Q 的分子为城市/国家层面的不动产资产总市值，分母为累计建设投资（或重置成本近似值）。报告覆盖六个国家（中国、日本、韩国、美国、德国、英国），并评估辅助变量（新建vs更新区分、建筑存量、GDP结构、城镇化率）的可得性。

**核心结论**：五个目标国家均可构建 Urban Q 的可行近似值，但数据口径、时间跨度和精度存在显著差异。美国和英国的数据基础最为完善；日本和德国次之；韩国在分子端（资产市值）的数据相对薄弱。中国的数据可从 six-curves 项目大量复用，但需补充国民资产负债表口径。

---

## 二、数据可得性矩阵

| 变量 | 中国 | 日本 | 韩国 | 美国 | 德国 | 英国 |
|------|:----:|:----:|:----:|:----:|:----:|:----:|
| 不动产总市值 V(t) | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ |
| 累计建设投资/资本存量 K(t) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 新建 vs 更新投资区分 | ⚠️ | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| 建筑存量面积 | ⚠️ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| 三产 GDP 结构 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 城镇化率 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**图例**: ✅ 可得（有公开、结构化的时间序列） / ⚠️ 部分可得（需构建、拼接或仅覆盖部分年份） / ❌ 不可得

---

## 三、逐国详细评估

### 3.1 美国 (United States) — 数据最完善

#### 分子：不动产资产市值 V(t)
- **首选来源**: Bureau of Economic Analysis (BEA) Fixed Assets Tables
  - Table 1.1: Current-Cost Net Stock of Fixed Assets（按资产类型分）
  - 包含 Residential structures、Nonresidential structures、Government structures
  - 时间跨度: 1925-present（年度）
  - 获取方式: 公开下载 CSV, https://apps.bea.gov/iTable/
  - **评估**: ✅ 直接可用。BEA 提供当期成本(current-cost)和链式美元(chained dollars)两种口径的净存量，可直接作为 V(t)
- **补充来源**: Federal Reserve Financial Accounts (Z.1)
  - Table B.101: Balance Sheet of Households — 含 Real estate at market value
  - 时间跨度: 1945-present（季度）
  - 获取方式: 公开下载, https://www.federalreserve.gov/releases/z1/
  - **评估**: ✅ 可用于交叉验证

#### 分母：累计建设投资 K(t)
- **首选来源**: BEA NIPA Tables
  - Table 5.4.5: Private Fixed Investment by Type — Structures
  - Table 5.8.5: Government GFCF — Structures
  - 时间跨度: 1929-present
  - **评估**: ✅ 直接可用
- **PIM 资本存量**: BEA Fixed Assets Tables 已提供 current-cost net stock，无需自行构建 PIM
- **OECD.Stat**: GFCF by asset type (AN.111 Dwellings, AN.112 Other buildings and structures)
  - 时间跨度: 1970-present
  - 获取方式: https://stats.oecd.org/ > National Accounts > Capital formation

#### 新建 vs 更新区分
- **Census Bureau**: Value of Construction Put in Place (C30 Survey)
  - 明确区分 New construction vs. Improvements/Additions
  - 时间跨度: 1993-present（月度），部分回溯至 1964
  - 获取方式: https://www.census.gov/construction/c30/c30index.html
  - **评估**: ✅ 这是所有国家中区分度最好的数据
- **补充**: Census Bureau Building Permits Survey — 区分 new units vs. alterations/additions

#### 建筑存量面积
- **American Housing Survey (AHS)**: 住宅单元数量与面积
  - 时间跨度: 1973-present（隔年）
  - 获取方式: https://www.census.gov/programs-surveys/ahs.html
- **Commercial Buildings Energy Consumption Survey (CBECS)**: 商业建筑面积
  - 时间跨度: 1979-present（不规则间隔，约每4年）
  - 获取方式: https://www.eia.gov/consumption/commercial/

#### 数据时间跨度
| 变量 | 起始年份 | 终止年份 | 频率 |
|------|---------|---------|------|
| 不动产净存量 (BEA) | 1925 | 2024 | 年度 |
| 建设投资 (BEA) | 1929 | 2024 | 年度/季度 |
| 新建vs改善 (C30) | 1993 | 2024 | 月度 |
| GDP结构 (BEA) | 1929 | 2024 | 年度 |
| 城镇化率 (Census/WB) | 1790 | 2024 | 年度(WB)/十年(Census) |

---

### 3.2 英国 (United Kingdom) — 数据质量高

#### 分子：不动产资产市值 V(t)
- **首选来源**: ONS National Balance Sheet
  - Table 10.1: National Balance Sheet — Non-financial assets
  - 包含 Dwellings (AN.111), Other buildings and structures (AN.112)
  - 按市场价值估计（基于 PIM + 价格指数调整）
  - 时间跨度: 1995-present
  - 获取方式: https://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts
  - **评估**: ✅ 直接可用，已按市场价值估计
- **补充来源**: 英格兰银行金融稳定性数据 — 住宅房地产市值
  - Residential property wealth estimates
  - 时间跨度: 约2000-present

#### 分母：累计建设投资 K(t)
- **首选来源**: ONS GFCF by Asset Type
  - 公开在 National Accounts 统计中
  - AN.111 Dwellings + AN.112 Other buildings and structures
  - 时间跨度: 1997-present（一致口径），部分回溯至 1965
  - 获取方式: ONS dataset NPQT/DLWF 等系列代码
  - **评估**: ✅ 直接可用
- **PIM 资本存量**: ONS 的 National Balance Sheet 已提供 net capital stock

#### 新建 vs 更新区分
- **ONS Construction Output Statistics**
  - 明确区分: New work vs. Repair and maintenance (R&M)
  - 进一步细分: New housing / Other new work / Housing R&M / Non-housing R&M
  - 时间跨度: 2010-present（一致序列），部分回溯至 1955
  - 获取方式: https://www.ons.gov.uk/businessindustryandtrade/constructionindustry
  - **评估**: ✅ 区分清晰，是与美国并列最好的来源
- **DLUHC (住房部)**: 住宅建设许可 — new builds vs. conversions/extensions

#### 建筑存量面积
- **Valuation Office Agency (VOA)**: 商业和住宅物业面积登记
  - 住宅: English Housing Survey 提供面积分布
  - 商业: VOA 提供非住宅建筑面积
  - 时间跨度: 住宅面积 1996-present
  - **评估**: ⚠️ 连续时间序列需拼接

#### 数据时间跨度
| 变量 | 起始年份 | 终止年份 | 频率 |
|------|---------|---------|------|
| 不动产净存量 (ONS) | 1995 | 2023 | 年度 |
| 建设投资 (ONS GFCF) | 1965 | 2024 | 季度 |
| 新建vs维修 (Construction Output) | 1955 | 2024 | 季度 |
| GDP结构 (ONS) | 1948 | 2024 | 年度 |
| 城镇化率 (WB) | 1960 | 2024 | 年度 |

---

### 3.3 德国 (Germany) — 数据体系完善但统一前后断裂

#### 分子：不动产资产市值 V(t)
- **首选来源**: Destatis — Volkswirtschaftliche Gesamtrechnungen (VGR)
  - Anlagevermogen nach Anlagearten (Fixed assets by type)
  - 提供 Bruttoanlagevermogen (gross) 和 Nettoanlagevermogen (net) — 按重置成本
  - 包含 Wohnbauten (dwellings) 和 Nichtwohnbauten (non-residential buildings)
  - 时间跨度: 1991-present（统一后），西德 1950-1990
  - 获取方式: https://www.destatis.de/ > VGR > Anlagevermogen
  - **评估**: ✅ 可用。注意德国官方提供的是重置成本(replacement cost)而非严格市场价值
- **补充来源**: Deutsche Bundesbank — 金融稳定性报告中的不动产价值估计
  - 住宅不动产市值估计（基于价格指数调整）
  - 时间跨度: 约2003-present
- **学术来源**: DIW Berlin — Vermogensbilanzen (Wealth accounts)
  - 含不动产市场价值的长期估计

#### 分母：累计建设投资 K(t)
- **首选来源**: Destatis VGR — Bruttoanlageinvestitionen (GFCF)
  - 按 Bauinvestitionen (construction investment) 细分
  - 进一步区分 Wohnbauten / Nichtwohnbauten / Tiefbauten (civil engineering)
  - 时间跨度: 1991-present（统一后一致口径），西德 1950-1990
  - **评估**: ✅ 直接可用
- **OECD.Stat**: 一致口径 GFCF by asset type, 1970-present

#### 新建 vs 更新区分
- **Destatis Bautatigkeitsstatistik (建设活动统计)**
  - 建筑许可和竣工按以下类别统计:
    - Neubau (new construction)
    - Um-/Ausbau, Erweiterung (conversion/extension)
    - 维护投资在 VGR 中有独立统计
  - 时间跨度: 1991-present
  - 获取方式: GENESIS-Online 数据库 (31111-0001 等表号)
  - **评估**: ✅ 分类清晰
- **ifo Institut**: Bauinvestitionen 按 Neubau vs. Bestandsmassnahmen 分类
  - 提供更细致的新建/存量投资拆分

#### 建筑存量面积
- **Destatis Wohnungsbestand (住宅存量)**
  - 住宅单元数量和面积 (Wohnflache)
  - 时间跨度: 统一后 1995-present
  - 获取方式: GENESIS-Online (31231-0001)
  - **评估**: ⚠️ 住宅面积可得，非住宅面积需从 Nichtwohngebaude 统计中拼接

#### 关键困难
- **两德统一断裂**: 1990年前后数据口径不连续。1950-1990为西德数据，1991年起为统一德国。需要在分析中处理这一结构性断裂，建议以1991年为起点或对西德数据做明确标注
- **市场价值 vs 重置成本**: Destatis 以重置成本为主，非严格市场价值。德意志联邦银行的市场价值估计时间较短

#### 数据时间跨度
| 变量 | 起始年份 | 终止年份 | 频率 |
|------|---------|---------|------|
| 不动产净存量 (Destatis) | 1991 (西德1950) | 2023 | 年度 |
| 建设投资 (Destatis GFCF) | 1991 (西德1950) | 2024 | 年度/季度 |
| 新建vs改造 (建设活动统计) | 1991 | 2024 | 年度 |
| GDP结构 (Destatis) | 1950 | 2024 | 年度 |
| 城镇化率 (WB) | 1960 | 2024 | 年度 |

---

### 3.4 日本 (Japan) — 东亚最重要的对标国

#### 分子：不动产资产市值 V(t)
- **首选来源**: 内阁府 SNA — 国民経済計算 (System of National Accounts)
  - ストック編 (Stock accounts): 非金融資産残高
  - 包含 住宅 (dwellings) 和 その他の建物・構築物 (other buildings and structures)
  - 以 当期価額 (current prices) 和 連鎖価額 (chained prices) 两种口径
  - 时间跨度: 1994-present（2008SNA基准），1980-2004（1993SNA基准）
  - 获取方式: https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/files_kakuhou.html
  - **评估**: ⚠️ 可用但需拼接两套SNA基准。日本SNA资产账户以重置成本为主
- **补充来源**: 日本不動産研究所 (Japan Real Estate Institute, JREI)
  - 市街地価格指数 (Urban Land Price Index): 1936-present
  - 获取方式: 部分公开，完整序列需付费
- **补充来源**: 国土交通省 — 土地白書/地価公示
  - 全国地価動向 (official land prices)
  - 时间跨度: 1970-present
  - 获取方式: https://www.mlit.go.jp/totikensangyo/totikensangyo_fr4_000043.html
  - **评估**: ⚠️ 地価数据可用于调整 SNA 存量到市场价值
- **学术来源**: 野村資本市場研究所; Nomura Research — 日本不動産総市場価値估计
  - 参考 Karato (2003) 等对日本住宅资本存量的市场价值估计

**构建策略**: 以 SNA 非金融资产存量(重置成本)为基础，用地価公示/市街地価格指数进行市场价值调整。这一方法在日本学界有成熟先例（参考国土交通省「土地関連資料集」中的方法论）。

#### 分母：累计建设投资 K(t)
- **首选来源**: 内阁府 SNA — フロー編 (Flow accounts)
  - 総固定資本形成 (GFCF): 住宅 + 非住宅建物 + 構築物（土木）
  - 时间跨度: 1955-present（68SNA/93SNA/08SNA 拼接）
  - 获取方式: 内阁府 SNA 数据下载页面
  - **评估**: ✅ 直接可用，长时序
- **国土交通省**: 建設総合統計 (Construction Statistics)
  - 建設投資見通し (Construction Investment Forecast) 年度报告
  - 时间跨度: 1960-present
  - 获取方式: https://www.mlit.go.jp/sogoseisaku/jouhouka/sosei_jouhouka_tk_000007.html
  - **评估**: ✅ 可作交叉验证

#### 新建 vs 更新区分
- **国土交通省 建設総合統計**
  - 明确区分: 新設 (new construction) vs. 維持修繕 (maintenance and repair)
  - 进一步区分: 住宅/非住宅/土木工事
  - 时间跨度: 1960-present
  - **评估**: ✅ 这是关键优势。日本从1960年代就有新建vs维修的统计区分，可完整观察从新建主导到维修主导的转折点
- **建築着工統計 (Building Starts Statistics)**
  - 按用途和新建/増改築分类
  - 时间跨度: 1951-present
  - 获取方式: e-Stat (https://www.e-stat.go.jp/)

**特别价值**: 日本约在2000年代中期，维持修繕投资占比超过新建投资，这一"交叉点"正是 Urban Q 框架要捕捉的关键相变节点。

#### 建筑存量面积
- **総務省 住宅・土地統計調査 (Housing and Land Survey)**
  - 住宅存量数量和面积
  - 时间跨度: 1948-present（每5年）
  - 获取方式: e-Stat
  - **评估**: ✅ 长时序，每5年一次，中间年份需插值
- **国土交通省 建築ストック統計**
  - 非住宅建筑存量面积
  - 时间跨度: 2003-present
  - **评估**: ⚠️ 时间较短

#### 数据时间跨度
| 变量 | 起始年份 | 终止年份 | 频率 |
|------|---------|---------|------|
| 不动产存量 (SNA) | 1980/1994 | 2023 | 年度 |
| 建设投资 (SNA GFCF) | 1955 | 2024 | 年度/季度 |
| 新建vs维修 (建設総合統計) | 1960 | 2024 | 年度 |
| 地価指数 (JREI/国交省) | 1936/1970 | 2024 | 年度 |
| 建筑面积 (住宅土地統計) | 1948 | 2023 | 5年一次 |
| GDP结构 (SNA) | 1955 | 2024 | 年度 |
| 城镇化率 (WB/UN) | 1960 | 2024 | 年度 |

---

### 3.5 韩国 (South Korea) — 快速工业化的对标

#### 分子：不动产资产市值 V(t)
- **首选来源**: 韩国银行 (Bank of Korea, BOK) — 国民対照表 (National Balance Sheet)
  - 非금융자산 (Non-financial assets): 건물 (buildings) + 구축물 (structures)
  - 以 시장가격 (market prices) 和 취득원가 (acquisition cost) 两种口径
  - 时间跨度: 2000-present（一致口径），部分变量回溯至 1995
  - 获取方式: ECOS 经济统计系统 (https://ecos.bok.or.kr/)
  - **评估**: ⚠️ 可用但起始年份较晚（2000年），覆盖不了韩国高速城镇化期（1970-1990年代）
- **补充来源**: 国토交通部 — 부동산 가격공시 (Official Land/Housing Prices)
  - 全国地价指数: 1975-present
  - 住宅价格指数: 1986-present (KB국민은행 주택가격지수)
  - 获取方式: https://www.reb.or.kr/ (한국부동산원, Korea Real Estate Board)
  - **评估**: ⚠️ 价格指数可用于延伸存量估计，但需构建面积基数
- **学术来源**: Kim & Park (2016); 韩国开发研究院 (KDI) 工作论文中的资本存量估计

#### 分母：累计建设投资 K(t)
- **首选来源**: 韩国银行 — 国民所得統計 (National Income Statistics)
  - 총고정자본형성 (GFCF): 건설투자 (Construction investment)
  - 细分: 건물건설 (buildings) + 토목건설 (civil engineering)
  - 时间跨度: 1970-present
  - 获取方式: ECOS (https://ecos.bok.or.kr/)
  - **评估**: ✅ 直接可用，时序较长
- **OECD.Stat**: 一致口径 GFCF by asset type, 1970-present

#### 新建 vs 更新区分
- **국토交通部 건축물 통계 (Building Statistics)**
  - 건축허가 (permits): 区分 신축 (new) vs. 증축/개축/대수선 (expansion/rebuild/major repair)
  - 时间跨度: 1990-present
  - 获取方式: 국가통계포털 KOSIS (https://kosis.kr/)
  - **评估**: ⚠️ 许可数据可得，但投资金额的新建/更新拆分不如日本清晰
- **한국건설산업연구원 (KICT)**: 建设投资预测报告中有新建/维修的拆分，但以研究报告形式发表，非公开数据库

#### 建筑存量面积
- **국토交通部 건축물대장 (Building Registry)**
  - 全国建筑物数量和面积的逐年登记
  - 时间跨度: 2000-present（电子化后）
  - 获取方式: KOSIS
  - **评估**: ✅ 登记制度完善

#### 关键困难
- **分子端时间跨度不足**: BOK 国民对照表仅从2000年起提供一致口径数据，难以覆盖韩国1970-1990年代的高速城镇化期。这是与日本相比的最大劣势
- **解决方案**: 可用 GFCF 存量（PIM 法）+ 地价指数调整的方法，将分子回溯至1970年代。学术上可参考 Pyo, Ha & Kim (2006) "Estimates of Fixed Reproducible Tangible Assets in the Republic of Korea" (KDI)

#### 数据时间跨度
| 变量 | 起始年份 | 终止年份 | 频率 |
|------|---------|---------|------|
| 不动产存量 (BOK) | 2000 | 2023 | 年度 |
| 建设投资 (BOK GFCF) | 1970 | 2024 | 年度/季度 |
| 地价指数 (KREB) | 1975 | 2024 | 月度 |
| 建筑许可新建/改建 (KOSIS) | 1990 | 2024 | 年度 |
| 建筑存量面积 (建筑台帐) | 2000 | 2024 | 年度 |
| GDP结构 (BOK) | 1953 | 2024 | 年度 |
| 城镇化率 (WB/UN) | 1960 | 2024 | 年度 |

---

### 3.6 中国 — 从 six-curves 项目复用

#### 可直接复用的数据（来自 six-curves-urban-transition/02-data/）

| six-curves 文件 | Urban Q 对应变量 | 复用方式 |
|----------------|-----------------|---------|
| `c1_urbanization_rate_NBS_1949-2024.csv` | 城镇化率 | 直接复用 |
| `c6_real_estate_investment_NBS_1987-2024.csv` | K(t) 分母的组成部分 | 直接复用 |
| `c6_infrastructure_investment_NBS_1990-2024.csv` | K(t) 分母的组成部分 | 直接复用 |
| `c3_new_construction_starts_NBS_1985-2024.csv` | 新建面积 (辅助变量) | 直接复用 |
| `c5_residential_price_NBS_1998-2024.csv` | V(t) 代理的组成部分 | 直接复用 |
| `c5_land_transfer_revenue_MOF_1999-2024.csv` | 土地价值代理 | 参考 |
| `c2_urban_built_area_MOHURD_1981-2023.csv` | 建筑存量面积 | 直接复用 |
| `c4_shantytown_renovation_MOHURD_2008-2024.csv` | 新建vs更新区分 | 直接复用 |
| `background_gdp_NBS_1978-2024.csv` | GDP结构 | 直接复用 |

#### 需要补充的中国数据

| 缺失数据 | 说明 | 建议来源 |
|----------|------|---------|
| 国民资产负债表 — 非金融资产 | V(t) 的官方口径 | 中国社科院国家资产负债表研究中心 (Li Yang et al.); 国家统计局2019年起试编制 |
| 城镇固定资产投资总额 | K(t) 的完整分母 | 国家统计局，已有部分在c6文件中 |
| 三产GDP比重 | six-curves GDP文件中含总量但需补充产业结构 | 国家统计局，公开可下载 |

#### 分子特别说明
中国不动产总市值没有官方统一统计。现有最佳来源：
1. **中国社科院《中国国家资产负债表》** (Li Yang, Zhang Xiaojing et al.) — 提供 2000-2019 年的住宅资产和建筑资产市值估计
2. **方正证券/中金公司等机构研报** — 基于住宅面积×均价的估算（约400-500万亿元，2023年）
3. **PIM 构建** — six-curves 项目的 codebook 中已记录方法论（参考 Bai et al. 2006; 张军等 2004）

---

## 四、跨国可比数据源（OECD / World Bank / UN）

以下国际数据库可提供统一口径的跨国可比数据，减少逐国拼接的工作量：

### 4.1 OECD.Stat

| 数据集 | 变量 | 覆盖国家 | 时间跨度 | 可得性 |
|--------|------|---------|---------|--------|
| SNA Table 9: Non-financial assets | 非金融资产存量（按类型） | OECD成员国（含日韩） | 因国家而异，多为1995+ | ⚠️ 部分国家上报不完整 |
| SNA Table 8: Capital formation | GFCF by asset type | OECD全覆盖 | 1970-present | ✅ 覆盖率高 |
| Affordable Housing Database | 住房存量、housing investment | OECD | 2000-present | ⚠️ 变量有限 |

**关键发现**: OECD.Stat 的 SNA Table 9 (Non-financial assets by type) 理论上最为理想，但实际上报情况参差不齐。美国、英国、德国上报较完整；日本部分年份缺失；韩国上报起始年份较晚。建议以此为基准框架，辅以各国国内数据源补充。

### 4.2 World Bank / UN

| 数据集 | 变量 | 用途 |
|--------|------|------|
| WDI: SP.URB.TOTL.IN.ZS | 城镇化率 | 六国统一口径, 1960-2024 |
| WDI: NE.GDI.FTOT.ZS | GFCF/GDP (%) | 投资强度跨国比较 |
| WDI: NV.SRV.TOTL.ZS / NV.IND.TOTL.ZS | 产业结构 | 三产GDP结构 |
| UN WUP | 城镇化率 (含预测) | 含历史预测 |
| Penn World Table 10.0+ | Capital stock at current PPPs | K(t) 的跨国可比版本 |

### 4.3 Penn World Table (PWT)

**特别推荐**: PWT 提供了基于 PPP 调整的跨国资本存量序列 (`ck` 和 `cn` 变量），覆盖 1950-2019。虽然是总资本存量（含设备和知识产权），但结合各国 GFCF 中建筑投资占比，可合理估算建筑资本存量。

获取方式: https://www.rug.nl/ggdc/productivity/pwt/

---

## 五、关键困难与解决方案

### 困难 1: V(t) 的"市场价值"vs"重置成本"口径差异

**问题**: 不同国家的 SNA 非金融资产采用不同估价方法。美国 BEA 和英国 ONS 采用 current-cost net stock（近似市场价值）；德国 Destatis 以重置成本为主；日本和韩国兼有两种口径但市场价值调整方法不同。

**解决方案**:
1. **基准方案**: 统一使用 SNA current-cost net stock 作为 V(t) 的代理，明确说明这是"重置成本近似"而非严格市场价值
2. **敏感性分析**: 对美英日三国，分别用"重置成本口径"和"市场价值口径"（后者用地产价格指数调整）计算 Urban Q，检验结论的稳健性
3. **论文讨论**: 在方法部分讨论估价差异，引用 Piketty & Zucman (2014) "Capital is Back" 中关于 wealth-income ratio 的跨国比较方法论

### 困难 2: 时间跨度不一致

**问题**: 各国可得数据的起始年份差异大。日本 GFCF 可追溯至 1955 年，但韩国资产存量仅从 2000 年起。

**解决方案**:
1. **核心分析窗口**: 设定统一分析期为 **1980-2024**（或 1990-2024），确保所有国家数据可得
2. **延伸分析**: 对日本和美国，延伸至 1960 年代以展示完整的城镇化-资产化周期
3. **PIM 回溯**: 对韩国等数据起始晚的国家，用 PIM 法基于 GFCF 序列回溯估算资本存量

### 困难 3: 新建 vs 更新投资的跨国可比性

**问题**: 各国对"更新/维修/改造"的统计定义不一致。日本区分 "新設" vs "維持修繕"；英国区分 "New work" vs "Repair and maintenance"；中国几乎没有这一区分。

**解决方案**:
1. 以日本和英国为"标杆国家"，它们的新建/维修区分最清晰
2. 对中国和韩国，采用 six-curves 项目中的残差法：Renewal = Total - New
3. 在方法论中明确各国定义差异，避免直接比较绝对水平，而是比较 **趋势转折点** 和 **相对比例变化**

### 困难 4: 中国数据的特殊挑战

**问题**: 中国没有官方的国民资产负债表中不动产市值统计；土地所有制差异使得 V(t) 的定义不同于私有制国家。

**解决方案**:
1. V(t) 采用多种代理指标：(a) 社科院国家资产负债表, (b) PIM 法重置成本估计, (c) 住房面积×均价的市场价值估计
2. 讨论中国土地国有制对 Urban Q 解释的影响（土地价值是否纳入 V(t)）
3. 做排除土地价值的敏感性分析

### 困难 5: 通胀调整与PPP转换

**问题**: 跨国比较需要处理价格因素。Urban Q 本身是比值，若分子分母采用同一价格体系（如当期价格），则通胀自然抵消。但跨国 Q 值水平比较需要考虑 PPP。

**解决方案**:
1. **国内时序**: 使用名义值（当期价格）计算各国 Q(t)，分子分母在同一价格体系下比值已消除通胀
2. **跨国比较**: 不比较 Q 值水平，而是比较 Q 值的 **动态轨迹** 和 **拐点位置**——这不受 PPP 影响
3. 如需水平比较，使用 PWT 的 PPP 调整资本存量

---

## 六、推荐的最小可行数据集 (MVP Dataset)

### 6.1 MVP 定义

以最小的数据收集成本，产出一组可用于 Nature 正刊级别论文的 Urban Q 跨国比较。

### 6.2 MVP 国家选择

| 优先级 | 国家 | 理由 | 数据获取难度 |
|--------|------|------|------------|
| 必须 | 中国 | 核心研究对象 | 中（需构建 V(t)） |
| 必须 | 日本 | 完成了完整 expansion-to-renewal 转型的东亚对标 | 低-中 |
| 必须 | 美国 | 数据最完善，成熟经济体对标 | 低 |
| 高度推荐 | 英国 | 数据质量高，城镇化历史最长 | 低 |
| 推荐 | 韩国 | 东亚发展型国家，与中国发展阶段最近 | 中（V(t) 需构建） |
| 可选 | 德国 | 欧洲大陆代表，两德统一提供"自然实验" | 低-中 |

### 6.3 MVP 变量组合

**核心变量（必须有）**:
1. **V(t)**: SNA 非金融资产中的建筑物存量（current-cost net stock）
2. **K(t)**: GFCF 中建筑投资的累积（或直接使用 SNA 资本存量总量口径）
3. **Urban Q = V(t)/K(t)**: 对每国计算年度序列

**辅助变量（强化故事线）**:
4. **New/Renewal ratio**: 新建投资占比 vs 维修改造投资占比的时序
5. **Urbanization rate**: World Bank 统一口径
6. **GDP per capita (PPP)**: 用于确定各国在"发展阶段"坐标系中的位置

### 6.4 MVP 数据获取行动计划

| 步骤 | 行动 | 数据源 | 预计耗时 |
|------|------|--------|---------|
| 1 | 下载 OECD.Stat SNA Table 9 (Non-financial assets) 和 Table 8 (GFCF) | OECD.Stat | 0.5天 |
| 2 | 下载美国 BEA Fixed Assets Tables | BEA website | 0.5天 |
| 3 | 下载英国 ONS National Balance Sheet 和 Construction Output | ONS website | 0.5天 |
| 4 | 下载日本内阁府 SNA ストック编 和 国交省建設総合統計 | ESRI/MLIT websites | 1天（含日文界面） |
| 5 | 下载韩国 BOK 国民对照表 和 ECOS 建设投资数据 | BOK ECOS | 0.5天 |
| 6 | 下载德国 Destatis VGR 资产存量 和 建设活动统计 | GENESIS-Online | 0.5天（含德文界面） |
| 7 | 复用 six-curves 中国数据，补充社科院资产负债表数据 | 已有 + 社科院报告 | 1天 |
| 8 | 下载 World Bank WDI (城镇化率、GDP结构、GFCF/GDP) | WDI API | 0.5天 |
| 9 | 数据清洗、口径统一、构建 Urban Q 序列 | R 脚本 | 2-3天 |
| 10 | 敏感性分析（不同 V(t) 口径） | R 脚本 | 1天 |

**总计预估**: 7-8 个工作日可完成 MVP 数据集构建。

### 6.5 MVP 的替代简化方案

如果时间紧迫，可考虑以下 **极简方案**，仅使用 OECD.Stat 统一口径数据：

- **V(t)**: OECD SNA Table 9 的 AN.111 + AN.112 net stock（覆盖不完整的国家用 PWT 补充）
- **K(t)**: OECD SNA Table 8 的 AN.111 + AN.112 GFCF 累积（或 PWT `cn` 变量）
- **中国**: 使用 PWT + six-curves 数据构建

这一方案可在 **3-4 个工作日** 内完成，但数据深度和精度不如完整方案。对于 Nature 正刊，建议采用完整方案并配合敏感性分析。

---

## 七、数据质量评估与注意事项

### 7.1 各国 SNA 基准修订

| 国家 | 当前 SNA 版本 | 基准年 | 注意事项 |
|------|-------------|--------|---------|
| 美国 | 2008 SNA | 2017 | BEA 定期修订历史数据 |
| 英国 | 2008 SNA (ESA 2010) | 2019 | Blue Book 修订 |
| 德国 | 2008 SNA (ESA 2010) | 2019 | VGR 大修订 |
| 日本 | 2008 SNA | 2015 | 2016年从93SNA切换至08SNA |
| 韩国 | 2008 SNA | 2020 | 2024年发布新基准 |
| 中国 | 2008 SNA (部分) | 2020 | SNA 资产账户仍在完善中 |

### 7.2 数据引用建议

在 Nature 正刊论文中，建议：
1. 主体分析使用各国官方统计机构的一手数据（BEA, ONS, Destatis, ESRI, BOK, NBS）
2. 跨国比较使用 OECD.Stat 或 PWT 确保口径一致性
3. 在 Supplementary Materials 中提供完整的数据来源表和数据处理脚本
4. 在 Methods 部分用 1-2 段讨论估价方法差异和稳健性

---

## 八、结论与建议

### 可行性判断: **可行，且具有重要学术价值**

1. **数据基本面良好**: 五个目标国家的核心变量（资产存量、建设投资）均可从官方统计中获得，无需依赖商业数据库
2. **日本是最关键的对标**: 日本同时具备长时序的资产数据和清晰的新建/维修区分，且已完成从扩张到更新的转型，是验证 Urban Q 框架最理想的案例
3. **中国的挑战是机遇**: 中国在 V(t) 端的统计空白，恰好证明了建立 Urban Q 监测体系的政策必要性——这可以成为论文 policy implications 的一部分
4. **时间窗口建议**: 核心分析期设为 1980-2024（或 1990-2024），涵盖各国主要的城镇化和资产化阶段

### 下一步行动
1. 启动 MVP 数据获取行动计划（见 6.4）
2. 编写数据下载和清洗的 R 脚本框架
3. 与 research-director 确认是否需要扩展至更多 OECD 国家
4. 确定 V(t) 估价口径的最终方案

---

*本报告将随数据获取进展持续更新。*
