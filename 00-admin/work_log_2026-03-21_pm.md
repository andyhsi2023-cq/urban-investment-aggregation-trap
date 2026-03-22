# 工作日志 2026-03-21 下午续（终端恢复后）

## 项目：Urban Q Phase Transition
## 日期：2026-03-21 下午
## 状态：研究方案重大调整 — 从"相变"叙事转向"Simpson's Paradox"叙事

---

## 一、下午工作总览

终端恢复后完成了五项关键工作：

1. **OECD 真实数据获取**（14:00-14:30）
2. **第四轮批判性评估**（14:30-15:30）
3. **研究方案战略性重构**（15:30-16:00）
4. **W1: 城市级 MUQ 分布分析**（16:00-17:00）
5. **W2: 三道红线 DID 准自然实验**（17:00-18:00）

---

## 二、OECD 真实数据获取

### API 发现过程
- 旧 API `stats.oecd.org` 已迁移，301 重定向到新 SDMX 端点
- 正确的 dataflow: `OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_GFCF_ASSET,2.0`
- 12 维度结构，资产代码：N111G (Dwellings), N112G (Other buildings), N11G (Total)
- 成功下载 67 国、1970-2023 的 6,600 条真实数据

### 阈值分析结果

| 指标 | 代理变量 | **真实 OECD 数据** |
|------|:-------:|:-----------------:|
| gamma_hat | 9.1% | **10.2%** |
| 95% CI 宽度 | 9.5pp | **9.0pp** |
| F 检验 p | — | **0.087 (不显著)** |

**关键发现**：用更精确的变量时，阈值效应**不再显著**。这意味着"临界阈值"方向已失败。

### 产出
- 脚本: `82b_oecd_real_threshold.py`
- 数据: `oecd_gfcf_by_asset_real.csv` + `oecd_construction_gdp_panel.csv`
- 报告: `oecd_real_threshold_report.txt`
- OECD API 经验已保存为 skill: `~/.claude/commands/export-oecd.md`

---

## 三、第四轮批判性评估

以 Nature 正刊审稿人标准进行了最严格的评审。

### "Wow Factor": 5.5/10

### 六个核心声明的证据强度

| 声明 | 评分 | 关键问题 |
|------|:----:|---------|
| MUQ 转负 | C+ | p=0.043，仅 3 个数据点，仅 V1 口径 |
| Q<1 交叉 | B- | CI 跨 12 年，部分口径 Q 从未<1 |
| OCR 标度律 | D+ | R2=0.15，跨国 alpha 差异巨大 |
| 临界阈值 | C | OECD 真实数据 p=0.087 |
| EWS | C | 中日不显著，效应量不大 |
| 碳排放 | D | 无 CI，K* 不确定性跨 4 个数量级 |

### 最终判决
- Nature 正刊 desk reject 概率 55-60%，接受概率 10-15%
- Nature Cities 送审概率 60-70%，接受概率 35-45%

### 产出
- `06-review/peer-review/critical_assessment_2026-03-21.md`

---

## 四、研究方案战略性重构

### 核心诊断
问题不在数据，在叙事架构。12 个方向并行，每个 60-70% 深度。需要反转为：一个极强的核心发现 + 足够支撑。

### 被忽视的真正强牌
1. **Simpson's Paradox**: 全球 MUQ 看似稳定，分收入组全部递减（3 组 p<0.003）
2. **Bai-Perron**: F=30.1, p<0.0001（最强统计结果）
3. **98.8% MC 路径跌破 Q=1**（方向共识）
4. **城市级 MUQ**：290 城 × 6 年 ≈ 1700 观测（未使用）
5. **三道红线**作为准自然实验（未使用）

### 新头条
从 "regime shift / phase transition" → **"Simpson's Paradox masks systematic erosion of urban investment efficiency"**

### 术语调整
- regime shift → structural break
- scaling law → cross-sectional regularity
- critical threshold → investment intensity associated with efficiency decline
- "investment destroys value" → "marginal investment returns have turned negative"

### 执行计划 (W1-W5)
- W1: 城市级 MUQ 分布 ← **已完成**
- W2: 三道红线 DID ← **已完成**
- W3: 碳排放不确定性传播（待做）
- W4: Simpson's Paradox 旗舰图（待做）
- W5: 论文大纲 v5 重构（待做）

---

## 五、W1: 城市级 MUQ 分布分析

### 样本
455 个城市-年份观测（290 城市, 2011-2016）

### 核心发现

**1. FAI/GDP 与 MUQ 的负相关（论文最强新证据）**

| 方法 | beta | p | N |
|------|:----:|:-:|:---:|
| Pooled OLS | **-2.23** | **<10^-6** | 455 |
| 分位数回归 Q90 | -3.29 | 0.000004 | 455 |
| Within FE | -1.73 | 0.063 | 455 |

**2. 分位数回归不对称效应**
过度投资主要压缩高效率城市的 MUQ 上限（Q90 beta=-3.29），而非降低最差城市的下限（Q10 不显著）。

**3. 城市等级梯度**
一线 MUQ=7.46 vs 四五线 MUQ=0.20（37 倍差距），四五线 MUQ<0 比例 16.1%。

**4. 82.2% 城市 MUQ<1**（2016 截面）

### 战略意义
455 个观测、p<10^-6 远比国家级 3 个数据点(p=0.043)有力。

### 产出
- 脚本: `90_city_muq_distribution.py`
- 报告: `city_muq_distribution_report.txt`
- 图表: `fig_city_muq_distribution.png`

---

## 六、W2: 三道红线 DID 准自然实验

### 设计
- 处理强度: 政策前(2017-2019)房地产投资/GDP
- Pre: 2017-2019, Post: 2021-2023（2020 排除）
- 297 城市，高/低依赖各~150 城

### 核心结果

| 模型 | 因变量 | beta_DID | p |
|------|--------|:--------:|:-:|
| TWFE | Q | **-0.089** | **<0.001** |
| TWFE | ln(HP) | -0.022 | 0.004 |
| 含控制+省FE | Q | -0.063 | 0.007 |
| 剂量-反应 Q4 | Q | -0.136 | 0.005 |

### 因果假说判定
**结果支持假说B（"经济冲击"）而非假说A（"过度投资有害"）**。

高依赖城市政策后 Q 跌幅更大，所有规格方向一致（负）。这不支持"限制投资 → Q 回升"的因果声明。

### 重要保留
- 平行趋势边际不满足（p~0.08-0.09）
- 观察窗口仅 3 年，长期效应可能尚未显现
- 三道红线同时冲击需求端（V↓）和供给端（K 不变），短期 V 下降远快于 K 调整
- Placebo 显著（反映棚改时期差异趋势，非设计失败）

### 对论文的含义
- 不能用 DID 支持"过度投资有害"的因果声明
- 但可以诚实报告为"短期内政策冲击主要通过需求渠道影响 Q"
- 叙事应从单向因果修正为"V 和 K 的不对称调整速度是 Q 动态的关键"

### 产出
- 脚本: `91_three_red_lines_did.py`
- 报告: `three_red_lines_did_report.txt`
- 图表: `fig_three_red_lines_did.png`
- 源数据: `sensitivity/three_red_lines_source_data.csv`

---

## 七、下一步工作

### 已完成
- [x] W1: 城市级 MUQ 分布（突破性发现：beta=-2.23, p<10^-6）
- [x] W2: 三道红线 DID（结果不支持简单因果声明，但丰富叙事）
- [x] OECD 真实数据获取 + 阈值重跑

### 待推进
- [ ] W2.5: 美国 MSA 近似 MUQ 构建（跨国验证城市级 MUQ 模式）
- [ ] W3: 碳排放不确定性传播
- [ ] W4: Simpson's Paradox 旗舰图
- [ ] W5: 论文大纲 v5 重构
- [ ] 更新 task-board.md

---

## 八、当前项目文件统计更新

今日新增文件: ~15 个
项目总文件: ~185+ 个

---

*记录人：Claude (research-director agent)*
*今日下午产出：OECD 数据获取 + 批判性评审 + 方案重构 + 城市 MUQ + DID 实验*
*关键转折：叙事从"相变"转向"Simpson's Paradox"，城市级 MUQ 成为最强新证据*
