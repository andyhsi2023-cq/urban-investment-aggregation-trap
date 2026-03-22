# White Hat Facts Audit -- v6 Draft
## 审查日期: 2026-03-22
## 审查范围: full_draft_v6.md vs. 4份分析报告 + references.md

---

## 1. 数字一致性审计

逐条对比论文中每一个关键数值与源数据报告。

### 1.1 beta_V 分解 (Box 1 / betav_decomposition_report.txt)

| 论文声明 | 源数据 | 一致? |
|----------|--------|-------|
| beta_V = 1.057 (SE = 0.060) | 池化: beta = 1.0567 (cluster SE = 0.0598) | YES (四舍五入) |
| beta_A = -0.256 (SE = 0.044) | 池化: beta = -0.2563 (cluster SE = 0.0438) | YES |
| beta_P = 0.313 (SE = 0.025) | 池化: beta = 0.3129 (cluster SE = 0.0248) | YES |
| 机械成分 94.6% | 报告: 94.6% | YES |
| 经济信号 5.4% | 报告: 5.4% | YES |
| 经济信号 = 0.057 | 报告: 0.0567 | YES |
| US beta_V = 1.131 (SE = 0.011) | 池化: 1.1313 (SE = 0.0109) | YES |
| US 经济信号 = 0.131 | 报告: 0.1313 | YES |
| Delta-beta = 0.057 - 0.131 = -0.075 | 报告: 0.0567 - 0.1313 = -0.0746 | **MINOR DISCREPANCY** -- 论文用四舍五入后的数字相减得到 -0.074, 但写成 -0.075; 源数据为 -0.0746 |
| Delta-beta SE = 0.054 | 报告未给出池化 Delta-beta 的 SE; 逐年 SE 范围 0.0540-0.0581, 均值约 0.056 | **APPROXIMATE** -- 论文取 0.054, 接近 2010 年 SE (0.0540), 但非精确均值 |
| SUR: 2/10 年 p < 0.05 | 报告 Part 5: 显著年份 2/10 | YES |
| US beta_A = -0.025 | 报告池化: -0.0249 | YES |
| US beta_P = 0.156 | 报告池化: 0.1561 | YES |
| CN 275 cities, 2005-2019 | 报告: 275 城市, 2005-2019 | YES |
| US 921 MSAs, 2010-2022 | 报告: 921 MSAs, 2010-2022 | YES |
| R^2 = 0.58 (V~Pop, CN) | 报告池化: R2 = 0.6211 | **DISCREPANCY** -- 论文写 0.58, 源数据池化 R^2 = 0.62; 逐年均值范围 0.537-0.590 (均值约 0.579) |

**说明**: R^2 = 0.58 可能取自逐年均值, 但池化值为 0.62. 论文未说明取哪个值. 此处存在歧义.

### 1.2 GDP-based MUQ (Finding 1 / phase0_gdp_muq_results.txt)

| 论文声明 | 源数据 | 一致? |
|----------|--------|-------|
| LI: rho = -0.116, p < 0.001, N = 1,284 | rho=-0.1160, p=0.0000, N=1284 | YES |
| LMI: rho = -0.131, p < 0.001, N = 1,681 | rho=-0.1306, p=0.0000, N=1681 | YES |
| UMI: rho = -0.248, p < 0.001, N = 1,834 | rho=-0.2475, p=0.0000, N=1834 | YES |
| HI: rho = -0.035, p = 0.080 | rho=-0.0351, p=0.0795 | YES |
| LOO: 40/40 negative, significant | 报告: 40/40 negative, 40/40 significant | YES |
| "all p < 0.003" (Abstract) | WDI 最大 p 值 (HI aside) = 0.0000; 但这是 GDP-based. Housing-based LMI p=0.002, UMI p=0.003 | **NEEDS CLARIFICATION** -- Abstract "all p < 0.003" 覆盖哪一组? GDP-based 全为 p<0.001; Housing-based UMI p=0.003 不满足 "< 0.003" (等于 0.003). 严格说 p = 0.003 不满足 p < 0.003 |
| "all developing groups p < 0.001" (Finding 1) | WDI: LI 0.0000, LMI 0.0000, UMI 0.0000 | YES (GDP-based) |
| Countries = 144 | 报告未直接给出总数; WDI 给出 29+37+40+51=157 countries | **DISCREPANCY** -- 各收入组国家总数为 157 (WDI method), 论文称 144 countries |

**说明**: 论文 Methods M1 说 "144 countries (from a panel of 158)". Phase 0 报告中 WDI 各组加总 = 29+37+40+51 = 157 (接近 158), 而 144 可能是 housing-based MUQ 的覆盖范围. 但论文在描述 GDP-based MUQ 时也用了 "144 countries", 实际 GDP-based 覆盖 157 国. 两个数字在论文中混用.

### 1.3 Clean Specification (Finding 2 / clean_spec_city_report.txt)

| 论文声明 | 源数据 | 一致? |
|----------|--------|-------|
| beta = -0.37, p = 0.019 | beta = -0.3669, p = 1.935e-02 | YES |
| 95% CI [-0.67, -0.06] | CI = [-0.6744, -0.0594] | YES |
| R^2 = 0.017 | R^2 = 0.0171 | YES |
| N = 455, 213 cities, 2011-2016 | N=455, 213 cities, year 6 | YES |
| Original beta = -2.26 | 报告: -2.2571 | YES |
| Attenuation = 83.7% | 报告: 83.7% | YES |
| City FE beta = +0.52, clustered SE = 0.10, p < 0.001 | beta = 0.5210, SE = 0.1022, p = 3.44e-07 | YES |
| TWFE beta = +0.16, p = 0.47 | beta = 0.1560, p = 4.68e-01 | YES |
| US: beta = +2.81, p < 10^-6 | beta = 2.8097, p = 2.39e-171 | YES |
| US: invest intensity beta = +1.39 | beta = 1.3914 | YES |
| US TWFE beta = +2.76 | beta = 2.7623 | YES |
| US: 10,760 obs, 921 MSAs, 2011-2022 | N=10760, 921 MSAs | YES |
| 82.2% cities MUQ < 1, 70.2% pop-weighted | 报告: 82.2%, 70.2% | YES |
| Quantile tau=0.50: beta=-0.05, p=0.53 | beta=-0.0464, p=0.529 | YES |
| Quantile tau=0.75: beta=-0.27, p=0.024 | beta=-0.2715, p=0.024 | YES |
| Quantile tau=0.90: beta=-0.89, p=0.016 | beta=-0.8908, p=0.0157 | YES |
| 150/213 cities = 1 observation | 报告: 150/213 = 1 期 | YES |

### 1.4 Carbon Estimates (Discussion / carbon_split_report.txt)

| 论文声明 | 源数据 | 一致? |
|----------|--------|-------|
| 2.7 GtCO2 (90% CI: 2.0-3.5) | 方法 C MC: 2.71 GtCO2, 90% CI [2.04, 3.47] | YES |
| Structural 0.5 GtCO2 (0.0-1.1) | 方法 C MC 结构期: 0.49 GtCO2 [0.00, 1.12] | YES |
| Market correction 2.2 GtCO2 (1.8-2.7) | 方法 C MC 市场期: 2.19 GtCO2 [1.76, 2.69] | YES |
| Physical: 3.8 GtCO2 (2.5-5.0) | 报告 Section 5: 中估 3.78, 低估 2.52, 高估 5.04 | YES |
| 42 m^2 vs 33 m^2 benchmark | 报告: 42.0 m2 vs 33.0 m2 | YES |
| Urban pop 933 million | 报告: 9.33 亿人 | YES |
| 0.3-0.6 tCO2/m^2 | 报告: 低 0.3, 高 0.6 | YES |
| 50% annual cap | 报告: 截断 Y 标记, Section 4 | YES |
| Abstract: "structural uncertainty: 0.3-5.0" | 报告: 保守下界 1.90, 上界 5.04 (物理法高估) | **DISCREPANCY** -- Abstract 写 0.3, 但最低估计为保守法 1.90 GtCO2. "0.3" 可能指结构期 0.37 GtCO2 (方法 C 点估计), 但这不是总碳的下界 |

**重要说明**: Abstract 中 "structural uncertainty: 0.3--5.0" 含义模糊. 如果指所有方法的总碳范围, 下界应为 1.90 GtCO2 (保守法). 如果 0.3 指结构期贡献, 那应明确说明. 当前写法可能误导读者认为总碳排放可能低至 0.3 GtCO2.

### 1.5 其他数值

| 论文声明 | 源数据 | 一致? |
|----------|--------|-------|
| GDP ~ N^1.04, R^2 = 0.69 | **无源数据** -- betav 报告仅含 V, PCA, Price 回归 | UNVERIFIABLE |
| K ~ N^0.86, R^2 = 0.63 | **无源数据** | UNVERIFIABLE |
| Q~Pop R^2 = 0.31 | **无源数据** | UNVERIFIABLE |
| MUQ tiers: 7.46, 2.84, 1.00, 0.52, 0.20 | **无源数据** (clean_spec 报告无此表) | UNVERIFIABLE |
| Kruskal-Wallis H=16.60, p=0.0002 | **无源数据** | UNVERIFIABLE |
| DeltaV composition: CN 44% quantity, US 11% quantity, 87% price; 3.8-fold | **无源数据** | UNVERIFIABLE |
| Housing-based MUQ: LI rho=-0.150, p=0.002; LMI rho=-0.122, p=0.002; UMI rho=-0.099, p=0.003; HI rho=-0.013, p=0.633 | **无源数据** (Phase 0 仅含 GDP-based) | UNVERIFIABLE |
| DID: F=2.82, p=0.093 | **无源数据** | UNVERIFIABLE |
| "Ten-country trajectories": China 44 obs, India 5, Indonesia 6 | **无源数据** | UNVERIFIABLE |
| India/Vietnam/Indonesia: "combined population exceeding 1.8 billion" | 公开数据: ~1.43B + 0.10B + 0.28B = ~1.81B | PLAUSIBLE |
| India/Vietnam/Indonesia: "urbanisation rates of 35-58%" | 公开数据: India ~36%, Vietnam ~39%, Indonesia ~58% | PLAUSIBLE |
| "Hsieh and Klenow documented... 30-50% in China and India" | Ref 20 原文: China 115%, India 127% (TFP losses); 30-50% 可能指 manufacturing sector 的特定指标 | **NEEDS VERIFICATION** -- H&K 2009 的主要数字是 TFP 损失为 China 约 2倍, India 约 1.5倍; "30-50%" 可能不准确 |
| "Hsieh and Moretti... reduces aggregate GDP by 36%" | Ref 22 原文: 约 36% GDP losses | PLAUSIBLE (widely cited figure) |
| CI decline: 1.20 to 0.60 tCO2/万元, 2.89% annual decay | **无源数据** | UNVERIFIABLE |
| BH FDR: 22/25 remained significant | **无源数据** | UNVERIFIABLE |

---

## 2. 声明-证据映射

### 2.1 有数据支撑的核心声明

| # | 声明 | 数据源 | 验证状态 |
|---|------|--------|----------|
| S1 | Simpson's paradox in GDP-based MUQ | phase0 report | VERIFIED |
| S2 | Clean spec beta = -0.37 | clean_spec report | VERIFIED |
| S3 | Attenuation ratio 83.7% | clean_spec report | VERIFIED |
| S4 | City FE sign reversal | clean_spec report | VERIFIED |
| S5 | US positive beta +2.81 | clean_spec report | VERIFIED |
| S6 | beta_V = 1.057, decomposition | betav report | VERIFIED |
| S7 | Mechanical component 94.6% | betav report | VERIFIED |
| S8 | Delta-beta 机械成分消去 | betav report | VERIFIED |
| S9 | Carbon 2.7 GtCO2 (Method C) | carbon report | VERIFIED |
| S10 | Physical validation 3.8 GtCO2 | carbon report | VERIFIED |
| S11 | LOO 40/40 | phase0 report | VERIFIED |
| S12 | 82.2% / 70.2% MUQ < 1 | clean_spec report | VERIFIED |

### 2.2 无数据支撑或不可验证的声明

| # | 声明 | 位置 | 问题 |
|---|------|------|------|
| U1 | GDP scaling beta = 1.04, R^2 = 0.69 | Finding 1 para 1 | 无源数据报告 |
| U2 | K scaling beta = 0.86, R^2 = 0.63 | Finding 1 para 1 | 无源数据报告 |
| U3 | Q~Pop R^2 = 0.31 | Finding 1 para 1 | 无源数据报告 |
| U4 | Housing-based MUQ rho 值 (4组) | Finding 1, "Housing-based MUQ" | Phase 0 报告仅含 GDP-based |
| U5 | City-tier MUQ: 7.46, 2.84, 1.00, 0.52, 0.20 | Finding 2 | 无源数据 |
| U6 | DeltaV composition: 44% vs 11% | Finding 2 | 无源数据 |
| U7 | Kruskal-Wallis H=16.60 | Finding 2 | 无源数据 |
| U8 | DID F=2.82, p=0.093; placebo p < 0.001 | Finding 2 | 无源数据 |
| U9 | BH FDR 22/25 significant | Methods M9 | 无源数据 |
| U10 | Bai-Perron breaks at 2004 and 2018 | Methods M6 | 无源数据 |
| U11 | "excluding China: UMI rho = -0.095, p = 0.005" | Finding 1 | 无源数据 |
| U12 | CI decay rate 2.89%, from 1.20 to 0.60 | Methods M5 | 无源数据 |
| U13 | Alpha=10/50 shifts Q=1 crossing by <1.5 yr | Methods M6 | 无源数据 |
| U14 | "Q=1 crossing year 90% CI spans ~12 years" | Limitations | 无源数据 |
| U15 | "Hegang: apartments < US$3,000" | Introduction | 无引用, 属于 anecdotal claim |
| U16 | Hsieh-Klenow "30-50%" | Introduction | 可能不准确 |
| U17 | "Six of ten countries have experienced MUQ < 1" | Finding 1 | 无源数据 |
| U18 | "first-tier Chinese cities approach the American pattern" | Finding 2 | 无源数据 |

---

## 3. 缺失信息清单

以下为论文提及但未提供具体数字或数据的项目:

| # | 缺失项 | 位置 | 说明 |
|---|--------|------|------|
| G1 | "MUQ coverage varies substantially" | Finding 1, ten-country | 仅给出3国(CN:44, IN:5, ID:6), 其余7国未给 |
| G2 | Housing-based MUQ 的 block bootstrap p 值 | Finding 1 | 仅声称 "robust to block bootstrap", 未给数字 |
| G3 | "compositional shifts across groups" 的量化 | Finding 1, within-between | 未给出 between-group uplift 的数值大小 |
| G4 | GDP-based MUQ 的 PWT parallel 结果 | Finding 1 | 仅说 "consistent results (all developing groups p < 0.001)", 未给 rho 和 N |
| G5 | 10 国轨迹的具体数据 | Finding 1 | 仅定性描述, 无 MUQ 数值表 |
| G6 | "balanced sub-panel (2015-2016, N=51)" 结果 | Methods M9 | 仅提及, 未报告 beta 和 p |
| G7 | Moran's I 空间自相关结果 | Methods M9 | 仅提及, 未报告数值 |
| G8 | Newey-West 结果 | Methods M9 | 仅提及, 未报告是否改变结论 |
| G9 | Winsorisation sensitivity (5%/95%) 结果 | Methods M9 | 仅提及 |
| G10 | 7种 calibration variants 的具体参数和结果 | Methods M1/M6 | 仅提及7种, 未列出 |
| G11 | BH FDR: 哪3个 tests 变为不显著 | Methods M9 | 仅说 22/25, 未说明哪3个 |
| G12 | "~1,400-1,900 MtCO2/yr" 建筑碳总量 | Discussion/Methods | 无引用来源 |
| G13 | 美国 V~Pop R^2 | Box 1 | 中国给了 R^2=0.58, 美国未给 |

---

## 4. 内部逻辑一致性

### 4.1 同一指标在不同位置的数值

| 指标 | Abstract | Introduction | Results | Discussion | Box 1 | Methods | 一致? |
|------|----------|-------------|---------|------------|-------|---------|-------|
| Clean beta | -0.37 | -0.37 | -0.37 | -- | -- | -- | YES |
| US beta | +2.81 | +2.81 | +2.81 | -- | -- | -- | YES |
| Carbon | 2.7 GtCO2 | -- | -- | 2.7 GtCO2 | -- | -- | YES |
| Carbon range | 0.3-5.0 | -- | -- | 2.0-3.5 (90% CI) | -- | -- | **INCONSISTENT** |
| GDP MUQ "all p < 0.003" | Abstract | -- | "all p < 0.001" (GDP-based) | -- | -- | -- | **INCONSISTENT** |
| Countries | 144 | 144 | -- | -- | -- | 144 (from 158) | See note |
| CN cities | 275 (scaling) | 275 | 213 (clean) | 213 | 275 | 213/275 | OK (different analyses) |

### 4.2 关键不一致详解

**Issue 4.2.1: Abstract "all p < 0.003" vs Results "all p < 0.001"**

Abstract 写: "Within every developing-economy income group, returns decline with urbanisation (all p < 0.003)". Results Finding 1 GDP-based 段写: "all developing groups p < 0.001".

- GDP-based MUQ: 所有 developing groups p = 0.0000, 即 p < 0.001.
- Housing-based MUQ: UMI p = 0.003.
- Abstract 的 "all p < 0.003" 似乎试图覆盖两种 MUQ 定义, 但 p = 0.003 是否满足 "p < 0.003"? 严格地说, 不满足 (等于, 不小于). 如果 p 值实际是 0.0030 四舍五入, 则可能满足; 但审稿人可能质疑.

**Issue 4.2.2: Abstract "structural uncertainty: 0.3--5.0" vs Discussion "90% CI: 2.0--3.5"**

Abstract 的 "0.3--5.0" 与 Discussion 的 "2.0--3.5" 是不同概念:
- 2.0--3.5 是方法 C 的 Monte Carlo 90% CI
- 0.3--5.0 似乎是所有方法/视角的极端范围

但 0.3 不对应任何源数据:
- 方法 C 结构期: 0.37 GtCO2 (点估计, 非总碳)
- 保守下界: 1.90 GtCO2
- MC 方法 C 下界: 2.04 GtCO2
- MC 方法 B 下界: 1.58 GtCO2
- 最低的任何全期估计: 1.58 GtCO2 (方法 B MC 下界)

**0.3 GtCO2 作为总碳下界没有任何源数据支撑.** 这是本次审计发现的最严重的数字问题.

**Issue 4.2.3: R^2 = 0.58 vs 源数据 0.62**

Finding 1 写 "V ~ N^1.06, R^2 = 0.58". 源数据池化 R^2 = 0.6211. 逐年 R^2 范围 0.537-0.590 (均值约 0.579). 论文的 0.58 更接近逐年均值, 但未说明取值依据. 与池化值差距约 0.04.

### 4.3 其他逻辑检查

- **V ~ N^1.06**: 论文写 beta_V = 1.06 (Finding 1 para 1) 和 1.057 (Box 1). 1.06 是 1.057 的四舍五入, 可接受.
- **Discussion 重复检查**: Discussion 中 "2.7 GtCO2", "0.5 GtCO2", "2.2 GtCO2" 与 Results/carbon 报告一致.
- **Limitations "9 limitations"**: 实际列出 9 条, 一致.

---

## 5. 新增参考文献验证 (#19-30)

v6 新增 12 条参考文献. 原 references.md 仅含 #1-18. 以下逐条检查.

### 5.1 格式检查

| Ref # | 引用 | Nature 格式? | 问题 |
|-------|------|-------------|------|
| 19 | Easterly, W. *J. Dev. Econ.* **60**, 423-438 (1999) | YES | OK |
| 20 | Hsieh, C.-T. & Klenow, P. J. *Q. J. Econ.* **124**, 1403-1448 (2009) | YES | OK |
| 21 | Bettencourt, L. M. A. *Science* **340**, 1438-1441 (2013) | YES | OK |
| 22 | Hsieh, C.-T. & Moretti, E. *Am. Econ. J. Macroecon.* **11**, 1-39 (2019) | YES | OK |
| 23 | Arcaute, E. et al. *J. R. Soc. Interface* **12**, 20140745 (2015) | YES | OK |
| 24 | Leitao, J. C. et al. *R. Soc. Open Sci.* **3**, 150649 (2016) | YES | OK |
| 25 | Bai, C.-E., Hsieh, C.-T. & Song, Z. M. *Brookings Pap. Econ. Act.* **2016**, 129-181 (2016) | YES | OK |
| 26 | Glaeser, E. L. & Gyourko, J. *J. Econ. Perspect.* **32**, 3-30 (2018) | YES | OK |
| 27 | Restuccia, D. & Rogerson, R. *Rev. Econ. Stud.* **75**, 707-731 (2008) | YES | OK |
| 28 | Cottineau, C. *PLoS ONE* **12**, e0183919 (2017) | YES | OK |
| 29 | Huang, L. et al. *Renew. Sustain. Energy Rev.* **81**, 1906-1916 (2018) | YES | OK |
| 30 | Pomponi, F. & Moncaster, A. *Renew. Sustain. Energy Rev.* **71**, 307-316 (2017) | YES | OK |

### 5.2 引用位置检查

| Ref # | 论文中引用位置 | 是否被引用? | 引用恰当性 |
|-------|---------------|-------------|-----------|
| 19 | Introduction para 2: "Easterly^19 showed..." | YES | APPROPRIATE -- financing gap 模型失败 |
| 20 | Introduction para 2: "Hsieh and Klenow^20 documented..." | YES | **NEEDS CHECK** -- "30-50%" 数字可能不准确 (见 1.5 U16) |
| 21 | Introduction para 2: "scaling laws^9,21"; Box 1: "Bettencourt scaling framework^9,21" | YES | APPROPRIATE -- 城市标度律 |
| 22 | Discussion para 2: "Hsieh and Moretti^22" | YES | APPROPRIATE -- 空间错配与 GDP 损失 |
| 23 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |
| 24 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |
| 25 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |
| 26 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |
| 27 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |
| 28 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |
| 29 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |
| 30 | **NOT FOUND in main text** | **NO** | ORPHAN REFERENCE -- 未在正文中被引用 |

**重大发现: 参考文献 #23-30 (共8条) 在正文中未被引用.** 这8篇论文被列入参考文献列表但没有对应的正文引用标记. 这可能是为 Extended Data 或后续修改预留的, 但在当前正文中属于孤立参考文献, Nature 格式不允许此情况.

### 5.3 反向检查: 正文引用是否都在参考文献列表中

正文中出现的所有引用标记: ^1 - ^22 (以上标数字形式). 参考文献列表 #1-30. 无遗漏 (^1-22 均对应 #1-22).

---

## 6. 综合问题清单 (按严重程度排序)

### CRITICAL (可能影响审稿结论)

| # | 问题 | 位置 |
|---|------|------|
| C1 | **Abstract "structural uncertainty: 0.3--5.0" 中 0.3 无源数据支撑.** 所有方法的总碳最低估计为 1.58 GtCO2 (方法 B MC 下界) 或 1.90 GtCO2 (保守法). 0.3 可能混淆了结构期贡献 (0.37 GtCO2) 与总碳下界. | Abstract |
| C2 | **8 条孤立参考文献 (#23-30) 未在正文中引用.** Nature 不允许参考文献列表中有未被引用的条目. | References |
| C3 | **144 vs 157 国家数混用.** GDP-based MUQ 覆盖 157 国 (WDI 各组加总), 但论文始终称 144 countries. | Abstract, Intro, Methods |

### MAJOR (需要修正但不致命)

| # | 问题 | 位置 |
|---|------|------|
| M1 | **Abstract "all p < 0.003"**: housing-based UMI p = 0.003, 不满足严格的 "< 0.003" | Abstract |
| M2 | **R^2 = 0.58 vs 源数据 0.62**: 取值依据不明, 与池化值不一致 | Finding 1 |
| M3 | **Delta-beta SE = 0.054**: 源数据逐年 SE 范围 0.054-0.058, 论文取最小值; 应取代表值或说明计算方法 | Box 1 |
| M4 | **Hsieh-Klenow "30-50%"**: 原文主要数字是 TFP 损失约 2x (China), 不是 30-50%. 需核实原文 | Introduction |
| M5 | **大量声明不可验证** (18项, 见 Section 2.2): 涉及 scaling, city-tier, DeltaV composition, DID, housing-based MUQ 等核心数据, 均无对应分析报告 | 多处 |

### MINOR (建议改进)

| # | 问题 | 位置 |
|---|------|------|
| m1 | Delta-beta = -0.075 四舍五入略有偏差 (精确值 -0.0746) | Finding 1 |
| m2 | 缺失信息: 10国轨迹中7国的数据覆盖量未给出 | Finding 1 |
| m3 | "~1,400-1,900 MtCO2/yr" 建筑碳总量无引用 | Discussion/Methods |
| m4 | carbon_split_report Section 4 显示年度碳 cap = 建筑碳 x 50%, 但 "建筑碳" 估计本身未给出来源引用 | Methods M5 |

---

## 7. 审计总结

**数据完整性**: 论文中约 60% 的核心数值可在提供的 4 份分析报告中找到匹配源数据, 且绝大多数一致 (在合理四舍五入范围内). 约 40% 的数值声明 (包括 scaling 指数、city-tier MUQ、DeltaV 分解、housing-based MUQ、DID 结果等) 无法在提供的报告中验证, 可能存在于其他未提供的分析输出中.

**最严重问题**: Abstract 中 "0.3--5.0" 的碳排放范围下界 (0.3 GtCO2) 在所有提供的源数据中找不到任何对应. 这需要立即澄清或修正.

**参考文献**: 8 条新增参考文献 (#23-30) 为孤立条目, 需要在正文中增加引用或从列表中移除.
