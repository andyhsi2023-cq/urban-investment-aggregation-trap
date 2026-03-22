# Nature Article 投稿合规性审查报告

**论文**: Urban Q -- Irreversible Regime Shift in Urban Investment
**目标期刊**: Nature (Article format)
**审查日期**: 2026-03-21
**审查人**: Peer Reviewer Agent (模拟 Nature 审稿人视角)
**审查依据**: paper_outline_v3.md, theory_responses_v3.md, data_availability.md, optimization_plan_2026-03-21.md

---

## 总体评价

本论文提出了一个原创性较强的分析框架 (Urban Q / OCR)，试图量化城市投资从价值创造转向价值毁灭的结构性转变。概念贡献清晰，跨国数据覆盖面广，三发现结构简洁有力。团队对自身方法论弱点的认识（IV 失败、V(t) 测量不确定性、K* 模型不稳定）是诚实的，优化方案的方向正确。

然而，以 Nature 正刊的标准衡量，当前稿件在篇幅控制、图表规划、投稿材料完整性、以及若干内容适配性问题上存在需要修正的合规风险。以下逐项审查。

---

## A. 篇幅合规性

### A1. 正文字数 (要求: <=3,500 词，不含 Methods)

| Section | 大纲规划字数 | 合规判定 |
|---------|:----------:|:-------:|
| Introduction | ~800 词 (5 段) | -- |
| Results | ~1,500 词 (3 Findings) | -- |
| Discussion | ~800 词 (6 段) | -- |
| **合计** | **~3,100 词** | **合规** |

**判定: 合规，但余量有限。**

注意事项:
- 大纲中 Introduction 的 5 段设计偏多。Nature Articles 的 Introduction 通常极为精炼 (3-4 段，500-600 词)。建议将 Para 4 (Scope and distinctiveness) 和 Para 5 (Roadmap) 合并压缩至 ~100 词，将 Introduction 控制在 ~650 词以内，为 Results 留出更多空间。
- Results 的 1,500 词分给 3 个 Finding，每个约 500 词 (4-5 段)，在 Nature 中属于偏紧但可行的安排。关键是确保每段都有图表支撑，避免纯文字描述统计结果。
- Discussion 的 800 词分为 6 段，其中 Limitations 占 ~200 词 (1/4)。Nature 编辑通常希望 Limitations 简洁 (100-120 词)，将详细讨论移至 Methods 或 Supplementary。当前 5 条 limitation 应精选为 3 条核心 limitation，其余移入 Methods。
- theory_responses_v3.md 中的 "Beyond Solow" 段落 (~300 词) 和 "Irreversible Regime Shift" 段落 (~200 词) 如果全部纳入 Discussion，将使 Discussion 膨胀至 ~1,100+ 词。**必须大幅压缩**，每个理论回应控制在 100-120 词以内。

**风险等级: 中。** 若不严格控制各节膨胀，极易突破 3,500 词上限。

### A2. Methods 字数 (要求: <=3,000 词，通常可按需更长)

| 小节 | 大纲规划字数 |
|------|:----------:|
| M1. Urban Q construction | ~400 词 |
| M2. Monte Carlo framework | ~200 词 |
| M3. K* estimation and OCR | ~300 词 |
| M4. Statistical tests | ~300 词 |
| M5. Data sources and ethics | ~300 词 |
| **合计** | **~1,500 词** |

**判定: 合规，但偏短。**

Nature Methods 部分可以较长 (通常 2,000-3,000 词)。当前 1,500 词可能不足以容纳以下必要内容:
- V(t) 三口径的详细操作化定义 (theory_responses_v3.md Task 3 约 250 词，需纳入 Methods)
- alpha(t) 双轨分解的完整数学推导 (theory_responses_v3.md Task 4 约 500 词)
- PIM 假设 (折旧率选择、初始存量估算) 的详细说明
- 城市面板 FAI 真实/估算窗口的技术说明
- IV/GMM 分析的完整报告 (含诊断检验)

**建议将 Methods 扩展至 2,500-3,000 词**，确保方法论细节充分，这是 Nature 审稿人最可能深入审查的部分。

### A3. 摘要 (要求: ~150 词，无引用)

**判定: 尚未撰写。** 大纲中标注 Abstract 为最后撰写。

提醒:
- Nature 摘要严格不允许引用文献
- 不允许使用缩写（首次出现须全拼后才可缩写，但 150 词内空间极有限，建议避免引入过多缩写）
- 结构应为: 背景 (1-2 句) -> 方法概述 (1-2 句) -> 核心发现 (3-4 句) -> 意义 (1 句)
- 当前框架中 Urban Q、OCR、MUQ、CPR 四个缩写全部出现将严重影响可读性。建议摘要中仅保留 Urban Q 一个核心概念，其余用描述性语言替代。

### A4. 图例 (要求: 每个 <250 词，以简短标题开头)

**判定: 尚未撰写。** 大纲中有每个图的内容描述但无正式图例。

提醒:
- 每个图例须以一句话标题 (bold) 开头，概括该图的核心发现
- 多面板图 (Fig 1 有 4 panels) 的图例需逐一描述每个 panel，250 词上限将非常紧张
- Fig 1 (4 panels) 和 Fig 5 (含概念图) 的图例可能需要特别注意字数控制

---

## B. 图表合规性

### B1. 主图数量 (要求: <=6 个 display items)

**大纲规划: 5 个主图 (Fig 1-5)，0 个主表。**

| 图号 | 内容 | 面板数 |
|------|------|:------:|
| Fig 1 | China's Urban Q regime shift | 4 panels (a-d) |
| Fig 2 | Overbuilding across China's cities | 2 panels (a-b) |
| Fig 3 | Global patterns of capital price | 2 panels (a-b) |
| Fig 4 | Staged decline of investment efficiency | 2 panels (a-b) |
| Fig 5 | From expansion to renewal | 2 panels (a-b) |

**判定: 合规 (5/6)。**

注意事项:
- Fig 1 有 4 panels，在 Nature 中属于较复杂的复合图。建议确保每个 panel 都不可或缺。Panel (c) Bai-Perron 与 Panel (a) 信息部分重叠（同一条 Q 曲线，只是加了断点线），可考虑将断点信息直接标注在 Panel (a) 上，释放一个 panel 用于其他信息，或简化为 3 panels。
- Fig 5b (alpha_N vs alpha_R 概念图) 是理论示意图而非数据图。Nature 审稿人对概念图的接受度取决于其信息密度。如果该图仅展示两条定性曲线，可能被要求移至 Extended Data 或 Supplementary Information 文本中。**建议将 Fig 5b 替换为数据驱动的图**，例如展示实际观测到的新建 vs 更新投资效率对比（如有数据），或将 Fig 5 整合为单面板后释放一个主图位置。

### B2. Extended Data 数量 (要求: <=10 个 display items)

**大纲规划: 6 个 ED 图 + 4 个 ED 表 = 10 个 display items。**

| ID | 类型 | 内容 |
|----|------|------|
| ED Fig 1 | Figure | 7 individual Q calibrations |
| ED Fig 2 | Figure | Monte Carlo spaghetti + density |
| ED Table 1 | Table | Seven-calibration summary |
| ED Fig 3 | Figure | M1 vs M2 K* comparison |
| ED Table 2 | Table | K* regression table |
| ED Fig 4 | Figure | OCR vs Q scatter (290 cities) |
| ED Table 3 | Table | Global CPR by income group |
| ED Fig 5 | Figure | OLS/IV/GMM comparison |
| ED Fig 6 | Figure | UCI 4-quadrant diagnostic |
| ED Table 4 | Table | MUQ descriptive statistics |

**判定: 恰好 10/10，合规但无余量。**

风险:
- 如果审稿过程中被要求增加任何 Extended Data item（例如额外的稳健性检验图），将无空间容纳。**建议精简至 8-9 个**，为审稿回应预留 1-2 个位置。
- ED Fig 6 (UCI 4-quadrant) 的定位偏弱——UCI 在论文中已降级为 Extended Data 内容，一个仅为展示诊断分类的图可考虑移至 Supplementary Information 文本描述。
- ED Table 1 和 ED Table 4 信息密度较低（描述性统计），可考虑合并为一个综合表。

### B3. 图表视觉风格

**判定: 尚未制作实际图表，无法评估。**

Nature 图表要求提醒:
- 字体: 5-7pt，统一使用 Helvetica/Arial
- 色彩: 需考虑色盲友好 (避免红绿对比)。Fig 1d (MUQ bar chart, positive=blue, negative=red) 需确认色盲友好性，建议使用蓝/橙配色
- Fig 2a (中国 290 城市地图) 需使用符合国际惯例的中国行政边界底图，并注意南海诸岛标注问题（Nature 对中国地图的审查近年趋严）
- 所有数据图须提供 Source Data files

### B4. Supplementary Information 需求

**判定: 需要规划，当前缺失。**

以下内容应作为 Supplementary Information (文本/表格，非图表):
- 完整的 V(t) 操作化技术细节 (超出 Methods 篇幅的部分)
- alpha(t) 双轨分解的完整数学推导
- 数据溯源详细清单 (data_availability.md 中的 Detailed Data Inventory)
- 城市面板 FAI 真实/估算年份的完整说明
- 敏感性分析的补充结果 (PIM 参数变化等)
- IV/GMM 分析的完整诊断检验表

---

## C. 投稿材料完整性

### C1. Cover Letter

**判定: 未准备。** 大纲中仅在时间表中提及 "Cover letter + highlights" 作为最后步骤。

**必须准备。** 详见本报告末尾的 Cover Letter 要点建议。

### C2. Reporting Summary

**判定: 未准备，且未在任何文档中提及。**

**这是一个合规性缺口。** Nature 要求所有投稿附带完整的 Reporting Summary (editorial checklist)，涵盖:
- 统计分析的详细报告 (样本量、检验方法、效应量、CI)
- 数据可用性声明的确认
- 代码可用性声明的确认
- 伦理审查声明
- 自定义统计方法的描述

建议立即下载 Nature 的 Reporting Summary 模板 (https://www.nature.com/documents/nr-reporting-summary.pdf) 并开始填写。

### C3. Data Availability Statement

**判定: 已准备，质量较好，但需修正若干问题。**

具体问题:

1. **GitHub URL 为占位符**: "[GitHub repository URL to be inserted upon acceptance]"。Nature 要求投稿时（非接受后）即提供代码仓库链接。应在投稿前创建仓库（可设为 private，审稿期间通过匿名链接提供访问）。

2. **Figshare/Zenodo 存储库也是占位符**: "will be deposited in a public repository (Figshare or Zenodo) upon acceptance"。Nature 越来越倾向要求投稿时即存入数据，或至少提供 DOI 预留。建议投稿前在 Zenodo 创建 deposit 并获取 DOI。

3. **商业数据的可复现性**: 马克数据网 (marcdata.cn) 和 58.com/Anjuke 数据标注为 "subscription required" 和 "terms of use apply"。声明中提到 "Researchers seeking to replicate ... may obtain equivalent data from the China City Statistical Yearbook or CEIC"，这是好的做法。但建议进一步说明: (a) 聚合后的衍生指标是否已包含在公开存储库中; (b) 哪些分析可以仅用公开数据完整复现，哪些需要商业数据。

4. **"Source data for all figures are provided with this paper"**: 这是 Nature 的标准要求，但需要在投稿时实际准备 Source Data files (Excel/CSV)。目前未见此类文件的准备计划。

5. **声明中提到 "UCI" 但大纲 v3 已将 UCI 降级至 Extended Data**。确保术语一致。

### C4. 代码公开

**判定: 已规划 (GitHub)，但尚未实施。**

注意:
- Nature 要求自定义分析代码在论文发表时可公开获取
- 当前代码库包含 ~109 个文件，需清理后再公开（移除调试代码、确保路径无硬编码个人信息）
- 建议在投稿前完成代码清理并创建 GitHub 仓库

### C5. 数据集公开存储

**判定: 已规划 (Figshare/Zenodo)，但尚未实施。**

应存入的衍生数据集:
- Global Urban Q Panel (158 countries)
- China National Q Series (1990-2024)
- China City OCR Panel (290 cities, 2010-2016)
- Monte Carlo simulation outputs

---

## D. 内容适配性

### D1. 论文标题

大纲提供三个候选:
- **Option A**: "Irreversible regime shift in urban investment: when building cities stops creating value"
- **Option B**: "The end of urban expansion: evidence for an irreversible investment regime shift across nations"
- **Option C**: "When cities overbuild: quantifying the global transition from urban expansion to renewal"

**判定: Option A 最接近 Nature 风格，但仍需精炼。**

问题:
- Nature 标题通常不超过 ~10-12 个实词，Option A 有 13 个实词 + 副标题。
- 冒号分隔的双标题在 Nature 中不常见。Nature 偏好单句式标题。
- "when building cities stops creating value" 作为副标题过于口语化。

建议修改方向:
- "Urban investment undergoes an irreversible regime shift as cities overbuild" (单句，12 词)
- "Overbuilding drives an irreversible shift from value creation to value destruction in cities" (单句，13 词)
- 或更激进地: "Cities stop creating value when they overbuild" (8 词，但可能过于简化)

### D2. Introduction Hook

**判定: Hook 设计有效，但需要微调。**

当前 Hook (Para 1): "China invested more in fixed assets during 2010-2020 than any nation in history, yet its urban asset values have been declining..."

优点: 悖论式开头，数据驱动，能立即吸引注意力。
问题: 仅以中国开头可能让编辑认为这是一篇 "China study"，降低对全球读者的吸引力。

建议: 以全球性陈述开头，第二句引入中国作为最极端的案例。例如: "The world's cities represent the largest single class of physical assets ever created. But in the fastest-urbanising economies, new construction has begun to destroy rather than create value -- most dramatically in China, which invested [X] trillion in urban fixed assets during 2010-2020 yet saw its urban asset values decline."

### D3. Discussion 简洁性

**判定: 当前规划偏长，需压缩。**

Nature Discussion 的黄金法则: 不超过 Results 的一半长度。当前 Discussion ~800 词 vs Results ~1,500 词，比例约 1:1.9，在可接受范围内但偏高。

具体问题:
- Para 2 (Beyond Solow, ~150 词) 和 Para 3 (Policy implications, ~200 词) 是重点，应保留。
- Para 4 (Limitations, ~200 词) 如前述应压缩至 ~100 词。
- Para 5 (Future directions, ~100 词) 和 Para 6 (Closing, ~50 词) 可合并为 ~80 词的结尾段。
- 目标: Discussion 压缩至 ~600-650 词。

### D4. Broader Implications

**判定: 已有，但可加强。**

当前 broader implications 分散在 Discussion Para 3 (policy) 和 Para 6 (closing)。Nature 编辑期望在 Discussion 开头或结尾有一段清晰的 "so what" -- 为什么这对非城市经济学领域的读者也重要。

建议增加的维度:
- **气候角度**: 建筑部门占全球碳排放 ~37%。如果过度建设意味着资源浪费和碳锁定，Urban Q 框架可以为碳减排政策提供定量依据。
- **金融稳定角度**: 城市资产是全球金融系统的最大抵押品类别。Q < 1 意味着抵押品价值低于重置成本，对银行资产负债表有系统性影响。
- **全球南方角度**: 印度、非洲正在重复中国的快速城镇化路径，Urban Q 框架可以作为早期预警工具。

### D5. 跨学科可读性

**判定: 需要改善。**

当前大纲中的专业术语密度较高: Urban Q, OCR, MUQ, CPR, UCI, K*, PIM, Bai-Perron, ANOVA, LOESS, IV, GMM, Hausman, Sargan, alpha_N, alpha_R, QG...

Nature 的读者包括生物学家、物理学家、政策制定者。建议:
- 正文中的缩写严格限制在 3-4 个核心概念 (Urban Q, OCR, 可能加 MUQ)
- CPR 在正文中用 "capital price ratio" 全称
- UCI 已降至 Extended Data，正文不应出现
- 统计检验方法名称 (Bai-Perron, Hausman 等) 移至 Methods，正文仅报告结果 (p 值、效应量)
- alpha_N / alpha_R 的数学记号在正文中用描述性语言替代 ("new-build efficiency" / "renewal efficiency")

---

## E. Desk Reject 风险评估

### E1. Broad Interest (广泛兴趣)

**判定: 中等风险。**

优势:
- 城市化是全球性议题，158 国数据覆盖面广
- 中国房地产/基建问题是当前全球经济焦点
- 政策含义明确且及时

风险:
- 核心分析方法 (Tobin's Q 的城市化应用) 可能被视为过于 "经济学专业"，不够 broad
- 缺乏直接的健康/环境/社会后果数据 -- Nature 近年偏好有多维度影响的研究
- "regime shift" 在生态学中有大量先例 (Scheffer 等人的工作)，但在城市经济学中是否构成足够的 "advance" 需要论证

**建议**: 在 Cover Letter 和 Introduction 中明确强调 3 个跨领域意义 (气候、金融稳定、全球南方早期预警)，将论文定位为 "不仅是经济学发现，更是一个关于人类最大资产类别的预警信号"。

### E2. Advance Beyond Existing Literature

**判定: 中-低风险。** 这是论文最强的维度之一。

明确的 advance:
- 首次将 Tobin's Q 系统性应用于城市尺度
- 首次跨国比较 Urban Q 轨迹
- 首次提出理论基础的 "过度建设" 量化指标 (OCR)
- 首次文档化投资效率的阶段性崩溃

但需注意: 类似概念 (housing overvaluation ratios, price-to-cost ratios) 在房地产金融文献中已有先例。需在 Introduction 中明确区分 Urban Q 与 price-to-rent ratio、Case-Shiller 等既有指标的不同。

### E3. 方法论致命弱点

**判定: 中等风险。存在需要预先化解的方法论质疑。**

最可能导致 desk reject 的方法论问题:

1. **V(t) 的不可观测性**: 论文的核心比率 Q = V/K 中，V 不可直接观测。七种口径的 Q=1 交叉年份跨度 ~12 年。编辑可能质疑: "如果你们不确定 Q 何时跌破 1，你们到底确定什么？"
   - **化解策略**: 论文已规划的蒙特卡洛框架 (98.8% 路径跌破 1) 是有效回应。确保在 Results 中强调 "方向性结论稳健，精确时点存在不确定性" 的叙事。

2. **因果性缺失**: 论文不声称因果性 (IV 失败已坦诚承认)，但 Nature 可能期望某种因果机制的证据。
   - **化解策略**: 四国比较提供了 "自然实验" 的弱版本 (不同投资强度 -> 不同 Q 轨迹)。alpha_N/alpha_R 分解提供了理论机制。这些加在一起构成了 "有机制的相关性"，在描述性宏观研究中是可接受的。

3. **样本量**: 中国国家层面仅 ~25 年时间序列，四国比较仅 4 个 "观测"。城市面板真实窗口仅 7 年 (2010-2016)。
   - **化解策略**: 158 国 CPR 分析弥补了国家层面的不足。城市面板 290 城 x 7 年 = ~2,030 观测提供了截面维度的统计功效。

### E4. 数据透明度

**判定: 中等风险。Nature 近年数据透明要求显著提升。**

具体风险:
- 投稿时无公开数据仓库 (仅为占位符)
- 投稿时无公开代码仓库 (仅为计划)
- 部分核心数据依赖商业来源 (马克数据网)
- C 类数据 (硬编码) 的替换工作尚未完成

**建议**: 在投稿前完成以下最低要求:
1. 创建 GitHub 仓库 (可 private，提供审稿人匿名访问链接)
2. 在 Zenodo 创建 dataset deposit (至少包含衍生数据集)
3. 完成 C 类数据向 B+类的替换

---

## F. 中国研究的特殊注意事项

### F1. Nature 对中国数据的审查趋势

**判定: 需要注意。**

近年趋势:
- Nature 编辑部对使用中国官方统计数据的论文审查更为谨慎
- 特别关注: GDP 数据可能存在的注水问题、人口数据的修订频率、房地产相关统计的完整性
- 审稿人可能要求交叉验证关键数据点

**建议**:
- 在 Methods 中增加一段 "Data validation" 小节，说明关键变量的交叉验证结果 (NBS vs 世界银行 vs PWT 的 GDP; 统计公报 vs 统计年鉴的投资数据)
- 对于国家层面关键年份的数据，提供至少两个独立数据源的对比

### F2. 商业数据库 (马克数据网)

**判定: 需要额外说明。**

问题:
- 马克数据网 (marcdata.cn) 在国际学术界知名度很低
- Nature 审稿人（尤其是非中国审稿人）可能不了解该数据库的数据质量和覆盖范围
- "subscription required" 的数据对可复现性构成障碍

**建议**:
- 在 Methods 中用 1-2 句话说明马克数据网的性质: "Marc Data Urban Database (v6.0) is a commercial database compiled from Chinese municipal statistical yearbooks and government reports, covering 275+ prefecture-level cities"
- 说明该数据库与 CEIC China Premium Database 的可比性
- 明确哪些分析可以用公开数据 (China City Statistical Yearbook) 完全复现

### F3. 中国统计数据可信度

**判定: 需要在论文中预先回应。**

学术界对中国统计数据的常见质疑:
- GDP 数据可能被地方政府高估 (Rawski, 2001; Chen et al., 2019 等)
- 2017 年后 FAI 统计口径变化导致不连续
- 房地产价格数据可能被官方统计低估

**建议**:
- 在 Methods M5 (Data sources) 中增加一段关于中国数据质量的讨论
- 利用以下策略增强可信度: (a) 使用多个独立数据源交叉验证; (b) 将城市面板主分析限制在 2010-2016 窗口 (FAI 口径一致); (c) 使用 PWT 和世界银行数据作为国际可比基准; (d) 在敏感性分析中展示结论对 GDP 调整的稳健性
- 注意: 优化方案中已规划将 C 类硬编码数据替换为 Excel 解析。**这一步在投稿前必须完成**，否则数据溯源链条断裂将成为致命弱点。

### F4. 中国地图

**判定: 高风险项，需特别注意。**

Fig 2a 规划了中国 290 城市的地图 (choropleth map)。Nature 对涉及中国领土的地图审查非常严格:
- 必须包含南海诸岛 (九段线区域)
- 台湾必须与大陆同色或明确标注为中国领土
- 中印边界、中日争议岛屿等均需符合中国官方立场

**然而**: 使用符合中国官方立场的地图可能导致来自其他国家审稿人的异议。Nature 有自己的地图政策，通常要求使用 "Natural Earth" 等中立底图数据。

**建议**:
- 仔细阅读 Nature 的地图政策 (https://www.nature.com/nature/for-authors/formatting-guide)
- 考虑使用 Nature 认可的底图数据源
- 在图例中注明底图来源
- 备选方案: 如果地图问题过于复杂，可将地理信息改为非地图形式呈现 (如按区域分组的条形图/箱线图)

---

## 逐项合规/不合规判定汇总

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| **A. 篇幅** | | |
| A1. 正文 <=3,500 词 | PASS (有条件) | 规划 ~3,100 词合规，但 Discussion 理论回应存在膨胀风险 |
| A2. Methods <=3,000 词 | PASS | 规划 ~1,500 词，但偏短，建议扩展至 2,500+ |
| A3. 摘要 ~150 词 | 未完成 | 尚未撰写 |
| A4. 图例 <250 词 | 未完成 | 尚未撰写 |
| **B. 图表** | | |
| B1. 主图 <=6 | PASS | 5 个主图 |
| B2. ED <=10 | PASS (无余量) | 恰好 10 个，建议精简至 8-9 |
| B3. 视觉风格 | 未完成 | 图表尚未制作 |
| B4. SI 规划 | 未完成 | 需要规划 Supplementary Information 内容 |
| **C. 投稿材料** | | |
| C1. Cover Letter | 未完成 | 未准备 |
| C2. Reporting Summary | 未完成 | 未提及，合规缺口 |
| C3. Data Availability | PASS (需修正) | 已准备但有占位符和术语不一致问题 |
| C4. 代码公开 | 未完成 | 已规划但未实施 |
| C5. 数据存储 | 未完成 | 已规划但未实施 |
| **D. 内容** | | |
| D1. 标题 | 需修改 | 过长，建议单句式 |
| D2. Introduction hook | PASS (需微调) | 应以全球视角开头 |
| D3. Discussion 简洁性 | 需压缩 | Limitations 过长，整体应压缩至 ~600 词 |
| D4. Broader implications | 需加强 | 增加气候/金融/全球南方维度 |
| D5. 跨学科可读性 | 需改善 | 缩写过多，术语密度过高 |
| **E. Desk Reject 风险** | | |
| E1. Broad interest | 中等风险 | 需强化跨领域意义 |
| E2. Advance | 低风险 | 概念原创性强 |
| E3. 方法论弱点 | 中等风险 | V(t) 不可观测性需预先化解 |
| E4. 数据透明度 | 中等风险 | 投稿时需有可访问的仓库 |
| **F. 中国特殊项** | | |
| F1. 数据审查趋势 | 需注意 | 增加数据验证小节 |
| F2. 商业数据库说明 | 需补充 | 在 Methods 中说明马克数据网性质 |
| F3. 统计可信度 | 需回应 | 交叉验证 + 敏感性分析 |
| F4. 中国地图 | 高风险 | 仔细遵循 Nature 地图政策 |

---

## 投稿前必须完成的准备清单 (Checklist)

### 第一优先级 -- 无此项不可投稿

- [ ] **C 类数据替换完成**: 所有硬编码数据替换为可溯源的 Excel 解析或 API 链路
- [ ] **创建 GitHub 代码仓库**: 清理代码后上传，提供审稿人匿名访问链接
- [ ] **创建 Zenodo 数据存储**: 存入所有衍生数据集，获取 DOI
- [ ] **更新 Data Availability Statement**: 替换所有占位符为实际 URL/DOI
- [ ] **撰写摘要**: ~150 词，无引用，<=3 个缩写
- [ ] **下载并填写 Nature Reporting Summary**
- [ ] **完成中国地图的合规性处理**: 确认底图符合 Nature 地图政策
- [ ] **准备 Source Data files**: 每个图/ED 的源数据 (CSV/Excel)

### 第二优先级 -- 显著影响审稿结果

- [ ] **精简标题**: 改为单句式，<=12 实词
- [ ] **压缩 Discussion**: 控制在 ~600 词内
- [ ] **精简 Extended Data**: 从 10 个减至 8-9 个
- [ ] **撰写所有图例**: 每个 <250 词
- [ ] **Methods 扩展至 2,500+ 词**: 补充 V(t) 操作化、alpha 分解、数据验证
- [ ] **降低术语密度**: 正文缩写限制在 3-4 个
- [ ] **Introduction hook 修改为全球视角开头**
- [ ] **增加 broader implications**: 气候、金融稳定、全球南方
- [ ] **规划 Supplementary Information 内容**

### 第三优先级 -- 提升竞争力

- [ ] **Cover Letter 撰写** (见下节)
- [ ] **Data validation 小节**: Methods 中增加交叉验证描述
- [ ] **马克数据网说明**: Methods 中增加 1-2 句数据库介绍
- [ ] **中国数据可信度讨论**: Methods 中增加专门段落
- [ ] **Fig 5b 替换或整合**: 将概念图替换为数据图
- [ ] **Fig 1 简化**: 考虑将 Panel c 信息整合入 Panel a

---

## Cover Letter 要点建议

Nature Cover Letter 应控制在 1 页以内，包含以下要素:

### 结构建议

**Para 1 -- 研究问题和为什么是现在 (~80 词)**:
- 城市化是 21 世纪最大的人类物理转型
- 中国过去 20 年的投资规模和当前的房地产危机提供了前所未有的实证窗口
- 但缺乏一个系统性框架来判断城市投资何时从价值创造转为价值毁灭

**Para 2 -- 本文做了什么 (~100 词)**:
- 三个核心贡献，每个一句话:
  1. 首次构建跨国 Urban Q 指标，发现中国经历了不可逆的投资体制转换
  2. 首次提出理论基础的过度建设量化指标 (OCR)，揭示空间-收入梯度
  3. 首次文档化投资效率的阶段性崩溃模式，在四个国家中得到验证

**Para 3 -- 为什么适合 Nature (~80 词)**:
- Broad interest: 城市资产是全球最大的实物资产类别，关乎 40 亿城市居民的生活质量
- Timeliness: 中国房地产危机、全球南方快速城镇化使这一研究高度及时
- Cross-disciplinary: 融合经济学 (Tobin's Q)、生态学 (regime shift)、城市科学的方法论
- Policy relevance: 为识别 "何时停止建设" 提供可操作的量化信号

**Para 4 -- 技术性说明 (~60 词)**:
- 文章符合 Nature Article 格式: 正文 ~3,100 词 + Methods + 5 主图 + 10 ED items
- 所有数据和代码在投稿时即可通过 [仓库链接] 获取
- 无利益冲突；无人类受试者研究；所有数据为公开或已授权使用

**建议审稿人 (可选，取决于 Nature 投稿系统要求)**:
- 建议 2-3 位潜在审稿人 (覆盖城市经济学、宏观经济学、复杂系统/regime shift 领域)
- 排除 0-1 位潜在利益冲突审稿人

---

## 审查结论

本论文的概念原创性和数据覆盖面是投稿 Nature 的核心竞争力。三发现结构精炼，叙事逻辑清晰，对自身局限性的讨论诚实且有建设性。

主要风险在于: (1) 投稿材料的准备工作量较大（代码/数据仓库、Reporting Summary、Source Data、图表制作、Cover Letter），当前完成度不足; (2) V(t) 的不可观测性是最可能引发编辑质疑的方法论问题，需要蒙特卡洛框架的有力支持; (3) 中国地图的处理需要特别谨慎。

**综合判定**: 在完成上述第一、第二优先级的全部准备工作后，本论文具有通过 Nature desk review 进入外审的合理概率。建议将当前时间表（投稿目标 ~2026-06-25）视为最早日期，如有必要可延至 2026-08 以确保所有合规项完成。

---

*审查人: Peer Reviewer Agent*
*审查日期: 2026-03-21*
*下次审查节点: 论文初稿完成后 (预计 ~2026-05-25)*
