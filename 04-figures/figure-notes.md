# Nature 主刊投稿图表规划

项目: Urban Q Phase Transition
目标期刊: Nature
日期: 2026-03-20

---

## 主图 (Main Figures)

### Figure 1: 理论框架示意图 (Conceptual Framework)

- **类型**: 概念图 / 示意图
- **布局**: 单幅，双栏宽度 (180mm x ~120mm)
- **核心内容**:
  - 左侧: Urban Q 的定义公式 Q = V/K，拆解 V (城市资产总价值) 与 K (累计投资重置成本)
  - 中部: Q 动态的三阶段理论 (Q>1 扩张期 -> Q=1 均衡 -> Q<1 收缩期)
  - 右侧: 从 Tobin's Q 到 Urban Q 的类比关系
  - 底部: 政策含义 (投资效率 -> MUQ -> 资源配置信号)
- **数据来源**: 无（纯理论图）
- **制作工具**: Matplotlib + 手动排版，或 Adobe Illustrator 精修
- **关键视觉元素**:
  - 三阶段用红/黄/蓝渐变色块
  - Q=1 作为分界线突出标注
  - 箭头表示因果关系与反馈循环
- **状态**: 待制作

---

### Figure 2: 四国 Urban Q 时序 + 蒙特卡洛置信带 [已完成]

- **类型**: 时序线图，2x2 panel
- **布局**: 双栏宽度 180mm x 150mm
- **Panel 结构**:
  - a: China — Q(V1/K2) + 90% Monte Carlo CI + Bai-Perron 断点 (2004, 2018)
  - b: Japan — urban_Q + 泡沫期阴影 (1986-1991) + 断点 (1987, 1992)
  - c: United States — urban_Q + 金融危机阴影 (2007-2009)
  - d: United Kingdom — urban_Q + 金融危机阴影 (2007-2009)
- **数据来源**:
  - `03-analysis/models/china_urban_q_real_data.csv` (Q_V1K2 列)
  - `03-analysis/models/monte_carlo_q_ci.csv` (p5, p25, p50, p75, p95)
  - `03-analysis/models/japan_urban_q_timeseries.csv`
  - `03-analysis/models/us_urban_q_timeseries.csv`
  - `03-analysis/models/uk_urban_q_timeseries.csv`
- **制作脚本**: `03-analysis/scripts/70_nature_main_figures.py`
- **输出文件**:
  - `04-figures/final/fig2_urban_q_four_countries.png` (300 DPI)
  - `04-figures/final/fig2_urban_q_four_countries.pdf` (矢量)
- **配色**: 中国红 #CC3311, 日本蓝 #0077BB, 美国青绿 #009988, 英国紫 #AA3377
- **关键标注**:
  - Q=1 参考线（黑色虚线）
  - 中国 Q=1 交叉: ~2013 [2002-2021] (Monte Carlo 90% CI)
  - 各国当前 Q 值显示于右上角
- **图注要点**: 各国 Q 的口径不同（中国用 V1/K2 即销售额/累计投资，其他国家用总资产价值/资本存量）；独立 Y 轴因绝对水平差异大
- **状态**: 已完成

---

### Figure 3: MUQ 转负 + 投资效率分时期

- **类型**: 组合图，上下双 panel 或左右分列
- **布局**: 双栏宽度 180mm x ~140mm
- **Panel 结构**:
  - a: MUQ (边际 Urban Q) 时序图
    - 三条线: MUQ_V1 (销售额口径), MUQ_V2 (增值口径), MUQ_V3 (综合口径)
    - MUQ=0 水平参考线（关键阈值）
    - MUQ=1 水平参考线（效率阈值）
    - 阴影区: MUQ < 0 的年份区域（2022 起）
    - 标注 MUQ=0 交叉年份: ~2021.65 [2021.12-2023.01]
  - b: 投资效率分时期柱状图 / 点图
    - 三个时期: 1998-2007 (快速扩张), 2008-2015 (刺激与调整), 2016-2024 (下行期)
    - 双指标: 平均投资/GDP 比率 vs 平均 MUQ
    - 误差棒表示标准差
    - ANOVA p 值标注
- **数据来源**:
  - `03-analysis/models/china_urban_q_real_data.csv` (MUQ_V1, MUQ_V2, MUQ_V3 列)
  - `03-analysis/models/muq_significance_test.txt` (分时期统计量)
- **关键视觉元素**:
  - MUQ 转负的区域用红色阴影强调
  - 分时期对比用"效率递减"的颜色梯度（绿->黄->红）
  - ANOVA F=7.04, p=0.004 在图上标注
- **状态**: 待制作

---

### Figure 4: K*/OCR 全球面板 + 中国城市

- **类型**: 散点图 / 面板图组合
- **布局**: 双栏宽度 180mm x ~160mm
- **Panel 结构**:
  - a: 全球 K* (最优资本存量) vs 实际 K 的散点图
    - 各国标注为点（按收入水平分色）
    - K*=K 的 45 度线
    - 中国用大号红点突出
    - 表明中国已显著超过 K*（过度资本化）
  - b: OCR (最优收敛比率) 全球分布
    - 柱状图或密度图，按发展阶段分组
    - 中国的 OCR 位置标注
  - c: 中国城市面板
    - 30+ 城市的 Urban Q 或 K*/K 散点
    - X 轴: 城市化率或人均 GDP
    - Y 轴: Urban Q 或 OCR
    - 一线/二线/三线城市分色
- **数据来源**:
  - `03-analysis/models/` 下全球面板数据 (需确认具体文件)
  - `03-analysis/models/` 下城市面板数据
- **关键视觉元素**:
  - 过度资本化区域阴影
  - 城市分层的不同标记形状
- **状态**: 待制作

---

### Figure 5: UCI 诊断 (Urban Capital Inefficiency Index)

- **类型**: 综合诊断仪表盘，多 panel
- **布局**: 双栏宽度 180mm x ~150mm
- **Panel 结构**:
  - a: UCI 时序图
    - 中国 UCI 随时间变化
    - 效率区 (UCI < 阈值) 和低效区的分色背景
  - b: UCI 组成分解
    - 堆叠面积图或瀑布图
    - 拆分 UCI 的各个组成成分（Q 偏离、MUQ 偏离、OCR 偏离等）
  - c: 国际比较
    - 四国 UCI 最新值的雷达图或条形图
    - 或时序对比
- **数据来源**:
  - `03-analysis/models/` 下 UCI 相关数据文件
- **关键视觉元素**:
  - 红绿色带标识效率分区
  - 国际对比中中国的突出标注
- **状态**: 待制作

---

## Extended Data Figures (扩展数据图)

### ED Figure 1: 数据来源与口径说明
- 表格形式，列出各国数据的具体来源、时间跨度、变量定义
- 包含 V 和 K 的不同度量方法对比

### ED Figure 2: 中国 Q 的多口径对比
- 6 条 Q 曲线: Q(V1/K1), Q(V1/K2), Q(V2/K1), Q(V2/K2), Q(V3/K2), Q(V3/K3)
- 展示不同 V/K 组合下 Q 动态的一致性
- 数据: `china_urban_q_real_data.csv` 所有 Q 列

### ED Figure 3: Bai-Perron 结构断点检验详情
- a: CUSUM 图 + 临界值线
- b: 分段回归拟合图（三段 + 断点竖线）
- c: Sup-Wald 统计量的滚动窗口图
- 数据: `structural_break_test.txt` + 脚本重新计算

### ED Figure 4: 蒙特卡洛模拟详情
- a: 参数扰动分布（直方图/密度图）
- b: Q 的模拟路径散点图（1000 条路径叠加）
- c: Q=1 交叉年份的分布直方图
- 数据: `monte_carlo_q_ci.csv` + 原始模拟脚本

### ED Figure 5: 日本泡沫经济的 Q 动态
- a: Q 与地价指数的双轴图
- b: Q 与住房开工数的关系
- c: 泡沫前后的投资效率对比

### ED Figure 6: 敏感性分析
- a: 折旧率敏感性 (delta = 3%, 5%, 7%)
- b: 价格指数选择的影响
- c: PIM 初始值假设的影响
- 数据: `03-analysis/sensitivity/` 目录下文件

### ED Figure 7: 省级面板 Urban Q 热力图
- 中国 31 省 x 20+ 年的 Q 值热力图
- 颜色从蓝 (Q<1) 到红 (Q>1) 渐变
- 数据: `03-analysis/models/` 下省级面板数据

### ED Figure 8: 投资效率前沿
- 投资/GDP 比率 vs MUQ 的散点图
- 效率前沿线的估计
- 分阶段标注

---

## 技术规范

| 参数 | Nature 要求 | 本项目设置 |
|------|------------|-----------|
| 分辨率 | >= 300 DPI | 300 DPI |
| 最大宽度 (单栏) | 88 mm | — |
| 最大宽度 (双栏) | 180 mm | 180 mm |
| 字体 | Sans-serif | Arial |
| 最小字号 | 5 pt | 6 pt (标注), 7 pt (刻度), 8 pt (标签) |
| 文件格式 | PDF/EPS (矢量) | PDF + PNG |
| 色彩模式 | RGB (在线), CMYK (印刷) | RGB |
| 色盲友好 | 必须 | Wong 2011 调色板 |
| Panel 标签 | 小写粗体 (a, b, c...) | 11pt 粗体 |

---

## 版本记录

| 日期 | 图表 | 变更内容 |
|------|------|---------|
| 2026-03-20 | Fig 2 | 初版完成: 四国 Urban Q 2x2 panel，含蒙特卡洛 CI 和断点标注 |
