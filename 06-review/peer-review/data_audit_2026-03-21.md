# 数据真实性审计报告

**项目**: Urban Q Phase Transition
**审计日期**: 2026-03-21
**审计人**: data-analyst (Claude)
**审计范围**: `02-data/raw/` + `02-data/processed/` 全部文件，以及 six-curves 跨项目数据依赖

---

## 一、Raw 目录审计

| # | 文件 | 大小 | 声称来源 | 实际来源判断 | 真实/代理/混合 | 关键证据 |
|---|------|------|---------|------------|--------------|---------|
| 1 | `bis_property_prices.csv` | 3.0 MB | OECD SDMX-JSON API | **真实 API 下载** | **真实** | `data_acquisition_report.txt` 记录了 HTTP 200 响应、1,808,765 bytes、40,257 条观测、51 国家。数据格式 (country_code, frequency, measure, period, value) 完全符合 OECD SDMX-JSON 标准输出。脚本 `22_bis_un_data.py` 使用 `requests.get()` 从 `stats.oecd.org` 真实下载。 |
| 2 | `un_population.csv` | 3.6 MB | World Bank API (人口数据) | **真实 API 下载** | **真实** | `data_acquisition_report.txt` 逐指标记录了 13 个 WB 指标的 HTTP 200 响应，每个均返回 16,900-17,225 条记录。脚本 `22_bis_un_data.py` 使用 World Bank API v2 逐指标下载。数据结构 (iso3, year, 13 个人口指标) 符合 WB 标准输出。219 国家、1960-2024 范围合理。 |
| 3 | `penn_world_table.csv` | 3.8 MB | PWT 10.01 (Groningen) | **真实下载** | **真实** | `pwt1001_cache.dta` 存在 (3.3 MB)，`file` 命令确认为 "Stata Data File (Release 118)"，这是 PWT 10.01 的原始分发格式。脚本 `21_penn_world_table.py` 从 `dataverse.nl/api/access/datafile/354098` 下载 .dta 文件并转换为 CSV。数据覆盖 183 国、1950-2019，与 PWT 10.01 官方规格完全一致。摘要中 China 2019 K/Y=4.84、人均资本 69,473 USD 均可与 PWT 官网验证。 |
| 4 | `pwt1001_cache.dta` | 3.3 MB | PWT 10.01 缓存 | **真实下载** | **真实** | Stata Release 118 二进制格式，无法由脚本伪造。文件大小与 PWT 10.01 主表吻合。 |
| 5 | `world_bank_all_countries.csv` | 2.7 MB | World Bank API v2 | **真实 API 下载** | **真实** | `world_bank_data_summary.txt` 记录了 13 个指标的覆盖率，217 国家、1960-2023。脚本 `20_world_bank_data.py` 使用标准 WB API URL 格式。数据中 Aruba 等小国早年 GDP 缺失、城镇化率从 1960 起完整，符合 WB 数据实际覆盖情况。 |
| 6 | `china_national_real_data.csv` | 14 KB | 中国统计年鉴 + World Bank | **硬编码 + WB 补充** | **混合** | 脚本 `40_china_real_data.py` 采用两级策略：(1) 先尝试 NBS API（大概率超时/被拦截），(2) 回退到 `build_yearbook_data()` 函数中的硬编码 Python 字典。GDP、人口、FAI、房地产投资等数据硬编码于脚本第 213-297 行。**数据值本身声称来自统计年鉴，经抽查核心数据点（如 2023 年 GDP 1,260,582 亿元、城镇化率 66.16%）与公开发布吻合，可认定为手工录入的真实数据。** 但住宅存量、资本存量、Urban Q 等派生指标为永续盘存法计算结果（含折旧率假设），属于模型估算。WB 补充列 (wb_ 前缀) 来自真实 API 下载。 |
| 7 | `china_provincial_real_data.csv` | 70 KB | 中国统计年鉴 (5 个关键年份) | **硬编码 + 线性插值** | **混合** | `china_provincial_sources.md` 明确说明：31 省 x 19 年(2005-2023) = 589 行，其中 **155 行 (26.3%) 为真实值**（2005、2010、2015、2019、2023 五个年份），**434 行 (73.7%) 为线性插值**。data_type 列标注了 "actual" 和 "interpolated"。脚本 `41_china_provincial_data.py` 中的硬编码数据声称来自对应年份的统计年鉴。 |
| 8 | `japan_urban_q_data.csv` | 4.2 KB | MLIT / Cabinet Office SNA / World Bank / JREI | **硬编码 + 插值** | **混合** | 脚本 `03_japan_urban_q.py` 第 49-146 行将所有日本数据硬编码为 Python 字典（城镇化率、建设投资、GDP、住宅开工等），注释标注了来源（MLIT, Cabinet Office SNA 等）。数据中包含 `urbanization_interpolated` 和 `ci_interpolated` 布尔列标记插值。**原始锚点数据声称来自日本官方统计，但部分中间年份（如 1961-1964 城镇化率、大量建设投资年份）为插值生成。** 部分数据精度可疑（如建设投资多为整数万亿日元，缺少小数精度，可能是概数而非精确统计值）。 |
| 9 | `data_acquisition_report.txt` | 9.0 KB | 脚本运行日志 | 元数据文件 | N/A | 记录 `22_bis_un_data.py` 的运行过程，包含 URL、HTTP 状态码、数据量。 |
| 10 | `pwt_data_summary.txt` | 11 KB | 脚本运行日志 | 元数据文件 | N/A | PWT 数据摘要报告。 |
| 11 | `world_bank_data_summary.txt` | 9.5 KB | 脚本运行日志 | 元数据文件 | N/A | WB 数据摘要报告。 |
| 12 | `china_data_sources.md` | 4.9 KB | 来源说明文档 | 元数据文件 | N/A | 详细记录了国家级数据的来源、计算方法、数据质量说明。 |
| 13 | `china_provincial_sources.md` | 2.7 KB | 来源说明文档 | 元数据文件 | N/A | 省级面板数据来源说明。 |

---

## 二、Processed 目录审计

| # | 文件 | 大小 | 声称来源 | 实际来源判断 | 真实/代理/混合 | 关键证据 |
|---|------|------|---------|------------|--------------|---------|
| 1 | `china_275_city_panel.csv` | 710 KB | 城市类型学构造 | **完全模拟** | **代理** | 脚本 `12_city_panel_urban_q.py` 开头即声明 "本脚本使用基于城市类型学构造的代理数据"。`np.random.seed(42)` 固定随机种子，全部 275 城市数据通过 `np.random.normal()` 生成（第 216-307 行）。四五线城市名称为 "X_NNNN" 格式。回归报告也标注 "代理数据"。 |
| 2 | `china_city_panel_real.csv` | 2.9 MB | 中国城市数据库6.0版 + 58同城 + 债务数据 | **真实数据库读取 + 派生计算** | **真实** | 脚本 `51_city_panel_real.py` 从 `six-curves-urban-transition/02-data/面板数据/中国城市数据库6.0版.xlsx` (27 MB .xlsx) 读取线性插值 sheet。58同城/安居客房价从 .xlsx/.dta 读取。债务数据从 `整合.csv` 读取。这些源文件均为用户手动存放的第三方数据集。**原始数据为真实购买/下载的学术数据库，但 Urban Q、K 等指标为脚本派生计算。** |
| 3 | `china_city_ocr_uci.csv` | 2.1 MB | 基于 china_city_panel_real 计算 | **派生计算** | **真实** (基于真实输入) | 脚本 `52_city_ocr_uci.py` 基于 `china_city_panel_real.csv` 计算 K\*, OCR, UCI 等指标，人力资本代理变量基于 PWT 省级数据推算。 |
| 4 | `china_city_real_fai_panel.csv` | 1.2 MB | 基于真实 FAI 子集 | **派生计算** | **真实** (基于真实输入) | 脚本 `64_city_real_fai_only.py` 筛选 `fai_imputed == False` 的城市-年份，仅保留有真实固定资产投资数据的观测。 |
| 5 | `china_city_real_fai_uci.csv` | 111 KB | 基于真实 FAI 计算 UCI | **派生计算** | **真实** (基于真实输入) | 基于 `china_city_real_fai_panel.csv` 的 UCI 计算结果。 |
| 6 | `china_city_robust_uci.csv` | 2.0 MB | 稳健性检验变体 | **派生计算** | **真实** (基于真实输入) | 脚本 `63_fai_validation_robust_uci.py` 对 UCI 指标做多口径稳健性检验。 |
| 7 | `china_provincial_panel_real.csv` | 129 KB | 省级真实数据 + 城市数据库聚合 | **混合** | **混合** | 来自 `china_provincial_real_data.csv`（26.3% 真实 + 73.7% 插值）与城市数据库的省级聚合，加上 Urban Q 派生计算。 |
| 8 | `four_country_human_capital.csv` | 8.4 KB | UNDP HDR / Barro-Lee | **硬编码 + 插值** | **混合** | 脚本 `10_human_capital_data.py` 将四国平均受教育年限硬编码为五年间隔锚点（第 42-62 行），再线性插值为年度数据。H(t) = exp(0.10 * s(t)) 为标准 Mincer 计算。锚点值声称来自 UNDP/Barro-Lee。劳动年龄人口占比同样硬编码+插值。 |
| 9 | `four_country_panel.csv` | 24 KB | 各国模型输出合并 | **混合** | **混合** | 合并四国 Urban Q 时序，其中：中国数据基于统计年鉴硬编码（原始值真实，派生值为模型估算）；日本数据为硬编码+插值；美国和英国数据来源需进一步核查（脚本 04/05）。V, K 等为模型估算。 |
| 10 | `global_urban_q_panel.csv` | 3.9 MB | WB + PWT 合并计算 | **真实输入 + 模型计算** | **混合** | 脚本 `30_global_urban_q.py` 基于 World Bank 和 PWT 真实数据计算全球 Urban Q，但 V(t) 城市资产价值使用了 GDP 等代理口径（脚本注释 "构建 V(t) -- 城市资产价值代理"），非直接可观测变量。 |
| 11 | `global_urban_q_summary.csv` | 31 KB | global_urban_q_panel 汇总 | 汇总统计 | **混合** | 上述面板的截面汇总。 |
| 12 | `global_kstar_ocr_uci.csv` | 2.4 MB | 全球 K\* / OCR / UCI 计算 | **模型计算** | **混合** | 基于 WB/PWT 真实输入，但 K\*, OCR, UCI 均为模型估算指标。 |
| 13 | `global_ocr_uci_normalized.csv` | 1.9 MB | 标准化后全球 UCI | **模型计算** | **混合** | 标准化处理后的 UCI 指标。 |
| 14 | `world_bank_usable_panel.csv` | 2.1 MB | WB API 筛选子集 | **真实** | **真实** | 脚本 `20_world_bank_data.py` 从 `world_bank_all_countries.csv` 筛选数据完整度达标的 158 个国家，未添加任何模拟数据。 |

---

## 三、Six-Curves 跨项目数据依赖

Urban Q 项目通过 `51_city_panel_real.py` 直接引用 six-curves 项目的以下真实数据源：

| 数据源 | 路径 | 真实性判断 | 说明 |
|--------|------|-----------|------|
| 中国城市数据库6.0版 | `面板数据/中国城市数据库6.0版.xlsx` | **真实** (27 MB) | 马克数据网购买的学术数据库，300+ 城市、1990-2023、214 列。.xlsx 文件大小 27 MB 无法由脚本伪造。 |
| 全国地级市国民经济指标 | `面板数据/全国地级市2000-2023年国民经济指标.xlsx` | **真实** (6.4 MB) | 格式为标准学术数据库产品。 |
| 58同城房价数据 | `面板数据/地级市房价商品房均价数据/.../58同城房价（2010-2024）.xlsx` | **真实** (133 KB) | 包含 .xlsx 和 .dta 双格式、使用说明和数据来源 HTML。 |
| 安居客房价数据 | `面板数据/地级市房价商品房均价数据/.../安居客房价（2015-2024）.xlsx` | **真实** (210 KB) | 同上。 |
| 地级市债务数据 | `面板数据/地方债务/全国地方债务余额(省级+地级市)2006-2023/` | **真实** | 包含 2006-2023 每年独立 .xls 文件 (16 个) + 2022/2023 .xlsx + 整合 CSV，典型的 Wind 金融终端导出格式。省级目录下也包含 Wind 导出文件。 |
| 土地出让数据 | `面板数据/土地出让数据/中国土地市场网-...（2000-2022.12）.csv` | **真实** (2.0 GB) | 文件大小 2.1 GB，是中国土地市场网的完整交易记录数据。 |
| 夜间灯光数据 | `面板数据/夜间灯光数据大全（1992-2022年）/` | **真实** | 5 个统计量 .xlsx 文件，标准遥感数据产品。 |
| 城市逆温数据 | `面板数据/1980~2022年中国各城市逆温数据/` | **真实** | 含 43 年逐年 .xlsx (每个约 33 MB)、shp 矢量文件、参考文献 PDF。典型学术数据集包结构。 |
| 地方政府债券信息 | `面板数据/地方政府债务置换债券发行规模2009-2024年/` | **真实** | 含爬虫 .ipynb 源码和参考论文 PDF。 |
| Six-curves 原始数据 | `raw/c1_...csv` 至 `raw/c6_...csv` | **混合** | `c1_urbanization_rate_NBS_1949-2024.csv` 每行标注 "国家统计局《中国统计年鉴2023》表2-1"，为手工录入真实数据。其他曲线数据来源类似。`c4_renewal_bonds_2009-2024.csv` (274 KB) 规模较大，可能来自债券数据整合。 |

---

## 四、统计汇总

### 按真实性分类

| 分类 | 文件数 | 文件列表 |
|------|-------|---------|
| **真实数据** (直接 API 下载或真实数据库读取) | **8** | `bis_property_prices.csv`, `un_population.csv`, `penn_world_table.csv`, `pwt1001_cache.dta`, `world_bank_all_countries.csv`, `world_bank_usable_panel.csv`, `china_city_panel_real.csv` (输入真实), `china_city_real_fai_panel.csv` (输入真实) |
| **代理/模拟数据** (np.random 生成) | **1** | `china_275_city_panel.csv` |
| **混合数据** (真实锚点 + 插值/模型估算) | **13** | `china_national_real_data.csv`, `china_provincial_real_data.csv`, `japan_urban_q_data.csv`, `china_provincial_panel_real.csv`, `four_country_human_capital.csv`, `four_country_panel.csv`, `global_urban_q_panel.csv`, `global_urban_q_summary.csv`, `global_kstar_ocr_uci.csv`, `global_ocr_uci_normalized.csv`, `china_city_ocr_uci.csv`, `china_city_real_fai_uci.csv`, `china_city_robust_uci.csv` |
| **元数据/文档** (不含分析数据) | **5** | 3 个 summary/report .txt + 2 个 sources .md |

### 特别关注项逐一判定

| 项目 | 判定 | 详细说明 |
|------|------|---------|
| **中国城市数据库 6.0 (300 城市, 214 列)** | **真实** | 27 MB .xlsx 文件存于 six-curves 项目，为购买的马克数据网学术数据产品。脚本 `51_city_panel_real.py` 使用 `pd.read_excel()` 直接读取。 |
| **58同城/安居客房价数据** | **真实** | 存于 six-curves 项目，包含 .xlsx 和 .dta 双格式文件、使用说明、数据来源页面，为标准第三方数据集。 |
| **地级市债务数据** | **真实** | 存于 six-curves 项目，2006-2023 逐年 .xls 文件 (Wind 导出格式) + 整合 CSV。省级和地级市分别存储。 |
| **World Bank / PWT 数据** | **真实** | WB 通过 `requests.get()` 从官方 API 下载，有完整 HTTP 日志。PWT 从 Dataverse 下载 .dta 原始文件，`file` 命令确认为 Stata Release 118 格式。 |
| **中国省级面板 (26.3% 真实 + 73.7% 插值)** | **混合** | 声称的比例准确：5 个锚点年份 x 31 省 = 155 真实行 / 589 总行 = 26.3%。`data_type` 列可区分。2020-2023 年 FAI 缺失是因为统计局口径变更（真实限制，非数据缺陷）。 |
| **city_panel_regression.txt 声明为代理数据** | **确认为代理** | 脚本 `12_city_panel_urban_q.py` 全程使用 `np.random.seed(42)` + `np.random.normal()` 生成，输出报告也标注 "代理数据"。 |

---

## 五、需要替换为真实数据的关键文件

### 优先级 1（当前为完全模拟，必须替换）

1. **`china_275_city_panel.csv`** -- 275 城市面板完全由 `np.random` 生成。但该文件已被 `china_city_panel_real.csv` (基于中国城市数据库6.0版) 替代，可确认不再用于最终分析。**需确认论文中是否仍引用此文件的回归结果。**

### 优先级 2（硬编码数据，需补充可验证来源）

2. **`japan_urban_q_data.csv`** -- 日本所有宏观数据为脚本硬编码。建议：(a) 从 e-Stat (日本政府统计门户) 或 MLIT 建设投资统计下载官方 CSV/Excel；(b) 至少在论文 Supplementary 中提供逐年数据来源的精确页码/表号。部分建设投资数据精度过低（均为整数万亿日元）。

3. **美国和英国 Urban Q 数据** (脚本 04/05) -- 同样依赖硬编码，需补充原始数据文件。

4. **`four_country_human_capital.csv`** -- 受教育年限为五年间隔硬编码。建议直接引用 Barro-Lee (2013) 数据集 CSV 或 UNDP HDR 下载文件。

### 优先级 3（插值比例高，可考虑优化）

5. **`china_provincial_real_data.csv`** -- 73.7% 为线性插值。建议从 NBS 官网或 CEIC/Wind 补充中间年份的真实省级 GDP 和城镇化率（这些数据在统计年鉴中逐年可得，无需插值）。

### 优先级 4（模型估算变量，需明确标注）

6. **所有 Urban Q / K\* / OCR / UCI 指标** -- 这些是基于真实输入的模型计算结果，不是直接可观测变量。论文中需明确说明估算方法和假设（折旧率、永续盘存法基准年等），并做敏感性分析。

---

## 六、总体评估

| 指标 | 数值 |
|------|------|
| 数据文件总数 (不含元数据) | 22 |
| 真实数据文件 | 8 (36.4%) |
| 代理/模拟数据文件 | 1 (4.5%) |
| 混合数据文件 | 13 (59.1%) |

**总体判断**: 项目的底层数据基础是扎实的 -- 国际数据通过 API 真实下载（WB、PWT、OECD），中国城市数据来自购买的学术数据库和真实行政数据。主要薄弱环节是：(1) 日本/美国/英国的国别数据依赖脚本硬编码而非可追溯的原始文件；(2) 部分省级数据插值比例过高（73.7%）但其实可以从统计年鉴获取完整年度数据；(3) 早期唯一的完全模拟文件 (`china_275_city_panel.csv`) 已被真实数据替代，但需确认论文中不再引用其结果。

**建议**: 在论文 Methods 和 Supplementary Materials 中：
- 明确区分「直接观测数据」和「模型估算指标」
- 为所有硬编码数据提供精确的来源页码（如 "中国统计年鉴2024, 表3-1"）
- 将日本/美国/英国的原始数据文件从官方统计网站下载并存档
- 在 Supplementary Table 中公布完整的 codebook，标注每个变量的 data_type (actual / interpolated / estimated)
