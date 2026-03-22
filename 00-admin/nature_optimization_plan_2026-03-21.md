# Urban Q — 面向 Nature 正刊的研究优化方案

**日期**: 2026-03-21
**目标**: 将论文从 "优秀的城市经济学论文" 升级为 "揭示城市投资普适规律的 Nature 论文"
**核心策略**: 从 "描述一个现象" 升级为 "发现一条定律"
**止损日期**: 2026-04-20（如果突破口验证失败，回到 v4 大纲投 Nature Cities）

---

## 一、核心诊断

### 当前论文为什么还不是 Nature 论文

| 维度 | 当前状态 | Nature 需要 | 差距 |
|------|---------|------------|------|
| 发现的性质 | 描述现象（中国 Q<1） | 普适规律/定律 | **大** |
| 公式化程度 | 定义了 Q = V/K | Q 背后的定量标度律 | **大** |
| 预测力 | 事后描述 | 事前可验证预测 | **中** |
| 跨学科冲击 | 城市经济学 + 碳排放 | 改变多学科思考方式 | **中** |
| 数据与方法 | 158 国 + 290 城市 | 已足够 | 小 |

### Nature 论文的"金标准"公式

**一个简洁的定量规律 + 跨国/跨城市的普适验证 + 可验证的未来预测 + 跨学科含义**

---

## 二、研究优化方案：三个层次

### 层次 1：寻找普适规律（核心突破）

#### 1A. 城市错配标度律 — OCR ~ Pop^(-α)
**优先级: 最高 | 工作量: 1-2 周 | 成功率: 55-65%**

**目标**: 证明过度建设遵循城市标度律——小城市系统性过度建设，且程度与人口的负幂律关系具有普适性。

**分析计划**:
1. 从 248 城市 (2015-2016 黄金窗口) 做 ln(OCR) ~ ln(Pop) 双对数回归
2. 估计标度指数 α 及 bootstrap 95% CI
3. 分区域（东/中/西/东北）检验 α 是否稳定
4. 控制 GDP_pc、三产占比等变量后 α 是否仍显著
5. 将 Q 也做标度分析：ln(Q) ~ β·ln(Pop)，与 Bettencourt 的产出标度对话
6. 如果中国数据成立，用全球面板的国家级数据检验是否存在类似的国家规模效应

**成功标准**: α 显著 (p<0.01)，R² > 0.3，分区域稳定（α 变化 < 30%）

**Nature pitch**: *"Urban overbuilding follows a scaling law: the capital-to-optimal ratio scales as Pop^(-0.X), revealing that city size governs investment efficiency through a universal power law — a new dimension of urban scaling."*

#### 1B. 临界投资阈值 — I_c/GDP
**优先级: 高 | 工作量: 2-3 周 | 成功率: 45-50%**

**目标**: 证明存在一个精确的临界投资强度，超过后城市资产价值增长必然转负。

**分析计划**:
1. 用 158 国面板构建 dCPR/dt ~ f(GFCF/GDP)
2. Hansen (2000) 阈值面板回归，grid search 估计 I_c
3. Bootstrap I_c 的 95% CI
4. 分收入组重复，检验 I_c 的稳定性
5. 非参验证：Kernel 回归 + 导数变号点
6. 样本外预测：用 1960-2000 数据估计 I_c，对 2001-2023 做预测

**成功标准**: I_c 的 bootstrap CI 宽度 < 10 个百分点，分收入组 I_c 重叠

**Nature pitch**: *"A critical threshold exists at ~X% of GDP: nations that sustain investment above this level invariably experience capital value erosion. This threshold is stable across income groups, providing a simple policy rule."*

#### 1C. 两者组合 — "城市投资相图"
**优先级: 取决于 1A+1B | 工作量: 1 周**

如果 1A 和 1B 都成功，构建"相图"：
- X 轴 = GFCF/GDP（国家层面投资强度）
- Y 轴 = 城市人口规模
- 相界 = I_c 线 + OCR=1 线
- 四象限：大城市安全区 / 大城市过度区 / 小城市安全区 / 小城市危险区

**Nature pitch**: *"We construct a 'phase diagram' for urban investment: two universal regularities — a critical national threshold and a city-size scaling law — define four investment regimes, enabling policymakers to identify which cities in which countries face the greatest risk of value destruction."*

---

### 层次 2：强化已有发现（补强证据链）

#### 2A. MUQ 口径统一与叙事锐化
**工作量: 3-5 天**

**问题**: 中国 NBS 数据的 MUQ 转负 (p=0.043) 与全球面板中中国 MUQ 递增存在矛盾。

**解决方案**:
1. 明确论文中使用两个不同的 MUQ：
   - **MUQ_national** (NBS 真实数据, V1_adj/K2 口径): 这是核心发现，2022-2024 转负
   - **MUQ_global** (WB/PWT 面板, CPR 口径): 用于跨国比较，受 Simpson's paradox 影响
2. 论文正文只报告 MUQ_national 转负作为 headline
3. MUQ_global 的 Simpson's paradox 解构放入 Methods/ED
4. 将 MUQ_national 转负与标度律/阈值发现串联：中国突破临界阈值 → MUQ 转负 → 小城市首先受害

#### 2B. EWS 证据锐化
**工作量: 3-5 天**

**现有**: 67.3% 国家在 CPR 下降前 AR(1) 上升，p=0.009。

**强化方案**:
1. 对 35 个有 EWS 信号的国家，计算 lead time（AR(1) 突破 0.7 到 CPR 峰值的年数）
2. 检验 lead time 是否与投资强度相关（投资越猛，预警越晚？）
3. 如果 lead time 可预测（如 5-8 年），这就从"描述性统计"升级为"可操作的预警"
4. 将 EWS 与临界阈值串联：接近 I_c 时 AR(1) 上升 → 突破 I_c 后 CPR 下降

#### 2C. 碳排放不确定性量化
**工作量: 1-2 天**

**终审要求**: 碳强度无敏感性分析，13.4 GtCO2 的精度虚假。

**解决方案**: 跑 5 种碳强度情景 {0.46, 0.55, 0.65, 0.75, 0.85 tCO2/万元}，报告范围。

#### 2D. 竞争性解释段落
**工作量: 2-3 天**

**终审要求**: 缺乏与 Glaeser-Gyourko、Rogoff-Yang、Bettencourt 的对话。

**解决方案**: 在 Discussion 中增加 ~150 词"competing explanations"段落：
- Glaeser-Gyourko (2005): 耐久住房均衡——Q<1 是正常稳态，非危机。回应：他们不考虑投资惯性和制度锁定
- Rogoff-Yang (2021): 中国房地产特殊性——不具普适性。回应：我们的跨国阈值证明这不是中国独有
- Bettencourt 标度律: 如果方向 5 成功，直接整合而非对抗

---

### 层次 3：论文重构（围绕规律而非现象）

#### 3A. 新 3-Finding 结构

如果层次 1 的两个突破口都成功：

| Finding | 内容 | 核心证据 | Nature pitch |
|---------|------|---------|-------------|
| **F1: 城市投资的临界阈值** | 存在 I_c ≈ X% of GDP 的普适阈值 | 158 国 Hansen 阈值 + 分组稳定性 + EWS 预警 | "一个数字决定城市投资的命运" |
| **F2: 过度建设的标度律** | OCR ~ Pop^(-α)，小城市系统性过度建设 | 248 城标度 + 区域稳健性 + 四国验证 | "城市规模决定错配程度" |
| **F3: 相图与碳成本** | 阈值 + 标度律 = 相图 + 13.4 GtCO2 | 相图可视化 + 碳估算 + 前瞻预测 | "何时停、哪里停、为什么必须停" |

如果只有方向 5 成功（方向 2 失败）：

| Finding | 内容 |
|---------|------|
| **F1: 中国的投资 regime shift** | Q<1 + MUQ 转负 + EWS（保持 v4 结构）|
| **F2: 过度建设的标度律** | OCR ~ Pop^(-α) + 跨区域稳健性 |
| **F3: 碳成本与预警** | 碳排放 + 前瞻预测 + EWS |

#### 3B. 新 5 张主图规划（如果两个突破口都成功）

| 图 | 内容 | Nature 震撼力 |
|----|------|-------------|
| **Fig 1** | **"The Phase Diagram"** — X=GFCF/GDP, Y=城市人口, 颜色=OCR/Q, 标注阈值线和标度律 | **旗舰图**：一张图讲完整个故事 |
| **Fig 2** | 临界阈值——158 国 dCPR/dt vs GFCF/GDP + 阈值分割线 + 分收入组 | 核心定量发现 |
| **Fig 3** | 标度律——248 城 OCR vs Pop 双对数图 + 拟合线 + Bettencourt 标度对比 | 第二核心发现 |
| **Fig 4** | 中国 regime shift——Q 时序 + MC 带 + MUQ 柱状图 | 最深入的案例 |
| **Fig 5** | 碳成本 + 前瞻预测——累计碳排放 + 印度/越南预测轨迹 | Broader implications |

**关键变化**: Fig 1 不再是中国 Q 曲线，而是**"相图"**——一张图包含全球规律。这是 Bettencourt 那种"一个公式解释一切"的视觉等价物。

#### 3C. 新标题（如果突破成功）

候选：
1. **"A phase diagram for urban investment"** (6 词，极简)
2. **"Universal scaling laws govern urban overbuilding and its carbon cost"** (10 词)
3. **"When and where cities overbuild: scaling laws and critical thresholds"** (10 词)
4. **"City size and investment intensity predict urban value destruction"** (9 词)

---

## 三、执行时间表

```
Phase A: 快速验证（2026-03-22 ~ 04-05）
├── Week 1: 城市标度律验证（方向 5）
│   ├── Day 1-2: 双对数回归 + 初步标度指数
│   ├── Day 3-4: 分区域稳健性 + 控制变量
│   └── Day 5-7: 与 Bettencourt 对比 + 国家级验证
├── Week 2: 临界阈值验证（方向 2）
│   ├── Day 1-3: Hansen 阈值模型实施
│   ├── Day 4-5: Bootstrap CI + 分组稳定性
│   └── Day 6-7: 非参验证 + 样本外预测
│
├── 决策点 (04-05): 评估两个方向的结果
│   ├── 如果两个都成功 → Phase B（全面升级）
│   ├── 如果只有方向 5 成功 → Phase B（部分升级）
│   └── 如果都失败 → 止损，回到 v4 投 Nature Cities
│
Phase B: 全面升级（2026-04-06 ~ 04-20）
├── Week 3: 相图构建 + 证据链补强
│   ├── 相图可视化
│   ├── MUQ 口径统一
│   ├── EWS lead time 分析
│   ├── 碳排放敏感性
│   └── 竞争性解释段落
├── Week 4: 论文重构 + 图表重制
│   ├── 论文大纲 v5（围绕规律重组）
│   ├── 5 张新主图（以相图为旗舰）
│   └── Extended Data 更新
│
Phase C: 论文撰写（2026-04-21 ~ 05-20）
├── Week 5-6: Results + Methods 初稿
├── Week 7: Introduction + Discussion 初稿
├── Week 8: 内部评审 + 修改
│
Phase D: 投稿准备（2026-05-21 ~ 06-10）
├── Week 9: 图表终版 + Reporting Summary
├── Week 10: Cover Letter + 代码/数据仓库
└── 投稿: 2026-06-15 (目标)
```

---

## 四、风险管理

### 止损机制

| 检查点 | 日期 | 条件 | 行动 |
|--------|------|------|------|
| 方向 5 初步结果 | 04-01 | α 不显著 (p>0.05) 或 R²<0.1 | 放弃方向 5，聚焦方向 2 |
| 方向 2 初步结果 | 04-08 | I_c 的 CI 宽度 > 20pp | 放弃方向 2 |
| 综合评估 | 04-12 | 两个都失败 | **止损**：回到 v4 投 Nature Cities |
| Phase B 质量检查 | 04-20 | 新发现经不起内部审查 | 降级为 ED，回到 v4 核心 |

### 最坏情况

如果两个突破口都失败，我们仍然有：
- paper_outline_v4 的 3 Findings（MUQ 转负 + OCR 分布 + 碳成本 + EWS）
- 5 张 Nature 格式主图
- Cover Letter + Data Availability + 全部投稿材料
- 这些足以投 **Nature Cities**（接受率 35-50%）

**失败的成本是 3-4 周时间，收益的上限是 Nature 正刊。风险收益比合理。**

---

## 五、预期成果对比

| 指标 | 当前 (v4) | 优化后 (如果成功) |
|------|:---------:|:----------------:|
| 核心发现性质 | 现象描述 | **普适规律** |
| 公式化程度 | Q = V/K (定义) | **OCR ~ Pop^(-α), I_c ≈ X%** |
| 预测力 | 事后描述 | **可验证的前瞻预测** |
| Desk reject (Nature) | 45-55% | **30-40%** |
| 最终接受 (Nature) | 15-22% | **25-35%** |
| 最终接受 (Nature Cities) | 35-50% | **55-70%** |

---

*研究优化方案制定人: Research Director*
*日期: 2026-03-21*
*本方案经 PI 批准后执行*
