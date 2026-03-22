# 最终战略定位会议纪要

**日期**: 2026-03-22
**会议级别**: 全体科研组 + 专家组最高级别战略讨论
**主持**: PI (研究主任)
**议题**: (A) 碳维度的命运; (B) 论文核心科学贡献; (C) 论文重新定位

---

## Part 1: 11 位专家逐一发言记录

---

### 第一轮: 五位学科审稿人

---

#### R1: Nature 主编视角

**碳维度立场: A4 (降为 ED 注释)**
**核心贡献定位: Aggregation Trap 定理**

Nature 选稿有三条硬标准: broad interest、novelty、rigour。让我评估这篇论文。

**一句话卖点**: "The statistics governments use to guide trillions of dollars in urban investment are structurally incapable of detecting that it is failing."

这句话能过 dinner party 检验。一个非专业读者能理解"你以为一切正常，但那是统计幻觉"。问题在于执行层面。碳维度在当前论文中是一个分散注意力的副产品。Nature 读者读完会记住 Simpson's Paradox 和 Aggregation Trap，不会记住 2.7 GtCO2 这个数字——因为这个数字只适用于中国，而且有大量 caveats。碳维度将论文从"揭示全球统计盲区"降格为"中国建筑碳排放的一种估算"。我的建议是将碳压缩到 Extended Data 的一个注释中，释放 150 词给 Aggregation Trap 的一般性讨论——那才是 Nature 读者会引用的东西。

**5 年后引用**: 方法论 (Aggregation Trap 定理) > 发现 (Simpson's Paradox in urban investment) > 数据集 (MUQ 面板)。碳不会被引用。

**竞争对手**: Hsieh-Klenow (2009) 在 QJE 上做了 firm-level misallocation。本文做的是 city-level misallocation。如果能清晰建立这个类比，这是一篇 Nature 级别的论文。碳维度模糊了这个类比。

---

#### R2: 城市标度律专家

**碳维度立场: A1 (完全删除) 或 A4**
**核心贡献定位: 标度律资产负债表分解 + Aggregation Trap**

从复杂系统角度看，这篇论文有两个理论贡献，一强一弱。

强贡献是 Aggregation Trap 定理。Simpson's Paradox 人人知道，但没人给出过"在什么条件下它必然发生"的充分条件定理，尤其是在经济发展语境中。三个条件 (A1 within-decline, A2 compositional shift, A3 dominance) 简洁、可检验、可推广。这不是标度律本身的创新，但它是对"为什么聚合指标会误导"的一般性形式化——这对整个复杂系统领域都有价值。我唯一的担忧是定理本身相当直接——本质上是对加权平均导数的 product rule 分解。但直接不等于平庸。Piketty 的 r > g 也是直接的，关键在于经验对应。

弱贡献是 beta_V 分解 (mechanical vs economic)。V = Pop x Area x Price 的分解本身是恒等式，不是发现。但将标度指数分解为 mechanical (=1) 和 economic (beta_A + beta_P) 部分，并指出 cross-national difference 中 mechanical 部分精确抵消——这是方法论上有用的澄清。它不会改变标度律文献的方向，但会被后续研究引用。

碳与标度律无关。它是一个应用，不是理论。从论文架构的纯净性考虑，我倾向完全删除碳，或者至多放在 ED。

**是否史无前例**: Aggregation Trap 定理的形式化是新的。标度律分解不是史无前例的——Arcaute et al. (2015) 和 Leitao et al. (2016) 都讨论过 boundary effects 和 mechanical components。但将两者结合用于城市投资效率诊断，是新的组合。

---

#### R3: 发展经济学家

**碳维度立场: A4 (降为注释)**
**核心贡献定位: 将 misallocation 从 firm 扩展到 city/nation**

这篇论文的经济学贡献我给出明确评价。

MUQ 作为指标: 是否会被采用？坦率地说，不确定。MUQ 本质上是 inverse ICOR，Easterly (1999) 已经批评过 ICOR 作为规划工具的问题。论文承认这一点并明确说"diagnostic, not normative"，这是正确的。但发展经济学界对 ICOR 类指标有深层怀疑。MUQ 要被采用，需要展示它比现有工具 (Dabla-Norris et al. 2012 的 PIMI, Gupta et al. 的 efficiency frontier) 提供了什么增量信息。当前论文没有做这个对比。

对 misallocation 文献的贡献: 这是论文真正的价值。Hsieh-Klenow (2009) 在 firm level 测量了 misallocation 对 TFP 的影响。本文在 city level 和 nation level 测量了类似的东西——投资回报率的 cross-sectional 异质性。China beta = -0.37 vs US beta = +2.81 这个 sign reversal 是强有力的。它说明: 在中国，投资越多的城市回报越低 (资本被配置到低效率的地方)；在美国，投资越多的城市回报越高 (资本追逐需求)。这个 pattern 值得发表。

碳维度对这个核心贡献没有帮助。一个发展经济学审稿人看到碳会想: "作者是不是想两头讨好？" 把碳放到 ED 注释里，作为"consequences of misallocation"的一个量化即可。

**5 年后引用**: 论文会因为 "China-US sign reversal in investment-return relationship" 和 "Aggregation Trap 定理" 被引用，不会因为碳数字。

---

#### R4: 计量经济学家

**碳维度立场: A4 (降为方法注释)**
**核心贡献定位: Clean specification + GDP-MUQ 交叉验证**

方法论角度的评估。

Clean specification: DeltaV/GDP ~ FAI/GDP 消除了 shared-denominator mechanical correlation。这不是方法论创新——文献中已知如何处理 ratio-on-ratio regression (Kronmal 1993)。但在城市经济学语境中系统性地这样做是有价值的。83.7% attenuation 的报告是极其诚实的——这种透明度在 Nature 上会加分。

GDP-MUQ 交叉验证: 同一个 pattern 在 housing-based 和 GDP-based 两个完全不同的操作化下重现，且 GDP-based 版本免疫于房价周期——这是方法论上最有说服力的部分。它使得"这只是房价泡沫的反映"这一攻击失效。

统一面板回归: 1,567 regions, 8 countries, beta = -0.043 with country + year FE, R^2 = 0.457。这是 solid panel work。R^2 被 FE 驱动没关系——关键变量的系数方向和显著性才重要。

碳维度的方法论质量: 说实话，碳估算的方法论是这篇论文最弱的部分。MUQ flow method 和 Q stock method 都依赖于"MUQ < 1 的部分全算浪费"这个强假设，50% cap 是 ad hoc 的，Monte Carlo 传播的不确定性范围很宽 (2.0-3.5 GtCO2)。如果碳是核心贡献，这些方法论弱点会被审稿人严厉攻击。如果碳是注释，这些弱点就无关紧要。结论清楚: 降级碳。

**独立方法论价值**: Clean specification 本身没有独立发表价值，但 Aggregation Trap 定理的形式化 + 三层验证 (cross-national PASS, within-country FAIL) 有方法论贡献。

---

#### R5: 碳核算专家

**碳维度立场: A2 (保留中国，不扩展) 或 A4**
**核心贡献定位: (从碳角度) 碳是 consequence, 不是 contribution**

让我直接回答: 碳维度是否增强还是分散了论文？

**分散**。原因有三:

第一，方法论不够严格。真正的 embodied carbon 研究需要 process-based LCA 或 input-output LCA。本文用"MUQ < 1 的投资量 x 碳强度系数"估算——这是一个 back-of-envelope calculation，不是 carbon accounting。Pomponi & Moncaster (2017) 的引用说明作者知道这个差距，但承认差距不等于弥补差距。

第二，只做中国没有说服力。如果 Aggregation Trap 是全球现象，那么碳后果也应该是全球的。只做中国会让审稿人问: "日本失去的三十年浪费了多少碳？西班牙建筑泡沫呢？" 这些问题现在无法回答。

第三，扩展到其他国家在数据上是否可行？答案是: 部分可行但不充分。日本的碳强度数据可以从 AIJ (Architectural Institute of Japan) 获得，但 prefecture-level 的 GFCF 碳拆分需要大量假设。欧洲有 Eurostat 的 NAMEA 环境账户，但 NUTS-2 级别的建筑碳强度数据缺失。韩国有 Korea LCI Database 但不覆盖时间序列。美国有 EPA GHGRP 但不按 MSA 汇总。总结: 扩展需要至少 3-6 个月的数据工作，且结果的精度会远低于中国。

**我的建议**: 如果碳必须保留，保留中国 (A2)，但压缩到 Discussion 的 2-3 句话 + Methods M5 的技术细节。如果可以选择，A4 是更安全的选项。碳维度的真正价值不在于 2.7 GtCO2 这个数字，而在于"MUQ < 1 → excess carbon"这个逻辑链接。这个链接用一句话就能建立，不需要 150 词。

---

### 第二轮: 六顶思考帽

---

#### 白帽 (事实)

**碳估算在其他国家的数据可行性**:

| 国家/地区 | 建筑碳强度数据 | GFCF 建筑拆分 | 时间序列长度 | 可行性 |
|-----------|:------------:|:------------:|:-----------:|:------:|
| 中国 | CABECA, 年度 | NBS FAI, 年度 | 25 年 | 高 |
| 日本 | AIJ 基准值 | Cabinet Office SNA | 67 年 | 中 (需假设) |
| 韩国 | Korea LCI | ECOS | 37 年 | 中-低 |
| 美国 | EPA + EIA | BEA | 12 年 (MSA) | 低 |
| 欧洲 | Eurostat NAMEA | Eurostat | 24 年 | 低 (NUTS-2 缺失) |
| 澳大利亚 | NGA 因子 | ABS | 33 年 | 低 |
| 南非 | DEA 因子 | StatsSA | 30 年 | 极低 |

结论: 只有日本可以做一个粗略的对比，且需要至少 2-4 周的专项数据工作。全面扩展 (A3) 不可行。

**当前碳数字的硬事实**:
- 综合法 C: 2.97 GtCO2 (点估计), 90% CI [2.04, 3.47]
- 物理交叉验证: 3.78 GtCO2 [2.52, 5.04]
- 两者差距 0.81 GtCO2，方向一致
- 87.5% 的碳排放归因于 2021-2024 市场崩盘期——这期间 MUQ 下降主要反映房价调整而非物理过建
- 50% cap 是 ad hoc 的，没有理论依据

---

#### 红帽 (直觉)

**读者读完论文后，碳是核心印象还是干扰？**

坦白说: **干扰**。

我模拟了三种读者的阅读体验:

1. **城市经济学教授**: 读到 Simpson's Paradox + China-US sign reversal，兴奋。读到 Aggregation Trap 定理，心想"这个我可以教给研究生"。读到碳——"哦，他们还做了碳"，翻页。碳不会被记住。

2. **世界银行政策分析师**: 读到 MUQ 下降在聚合统计中不可见——直接影响他的工作。读到碳——"有趣，但这个数字对我的政策建议没有直接用途"。

3. **气候研究者**: 读到碳——"2.7 GtCO2？让我看看方法...MUQ < 1 的投资量乘以碳强度？这不是 LCA。而且 87% 来自 2021-2024 的房价调整？这不是真正的 embodied carbon overbuilding。" 不信服。

三种读者中，没有一种会因为碳维度而更重视这篇论文。第三种读者反而会因为碳而降低对论文的评价。直觉告诉我: 碳是一个 net negative。

---

#### 黑帽 (风险)

**碳维度最可能招致的攻击**:

1. "87.5% of your carbon estimate comes from 2021-2024 when MUQ decline is driven by housing price collapse, not physical overbuilding. You are conflating market correction with resource waste." —— 这个攻击在当前论文中没有充分的防线。

2. "Your 50% cap is arbitrary. Why not 30%? Why not 70%? The sensitivity analysis shows the point estimate shifts by over 1 GtCO2 depending on cap choice." —— Cap 的选择没有理论依据。

3. "You only do carbon for China but claim the Aggregation Trap is global. This asymmetry undermines both: the carbon estimate lacks global context, and the global claim lacks carbon quantification." —— 这是最致命的结构性攻击。

**不要碳会失去什么**:

1. 失去 Climate/Sustainability 标签——Nature 编辑可能看不到"broad relevance to climate"这条路径。
2. 失去媒体吸引力——"2.7 GtCO2" 是一个可以上新闻标题的数字。
3. 失去 IPCC Avoid-Shift-Improve 的政策桥梁。
4. 失去 cover letter 中的 "climate mitigation" 卖点。

**风险评估**: 碳维度被攻击的概率 > 70%。碳维度帮助过审的概率 < 20%。净预期值为负。

---

#### 黄帽 (价值)

**碳维度的真正价值是什么？有没有被低估的方面？**

被低估的方面: **碳维度建立了 MUQ 的政策工具属性**。

没有碳，MUQ 是一个诊断指标——它告诉你"投资效率在下降"。有了碳，MUQ 变成一个政策工具——它不仅告诉你效率在下降，还量化了"下降的物理后果"。这个区别在 IPCC 的 Avoid-Shift-Improve 框架中是关键的: MUQ < 1 可以作为 "Avoid" 层的 ex ante 筛选器——在浇筑混凝土之前就判断这笔投资是否值得。

但这个价值可以用一句话建立，不需要 150 词和一整个 Methods 段落。

真正被低估的价值: **2.7 GtCO2 等于一个全球大事件的规模**。为了给读者提供参照: 全球航空业年碳排放约 0.9 GtCO2，2.7 Gt 相当于全球航空业 3 年的碳排放。这个比较在当前论文中完全没有出现。如果要保留碳，至少应该加上这种 anchoring。

---

#### 绿帽 (创意)

**如果不要碳，用什么替代来提供政策桥梁？**

三个替代方案:

1. **"Trillions of dollars" 的量化**: 直接量化 MUQ < 1 对应的 below-parity investment 的美元规模。中国 2018-2024 年的 below-parity cumulative investment 粗估约 10-15 万亿美元。"$10 trillion in below-parity urban investment" 比 "2.7 GtCO2" 更直接、更容易理解、且不需要碳强度假设。这个数字直接来自 MUQ 本身，方法论上无懈可击。

2. **"India/Vietnam/Indonesia projection"**: 不量化碳，而是量化"如果印度/越南/印尼重复中国的 MUQ 轨迹，他们将在什么城镇化率阈值面临同样的效率陷阱"。这是 forward-looking 的政策桥梁，比回顾性的碳计算更有吸引力。

3. **"Japan cautionary tale" 的量化**: 日本 1991-2022 年 MUQ 均值 0.034 意味着 30 年间每单位投资只产生 3.4% 的价值增量。量化日本"失去的三十年"中 below-parity investment 的累计规模——这是一个已经完结的自然实验，数据完整，不需要碳强度假设。

**PI 权衡**: 方案 1 最简洁有力。方案 2 最具前瞻性。方案 3 最有数据支撑。三者可以组合使用。

---

#### 蓝帽 (综合)

**从论文整体架构看，碳的最优定位是什么？**

当前论文的叙事弧线是:

```
发现 (Simpson's Paradox)
  --> 机制 (Aggregation Trap 定理)
    --> 证据 (multi-country, multi-scale)
      --> 后果 (碳/美元/政策)
```

碳在架构中的角色是"后果"——它不是发现，不是机制，不是证据。后果可以有多种量化方式，碳只是其中一种，而且是方法论最薄弱的一种。

**最优定位 (我的建议)**:

Discussion 中用 2-3 句话建立 MUQ-碳逻辑链接:

> "Below-parity investment carries physical consequences. In China, where detailed data permit estimation, the cumulative excess embodied carbon associated with MUQ < 1 investment during 2000-2024 is approximately 2.7 GtCO2 (Methods M5; Extended Data Table 6). This positions MUQ as a potential ex ante screening tool within climate mitigation frameworks."

技术细节全部放入 Methods M5 和 ED Table 6。Discussion 段落从当前的 ~150 词压缩到 ~50 词。释放的 ~100 词分配给:
- Aggregation Trap 一般性讨论 (+50 词)
- "Trillions of dollars" 的量化 (+30 词)
- India/Vietnam/Indonesia 前瞻 (+20 词)

这个方案实质上是 **A4 的强化版**: 碳保留为数据点但不突出，政策桥梁由美元量化和前瞻预测替代。

---

## Part 2: 投票表决

### 碳维度投票

| 选项 | 投票 | 投票者 |
|------|:----:|--------|
| A1 完全删除 | 1 | R2 |
| A2 保留中国不扩展 | 1 | R5 (备选) |
| A3 扩展到其他国家 | 0 | — |
| A4 降为 ED 注释 | 9 | R1, R3, R4, R5 (首选), 白帽, 红帽, 黑帽, 黄帽, 蓝帽 |

**碳维度决议: A4 (降为 ED 注释)，以 9:1:1:0 压倒性通过。**

具体执行: Discussion 保留 2-3 句话 + Methods M5 保留技术细节 + ED Table 6 保留完整数据。从 Discussion 释放 ~100 词用于强化 Aggregation Trap 一般性讨论和美元量化。

---

### 核心贡献一句话 (综合 11 位共识)

各位专家的一句话概括:

| 专家 | 一句话 |
|------|--------|
| R1 | 现有统计体系无法检测城市投资效率的衰退 |
| R2 | 加权平均在发展演化中必然掩盖组内衰退 |
| R3 | 城市资本的 misallocation 可从 firm level 扩展到 city level |
| R4 | 同一个 pattern 在两种完全不同的操作化下重现 |
| R5 | MUQ < 1 建立了投资效率与物理后果的逻辑链接 |
| 白帽 | 1,567 regions x 8 countries 的统一面板是最扎实的数据贡献 |
| 红帽 | 读者会记住"每个国家都在衰退但加总看不出来" |
| 黑帽 | 论文最脆弱之处是因果推断的缺失，最强之处是多重验证的收敛 |
| 黄帽 | Aggregation Trap 定理的一般性远超城市投资 |
| 绿帽 | 这篇论文的真正遗产是一个可推广的统计陷阱定理 |
| 蓝帽 | Simpson's Paradox + 定理 + 多国证据 = 完整叙事弧线 |

**综合共识版本**:

> "Aggregate statistics on urban investment returns are structurally misleading: a Simpson's paradox, proven to be a mathematical necessity under three empirically verified conditions, conceals declining marginal returns within every developing-economy income group -- confirmed independently under both housing-based and GDP-based formulations across 157 countries and 1,567 subnational regions."

---

### 是否需要改标题

**投票: 7:4 倾向修改标题。**

当前标题: "Simpson's paradox masks declining returns on urban investment worldwide"

问题: 标题将论文定位为"一个统计现象的发现"，而论文的真正贡献是"一个统计陷阱的形式化 + 多层级证据"。

**建议标题** (按偏好排序):

1. **"The aggregation trap: declining urban investment returns hidden in plain sight"**
   - 优势: 突出理论贡献 (Aggregation Trap)，暗示问题的普遍性
   - 劣势: "hidden in plain sight" 略口语化

2. **"A global aggregation trap conceals declining returns on urban investment"**
   - 优势: 严谨，包含 global scope
   - 劣势: 稍显平淡

3. **"Simpson's paradox masks declining returns on urban investment worldwide"** (保留原标题)
   - 优势: Simpson's Paradox 知名度高，搜索友好
   - 劣势: 低估了论文的理论贡献

4. **"Every city declines but the nation appears fine: an aggregation trap in urban investment"**
   - 优势: 叙事力量强，Box 1 标题已验证有效
   - 劣势: 太长，Nature 偏好短标题

**PI 评估**: 保留当前标题不会致命。如果要改，首选方案 2，因为它最平衡地传达了论文的三个维度: global scope + aggregation trap + declining returns。但这个决策可以推迟到最终投稿前。

---

### 议题 B: 论文核心科学贡献的深度评估

**11 位专家的综合回答**:

**1. 用一句话概括核心贡献**:
(见上方综合版本)

**2. 是否"史无前例"？**
不是完全史无前例，但是一个**新颖的组合**:
- Simpson's Paradox 本身是 1951 年的概念
- ICOR / Tobin's Q 在宏观经济学中已有广泛应用
- 但将 Tobin's Q 应用于城市资产负债表，跨 157 国构建统一面板，并证明 Aggregation Trap 定理——这个组合是新的
- 在已有文献中的位置: 介于 Hsieh-Klenow (2009, firm misallocation) 和 Bettencourt et al. (2007, urban scaling) 之间，填补了"城市级别资本配置效率"的空白

**3. 5 年后引用原因**:
- 排名 1: **Aggregation Trap 定理** — 作为一般性方法论工具被引用 (类似 Simpson's Paradox 本身被引用的方式)
- 排名 2: **MUQ 的 cross-national 比较** — 作为城市投资效率的基准数据集被引用
- 排名 3: **China-US sign reversal** — 作为 institutional divergence 的证据被引用
- 排名 4: 碳 (不太可能被引用)

**4. 如果删掉碳维度，核心贡献是否受损？**
**共识: 不受损。** 11 位中有 10 位认为核心贡献不依赖于碳。1 位 (黄帽) 认为碳提供了"物理后果"的量化，有独立价值，但同意可以用美元量化替代。

**5. 论文最大的竞争对手？**
- **Hsieh & Klenow (2009) QJE**: Firm-level misallocation。最接近的概念性竞争对手——但他们做的是 firm，我们做的是 city/nation，且他们没有 aggregation trap。
- **Bai, Hsieh & Song (2016) Brookings**: China fiscal expansion 的长期影子。最接近的实证竞争对手——但他们聚焦中国，我们做全球比较。
- **没有直接竞争对手** 同时做: cross-national MUQ + Simpson's Paradox + 形式化定理。

**6. 普通 Nature 读者读完会说什么？**
> "哦，原来全球城市投资回报率一直在下降，只不过因为穷国变成中等收入国家，加总数据看上去没事。但这个掩盖效应有数学证明，而且不只适用于城市投资。"

---

### 议题 C: 论文重新定位

**当前定位**: "Simpson's Paradox masks declining returns"
**推荐定位**: 不需要根本性重新定位，但需要**重心微调**。

当前论文的叙事重心在 Finding 1 (Simpson's Paradox) 和 Finding 2 (city-level sign reversal) 之间分配较均匀。11 位专家的共识是:

**Aggregation Trap 定理应该被提升为论文的第一卖点**，Simpson's Paradox 从"发现"降为"定理的经验背景"，city-level 证据从"并列发现"降为"定理的多层级验证"。

这不是改变内容，而是改变**叙事框架**:

| 元素 | 当前定位 | 推荐定位 |
|------|---------|---------|
| Simpson's Paradox | 核心发现 | 定理的经验动机 |
| Aggregation Trap 定理 | Box 1 的一部分 | 论文的核心理论贡献 |
| City-level sign reversal | 并列发现 | 定理的多层级验证 |
| China-Japan mirror | 比较分析 | 定理预测的自然实验 |
| 碳 | Discussion 段落 | ED 注释 |

---

## Part 3: PI 最终裁决

我在听取了全部 11 位专家的意见后，做出以下决策。

### 裁决 1: 碳维度 -- 采纳 A4 (降为 ED 注释)

理由:
1. 碳估算的方法论是论文最弱的环节，突出它是给审稿人递刀子
2. 87.5% 归因于 2021-2024 市场崩盘期这一事实使得"碳后果"的叙事在学术上站不稳
3. 碳只做了中国而论文主打"全球"——这个不对称是结构性矛盾
4. 碳维度被攻击的概率远高于它帮助论文过审的概率
5. 绿帽提出的"美元量化"替代方案更简洁、更直接、方法论上更无懈可击

**具体执行**:
- Discussion 碳段落从 ~150 词压缩至 ~50 词 (2-3 句话)
- Methods M5 保留但标注为 "Extended Data Methods"
- ED Table 6 保留完整碳数据
- 释放的 ~100 词分配给: Aggregation Trap 一般性 (+50), 美元量化 (+30), 前瞻预测 (+20)
- Cover letter 中 "climate mitigation" 从四大卖点降为一句辅助说明
- Abstract 中 "2.7 GtCO2" 删除，替换为 aggregation trap 一般性的表述

### 裁决 2: 核心定位 -- 维持当前框架，微调重心

不做根本性重新定位。但:
- Aggregation Trap 定理在 Discussion 中获得独立段落 (已有)，进一步强化其一般性
- Abstract 的最后一句话 (目前是碳) 改为 Aggregation Trap 的推广性
- 标题暂时保留，投稿前一周再做最终决定
- Cover letter 的"四大贡献"重新排序: (1) Aggregation Trap 定理, (2) Simpson's Paradox, (3) Multi-country evidence, (4) Policy tools

### 裁决 3: 标题 -- 暂时保留，候选替代方案备选

当前标题 "Simpson's paradox masks declining returns on urban investment worldwide" 的优势在于搜索友好性和概念清晰度。Aggregation Trap 作为新术语需要论文本身来建立认知度。在论文被接受或进入 R&R 之前，Simpson's Paradox 是更好的"入口概念"。如果审稿人建议改标题，首选: "A global aggregation trap conceals declining returns on urban investment"。

---

## Part 4: 具体行动清单

### 立即执行 (v7.1 微调, 预计 2-3 小时)

| # | 行动 | 位置 | 优先级 |
|---|------|------|:------:|
| 1 | Abstract: 删除 "Below-parity investment in China is associated with an estimated 2.7 GtCO2 in excess embodied carbon."，替换为 "The aggregation trap -- in which compositional shifts between income groups mask within-group decline -- may extend to any domain where heterogeneous units are evaluated on pooled metrics." | Abstract | P0 |
| 2 | Discussion 碳段落: 压缩为 2-3 句话 | Discussion | P0 |
| 3 | Discussion: 增加 "美元量化" (below-parity investment 的累计美元规模) | Discussion | P1 |
| 4 | Discussion: 增加 India/Vietnam/Indonesia 前瞻 1 句 | Discussion | P1 |
| 5 | Discussion Aggregation Trap 段落: +50 词强化一般性 | Discussion | P1 |
| 6 | Cover letter: 重新排序四大贡献，碳降为辅助 | Cover letter | P1 |
| 7 | ED Table 6: 确保碳数据完整保留 | Extended Data | P2 |
| 8 | Methods M5: 标注为 Extended Data Methods 或保留但精简 | Methods | P2 |

### 投稿前检查 (v7.1 定稿后)

| # | 检查项 |
|---|--------|
| 1 | 全文搜索 "carbon" / "GtCO2" / "embodied"，确认只在 Discussion 2-3 句 + Methods M5 + ED 中出现 |
| 2 | 确认美元量化的数字来源和计算逻辑 |
| 3 | 确认 Abstract 修改后仍在 Nature 字数限制内 (~200 词) |
| 4 | 标题最终决定: 保留原标题或更换 |
| 5 | Cover letter 与论文内容一致性检查 |

---

## 附录: 关键引文存档

**碳维度讨论中形成的关键判断** (供未来审稿回复使用):

1. 碳估算的 87.5% 归因于 2021-2024 市场崩盘期——这不是物理过建，而是市场调整
2. 50% cap 没有理论依据，是 ad hoc 选择
3. 只做中国碳与全球 Aggregation Trap 之间存在结构性不对称
4. MUQ-碳逻辑链接可以用一句话建立，不需要详细量化
5. 如果审稿人要求扩展碳到其他国家: 只有日本部分可行，需 2-4 周，精度低于中国

**论文核心价值的最终共识** (供 cover letter 和 rebuttal 使用):

1. Aggregation Trap 定理: 一般性理论贡献，超越城市投资
2. Simpson's Paradox 的双重验证: housing-based + GDP-based
3. 1,567-region 统一面板: 最大的 subnational 城市投资效率数据集
4. China-US sign reversal: institutional divergence 的定量证据
5. Japan 67 年自然实验: 最长的城市投资效率时间序列

---

*会议结束。下一步: 执行 v7.1 修改。*
