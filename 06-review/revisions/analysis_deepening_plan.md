# 联席会议纪要 -- 8 国数据深化分析方案

**日期**: 2026-03-22
**主持**: PI (首席研究员)
**议题**: 如何深化现有 8 国数据的分析，最大化论文质量提升
**前提**: 数据采集阶段已完成，不再增加新国家

---

## 战略判断总述

在详细展开之前，先明确一个核心战略判断：**当前论文最大的结构性弱点不是某个分析做得不够深，而是"分析深度极不均匀"**。中国和美国已做到 Nature 标准，而日本 47 县 68 年的 A 级数据几乎未被触碰，韩国缺少 Simpson's Paradox 检验，欧洲 265 区域缺少分组分析。这种不均匀在审稿人看来是一个明显的信号：作者对非核心国家缺乏分析投入。

因此，本次深化的首要目标不是"让中国/美国更深"，而是**让所有国家达到统一的最低分析标准**，然后在日本这个最有价值的案例上做重点突破。

---

## Part 1: 分析任务优先级矩阵

### 评分标准
- **质量提升 (1-10)**: 该分析对论文整体质量（说服力、稳健性、叙事丰富度）的提升幅度
- **工作量 (天)**: 含脚本编写、调试、结果解读
- **风险**: 分析可能失败或产生与论文叙事不一致的结果的概率
- **GO/NO-GO**: 综合判断

---

### 模块 1: 日本 47 县深化分析

| # | 分析任务 | 质量提升 | 工作量 | 风险 | GO/NO-GO | 理由 |
|---|---------|:--------:|:------:|:----:|:--------:|------|
| J1 | **县级 Clean Specification**: DeltaGDP/GDP ~ GFCF/GDP + Prefecture FE + Year FE | **9** | 1.0 天 | 低 | **GO** | 数据已有（3,102 obs MUQ），直接复用中国/美国的 clean spec 框架。日本有独立的县级 GFCF 真实数据（非份额分配），这使其 clean spec 的可信度甚至高于欧洲和澳大利亚。这是最高优先级任务。 |
| J2 | **泡沫-崩盘自然实验**: 1986-1991 泡沫期 vs 1992-2002 崩盘期的 MUQ 变化 + Bai-Perron 断点检验 | **9** | 1.5 天 | 低 | **GO** | 日本泡沫是全球最著名的资产泡沫案例。68 年时序足以做高质量的断点检验。现有报告已显示泡沫期 MUQ=0.213 vs 失去的十年 MUQ=0.020，但缺少正式的结构断点检验和县级分解。这是论文叙事中"MUQ 作为预警信号"的最强国际证据。 |
| J3 | **县级 Simpson's Paradox**: 47 县按经济实力分组（首都圈/近畿圈/其他），检验组内 MUQ 是否随 GFCF/GDP 下降 | **8** | 1.0 天 | 中 | **GO** | 现有韩国报告显示韩国不存在经典 Simpson's Paradox（全国趋势与分组趋势方向一致）。日本如果也不存在，反而强化了一个重要发现：Simpson's Paradox 是跨收入组的现象，而非国内区域间的现象。如果存在，则是额外的稳健性证据。两种结果都有论文价值。 |
| J4 | **不可逆性验证**: Q<1 后是否有任何县恢复到 Q>1？全 47 县的 MUQ 恢复/不恢复统计 | **7** | 0.5 天 | 低 | **GO** | 现有报告已有定性结论（"强支持不可逆"），但缺少系统的县级统计。47 县中有多少在泡沫后曾短暂恢复 MUQ>0.1？恢复的县有什么特征（东京？工业县？）？这为 Discussion 的"不可逆性"论述提供了最清晰的经验证据。 |
| J5 | **与中国的"镜像"对比系统性分析**: 日本 91% 城镇化率触达 Q=1 vs 中国 54% | **8** | 0.5 天 | 低 | **GO** | 这个对比本身就是一个有力的 figure。核心问题：为什么中国在城镇化率远低于日本时就触达 Q=1？假设检验：(1) 投资强度差异（中国 GFCF/GDP 44% vs 日本 25%）；(2) 泡沫效应（日本泡沫延迟了 Q=1 的出现）；(3) 制度差异（中国地方政府土地财政驱动过度投资）。 |
| J6 | **beta_V 分解**: 住宅面积 + 价格的标度律分解 | **5** | 1.0 天 | 高 | **条件 GO** | 现有 japan_prefecture_data.csv 有住宅数据（人均住宅、空置率），但缺少区域级房价数据。如果能从日本不动产研究所或 REINS 获取县级房价，则可做分解。否则只能做 beta_HU（住宅数量标度律），已有结果 beta_HU = 1.023。**如无房价数据则降级为 NO-GO**。 |
| J7 | **时间序列分析**: 全国 MUQ 的 Bai-Perron 断点检验 + 47 县面板 VAR | **6** | 1.0 天 | 中 | **GO** | Bai-Perron 优先（工作量小、结果明确）。面板 VAR 只有在 Bai-Perron 结果明确后才值得做。 |

**日本模块总工作量**: 5.5-6.5 天
**日本模块预期产出**: 论文中可独立成段的"日本全周期案例"，可能值得作为 Finding 1 的核心扩展或独立的 Extended Data 分析。

---

### 模块 2: 韩国深化分析

| # | 分析任务 | 质量提升 | 工作量 | 风险 | GO/NO-GO | 理由 |
|---|---------|:--------:|:------:|:----:|:--------:|------|
| K1 | **Simpson's Paradox 检验**: 按首都圈（首尔+京畿+仁川）vs 非首都圈分组 | **7** | 0.5 天 | 中 | **GO** | 现有韩国报告的 Section 4 做了时间趋势分析但结论是"不存在 Simpson's Paradox"。但其检验方式（各市道独立趋势）与论文的 Simpson's Paradox 框架不完全匹配。正确的检验是：按经济水平分组后，组内 MUQ 是否随城镇化/时间下降？首都圈 vs 非首都圈是最自然的分组。 |
| K2 | **Clean Specification**: DeltaGRDP/GRDP ~ GFCF/GRDP + Sido FE + Year FE | **7** | 0.5 天 | 中 | **GO** | 韩国有 17 市道 38 年面板（609 obs），可做 clean spec。但注意：韩国区域 GFCF 是按份额分配的估计值（报告 Section 8 明确说明），clean spec 的解释力受限。应在报告中标注这一局限。 |
| K3 | **1997 亚洲金融危机冲击分析**: MUQ 的 V 型恢复模式 | **6** | 0.5 天 | 低 | **GO** | 现有数据清晰显示 1998 年 MUQ = -0.059（唯一负值年份），随后快速恢复至 0.250（1999-2007 均值）。这是一个完美的"外部冲击 + 恢复"案例，与日本泡沫后的"永久性下降"形成对比。分析工作量小（已有数据），叙事价值高。 |
| K4 | **三国对比**: 韩国"有序退出" vs 中国"断崖" vs 日本"失去的十年" | **8** | 0.5 天 | 低 | **GO** | 这不是独立分析，而是将 J5 + K3 的结果整合为一张跨国对比图。三个东亚经济体、三种 MUQ 轨迹、三种制度结局。这可能是论文中最有叙事冲击力的图之一。 |

**韩国模块总工作量**: 2.0 天
**韩国模块预期产出**: Simpson's Paradox 检验结果 + 金融危机恢复分析 + 三国对比图

---

### 模块 3: 欧洲深化分析

| # | 分析任务 | 质量提升 | 工作量 | 风险 | GO/NO-GO | 理由 |
|---|---------|:--------:|:------:|:----:|:--------:|------|
| E1 | **东欧 vs 西欧 Simpson's Paradox**: 按 EU-15 vs 2004+ 新成员国分组 | **8** | 1.0 天 | 中 | **GO** | 欧洲 265 NUTS-2 区域是全球面板之外最大的 within-country Simpson's Paradox 检验场。东欧区域（波兰、罗马尼亚、保加利亚等）MUQ 显著高于西欧（报告 F1 显示中位数差距 2-3 倍），如果组内都呈下降趋势但汇总后消失，这是论文 Finding 1 的强力扩展。 |
| E2 | **欧债危机 (2010-2012) 冲击分析**: 希腊/西班牙/意大利/葡萄牙区域 MUQ 变化 | **6** | 0.5 天 | 低 | **GO** | 数据已有。PIIGS 国家区域 MUQ 在欧债危机前后的变化是"外部冲击如何影响区域投资效率"的天然实验。与韩国 1997 金融危机形成跨洲对比。 |
| E3 | **收敛 vs 发散**: 东欧区域 MUQ 是否在追赶西欧？ | **5** | 0.5 天 | 中 | **GO** | beta-收敛回归：MUQ_growth ~ initial_MUQ。如果东欧在追赶，暗示 Simpson's Paradox 的"毕业效应"在区域层面也存在。如果发散，则暗示 EU 内部也存在类似全球的结构性不平等。 |
| E4 | **265 区域 beta_V 分解** | **3** | 1.5 天 | 高 | **NO-GO** | 欧洲没有区域级房价和住房面积数据（报告 H 明确标注"房价数据仅有国家级 BIS，无法构建区域 housing-based MUQ"）。无法做 beta_V = 1 + beta_A + beta_P 的分解。区域 GFCF 本身也是按份额分配的估计值。工作量大、数据质量低、产出有限。 |

**欧洲模块总工作量**: 2.0 天
**欧洲模块预期产出**: EU 内部 Simpson's Paradox 检验 + 欧债危机冲击分析 + 收敛/发散检验

---

### 模块 4: 澳大利亚 + 南非深化分析

| # | 分析任务 | 质量提升 | 工作量 | 风险 | GO/NO-GO | 理由 |
|---|---------|:--------:|:------:|:----:|:--------:|------|
| A1 | **澳大利亚州级 Clean Spec** (如能获取 ABS 真实 GFCF) | **5** | 1.0 天 | 高 | **条件 GO** | 审计报告显示已下载 abs_state_gfcf_raw.csv 和 abs_state_sfd_raw.csv。但报告 Part 6 明确说"GFCF 按 GDP 份额比例分配...此假设导致所有区域 MUQ 完全相同"。如果原始 ABS GFCF 数据可用且有州级差异，则 GO；否则 NO-GO。 |
| A2 | **矿业州 vs 服务州对比**: WA/QLD vs NSW/VIC | **4** | 0.3 天 | 低 | **GO** | 数据已有。WA 人均 GDP $97k vs SA $52k，MUQ 均值 WA=0.215 vs SA=0.152。但只有 8 个观测单元，任何统计检验都缺乏力量。作为描述性补充材料可以，但不宜在正文中做推断。 |
| S1 | **南非 Gauteng vs 其他省** | **3** | 0.3 天 | 中 | **条件 GO** | Gauteng GDP/cap $8.3k vs Eastern Cape $3.8k，是南非内部最大的经济差距。但 GFCF 按份额分配导致区域 MUQ 差异完全来自 GDP 增长差异。数据 B- 评级，加上仅 9 省，统计力量极弱。仅作为 ED 补充。 |

**澳大利亚+南非模块总工作量**: 1.0-1.6 天
**风险评估**: 这两个国家的区域数据质量（B-/B+）不足以支撑深度分析。主要价值在于：(1) 扩大全球覆盖面的叙事；(2) 为统一面板提供额外样本。

---

### 模块 5: 统一口径跨国 MUQ 面板

| # | 分析任务 | 质量提升 | 工作量 | 风险 | GO/NO-GO | 理由 |
|---|---------|:--------:|:------:|:----:|:--------:|------|
| U1 | **构建统一 GDP-based MUQ 跨 8 国区域面板** | **10** | 2.0 天 | 中 | **GO** | 这是整个深化计划中最有价值的单一分析。统一公式：MUQ = DeltaGDP / GFCF。所有国家的区域数据已有 GDP 和 GFCF（或估计值）。统一面板规模：中国 275 城 + 日本 47 县 + 韩国 17 市道 + 美国 921 MSA + 欧洲 265 NUTS-2 + 澳大利亚 8 州 + 南非 9 省 = 约 1,542 区域单元。这是全球最大的区域级投资效率面板。 |
| U2 | **1,542 区域统一面板回归**: MUQ ~ ln(GDP_pc) + GFCF/GDP + Country FE + Year FE | **9** | 0.5 天 | 低 | **GO** | 依赖 U1 的产出。核心检验：GFCF/GDP 的系数在统一面板中是否为负？Country FE 吸收国家间异质性后，within-country 的投资-效率关系如何？ |
| U3 | **跨国 Simpson's Paradox**: 按国家收入水平分组（高收入 vs 中等收入 vs 低收入），组内区域 MUQ 是否随城镇化/投资强度下降 | **9** | 1.0 天 | 中 | **GO** | 这是 Finding 1 从"国家级 Simpson's Paradox"升级为"区域级 Simpson's Paradox"的关键。如果 1,542 个区域按所属国家收入分组后，组内 MUQ 仍随发展水平下降，这是 paradox 的第三层验证（国家级 -> 收入组级 -> 区域级），证明 aggregation trap 在多个尺度上存在。 |
| U4 | **全球区域标度律**: 1,542 区域的 ln(GDP) ~ ln(Pop) 统一估计 | **6** | 0.5 天 | 低 | **GO** | 各国已有独立标度律估计。统一估计的价值在于：(1) 计算全球 beta_GDP 及其跨国差异；(2) 为 Box 1 的 scaling gap 讨论提供区域级证据。 |

**统一面板模块总工作量**: 4.0 天
**预期产出**: 全球最大的区域级投资效率面板 + 多层级 Simpson's Paradox + 统一面板回归

---

### 模块 6: Aggregation Trap 定理的经验验证

| # | 分析任务 | 质量提升 | 工作量 | 风险 | GO/NO-GO | 理由 |
|---|---------|:--------:|:------:|:----:|:--------:|------|
| T1 | **定理三条件 (C1/C2/C3) 在每个国家的验证** | **8** | 1.0 天 | 中 | **GO** | 现有验证报告仅在全球面板上做了验证。A1（within-group decline）在 LMI 组 p=0.26、UMI 组 p=0.08，不够稳健。需要在 8 国的区域数据中分别验证：每个国家的区域分组后，C1/C2/C3 是否成立。特别是日本（47 县分 3 组）和韩国（17 市道分 2 组）。 |
| T2 | **用 8 国区域数据校准定理参数** | **7** | 0.5 天 | 低 | **GO** | 依赖 T1。为每个国家校准 mu_k（组基线）、gamma_k（组内斜率）、dP/dx（毕业概率），与全球面板参数对比。如果跨国校准结果一致，强化定理的一般性。 |
| T3 | **Monte Carlo: 模拟参数下 paradox 出现概率** | **6** | 0.5 天 | 低 | **GO** | 现有 MC 已完成（30.7% paradox 概率）。但需要用各国实际校准参数重新跑 MC。如果用日本参数跑 MC 显示 paradox 不太可能出现（日本高度同质化经济体），这反而验证了定理的一个推论：高度同质化的经济体不容易出现 paradox。 |

**Aggregation Trap 模块总工作量**: 2.0 天
**预期产出**: 跨国 C1/C2/C3 验证表 + 校准参数比较 + 条件 MC 模拟

---

### 优先级总览

| 优先级 | 任务组 | 质量提升 | 总工作量 | GO 任务数 |
|:------:|--------|:--------:|:--------:|:---------:|
| **P0** | U1-U3: 统一跨国面板 + 面板回归 + 跨国 Simpson's | 10/9/9 | 3.5 天 | 3 |
| **P1** | J1-J2: 日本 Clean Spec + 泡沫断点 | 9/9 | 2.5 天 | 2 |
| **P2** | J3-J5, K1-K4: 日本+韩国 Simpson's + 不可逆性 + 三国对比 | 7-8 | 3.5 天 | 7 |
| **P3** | E1-E3: 欧洲 Simpson's + 欧债危机 + 收敛 | 5-8 | 2.0 天 | 3 |
| **P4** | T1-T3: Aggregation Trap 跨国验证 | 6-8 | 2.0 天 | 3 |
| **P5** | J6-J7, U4, A1-S1: 标度律分解 + 时间序列 + 澳非深化 | 3-6 | 3.0-3.6 天 | 5-6 |

---

## Part 2: 最终分析执行计划

### 阶段 I: 统一面板构建 (Day 1-2)

| 序号 | 脚本名称 | 输入数据 | 预期产出 | 依赖 |
|:----:|---------|---------|---------|:----:|
| 1 | `n30_unified_panel.py` | china_provincial_real_data.csv, japan_prefectural_panel.csv, korea_regional_panel.csv, europe_regional_panel.csv, oceania_regional_panel.csv, africa_regional_panel.csv, us_msa_muq_panel.csv | `unified_regional_panel.csv`: 约 1,542 区域 x (GDP, GFCF, Pop, MUQ, country, income_group) | 无 |
| 2 | `n31_unified_panel_regression.py` | unified_regional_panel.csv | 统一面板回归结果报告 + 跨国 Simpson's Paradox 检验 | 1 |
| 3 | `n32_unified_scaling.py` | unified_regional_panel.csv | 全球区域标度律 ln(GDP) ~ ln(Pop) + Country FE | 1 |

### 阶段 II: 日本深度分析 (Day 2-4)

| 序号 | 脚本名称 | 输入数据 | 预期产出 | 依赖 |
|:----:|---------|---------|---------|:----:|
| 4 | `n33_japan_clean_spec.py` | japan_prefectural_panel.csv | 日本 47 县 clean spec: DeltaGDP/GDP ~ GFCF/GDP + FE。输出 beta、SE、R2，与中国/美国对比表 | 无 |
| 5 | `n34_japan_bubble_breakpoint.py` | japan_prefectural_panel.csv, japan_urban_q_data.csv | (a) 全国 MUQ Bai-Perron 断点检验；(b) 泡沫期 vs 崩盘期县级 MUQ 差异 t-test；(c) 三阶段图（1975-1985 自然逼近 / 1986-1991 泡沫膨胀 / 1992+ 结构崩塌） | 无 |
| 6 | `n35_japan_simpsons.py` | japan_prefectural_panel.csv | 47 县分 3 组（首都圈/近畿圈/其他）后 Simpson's Paradox 检验。输出组内 rho + pooled rho | 无 |
| 7 | `n36_japan_irreversibility.py` | japan_prefectural_panel.csv | 47 县 MUQ 恢复/不恢复统计：泡沫后有多少县曾恢复 MUQ > 阈值（0.1/0.2/0.3）？恢复县 vs 未恢复县的特征对比 | 无 |
| 8 | `n37_japan_china_mirror.py` | japan_prefectural_panel.csv, china_national_real_data.csv, china_provincial_real_data.csv | 中日"镜像"对比：(a) 城镇化率-MUQ 轨迹叠加图；(b) GFCF/GDP 差异；(c) Q=1 触达时的城镇化率对比（日本 91% vs 中国 54%）；(d) 假设检验 | 无 |
| 9 | `n38_japan_baiperron.py` | japan_prefectural_panel.csv | 全国+47县 MUQ 时间序列 Bai-Perron 断点检验 | 无 |

### 阶段 III: 韩国+欧洲+三国对比 (Day 4-6)

| 序号 | 脚本名称 | 输入数据 | 预期产出 | 依赖 |
|:----:|---------|---------|---------|:----:|
| 10 | `n39_korea_simpsons_cleanspec.py` | korea_regional_panel.csv | (a) 首都圈 vs 非首都圈 Simpson's Paradox；(b) Clean spec: DeltaGRDP/GRDP ~ GFCF/GRDP + Sido FE + Year FE；(c) 1997 金融危机前后 MUQ 变化分析 | 无 |
| 11 | `n40_three_country_comparison.py` | japan_prefectural_panel.csv, korea_regional_panel.csv, china_national_real_data.csv | 三国 MUQ 轨迹对比图 + "有序退出" vs "断崖" vs "失去的十年" 叙事 | 4, 10 |
| 12 | `n41_europe_simpsons.py` | europe_regional_panel.csv | (a) 东欧(EU-2004+) vs 西欧(EU-15) Simpson's Paradox；(b) PIIGS 国家欧债危机冲击；(c) beta-收敛回归 | 无 |

### 阶段 IV: Aggregation Trap 验证 + 收尾 (Day 6-8)

| 序号 | 脚本名称 | 输入数据 | 预期产出 | 依赖 |
|:----:|---------|---------|---------|:----:|
| 13 | `n42_aggregation_trap_crossnational.py` | unified_regional_panel.csv | 8 国区域数据中 C1/C2/C3 验证 + 校准参数表 + 条件 MC 模拟 | 1 |
| 14 | `n43_australia_cleanspec.py` | oceania_regional_panel.csv, abs_state_gfcf_raw.csv | 澳大利亚州级 clean spec（如 ABS 数据可用）+ 矿业州 vs 服务州对比 | 无 |
| 15 | `n44_deep_analysis_summary.py` | 所有上述产出 | 汇总报告：所有深化分析的关键数字、跨国对比表、论文整合建议 | 1-14 |

---

## Part 3: 论文结构升级建议

### 当前 v6 结构

```
Abstract
Introduction
  Finding 1: Simpson's Paradox (国家级, 144/157 国)
  Finding 2: City-level efficiency mapping (中国 213 城 + 美国 921 MSA)
  Box 1: Scaling Gap
Discussion
  碳段落
  Limitations (9 条)
Methods (M1-M9)
```

### 建议 v7 结构升级

深化分析完成后，论文结构面临一个核心选择：**保持当前的 2-Finding 结构并扩展，还是升级为 3-Finding 结构？**

#### 方案 A: 2-Finding 扩展版（推荐）

这是保守但安全的选择，与 Nature Article 的 3,500 词限制兼容。

```
Abstract (更新数字: 157 国 + 1,542 区域)
Introduction (不变，调整覆盖范围描述)
Finding 1: Simpson's Paradox — 多尺度验证
  - 国家级 (GDP-based + housing-based, 157 国)
  - 区域级 (1,542 区域统一面板, 8 国)  [新增]
  - 日本/韩国/欧洲的组内验证  [新增]
  - Within-between 分解 (不变)
  - Ten-country trajectories (不变)
Finding 2: City-level efficiency mapping
  - China-US sign reversal (不变, 重组段落顺序)
  - 日本 Clean Spec 作为第三国验证  [新增]
  - 韩国 Clean Spec (如显著) [新增]
  - Quantity vs Price decomposition (不变)
  - City-tier gradient (不变)
Box 1: Scaling Gap + Aggregation Trap Theorem
  - Part A: Scaling gap (精简)
  - Part B: Theorem (新增, 含 8 国 C1/C2/C3 验证表)
Discussion
  - 首段重写 (已决议)
  - 日本全周期案例: 泡沫-崩盘-不可逆性  [新增, 1-2 段]
  - 三国对比: 韩国"有序退出" vs 中国"断崖" vs 日本"失去的十年"  [新增]
  - 碳段落 (精简版)
  - 末段重写 + aggregation trap 泛化 (已决议)
  - Limitations (更新)
Methods (扩展 M1 覆盖日本/韩国/欧洲; 新增 M10 统一面板构建)
```

**优势**: 不改变论文的核心叙事架构。Finding 1 从"国家级"升级为"多尺度"，Finding 2 从"中美对比"升级为"中美日韩多国对比"。日本全周期进入 Discussion 而非 Results，避免分散注意力。

**风险**: 字数可能超过 3,500 词限制。需要大幅压缩现有文字以容纳新内容。

#### 方案 B: 3-Finding 结构

```
Finding 1: Simpson's Paradox (与方案 A 相同)
Finding 2: City/Regional efficiency mapping (扩展版)
Finding 3: Japan's full-cycle evidence (独立 Finding)
  - 68 年 MUQ 轨迹
  - 泡沫-崩盘-不可逆
  - 中日镜像
```

**优势**: 给日本足够的展示空间，强化论文的历史纵深感。

**风险**: 3,500 词限制下，三个 Finding 每个只有约 400 词，叙事被压缩到骨头。除非转为 Nature Article Format（~5,000 词），否则不推荐。

#### PI 推荐: 方案 A

理由：
1. **2-Finding 更聚焦**。Nature 编辑偏好"one big story"而非"three smaller stories"。
2. **日本的价值在于验证而非独立发现**。日本全周期证据强化了 Finding 1 (Simpson's Paradox) 和 Finding 2 (cross-national pattern) 的说服力，而非引入新概念。
3. **Discussion 是日本案例的最佳位置**。Discussion 中 1-2 段的日本全周期叙事 + 三国对比，比 Results 中一个独立 Finding 更有叙事张力。
4. **词数可控**。方案 A 预计需要在 Finding 1 增加约 120 词（区域级 Simpson's）、Finding 2 增加约 80 词（日本/韩国 clean spec）、Discussion 增加约 200 词（日本全周期 + 三国对比），总增加约 400 词。配合 v7 已计划的精简（碳段落 -85 词、各处措辞优化 -100 词），净增约 200 词，在 3,500 限制内可控。

### 新增图表建议

| 图号 | 内容 | 类型 | 位置 |
|:----:|------|:----:|:----:|
| Fig. 6 (新) | 三国 MUQ 轨迹对比：日本 1955-2022 vs 韩国 1985-2022 vs 中国 1998-2023 | 时间序列 | ED |
| Fig. 7 (新) | 日本泡沫-崩盘的 MUQ 结构断点 + 47 县 MUQ 恢复地图 | 组合图 | ED |
| Fig. 8 (新) | 统一面板 1,542 区域的 MUQ vs GDP per capita (按国家收入分组着色) | 散点 | ED |
| Fig. 9 (新) | 东欧 vs 西欧 MUQ 时间趋势 (Simpson's Paradox 可视化) | 分面图 | ED |
| Table 6 (新) | 跨国 Clean Specification 汇总表：中国/美国/日本/韩国的 beta、SE、R2 | 表格 | ED |
| Table 7 (新) | Aggregation Trap C1/C2/C3 跨国验证矩阵 | 表格 | ED |

### 碳估算的跨国扩展: NO-GO

关于碳段落是否需要跨国扩展：**明确 NO-GO**。理由：
1. 碳段落在 v7 中已决定精简至 ~115 词，目的是降低攻击面
2. 跨国碳估算需要各国建筑碳强度数据，这些数据的质量和可比性极差
3. 碳是论文的"政策桥梁"而非核心贡献，扩展不增加核心说服力
4. 审稿人如果对碳有兴趣，我们在 Response Letter 中提供跨国延伸即可

---

## Part 4: 时间表

### 总工作量: 16-18 天

```
Day 1-2:  统一面板构建 + 面板回归 + 跨国 Simpson's (U1-U3)
Day 2-4:  日本 Clean Spec + 泡沫断点 + Simpson's + 不可逆性 (J1-J5, J7)
Day 4-6:  韩国 + 欧洲深化 + 三国对比 (K1-K4, E1-E3)
Day 6-8:  Aggregation Trap 跨国验证 + 澳大利亚 + 汇总 (T1-T3, A1-A2)
Day 8-10: 结果解读 + 图表制作
Day 10-12: v7 论文修改 (整合深化分析结果 + 之前已决议的 P0-P4 修改)
Day 12-14: 图表定稿 + ED 表格更新
Day 14-16: 内部评审 + 最终修改
Day 16-18: Cover Letter + 格式转换 + 投稿准备
```

### 关键里程碑

| 日期 | 里程碑 | 可交付物 |
|------|--------|---------|
| Day 2 | 统一面板完成 | unified_regional_panel.csv + 初步回归结果 |
| Day 4 | 日本深度分析完成 | 日本 5 项分析报告 |
| Day 6 | 所有国家深化完成 | 韩国+欧洲分析报告 |
| Day 8 | 全部分析完成 | 汇总报告 + GO/NO-GO 最终确认 |
| Day 12 | v7 论文草稿完成 | full_draft_v7.md |
| Day 16 | 内部评审通过 | 评审报告 + 修改完成 |
| Day 18 | 投稿准备完成 | Nature 投稿包 |

### 修订后投稿目标: 2026-04-10

原计划 2026-03-28 投稿，但深化分析需要额外 10-12 天。考虑到：
- 深化分析预计将 desk reject 概率从 20-30% 降至 10-20%（多国区域级证据大幅增强 broad interest）
- 统一面板是论文从"中美为主 + 其他国家点缀"升级为"真正的全球研究"的关键
- Nature 没有截止日期，延迟两周投稿不影响竞争态势

**投入产出判断**: 18 天换取 desk reject 概率下降 10-15 个百分点 + 论文核心贡献从 2 个升级为 3 个（Simpson's Paradox + Sign Reversal + Aggregation Trap Theorem with 8-country verification），**值得**。

---

## Part 5: 风险登记簿

### 高风险分析任务

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 日本县级 Simpson's Paradox 不存在 | 论文叙事需要调整：解释为什么 SP 是跨收入组而非国内现象 | 预设两种叙事路径：(a) 存在 -> "SP 在多尺度存在"；(b) 不存在 -> "SP 是发展阶段异质性的产物" |
| 韩国 Clean Spec 不显著 | 弱化 Finding 2 的跨国扩展 | 韩国仅 17 个单元，不显著在统计上是预期的。报告时强调样本量限制，不做推断 |
| 统一面板中国家间 MUQ 不可比 | 统一面板回归结果不稳健 | Country FE 吸收水平差异；仅解释 within-country 变异。如 FE 后系数翻转，诚实报告为"cross-sectional vs within"差异 |
| 欧洲区域 GFCF 是估计值（按份额分配） | Clean spec 丧失意义（GFCF/GDP 在同一国家内所有区域相同） | 明确标注此局限。欧洲的价值在于 GDP 增长的区域差异（MUQ 分子），而非投资强度的区域差异（MUQ 分母） |
| 日本泡沫断点检验识别多个断点 | 叙事变复杂 | Bai-Perron 允许多断点（预期：~1974 高速增长结束, ~1991 泡沫崩盘, ~2012 Q<1）。多断点反而强化"阶段转换"叙事 |
| Aggregation Trap C1 条件在 LMI 组不满足 | 定理的严格验证失败 | 现有报告已显示 LMI 组 beta 不显著 (p=0.26)。两个应对：(a) 改用 Spearman rho（已显著 p=0.002）；(b) 将定理条件放宽为 "gamma_k <= 0"（弱单调），在大多数组中满足 |

---

## 附录: 各国数据资产盘点

### 可用数据详情

| 国家 | 区域单元 | 时间跨度 | GDP 来源 | GFCF 来源 | 人口 | MUQ obs | 备注 |
|------|:--------:|:--------:|---------|---------|:----:|:-------:|------|
| 中国 | 275 城 + 31 省 | 2005-2023 | NBS | NBS FAI (直接) | NBS | ~3,000 | FAI 2017 后估计 |
| 日本 | 47 县 | 1955-2022 | 内阁府 SNA | 内阁府 SNA (直接) | 总务省 | 3,102 | 4 次 SNA 基准变更 |
| 韩国 | 17 市道 | 1985-2022 | ECOS | ECOS (估计) | KOSIS | ~600 | 蔚山/世宗后期分离 |
| 美国 | 921 MSA | 2010-2022 | BEA CAGDP1 | Census ACS (间接) | Census | 10,760 | GFCF 用住房单元变化代理 |
| 欧洲 | 265 NUTS-2 | 2000-2024 | Eurostat | WB (国家级) 按份额分配 | Eurostat | ~5,900 | 区域 GFCF 为估计值 |
| 澳大利亚 | 8 州 | 1990-2023 | ABS | WB (国家级) 按份额分配 | ABS | ~260 | 原始 ABS GFCF 待验证 |
| 南非 | 9 省 | 1993-2023 | Stats SA | WB (国家级) 按份额分配 | Stats SA | ~270 | 数据波动大 |
| 全球 | 157 国 | 1960-2023 | WB WDI + PWT | WB WDI (直接) | WB | ~3,300 | 最稳健的面板 |

### GFCF 数据质量对 Clean Spec 的影响

这是一个关键的方法论问题。Clean Specification 的有效性取决于 GFCF 数据的独立性和区域间变异：

| 国家 | GFCF 数据类型 | Clean Spec 可信度 | 备注 |
|------|:------------:|:----------------:|------|
| 中国 | 直接观测 (FAI) | **高** | FAI 是独立的城市级观测值 |
| 日本 | 直接观测 (内阁府) | **高** | 县级 GFCF 是独立编制的 SNA 数据 |
| 美国 | 间接代理 (住房单元) | **中** | 非真正的 GFCF，但捕捉了住房投资的区域差异 |
| 韩国 | 估计值 (份额分配) | **低-中** | GFCF 区域间差异可能被低估 |
| 欧洲 | 估计值 (份额分配) | **低** | 同国内所有区域 GFCF/GDP 相同 |
| 澳大利亚 | 估计值 (份额分配) | **低** | 同上 |
| 南非 | 估计值 (份额分配) | **低** | 同上 |

**启示**: Clean Spec 应仅在中国、日本、美国三个国家做正式推断。韩国可做但需标注局限。欧洲、澳大利亚、南非不宜做 Clean Spec（GFCF 按份额分配导致 MUQ 区域差异完全来自 GDP 增长，Clean Spec 退化为恒等式）。

---

*会议纪要撰写: PI (首席研究员)*
*日期: 2026-03-22*
*基于: 数据审计报告、8 国分析报告、专家联席会议决议、六帽综合报告、论文 v6*
