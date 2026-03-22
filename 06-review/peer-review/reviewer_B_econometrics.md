# Reviewer B: Econometrics / Causal Inference Review

## 审稿人 B — 计量经济学与因果推断专家
### 论文: "A Simpson's paradox masks declining returns on urban investment worldwide"
### 目标期刊: Nature (main journal)
### 审稿日期: 2026-03-21

---

## 1. 总体评价

**推荐: Major Revision (倾向 Reject & Resubmit)**

**方法论总体质量等级: B-/C+**

这篇论文提出了一个有趣的描述性发现——全球城市投资效率的 Simpson's paradox——这一发现本身具有发表价值。Simpson's paradox 的文档化工作扎实，leave-one-out 和排除中国的稳健性检验令人信服。作者在多处主动声明了描述性定位，这种自觉值得肯定。

然而，从计量经济学的角度看，这篇论文存在几个严重问题：(1) 论文的语言在"描述性"和"因果性"之间反复摇摆，多处暗示因果关系却没有可信的识别策略支撑；(2) DID 分析存在根本性的设计缺陷，其呈现方式可能误导读者；(3) 核心变量 MUQ 的构建方式引入了系统性的机械相关，虽然作者做了 Monte Carlo 检验，但检验设计本身存在问题；(4) 中国城市面板的非平衡性极为严重（2011年仅20城 vs 2016年213城），这一选择偏差未被充分讨论。

论文在碳排放估算部分展现了良好的不确定性量化实践，但三个不确定性源的独立性假设值得商榷。

---

## 2. 因果识别审查（最严格的部分）

### 2.1 逐句因果声明审查

**声明 1**: "Higher investment intensity predicts lower returns in China" (Abstract)

- 因果声明？**模糊**。"predicts" 在统计学语境中可以是纯预测性的，但在 Nature 的一般读者语境中，很容易被解读为 "causes"。
- 证据是否支持？仅有横截面/面板关联，无识别策略。
- **建议**: 改为 "is associated with" 或 "covaries negatively with"。"predicts" 在计量经济学中有特定的外样本预测含义（out-of-sample prediction），此处并非该用法。

**声明 2**: "a divergence consistent with supply-driven versus demand-driven investment regimes" (Abstract, Results)

- 因果声明？**是，隐含因果叙事**。"supply-driven" 和 "demand-driven" 本身就是因果机制标签，暗示投资被"供给推动"或"需求拉动"。
- 证据是否支持？**不充分**。论文仅展示了中美系数方向相反，但这一符号反转有多种替代解释：(a) 度量差异（FAI vs housing units）；(b) 市场结构差异（中国土地国有 vs 美国私有）；(c) 发展阶段差异；(d) 价格管制程度差异。符号反转本身不能识别"供给驱动"和"需求驱动"的因果渠道。
- **建议**: 将 "supply-driven versus demand-driven investment regimes" 框架明确标注为"解释性假说"（interpretive hypothesis），而非实证结论。可以说 "a pattern consistent with, but not proof of, distinct investment regimes"。

**声明 3**: "investment intensity is negatively associated with MUQ" (Results, Finding 2) — 此处措辞恰当，无异议。

**声明 4**: "cities with greater pre-policy real-estate dependence experienced larger subsequent Q declines" (Results, Finding 2, para 4)

- 因果声明？**是**。DID 框架本身就是因果推断工具。
- 证据是否支持？**不充分，详见 2.2 节**。

**声明 5**: "This decoupling of investment from underlying demand is the mechanism through which the Simpson's paradox arises at the global level" (Discussion, para 2)

- 因果声明？**是，明确因果**。"is the mechanism" 是不折不扣的因果声明。
- 证据是否支持？**不支持**。论文没有提供任何识别投资-需求"脱钩"的因果证据。这一句断言了一个从未被检验的因果链。
- **建议**: 改为 "may be a mechanism" 或 "is a candidate mechanism"。

**声明 6**: "the construction-led growth model has exhausted its capacity to generate asset value at the margin" (Discussion, para 3)

- 因果声明？**是**。"exhausted its capacity" 是因果性表述。
- 证据是否支持？**不支持**。MUQ < 1 是描述性事实，不等于"模式耗竭"的因果结论。MUQ < 1 可能反映：(a) 暂时的周期性低谷；(b) 度量误差（V的计算方式）；(c) 结构性变化。
- **建议**: 改为 "the data are consistent with the hypothesis that..." 或类似的对冲表述。

**声明 7**: "carbon cost of investment that fails to create value" (标题 Finding 3; Discussion)

- 因果声明？**模糊偏因果**。"fails to create" 暗示投资本应创造价值但未能做到——这是一个因果反事实。
- **建议**: 改为 "investment associated with no net value creation" 或 "investment during periods when MUQ < 1"。

**声明 8**: "carbon waste accelerates nonlinearly as marginal returns approach zero" (Discussion, para 4)

- 因果声明？**是**。"accelerates" 暗示因果动态过程。
- 证据是否支持？这是定义上的恒等式（excess_I = I * (1 - MUQ)，当 MUQ 趋近零时 excess_I 趋近 I），而非实证发现。
- **建议**: 明确说明这是数学定义的结果，不是独立的实证发现。

### 2.2 DID 分析的根本性问题

这是本审稿意见中最关键的部分。我认为 DID 分析在目前的形式下**不应出现在论文正文中**，原因如下：

**(a) 平行趋势不满足**

- ln(HP): Joint F = 3.067, p = 0.080
- Urban Q: Joint F = 2.824, p = 0.093

两个因变量的平行趋势检验均为边际拒绝（在 10% 水平上可以拒绝零假设）。这意味着**在政策实施前，高依赖城市和低依赖城市已经存在差异性趋势**。在标准的应用微观经济学文献中（AER, QJE, Econometrica），平行趋势 p < 0.10 通常被视为 DID 的致命伤。

作者称其为"marginal"，但这是在最有利的方向上解读边界结果。更诚实的表述是：我们无法排除预存差异趋势。

**(b) Placebo 检验显著**

Placebo DID (假政策时点 2016): beta = 0.067, p < 0.001

这是毁灭性的结果。Placebo 检验的目的是验证在没有真实政策冲击的时段，DID 估计量是否为零。p < 0.001 意味着在完全没有 Three Red Lines 政策的 2014-2018 窗口中，也能检测到类似方向和大小的"效应"。这说明所谓的"政策效应"实际上可能只是高房地产依赖城市的长期差异趋势的延续。

**(c) 事件研究系数全部不显著**

事件研究（Urban Q）:
- 2021: beta = 0.059, p = 0.265
- 2022: beta = 0.037, p = 0.465
- 2023: beta = -0.015, p = 0.763

**没有一个政策后年份的系数在统计上显著**。如果政策确实产生了差异化效应，我们至少应在某些年份看到显著的系数。所有年份均不显著，加上预趋势边际违反和 placebo 显著，三重证据共同指向同一结论：这个 DID 没有信息量。

**(d) 机制检验直接否定了因果链**

FAI/GDP 的 DID 系数: beta = 0.0002, p = 0.330

如果 Three Red Lines 通过限制高依赖城市的投资来影响 Q，我们首先应该观察到高依赖城市投资的差异化下降。但机制检验显示**没有**这一差异化效应——高依赖和低依赖城市的 FAI/GDP 变化几乎完全一致。这直接否定了论文隐含的因果链条。

**(e) 处理变量的内生性**

RE_dep = mean(RE_investment/GDP, 2017-2019) 作为处理强度存在明显的内生性。房地产依赖度高的城市，在所有可观测和不可观测的维度上都与低依赖城市系统性不同：经济结构、人口流动、财政状况、土地储备等。省份固定效应和少量控制变量不足以消除这种系统性差异。

**(f) FAI 2017+ 为估算值**

报告明确指出 "FAI 在 2017+ 为估算值 (fai_imputed=True)"。DID 的样本窗口恰好是 2017-2023，意味着**整个分析使用的是估算投资数据**。这对因果推断的可信度是致命的——我们无法区分真实的政策效应和数据估算过程引入的系统性偏差。

**建议**: 将 DID 结果完全移至 Supplementary Information，并明确标注为"仅供参考的描述性分析"，而非作为论文三大发现之一的支撑证据。在正文中以一句话提及即可："A quasi-experimental analysis using the Three Red Lines policy yields directionally consistent but inconclusive results (Supplementary Information)."

---

## 3. 统计方法逐项审查

| 检验 | 方法 | 是否恰当 | 替代/改进方法 | 严重程度 |
|------|------|---------|-------------|---------|
| Simpson's paradox 组内趋势 | Spearman rho | **基本恰当**，但不够。Spearman 不控制任何混杂因素，可能反映组内未观测异质性 | 补充分层 OLS with country FE 和 time trends；面板 FE 模型 | 中等 |
| China MUQ ~ FAI/GDP | Pooled OLS (HC1) | **有问题**。455个观测来自高度非平衡面板（20-213城/年），Pooled OLS 不考虑城市内相关和年份效应 | TWFE with cluster-robust SE（已有，但 p=0.063）；更应报告 TWFE 为主要结果 | 高 |
| 分位数回归 CI | 未明确说明 bootstrap 或 asymptotic | **可能有问题**。对于非平衡面板的分位数回归，渐近 CI 可能不可靠 | 建议使用 cluster-bootstrap CI（至少 1000 reps, clustered at city level） | 中等 |
| US MUQ ~ hu_growth TWFE | TWFE with demeaning | **恰当** | 无重大问题 | 低 |
| Kruskal-Wallis 区域差异 | Non-parametric rank test | **恰当** | 可补充 post-hoc pairwise tests (Dunn test) | 低 |
| MC 机械相关检验 | 打乱 DeltaV 和 FAI | **设计有瑕疵**，见下文 3.1 | 需要更严格的检验设计 | 高 |
| MC 碳排放不确定性 | Dirichlet + Normal sampling | **基本恰当**，但独立性假设可疑，见下文 3.2 | 考虑相关性结构 | 中等 |
| 多重比较 | 未做任何校正 | **有问题** | 至少应报告 Bonferroni 或 BH-FDR 校正后的结果 | 中等 |

### 3.1 机械相关检验的设计问题

MUQ = DeltaV / FAI，FAI/GDP 中包含 FAI。因此 MUQ 和 FAI/GDP 共享 FAI 作为分母和分子，这引入了机械负相关。

作者的 MC 检验（方案 A: 同时打乱 DeltaV 和 FAI）虽然思路正确，但**打乱方式保留了边际分布却破坏了联合分布**，这会低估机械相关的程度。更严格的检验应该：

1. **生成纯随机 MUQ**: 固定真实 FAI 和真实 GDP，仅从 DeltaV 的经验分布中抽样，然后计算 MUQ = DeltaV_shuffled / FAI_real。这样 MUQ 和 FAI/GDP 之间的唯一相关来源就是共享的 FAI 成分。
2. **分析机械偏差的解析公式**: 当 Y = X/Z 回归到 X/W 上，且 Z 和 W 相关时，Kronmal (1993, JRSS-A) 和 Pearson (1897) 提供了解析公式来计算伪相关的大小。建议补充这一理论基准。

此外，替代度量中的 DeltaV/GDP ~ FAI/GDP（检验 3a）仍然共享 GDP 作为分母，只是消除了 FAI 作为共享成分，但引入了新的 spurious ratio correlation（Kronmal, 1993）。beta = -0.37 (p = 0.019, R2 = 0.017) 的效应量极小，仅解释 1.7% 的变异，这可能完全在比率变量伪相关的范围内。

**建议**: 补充 Kronmal (1993) 的解析基准；对 DeltaV/GDP ~ FAI/GDP 回归，计算 spurious ratio correlation 的理论预期值并与观测值比较。

### 3.2 碳排放 MC 中三个不确定性源的独立性

MC 联合采样三个参数：MUQ 校准权重、碳强度水平、碳强度衰减率。论文假设三者独立采样，但：

- MUQ 校准中 V1（住房存量 x 价格）的权重与碳强度基线水平可能**正相关**：如果住房价格被高估（V1 权重偏高），则 MUQ 偏高，excess_I 偏低；同时，如果建筑质量更高（高碳强度），价格也更高。这会导致独立采样**低估**不确定性。
- 碳强度水平与衰减率之间存在**负相关**：如果 CI(2000) 更高，则从 2000 到 2024 的实际衰减率也应更高（因为终点 CI(2024) 有独立约束）。独立采样允许 CI(2000)高 + 衰减率低 的组合，这会产生不合理的高碳排放估计，人为扩大 CI 的上尾。

**建议**: (1) 对 CI_base 和 decay_rate 施加联合分布约束，例如锚定 CI(2024) 在 [0.45, 0.75] 范围内截断；(2) 报告 CI_base 和 decay_rate 的联合采样与独立采样结果的差异。

### 3.3 Dirichlet 浓度参数 alpha = 20 的选择

alpha = 20 意味着权重向量围绕中心权重的集中程度相当高（有效样本量约 20）。这是一个**主观选择**，对 CI 宽度有直接影响：

- alpha = 5: 权重更分散 -> CI 更宽
- alpha = 50: 权重更集中 -> CI 更窄

论文没有提供 alpha = 20 的理论依据或敏感性分析。

**建议**: 报告 alpha = {5, 10, 20, 50} 下的 CI 宽度变化，或提供 alpha 选择的先验理由（例如基于校准变量的外部验证精度）。

### 3.4 多重比较问题

论文报告了至少以下独立假设检验：
- 4 个收入组的 Spearman rho (p = 0.002, 0.002, 0.003, 0.633)
- China pooled OLS, within estimator, quantile regressions (5 quantiles)
- US pooled OLS, TWFE
- DID: 至少 5 个模型 + event study (6 年) + placebo + dose-response (3 组)
- 区域差异 Kruskal-Wallis
- 机械相关 MC

总计约 25-30 个假设检验，无任何多重比较校正。在 Nature 的标准下，这是一个应该被标记的问题。

**建议**: 至少在 Methods 或 Extended Data 中报告 Benjamini-Hochberg FDR 校正后的结果，特别是对 Simpson's paradox 的四个组内检验和 DID 的多个规格。

---

## 4. 数据质量与可复现性

### 4.1 中国城市面板的非平衡性问题（致命级别）

城市覆盖率的年际差异是惊人的：

| 年份 | 城市数 | 覆盖率 (300城基数) |
|------|-------|-------------------|
| 2011 | 20 | 6.7% |
| 2012 | 61 | 20.3% |
| 2013 | 61 | 20.3% |
| 2014 | 49 | 16.3% |
| 2015 | 51 | 17.0% |
| 2016 | 213 | 71.0% |

这不是普通的非平衡面板——2011年仅有20个城市有数据，而2016年有213个。这引入了严重的**选择偏差**：哪些城市在早期有房价数据？很可能是经济较发达、信息透明度较高的城市——这些城市恰恰可能具有较高的 MUQ。这意味着：

- Pooled OLS 的 beta = -2.23 可能部分反映的是**城市组成变化效应**：早期样本偏向高 MUQ 城市，后期样本加入大量低 MUQ 城市，制造出一个假的负斜率。
- 这本身就是一种 Simpson's paradox——讽刺的是，一篇揭示 Simpson's paradox 的论文可能在自己的城市面板中犯了同样的错误。

**建议**: (1) 报告仅使用 2016 年截面（N=213）的结果——这消除了面板组成变化的问题（论文已部分做到，82.2% 的数字来自 2016 截面）；(2) 报告仅使用"平衡子面板"（所有年份都有数据的城市）的结果；(3) 对 Pooled OLS 加入年份固定效应和城市固定效应的完整规格作为主要报告。

### 4.2 V = population x price x area 的可靠性

城市级 V 通过 population x median housing price x per-capita housing area 重建。这一构建方式有几个问题：

- **Median price 不等于 average price**: 在右偏的房价分布中，中位数系统性低于均值，导致 V 被低估。
- **Per-capita housing area 可能不按年更新**: 许多城市的人均住房面积数据来自普查或抽样调查，不是每年更新。如果使用插值，DeltaV 的年际变化会被人为平滑。
- **不包含商业地产和工业地产**: FAI 涵盖所有固定资产投资，但 V 只计算住房。这引入了系统性的分母-分子不匹配。

### 4.3 FAI 2017+ 估算值

论文在 Methods M7 中承认 "FAI after 2017 was estimated from published growth rates due to discontinuation of the total-society series"。这意味着 2017-2024 的 FAI 是从公布的增长率反推的估算值，而非直接统计数据。对于国家级 MUQ 和 DID 分析，这一数据质量问题应该被更突出地讨论。

### 4.4 美国 ACS 5-Year Estimates 的平滑效应

ACS 5-year estimates 是 5 年滚动平均。这意味着：
- 2010 ACS 数据实际反映 2006-2010 的平均
- 2022 ACS 数据实际反映 2018-2022 的平均
- 相邻年份的估计值有 4/5 的样本重叠

这引入了严重的**序列相关**。DeltaV（相邻年份差分）本质上是 (平均_t) - (平均_{t-1})，其中两个平均共享 4 年的数据。这会：
- 低估 DeltaV 的真实年际变异
- 人为增加 DeltaV 序列的平滑性
- 标准误可能被严重低估

**建议**: (1) 计算 Newey-West 标准误（选择合适的带宽，至少 4-5 年）而非 HC1；(2) 仅使用每隔 5 年的非重叠观测（如 2010, 2015, 2020）作为稳健性检验；(3) 在 Methods 中明确讨论这一平滑效应的影响方向。

---

## 5. 缺失的稳健性检验（按优先级排序）

### 优先级 1（必须补充，否则 Nature 审稿人会拒稿）

**R1. 中国城市面板的平衡子面板检验**
- 为什么需要：非平衡面板的组成变化可能驱动核心结果。
- 不做的后果：审稿人会质疑 beta = -2.23 是真实关系还是样本选择伪迹。
- 执行难度：低。仅需限制样本为所有年份都有数据的城市子集。

**R2. 美国数据的 Newey-West 或 Driscoll-Kraay 标准误**
- 为什么需要：ACS 5-year estimates 引入了 4 年的序列相关，HC1 标准误不考虑这一点。
- 不做的后果：审稿人会质疑 beta = +2.75 的 p 值是否可信。如果真实标准误是 HC1 的 2-3 倍（考虑序列相关后），结论可能不变（因为 t = 30），但这是方法论规范问题。
- 执行难度：低。

**R3. Simpson's paradox 的参数化检验**
- 为什么需要：Spearman rho 不控制任何混杂因素。需要展示在控制 time trends、country FE、income-group x year 交互项之后，组内负趋势是否存续。
- 不做的后果：审稿人会问 "控制国家固定效应和时间趋势后，组内下降还存在吗？"
- 执行难度：中等。需要面板固定效应回归。

**R4. 多重比较校正**
- 为什么需要：Nature 编辑和统计审稿人会标记此问题。
- 不做的后果：被要求修改后补充。
- 执行难度：低。

### 优先级 2（强烈建议，显著增强论文可信度）

**R5. Spurious ratio correlation 的解析基准**
- 为什么需要：MUQ 和 FAI/GDP 共享 FAI，DeltaV/GDP 和 FAI/GDP 共享 GDP。
- 不做的后果：方法论审稿人会引用 Kronmal (1993) 质疑所有基于比率的回归。
- 执行难度：中等。需要计算理论伪相关。

**R6. 碳排放 MC 的参数相关性敏感性**
- 为什么需要：三个参数的独立性假设可能导致 CI 被低估或高估。
- 不做的后果：气候科学审稿人会质疑 90% CI 的校准。
- 执行难度：中低。

**R7. Dirichlet alpha 敏感性**
- 为什么需要：alpha = 20 是主观选择，直接影响 CI 宽度。
- 不做的后果：审稿人会问 "为什么是 20？"
- 执行难度：低。

### 优先级 3（锦上添花，但非必需）

**R8. 中国 MUQ 的替代 V 构建**
- 使用土地出让收入或商品房销售额作为 V 的替代代理。
- 执行难度：中等。

**R9. 美国非重叠 5 年间隔检验**
- 使用 2010, 2015, 2020 三期数据消除 ACS 重叠。
- 执行难度：低，但样本量大幅缩减。

**R10. IV 策略探索**
- 使用地形或历史因素作为投资强度的工具变量。
- 执行难度：高。但如果可行，将大幅提升论文的因果推断深度。

---

## 6. 机密评语（给编辑的）

### Confidential Comments to the Editor

This paper presents a genuinely novel descriptive finding -- the Simpson's paradox in global urban investment efficiency -- that merits publication in a high-impact venue. The documentation of the paradox is thorough, and the robustness checks (leave-one-out, excluding China, time-varying income classification) are commendable. The carbon cost estimation, while imprecise, is a creative application that adds policy relevance.

However, I have significant reservations about three aspects:

**1. The DID analysis should be removed or radically restructured.** The parallel trends test is marginal (p ~ 0.09), the placebo test is highly significant (p < 0.001), event study coefficients are individually insignificant, and the mechanism test directly contradicts the causal story. Presenting this as a "quasi-natural experiment" in a Nature paper sets a poor precedent. Even the authors' own interpretation ("suggestive rather than definitive") is too generous given the cumulative weight of diagnostic failures. The DID contributes nothing to the paper's credibility and actually undermines it by inviting methodological attack on an otherwise solid descriptive piece.

**2. The paper oscillates between descriptive and causal framing.** Multiple sentences in the Abstract, Results, and Discussion make implicit or explicit causal claims (see Section 2 of my review). While the authors include self-aware disclaimers, these are undermined by the surrounding language. A Nature reader will come away believing that supply-driven investment causes efficiency decline, which is not supported by the evidence. The paper needs a thorough linguistic audit to ensure all claims are genuinely descriptive.

**3. The unbalanced panel issue is underappreciated.** The China city panel ranges from 20 to 213 cities across years. This is not a minor data limitation -- it could drive the core beta through composition effects. The authors should either demonstrate robustness on a balanced subsample or restructure the analysis around the 2016 cross-section (N=213), which is the year with adequate coverage.

**My overall assessment:** If the authors (a) remove or radically downgrade the DID, (b) conduct a thorough linguistic audit to eliminate causal overclaims, (c) demonstrate robustness of the city-level result on a balanced panel, and (d) address the ACS smoothing issue for the US data, this paper could be appropriate for Nature. The Simpson's paradox finding alone, combined with the China-US contrast and the carbon cost estimate, constitutes a sufficient contribution -- but only if the paper disciplines itself to stay within the descriptive lane.

Without these changes, I recommend **Major Revision** with a possibility of rejection if the causal overclaims persist.

---

### 附注: 论文中做得好的部分

为避免审稿意见完全负面，我特别肯定以下几个方面：

1. **Introduction 第三段的自我约束声明**极为罕见且值得赞赏："MUQ is a descriptive measure of investment outcomes, not an identification strategy for causal mechanisms." 这段话应该在 Abstract 和 Discussion 中得到同等程度的贯彻。

2. **Simpson's paradox 的文档化**是一流的。Leave-one-out 检验（47/47 为负）、排除中国检验、时变收入分类检验、within-between 分解——这些稳健性检验的全面性超过了大多数 Nature 论文。

3. **机械相关的主动检验**展示了方法论自觉，尽管检验设计可以改进。许多论文在面对 ratio-variable 问题时直接忽视；本文至少正面处理了这一问题。

4. **碳排放的多方法交叉验证**（MUQ 直接法 vs Q-percentile 法）和完整的敏感性分析（CI 水平 +/-30%, MUQ 阈值变化, 衰减率变化）展示了负责任的不确定性量化实践。

5. **字数控制**精准，符合 Nature 格式要求。

---

*本审稿意见由计量经济学/因果推断视角出发，不涉及领域专业性（城市经济学理论）和呈现质量（图表设计等）的评判，这些应由其他审稿人覆盖。*
