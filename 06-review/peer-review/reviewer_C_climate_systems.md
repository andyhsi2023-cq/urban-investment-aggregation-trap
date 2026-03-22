# Reviewer C: Climate Science / Complex Systems / Sustainability

**Reviewer profile**: 可持续发展科学教授 (Oxford/ETH/Columbia 级别)，研究方向涵盖城市碳排放、planetary boundaries、复杂系统临界转变。Nature / Nature Climate Change / Nature Sustainability 审稿人。
**审稿日期**: 2026-03-21
**论文**: "A Simpson's paradox masks declining returns on urban investment worldwide" (full_draft_v2.md)
**目标期刊**: Nature (Article format)

---

## 1. 总体评价

**推荐: Major Revision** (倾向积极，修改后可达到 Nature 或 Nature Cities 水准)

这是一篇在概念上具有吸引力的论文。核心贡献 -- 用 Simpson's Paradox 揭示全球城市投资效率衰减被聚合数据掩盖 -- 是一个优雅的发现，具有跨学科可读性。将 Tobin's Q 从企业金融移植到城市尺度，再与碳核算交叉，这种跨域架构如果执行到位，完全可以成为一篇有影响力的多学科论文。

然而，作为一位关注气候政策和复杂系统的审稿人，我对这篇论文的碳排放估计方法和政策含义有重要保留意见。5.3 GtCO2 这个数字在传播中可能被放大或误读，但其方法学基础比数字本身暗示的要脆弱。此外，论文在跨学科"落地"方面存在不足 -- 它没有与建筑碳核算 (embodied carbon) 的成熟文献充分对话，这在 Nature 审稿过程中可能成为一个致命短板。

**对标 Nature**: 论文的"故事"足够引人注目（Simpson's Paradox + 全球最大资本错配 + 碳成本），但执行水平目前更接近 Nature Cities 而非 Nature 正刊。要跨过 Nature 的 bar，需要在碳估计的方法学可信度和跨学科文献嵌入方面做实质性加强。

---

## 2. 跨学科贡献评估

### 2a. 对城市科学的贡献: 高

MUQ 框架的最大价值在于它提供了一个可跨国比较的、边际性质的投资效率指标。现有城市经济学文献中，Glaeser-Gyourko 的住房供需分析和 Bettencourt 的城市标度律分别从需求端和产出端研究城市，但没有一个指标直接回答"下一单位投资是否还值得"这个问题。MUQ 填补了这个空白。

Simpson's Paradox 的发现具有方法论示范意义。它提醒城市研究者在使用跨国面板数据时必须进行收入组分层分析 -- 这个教训对 SDG 11 (可持续城市) 相关的全球监测框架有直接意义。我预期这个发现如果发表在高影响力期刊上，会被后续研究广泛引用。

中国-美国对比（beta = -2.23 vs. +2.75 的符号反转）是一个干净的实证 stylized fact，可以被后续的理论和实证工作引用。

**但需注意**: MUQ 目前是一个"描述性指标"而非"因果工具"。论文在这一点上是诚实的（反复强调 descriptive），但这也意味着 MUQ 框架的采用率可能受限于其因果可解释性的不足。

### 2b. 对气候/碳核算的贡献: 中等偏低（这是主要弱点）

5.3 GtCO2 的估计是论文中最具政策冲击力的数字，但恰恰是方法学上最薄弱的环节。具体问题见第 3 节详述。

从气候科学角度，这个数字缺乏与现有碳核算文献的对话。论文没有引用：
- IPCC AR6 WG3 第 9 章 (Buildings) 关于 embodied carbon 的结论
- Global Alliance for Buildings and Construction (GlobalABC) 的年度全球报告
- IEA 的 Global Status Report for Buildings and Construction
- Creutzig et al. (2016, Nature Climate Change) 关于城市形态与碳排放的系统综述
- Zhong et al. (2021, Nature Communications) 关于中国建筑 embodied carbon 的研究

没有这些锚定，5.3 GtCO2 这个数字就悬浮在真空中 -- 读者无法判断它在全球建筑碳排放的版图中处于什么位置。

### 2c. 对发展经济学的贡献: 中等偏高

Simpson's Paradox 的发现对发展经济学有直接意义。Pritchett (2000) 的经典论文指出发展中国家公共投资回报率可能很低，但没有在全球面板中系统地分解聚合偏差。本文补充了这一空白。

"收入组毕业效应"作为 Simpson's Paradox 的机制解释是有说服力的：随着国家从低收入向中等收入过渡，它们同时经历投资效率衰减和收入组跃迁，两者的组合在聚合数据中制造了"一切正常"的假象。这个洞见对世界银行、亚开行等机构的投资评估框架有直接批判性意义。

### 2d. 对复杂系统科学的贡献: 有限（但放弃相变叙事是正确的决策）

v5 放弃了"相变/标度律"叙事，我认为这是一个明智的决定。原因：

1. **数据不支持相变叙事**。真正的相变需要临界指数（critical exponents）、标度不变性（scale invariance）、普适性（universality class）等严格的物理学诊断。论文的数据 -- 无论是 Bai-Perron 断点还是 MUQ 衰减 -- 都更接近于一个渐进的体制转变（regime transition）而非物理学意义上的相变。如果保留相变叙事，任何受过统计物理训练的审稿人都会指出这一点。

2. **避免了术语滥用的批评**。"Phase transition" 在复杂系统文献中被过度使用已经引起反弹（参见 Scheffer et al. 2012 在 Science 上关于 critical transitions 的综述中对术语滥用的警告）。Nature 的编辑对此高度敏感。

3. **但仍有空间**。如果作者有意，可以在 Discussion 中用一段话（~50词）指出：MUQ 的非线性衰减（碳排放在 MUQ 接近零时非线性加速）与复杂系统中的 "tipping point" 行为有表面相似性，但需要更长时间序列和更严格的诊断才能确认。这种谨慎的表述既保留了跨学科趣味性，又不招致方法论批评。我特别注意到碳排放的时间分布（>90% 集中在 2021-2024）确实展现了一种非线性加速模式，这值得在未来工作中用临界转变的分析框架来检验。

---

## 3. 碳排放估计的深度审查

### 3a. 方法学审查

**核心假设 "MUQ < 1 = 浪费性投资" 存在根本性问题。**

这是我最重要的审查意见。论文将 MUQ < 1 等同于"投资未能创造相应价值"，进而将对应的建设碳排放定义为"过度排放"。这个逻辑链条忽略了：

(i) **基础设施的正外部性**。即使一个城市的 MUQ < 1（即边际投资的资产价值回报低于成本），该投资也可能产生大量正外部性 -- 交通网络降低通勤成本、医院改善公共健康、学校提高人力资本。这些价值不会体现在房产价格中（论文的 V 主要由房价驱动），但它们是投资的核心正当理由。将这些投资的碳排放全部归为"浪费"，在概念上是成问题的。

(ii) **时间维度的价值实现**。基础设施投资的回报通常需要 10-30 年才能完全体现。一条 2022 年建成的高铁线路在 2024 年的 MUQ 中显示为负回报，但在 2035 年可能已经充分创造了价值。论文的年度 MUQ 框架天然偏向低估长期基础设施投资的价值。

(iii) **碳排放的不可逆性定义问题**。论文暗示这些碳排放是"可避免的"（avoidable），但这取决于反事实：如果不建设这些项目，替代投资是什么？如果替代投资同样涉及碳密集型活动（如制造业出口），净碳效果可能并不如论文暗示的那样清晰。

**建议**：论文应在正文中增加一段对 MUQ < 1 阈值的批判性讨论（而非仅在 Methods 中做敏感性分析），明确承认 MUQ 衡量的是"资产价值回报"而非"综合社会价值回报"，并建议读者将 5.3 GtCO2 理解为"与低资产回报投资相关联的碳排放"（carbon associated with low-asset-return investment），而非"浪费的碳排放"（wasted carbon）。

**仅计算建设阶段碳排放确实是保守的，但需要量化"保守了多少"。**

论文正确指出这是 conservative lower bound，但没有给出 operational carbon 的量级估计。按照 IEA 和 GABC 的数据，建筑全生命周期中运营碳（暖通空调、照明等）通常占总碳的 60-80%，embodied carbon 仅占 20-40%。如果将运营碳纳入，即使仅按 50% 的过度建设率（即论文的 MUQ < 1 标准），数字可能膨胀 2-4 倍。论文应至少在 Discussion 中提供一个 back-of-envelope 估计，说明如果包含运营碳，总量可能是 10-20 GtCO2 量级。这既增强了政策紧迫感，也为未来研究指明方向。

**时变碳强度 (1.20 -> 0.60 tCO2/万元) 的数据来源需要加强。**

论文引用"China Building Energy Conservation Association (2022)"作为碳强度来源，但：
- 这个来源是否覆盖了全部固定资产投资（包括道路、桥梁、工业厂房），还是仅覆盖建筑部门？FAI 的构成中建筑仅占一部分。
- 2.89% 的年均衰减率是否有独立验证？与 IEA 的中国建筑碳强度数据是否一致？
- CI(2000) = 1.20 tCO2/万元这个基准值是否考虑了 2000 年的能源结构（当时煤电占比更高）？

**建议**：增加一个 Extended Data 表格，列出碳强度参数的多个独立来源及其估计值，展示 1.20-0.60 的衰减路径与外部数据的一致性。

### 3b. 与现有碳核算文献的对话

**这是论文最大的缺陷之一。** 一篇声称估计了 5.3 GtCO2 碳排放的论文，必须与以下文献进行对话：

| 文献/来源 | 相关估计 | 论文是否引用 |
|-----------|---------|:----------:|
| IPCC AR6 WG3 Ch.9 (Buildings) | 全球建筑 embodied carbon: ~4.3 GtCO2/yr (2019) | 未引用 |
| GlobalABC Global Status Report 2023 | 建筑运营 + embodied: 全球 ~21% 能源相关 CO2 | 未引用 |
| IEA Buildings Tracking Report | 中国建筑碳排放时间序列 | 未引用 |
| Zhong et al. 2021 Nature Comms | 中国建筑 embodied carbon 19.1 GtCO2 (1995-2020) | 未引用 |
| Creutzig et al. 2016 NCC | 城市碳排放的驱动因素分类框架 | 未引用 |
| Huang et al. 2018 Nature CC | 中国建筑部门碳排放趋势 | 未引用 |
| Rao & Min 2018 Nature CC | 发展中国家基础设施碳锁定 | 未引用 |

这些文献的缺失不仅是学术礼仪问题，更导致了一个实质性缺陷：读者无法将 5.3 GtCO2 放入已有的碳核算知识体系中。例如，Zhong et al. (2021) 估计中国 1995-2020 年建筑 embodied carbon 为 19.1 GtCO2。论文的 5.3 GtCO2（2000-2024）是否大致是其中"过度建设"部分？如果两个估计在数量级上一致（5.3/19.1 ≈ 28%），这将大大增强论文估计的可信度。如果不一致，则需要解释原因。

### 3c. 政策含义审查

**"将投资效率指标整合到碳核算中"的建议**有吸引力但缺乏操作路径。

论文提出"integrating investment efficiency metrics into carbon accounting frameworks could identify avoidable embodied emissions before construction begins"。这个想法很好，但：

(i) **NDC 中纳入 embodied carbon 尚处起步阶段**。目前全球仅少数国家（如法国 RE2020、北欧国家的 Level(s) 框架）在建筑法规中限制 embodied carbon。在国家碳预算或 NDC 中纳入 embodied carbon 的先例几乎为零。论文应当指出这一制度缺口。

(ii) **MUQ 作为事前筛选工具的可操作性存疑**。MUQ 是事后衡量指标（需要投资完成后才能计算 Delta V）。要将其变为事前筛选工具，需要预测模型（predicted MUQ based on city characteristics + project type），而论文没有提供这样的模型。

(iii) **对新兴城镇化国家的警示价值是论文最强的政策贡献**。印度（当前城镇化率 ~36%，与中国 2000 年相似）、越南、印尼正在或即将进入大规模城市化。Simpson's Paradox 的发现暗示，这些国家的聚合投资统计可能同样掩盖效率衰减。论文应更明确地发展这个方向 -- 例如在 Discussion 中增加一段关于"全球碳预算含义"的讨论：如果印度、越南、印尼在城镇化过程中重复中国的投资模式，全球碳预算面临的额外压力可能是多少 GtCO2？即使只是 back-of-envelope 估计，也会极大增强论文对气候政策受众的吸引力。

**5.3 GtCO2 vs 中国总排放 2.7% -- 这个比例的政策意义**。

2.7% 听起来不大，但需要上下文：
- 全球年碳预算（1.5C 路径）剩余约 250 GtCO2（IPCC AR6），5.3 GtCO2 约为其 2%
- 中国建筑碳排放约占其总排放的 20%（IEA 数据），5.3 GtCO2 占建筑碳排放的 ~14%
- 5.3 GtCO2 大致相当于英国 10 年的总碳排放

论文应在 Discussion 中提供这些比较坐标系，帮助非专业读者理解数字的量级意义。

---

## 4. 图表质量与可视化审查

### Fig 1 (Simpson's Paradox) -- 论文成败之图

**整体评价**: 概念传达有效，但执行需要打磨。

**Panel a**: 灰色散点 + LOESS 展示聚合平坦趋势，思路正确。但灰色点云太密集、信息密度低。建议：(1) 用半透明 hexbin 替代散点以减少视觉噪声；(2) 在 LOESS 带上用大号数字标注 Spearman rho 和 p。

**Panel b**: 这是核心面板。按收入组展示的中位 MUQ 趋势线清晰可辨，红色（低收入）和绿色（上中等收入）线的下降趋势一目了然。蓝色虚线（高收入）的水平走势提供了对照。但：
- Y 轴标签 "Real MUQ (median)" 需要在图注中解释
- 高收入组（蓝色虚线）的波动较大，可能干扰读者对"水平趋势"的感知
- 建议增加趋势置信带（shaded area）以帮助读者判断趋势显著性

**Panel c**: Within vs Between 分解的柱状图是一个简洁的概念传达工具。Pooled rho = +0.038、Within = -0.076、Between = +0.114 的三个数字一目了然。这个面板是有效的。

**3 秒测试**: 对于城市科学/经济学读者，可以通过。对于分子生物学家，可能需要 10 秒 -- "Real MUQ" 这个术语太专业了。建议在图注第一句话就定义 MUQ = "每单位新增投资创造的资产价值"。

**色盲友好性**: 红/绿/蓝/青的配色方案对红绿色盲（约 8% 男性）可能有问题。建议使用 viridis 或 ColorBrewer 的 qualitative palette。

### Fig 2 (China cities) -- 有效但可改进

**Panel a**: 散点 + OLS 线 + 分位回归线的组合信息密集。按城市层级的颜色编码有效。OLS 线（beta = -2.26）和 Q90 线的明显分离清晰传达了"高回报城市对过度投资最敏感"的信息。

**需改进**:
- 图较小（可能是缩放问题），点过于密集
- X 轴 "Investment Intensity (FAI / GDP)" 的范围 0.2-1.4 需要帮助非中国研究者理解 -- 1.0 意味着固定资产投资等于 GDP，这本身就是一个惊人的数字
- 建议在图中标注几个代表性城市（如 Beijing, Shenzhen, Ordos）

**Panel b**: 层级梯度的箱线图清晰有效。MUQ = 0 和 MUQ = 1 的参考线是关键视觉锚点。

### Fig 3 (China-US contrast) -- 论文的"punchline"图

**Panel a**: 美国 MSA 散点图，beta = +1.39（注：图中标注的 beta 值与正文中的 beta = +2.75 不一致 -- 这是因为 Panel a 使用 DeltaV/GDP 而非 MUQ 作为 Y 轴？需要确认和澄清）。

**重大问题**: 图中 Panel a 的 beta 标注为 +1.39，但正文报告 beta = +2.75。如果这是不同规格的结果，必须在图注中明确说明。如果是错误，必须修正。这种数字不一致在 Nature 审稿中是"红旗"。

**Panel b**: 中美系数对比柱状图（DeltaV/GDP 统一规格）非常清晰。China = -0.37 vs US = +1.78 的对比具有视觉冲击力。95% CI 的误差线确认了统计显著性。"Supply-driven" 和 "Demand-driven" 的标签直接传达了制度解释。

**建议**: 这张图是论文的亮点之一。Panel b 的设计应作为模板。

### Fig 4 (Carbon) -- 目前仅有草图

碳排放不确定性图（fig_carbon_uncertainty.png）是四面板布局：

**Panel A (Monte Carlo 分布)**: 直方图清晰展示了中位数和 90% CI。红色/蓝色区分有效。

**Panel B (三情景时间序列)**: 保守/中等/激进情景的对比有效，但三条线在 2020 前几乎重叠，信息价值有限。

**Panel C (碳强度敏感性)**: 展示了 CI +/-30% 的影响，有用。

**Panel D (年度碳排放 + CI)**: 这是最重要的面板 -- 清晰展示了 2021-2024 的非线性爆发。90% CI 带的宽度合理。

**对 Nature 的适配性**: 四面板布局信息太密集。建议精简为两面板（Panel A 时间序列 + Panel B 龙卷风图/敏感性），将 Monte Carlo 分布和方法对比移入 Extended Data。

**总体图表评价**: 图表在概念传达上基本成功，但视觉打磨不足以达到 Nature 标准。字体、线宽、颜色一致性、色盲友好性均需统一调整。建议聘请专业科学可视化设计师做最后一轮打磨。

---

## 5. Broad Interest 评估

**如果这篇论文出现在 Nature 目录页上，以下读者会点开吗？**

| 读者群 | 会点开？ | 原因 |
|--------|:--------:|------|
| 气候科学家 | 可能 | "5.3 GtCO2 的碳浪费"是吸引人的钩子，但需要看到与 IPCC/IEA 框架的对话才会认真对待 |
| 分子生物学家 | 不太可能 | "Simpson's Paradox"是唯一可能吸引的钩子，但论文标题中的"urban investment"会立刻劝退 |
| 经济学家 | 是 | Tobin's Q 的城市化应用 + 中美对比是经济学家关心的问题 |
| 政策制定者 | 是 | "82.2% 的中国城市投资在亏本"是一个有冲击力的政策信号 |
| 媒体记者 | 是 | "全球最大的资本错配隐藏在统计数据中"是一个好标题 |

**Nature News & Views 潜力**: 有。一位城市经济学家或可持续发展学者可以围绕"当聚合统计掩盖衰退"写一篇 N&V。故事线清晰：Simpson's Paradox（方法论趣味性）+ 中国70万亿美元投资（规模冲击力）+ 碳成本（政策紧迫性）。

**5 年预期引用量**:
- 如果发表在 Nature: 150-300 次（跨学科引用，包括城市经济学、气候政策、发展经济学、统计方法论）
- 如果发表在 Nature Cities: 80-150 次（更集中于城市学科）
- 如果发表在 Nature Sustainability: 100-200 次（可持续发展 + 气候政策引用）

**最大障碍**: 分子生物学家是 Nature 最大的读者群，而这篇论文对他们没有吸引力。Nature 编辑在评估 broad interest 时会考虑这一点。Simpson's Paradox 作为方法论概念有跨学科趣味性，但论文的实质内容（城市投资效率）太"社会科学"了。这不意味着论文不适合 Nature -- Nature 定期发表经济学和城市学论文 -- 但它需要在标题和摘要中最大化跨学科可读性。

**标题建议**: 当前标题 "A Simpson's paradox masks declining returns on urban investment worldwide" 是好的 -- "Simpson's paradox" 是跨学科钩子。但可以考虑更具冲击力的替代方案：
- "Hidden decline: a global Simpson's paradox in urban investment efficiency"
- "The world's largest capital misallocation hides behind aggregate statistics"（更具媒体效果但不够学术）

---

## 6. 与 Nature 子刊的适配性比较

| 期刊 | 适配度 | 理由 |
|------|:------:|------|
| Nature | 6/10 | 跨学科"故事"有吸引力，但碳核算方法学薄弱、与气候文献缺乏对话是短板。Broad interest 对非社会科学读者偏弱。编辑可能 desk reject 后建议转投子刊。 |
| Nature Cities | 9/10 | **最佳适配**。论文的三个发现都直接服务于城市科学受众。Nature Cities 读者群是城市规划、城市经济学、可持续城市化领域的学者和政策制定者，这正是本文的目标受众。格式要求也更宽松（正文可到 5,000-6,000 词）。 |
| Nature Sustainability | 7/10 | 碳核算部分如果加强可以成为卖点，但论文目前的重心在投资效率而非可持续性。需要重新构架叙事，将碳成本从 Finding 3 提升到核心叙事线。 |
| Nature Climate Change | 4/10 | 碳估计是论文最弱的部分，而这恰恰是 NCC 最关心的。除非碳核算方法学得到大幅加强（增加全生命周期分析、与建筑碳数据库对比验证），否则不推荐。 |

---

## 7. 具体修改建议（按优先级排序）

### Priority 1 (必须修改 -- 影响可发表性)

**P1. 碳排放估计需要与建筑碳核算文献对话。**
在 Discussion 或 Methods 中增加一段（~100词），将 5.3 GtCO2 与 IPCC AR6 WG3 Ch.9、GlobalABC、Zhong et al. (2021 Nature Comms) 的估计进行三角验证。如果 Zhong et al. 估计中国 1995-2020 建筑 embodied carbon 为 19.1 GtCO2，那么 5.3 GtCO2（其中约 28%）作为"低效投资份额"是否合理？这种交叉验证将极大增强估计的可信度。

**P2. 明确 MUQ < 1 阈值的局限性 -- 资产价值 ≠ 社会价值。**
在 Discussion 的 Limitations 中增加一段话，承认 MUQ 衡量的是房地产资产价值回报而非综合社会回报（包括健康、教育、交通等外部性）。建议将碳估计的表述从"wasted carbon"调整为"carbon associated with investment that generated below-cost asset returns"。

**P3. 修复 Fig 3a 的数字不一致。**
图中 beta = +1.39 vs 正文 beta = +2.75。必须确认哪个是正确的，并在图注中解释规格差异（如果是不同规格）。任何数字不一致在 Nature 审稿中都是严重问题。

### Priority 2 (强烈建议修改 -- 显著提升论文质量)

**P4. 增加碳排放的全球外推讨论。**
在 Discussion 中增加 ~80 词，讨论如果 Simpson's Paradox 中隐含的投资效率衰减模式在印度、越南、印尼等新兴城镇化国家重复，全球碳预算面临的额外压力。即使只是量级估计（"potentially tens of GtCO2 over the coming decades"），也会大幅增强论文的气候政策相关性。

**P5. 增加碳强度参数的多源验证。**
在 Methods M5 中增加 CI 参数的多个独立来源（IEA、GABC、国内学者的估计），展示 1.20->0.60 的衰减路径与外部数据的一致性。如果可能，区分建筑 vs 基础设施 vs 工业厂房的碳强度差异，说明 FAI 的异质组成对碳估计的影响。

**P6. 图表色盲友好性统一调整。**
所有图表采用 viridis 或 ColorBrewer qualitative palette 替换当前的红/绿配色。这是 Nature 的硬性要求。

**P7. 在 Discussion 中增加运营碳的量级估计。**
Back-of-envelope: 如果 embodied carbon 占全生命周期的 ~30%，则运营碳约为 5.3 / 0.3 * 0.7 ≈ 12 GtCO2。即使只在一个脚注中提到这个数字，也比不提好。

### Priority 3 (建议修改 -- 锦上添花)

**P8. 复杂系统视角的谨慎重新引入。**
在 Discussion 中增加 ~50 词，指出碳排放在 MUQ 接近零时的非线性加速与 tipping point 行为的表面相似性，但明确表示这需要更严格的诊断（longer time series, early warning signals）才能确认。这为后续研究打开了一扇有趣的门，同时不招致方法论批评。

**P9. 标注代表性城市名称。**
在 Fig 2a 的散点图中标注 5-8 个代表性城市（如 Shenzhen, Beijing, Ordos, Guiyang 等），帮助非中国研究者理解数据中的具体含义。

**P10. 参考文献部分亟需完成。**
当前 "[placeholder]" 状态显然是草稿标记，但提醒作者：Nature 要求 ≤50 条参考文献（主文），与本文引用密度匹配应该不成问题。关键是确保气候/碳核算相关文献被充分覆盖。

---

## 8. 机密评语（给编辑的）

Dear Editor,

This manuscript presents an intellectually stimulating cross-disciplinary contribution that applies Tobin's Q to urban investment at global scale and uncovers a Simpson's paradox in the aggregate data. The core finding -- that within every developing-economy income group, marginal investment returns decline with urbanisation, but compositional shifts mask this decline in pooled data -- is well-documented, statistically robust (47/47 leave-one-out tests maintain direction), and has genuine implications for development policy and carbon accounting.

**Strengths that favour publication in a high-impact venue:**
1. The Simpson's paradox is a clean, replicable statistical finding with cross-disciplinary methodological interest.
2. The China-US sign reversal (beta = -2.23 vs +2.75) is a striking empirical stylized fact that will generate productive debate.
3. The paper is refreshingly honest about its limitations -- the causal language downgrade from v4 to v5 (which I infer from the outline) is the right decision.

**Concerns that need addressing before publication:**
1. The 5.3 GtCO2 carbon estimate is the paper's most policy-relevant number but rests on a debatable assumption (MUQ < 1 = wasted investment). The paper needs to acknowledge that asset value is not the same as social value, and that infrastructure with MUQ < 1 may still generate substantial positive externalities.
2. The carbon section operates in near-complete isolation from the building embodied carbon literature (IPCC AR6 WG3, GlobalABC, Zhong et al. 2021). This is a significant gap that any climate-oriented reviewer will flag.
3. There is a numerical discrepancy between Fig 3a (beta = +1.39) and the main text (beta = +2.75) for the US result. This must be resolved.

**My recommendation:**
- For **Nature**: this is a borderline case. The "story" is strong enough for Nature's audience, but the carbon methodology needs strengthening. I would recommend **Major Revision** with the carbon and literature gaps addressed, and re-evaluation after revision.
- For **Nature Cities**: this is a strong candidate. The three findings align perfectly with the journal's scope, and the methodological standards are appropriate for a specialist audience that will engage deeply with the MUQ framework.
- I would suggest the editor consider offering the authors the option to revise for Nature Cities if the Nature submission is ultimately not accepted.

The paper's greatest asset is its potential to change how we read aggregate urban investment statistics -- a contribution that matters for trillions of dollars of ongoing and planned investment across the developing world. With the carbon methodology strengthened, this could be a high-impact publication regardless of the specific venue.

Sincerely,
Reviewer C

---

*审稿完成于 2026-03-21*
