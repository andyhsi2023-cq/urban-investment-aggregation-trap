"""
50b_china_q_adjusted.py
========================
目的：构建 V1_adjusted（年龄折价版本）和口径不确定性框架，
     回应审稿意见"V1 = 新房均价 x 全部存量面积 系统性高估 20-40%"。

核心改进：
  Part A: V1_adj(t) = Sum_{s} Price(s) * NewArea(s) * (1 - delta_age)^(t-s)
          每个 vintage 按建成当年价格购入后折旧，避免用当期新房价给全存量定价
  Part B: 7口径加权 Q + Dirichlet 口径权重不确定性
  Part C: Q=1 交叉时点的不确定性带

输入数据：
  - c5_residential_price_NBS_1998-2024.csv — 各年住宅均价
  - c3_new_construction_starts_NBS_1985-2024.csv — 各年竣工面积
  - china_urban_q_real_data.csv — 现有多口径 Q 数据

输出：
  - china_q_adjusted.csv — 调整后时序数据
  - china_q_adjusted_report.txt — 分析报告
  - fig_china_q_adjusted.png — 不确定性带可视化

依赖包：pandas, numpy, matplotlib, scipy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
from pathlib import Path
import warnings
import textwrap

warnings.filterwarnings('ignore')
np.random.seed(42)

# ============================================================
# 0. 路径设置
# ============================================================

SIX_CURVES = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition/02-data")
URBAN_Q = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")

# 输入
PRICE_CSV  = SIX_CURVES / "raw" / "c5_residential_price_NBS_1998-2024.csv"
STARTS_CSV = SIX_CURVES / "raw" / "c3_new_construction_starts_NBS_1985-2024.csv"
Q_DATA_CSV = URBAN_Q / "03-analysis" / "models" / "china_urban_q_real_data.csv"

# 输出
OUT_CSV    = URBAN_Q / "03-analysis" / "models" / "china_q_adjusted.csv"
OUT_REPORT = URBAN_Q / "03-analysis" / "models" / "china_q_adjusted_report.txt"
OUT_FIG    = URBAN_Q / "04-figures" / "drafts" / "fig_china_q_adjusted.png"

print("=" * 70)
print("中国 Urban Q — 年龄折价 V1_adj + 口径不确定性框架")
print("=" * 70)

# ============================================================
# 1. 数据加载
# ============================================================

print("\n[1] 加载数据...")

price_df = pd.read_csv(PRICE_CSV).set_index('year')
starts_df = pd.read_csv(STARTS_CSV).set_index('year')
q_df = pd.read_csv(Q_DATA_CSV).set_index('year')

# 提取关键序列
# 住宅均价 (元/m2)
res_price = price_df['residential_avg_price_yuan_m2']

# 竣工面积 (万m2)：1998+ 使用真实数据，1985-1997 用新开工 x 0.70 估算
EARLY_COMP_RATIO = 0.70
completion = {}
for yr in range(1985, 1998):
    ns = starts_df.loc[yr, 'new_starts_10k_m2'] if yr in starts_df.index else np.nan
    if pd.notna(ns):
        completion[yr] = ns * EARLY_COMP_RATIO
for yr in range(1998, 2025):
    completion[yr] = starts_df.loc[yr, 'completion_10k_m2']
completion = pd.Series(completion).sort_index()

# 从现有 Q 数据中提取 K1, K2, V1, V2, V3 以及各口径 Q
YEARS = range(1998, 2025)

print(f"  住宅均价: {res_price.index.min()}-{res_price.index.max()}")
print(f"  竣工面积: {completion.index.min()}-{completion.index.max()}")
print(f"  现有Q数据: {q_df.index.min()}-{q_df.index.max()}, {len(q_df.columns)} 列")

# ============================================================
# Part A: V1_adjusted — 年龄折价存量估值
# ============================================================

print("\n" + "=" * 70)
print("Part A: V1_adjusted — 年龄折价存量估值")
print("=" * 70)

# V1_adj(t) = Sum_{s=earliest}^{t} Price(s) * Completion(s) * (1 - delta_age)^(t-s)
#
# 与原 V1 = Price(t) * Stock_PIM(t) 的区别：
# - 原方法: 用当期新房价给所有存量估值 -> 老旧住宅被高估
# - 新方法: 每个 vintage 用建成当年价格，然后按年折旧 -> 更保守

# 1998 年之前存量的初始化：
# 1985-1997 年无住宅均价数据，统一用 1998 年价格折旧
# 这仍可能略高估，但 1998 前存量经过多年折旧后权重较小

PRICE_PRE1998 = res_price.loc[1998]  # 1854 元/m2

def compute_v1_adjusted(delta_age, price_series, completion_series, years):
    """
    计算 V1_adjusted：按年份-价格折旧的存量估值。

    每个 vintage s 的住宅在时点 t 的价值 = Price(s) * Area(s) * (1-delta)^(t-s)
    V1_adj(t) = Sum_s 上述值

    单位: 元/m2 * 万m2 = 万元 => / 10000 = 亿元
    """
    v1_adj = {}
    for t in years:
        total_value = 0.0
        for s in range(completion_series.index.min(), t + 1):
            if s not in completion_series.index or pd.isna(completion_series[s]):
                continue
            area = completion_series[s]  # 万m2
            # 价格：1998+ 用当年价格，1998 前用 1998 年价格
            if s in price_series.index and pd.notna(price_series[s]):
                p = price_series[s]
            else:
                p = PRICE_PRE1998
            # 折旧
            depreciation = (1 - delta_age) ** (t - s)
            total_value += p * area * depreciation
        v1_adj[t] = total_value / 10000.0  # 转换为亿元
    return pd.Series(v1_adj)


# 三种折旧率情景
DELTA_SCENARIOS = {
    'low':  0.010,  # 1.0% — 乐观（住宅保值较好）
    'mid':  0.015,  # 1.5% — 基准
    'high': 0.020,  # 2.0% — 保守（经济贬值较快）
}

print("\n计算三种折旧率情景下的 V1_adj...")

v1_adj_results = {}
for label, delta in DELTA_SCENARIOS.items():
    v1_adj_results[label] = compute_v1_adjusted(delta, res_price, completion, YEARS)
    latest = v1_adj_results[label].iloc[-1]
    print(f"  delta={delta:.1%} ({label}): V1_adj(2024) = {latest:,.0f} 亿元")

# 与原 V1 对比
v1_original = q_df['V1_100m']
print(f"\n  原 V1(2024) = {v1_original.loc[2024]:,.0f} 亿元")

for label, delta in DELTA_SCENARIOS.items():
    ratio = v1_adj_results[label].loc[2024] / v1_original.loc[2024]
    discount = (1 - ratio) * 100
    print(f"  V1_adj({label})/V1 = {ratio:.3f} (折价 {discount:.1f}%)")

# 构建输出 DataFrame
out_df = pd.DataFrame(index=YEARS)
out_df.index.name = 'year'

out_df['V1_original_100m'] = v1_original
out_df['V1_adj_low_100m'] = v1_adj_results['low']
out_df['V1_adj_mid_100m'] = v1_adj_results['mid']
out_df['V1_adj_high_100m'] = v1_adj_results['high']

# 使用基准 V1_adj (mid) 计算 Q_V1adj_K2
K2 = q_df['K2_100m']
out_df['K2_100m'] = K2

out_df['Q_V1adj_K2_low'] = v1_adj_results['low'] / K2
out_df['Q_V1adj_K2_mid'] = v1_adj_results['mid'] / K2
out_df['Q_V1adj_K2_high'] = v1_adj_results['high'] / K2

# 各年偏差百分比
for label in ['low', 'mid', 'high']:
    col = f'discount_pct_{label}'
    out_df[col] = (1 - v1_adj_results[label] / v1_original) * 100

print(f"\n偏差幅度 (V1_adj_mid 相对 V1 的折价%):")
for yr in [1998, 2005, 2010, 2015, 2020, 2024]:
    d = out_df.loc[yr, 'discount_pct_mid']
    print(f"  {yr}: {d:.1f}%")

# ============================================================
# Part B: 口径不确定性框架
# ============================================================

print("\n" + "=" * 70)
print("Part B: 口径不确定性框架 — 7口径加权 Q + 蒙特卡洛")
print("=" * 70)

# --- B.1 七口径 Q 时序 ---

# 从现有数据读取六口径
q_cols_original = ['Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2', 'Q_V3K2', 'Q_V3K3']
for col in q_cols_original:
    out_df[col] = q_df[col]

# 第七口径: Q_V1adj_K2 (使用基准 delta=1.5%)
out_df['Q_V1adjK2'] = out_df['Q_V1adj_K2_mid']

# 所有七口径列名
Q_COLS_7 = ['Q_V1adjK2', 'Q_V1K2', 'Q_V1K1', 'Q_V3K2', 'Q_V2K2', 'Q_V2K1', 'Q_V3K3']

# --- B.2 确定性加权 ---
# 权重基于与 Urban Q 理论定义的匹配度
# Urban Q = 城市资产市场价值 / 重置成本
# V1_adj/K2 最接近：保守市场价值 / 全口径重置成本

WEIGHTS_DETERMINISTIC = {
    'Q_V1adjK2': 0.30,  # 最保守的市场价值 / 全口径建设投资
    'Q_V1K2':    0.25,  # 标准市场价值 / 全口径建设投资
    'Q_V1K1':    0.15,  # 市场价值 / 房地产投资
    'Q_V3K2':    0.10,  # 综合价值 / 全口径投资
    'Q_V2K2':    0.08,  # 累计销售 / 全口径投资
    'Q_V2K1':    0.07,  # 累计销售 / 房地产投资
    'Q_V3K3':    0.05,  # 综合资产 / 全口径PIM
}

# 验证权重和为1
w_sum = sum(WEIGHTS_DETERMINISTIC.values())
assert abs(w_sum - 1.0) < 1e-10, f"权重和 = {w_sum}, 应为 1.0"

# 确定性加权 Q
out_df['Q_weighted'] = sum(
    WEIGHTS_DETERMINISTIC[col] * out_df[col] for col in Q_COLS_7
)

print("\n确定性加权 Q（7口径）:")
for yr in [1998, 2005, 2010, 2015, 2020, 2024]:
    print(f"  {yr}: Q_weighted = {out_df.loc[yr, 'Q_weighted']:.4f}")

# --- B.3 蒙特卡洛升级：参数 + 口径双重不确定性 ---

N_SIM = 5000
print(f"\n蒙特卡洛模拟: {N_SIM} 次 (参数 + 口径不确定性)...")

# Dirichlet 浓度参数：基于确定性权重 x 浓度因子
# 浓度因子越大，权重越集中于先验
CONCENTRATION = 20  # 适度浓度：允许合理变动但不会太离散
dirichlet_alpha = np.array([WEIGHTS_DETERMINISTIC[col] * CONCENTRATION for col in Q_COLS_7])

# 参数不确定性的标准差
PRICE_NOISE_STD = 0.05   # 价格测量误差 +-5%
DELTA_AGE_STD = 0.003    # 折旧率不确定性 (基准 0.015 +- 0.003)
DELTA_AGE_BASE = 0.015

# 存储结果
mc_q_weighted = np.zeros((N_SIM, len(list(YEARS))))
mc_q1_crossing = []  # 记录每次模拟的 Q=1 交叉年份

years_arr = np.array(list(YEARS))
n_years = len(years_arr)

# 预计算不随参数变化的量
# 原六口径 Q 值矩阵 (n_years x 6)
q_original_matrix = np.column_stack([
    q_df.loc[years_arr, col].values for col in Q_COLS_7[1:]  # 除 V1adjK2 外的6个
])

# 预计算竣工面积向量
comp_arr = np.array([completion.get(s, 0.0) for s in range(completion.index.min(), 2025)])
comp_years = np.arange(completion.index.min(), 2025)

# 预计算价格向量（含 1998 前填充）
price_arr = np.array([
    res_price.get(s, PRICE_PRE1998) if s >= 1998 else PRICE_PRE1998
    for s in comp_years
])

K2_arr = K2.loc[years_arr].values

print("  运行蒙特卡洛...")

for sim in range(N_SIM):
    # (a) 抽取参数
    price_shock = 1.0 + np.random.normal(0, PRICE_NOISE_STD)  # 全局价格偏移
    delta_age_draw = np.clip(
        np.random.normal(DELTA_AGE_BASE, DELTA_AGE_STD), 0.005, 0.035
    )

    # (b) 抽取口径权重 (Dirichlet)
    weights_draw = np.random.dirichlet(dirichlet_alpha)

    # (c) 计算 V1_adj 的扰动版本
    v1_adj_sim = np.zeros(n_years)
    for ti, t in enumerate(years_arr):
        total_val = 0.0
        for si, s in enumerate(comp_years):
            if s > t:
                break
            total_val += (price_arr[si] * price_shock) * comp_arr[si] * (1 - delta_age_draw) ** (t - s)
        v1_adj_sim[ti] = total_val / 10000.0

    # Q_V1adjK2 的扰动版本
    q_v1adj_k2_sim = v1_adj_sim / K2_arr

    # 原六口径也叠加微小扰动（反映数据测量误差）
    # 对原六口径施加 +-2% 随机扰动
    q_original_perturbed = q_original_matrix * (1 + np.random.normal(0, 0.02, q_original_matrix.shape))

    # 组合七口径
    q_all_sim = np.column_stack([q_v1adj_k2_sim, q_original_perturbed])

    # 加权平均
    q_weighted_sim = q_all_sim @ weights_draw
    mc_q_weighted[sim, :] = q_weighted_sim

    # (d) 寻找 Q=1 交叉点
    for i in range(1, n_years):
        if (q_weighted_sim[i-1] - 1) * (q_weighted_sim[i] - 1) < 0:
            # 下穿
            if q_weighted_sim[i-1] > 1 and q_weighted_sim[i] < 1:
                cross_yr = years_arr[i-1] + (1 - q_weighted_sim[i-1]) / (q_weighted_sim[i] - q_weighted_sim[i-1])
                mc_q1_crossing.append(cross_yr)
                break  # 只记录第一次下穿

if sim % 1000 == 999:
    pass  # 进度（静默）

# --- B.4 计算统计量 ---

q_median = np.median(mc_q_weighted, axis=0)
q_mean = np.mean(mc_q_weighted, axis=0)
q_p05 = np.percentile(mc_q_weighted, 5, axis=0)
q_p10 = np.percentile(mc_q_weighted, 10, axis=0)
q_p25 = np.percentile(mc_q_weighted, 25, axis=0)
q_p75 = np.percentile(mc_q_weighted, 75, axis=0)
q_p90 = np.percentile(mc_q_weighted, 90, axis=0)
q_p95 = np.percentile(mc_q_weighted, 95, axis=0)

out_df['Q_mc_median'] = q_median
out_df['Q_mc_mean'] = q_mean
out_df['Q_mc_p05'] = q_p05
out_df['Q_mc_p10'] = q_p10
out_df['Q_mc_p25'] = q_p25
out_df['Q_mc_p75'] = q_p75
out_df['Q_mc_p90'] = q_p90
out_df['Q_mc_p95'] = q_p95

print(f"\n蒙特卡洛结果 (Q_weighted):")
for yr in [2000, 2005, 2010, 2015, 2020, 2024]:
    idx = list(YEARS).index(yr)
    print(f"  {yr}: median={q_median[idx]:.3f}, "
          f"90%CI=[{q_p05[idx]:.3f}, {q_p95[idx]:.3f}]")

# ============================================================
# Part C: Q=1 交叉时点不确定性
# ============================================================

print("\n" + "=" * 70)
print("Part C: Q=1 交叉时点的不确定性带")
print("=" * 70)

mc_q1_crossing = np.array(mc_q1_crossing)
n_crossing = len(mc_q1_crossing)
pct_crossing = n_crossing / N_SIM * 100

print(f"\n  在 {N_SIM} 次模拟中，{n_crossing} 次 ({pct_crossing:.1f}%) Q 下穿 1")

if n_crossing > 10:
    cross_median = np.median(mc_q1_crossing)
    cross_mean = np.mean(mc_q1_crossing)
    cross_p05 = np.percentile(mc_q1_crossing, 5)
    cross_p25 = np.percentile(mc_q1_crossing, 25)
    cross_p75 = np.percentile(mc_q1_crossing, 75)
    cross_p95 = np.percentile(mc_q1_crossing, 95)

    print(f"  Q=1 交叉年份:")
    print(f"    中位数: {cross_median:.1f}")
    print(f"    均值:   {cross_mean:.1f}")
    print(f"    50% CI: [{cross_p25:.1f}, {cross_p75:.1f}]")
    print(f"    90% CI: [{cross_p05:.1f}, {cross_p95:.1f}]")
else:
    cross_median = cross_mean = cross_p05 = cross_p95 = cross_p25 = cross_p75 = np.nan
    print("  交叉次数过少，无法估计可靠区间")

# 确定性加权 Q 的交叉点
q_weighted_series = out_df['Q_weighted']
det_crossing = np.nan
for i in range(1, len(years_arr)):
    y0, y1 = years_arr[i-1], years_arr[i]
    v0, v1 = q_weighted_series.loc[y0], q_weighted_series.loc[y1]
    if v0 > 1 and v1 < 1:
        det_crossing = y0 + (1 - v0) / (v1 - v0)
        break

print(f"\n  确定性加权 Q 交叉年份: {det_crossing:.1f}")

# ============================================================
# 保存数据
# ============================================================

print("\n" + "=" * 70)
print("保存输出...")
print("=" * 70)

out_df.to_csv(OUT_CSV, float_format='%.4f')
print(f"  数据 -> {OUT_CSV}")

# ============================================================
# 生成报告
# ============================================================

report_lines = []
report_lines.append("=" * 70)
report_lines.append("中国 Urban Q — 年龄折价 V1_adj + 口径不确定性框架")
report_lines.append("=" * 70)
report_lines.append("")

report_lines.append("Part A: V1_adjusted 年龄折价估值")
report_lines.append("-" * 40)
report_lines.append("")
report_lines.append("方法: V1_adj(t) = Sum_s [Price(s) * Completion(s) * (1-delta)^(t-s)]")
report_lines.append("  每个 vintage 按建成当年价格购入后折旧，替代原方法")
report_lines.append("  原方法 V1 = Price(t) * Stock_PIM(t) 用当期新房价给全存量定价")
report_lines.append("")
report_lines.append("折旧率敏感性分析:")
report_lines.append(f"  {'年份':<6} {'V1_原始':>12} {'V1_adj(1.0%)':>14} {'V1_adj(1.5%)':>14} {'V1_adj(2.0%)':>14} {'折价%(1.5%)':>12}")
for yr in list(YEARS):
    v1_o = out_df.loc[yr, 'V1_original_100m']
    v1_l = out_df.loc[yr, 'V1_adj_low_100m']
    v1_m = out_df.loc[yr, 'V1_adj_mid_100m']
    v1_h = out_df.loc[yr, 'V1_adj_high_100m']
    d = out_df.loc[yr, 'discount_pct_mid']
    report_lines.append(f"  {yr:<6} {v1_o:>12,.0f} {v1_l:>14,.0f} {v1_m:>14,.0f} {v1_h:>14,.0f} {d:>11.1f}%")

report_lines.append("")
report_lines.append("关键发现:")
d_2024 = out_df.loc[2024, 'discount_pct_mid']
d_early = out_df.loc[2005, 'discount_pct_mid']
report_lines.append(f"  - V1_adj(mid) 在 2024 年折价 {d_2024:.1f}%（审稿人预期 20-40%）")
report_lines.append(f"  - 折价幅度随时间扩大: 2005年 {d_early:.1f}% -> 2024年 {d_2024:.1f}%")
report_lines.append(f"  - 折价主要来源：旧存量按历史低价+折旧估值，而非用当期高价")

report_lines.append("")
report_lines.append("")
report_lines.append("Part B: 口径不确定性框架")
report_lines.append("-" * 40)
report_lines.append("")
report_lines.append("七口径权重分配:")
for col in Q_COLS_7:
    w = WEIGHTS_DETERMINISTIC[col]
    report_lines.append(f"  {col:<15} w = {w:.2f}")
report_lines.append("")
report_lines.append(f"蒙特卡洛: {N_SIM} 次模拟")
report_lines.append(f"  参数不确定性: 价格噪声 +/-{PRICE_NOISE_STD*100:.0f}%, "
                    f"折旧率 {DELTA_AGE_BASE:.3f} +/- {DELTA_AGE_STD:.3f}")
report_lines.append(f"  口径不确定性: Dirichlet(alpha), 浓度因子 = {CONCENTRATION}")
report_lines.append("")
report_lines.append(f"  {'年份':<6} {'Q_median':>10} {'Q_p05':>10} {'Q_p25':>10} {'Q_p75':>10} {'Q_p95':>10}")
for yr in list(YEARS):
    idx = list(YEARS).index(yr)
    report_lines.append(
        f"  {yr:<6} {q_median[idx]:>10.4f} {q_p05[idx]:>10.4f} "
        f"{q_p25[idx]:>10.4f} {q_p75[idx]:>10.4f} {q_p95[idx]:>10.4f}"
    )

report_lines.append("")
report_lines.append("")
report_lines.append("Part C: Q=1 交叉时点不确定性")
report_lines.append("-" * 40)
report_lines.append("")
report_lines.append(f"  蒙特卡洛中 Q 下穿 1 的比例: {pct_crossing:.1f}% ({n_crossing}/{N_SIM})")
report_lines.append(f"  确定性加权 Q 交叉年份: {det_crossing:.1f}")
if n_crossing > 10:
    report_lines.append(f"  蒙特卡洛 Q=1 交叉年份:")
    report_lines.append(f"    中位数: {cross_median:.1f}")
    report_lines.append(f"    50% CI: [{cross_p25:.1f}, {cross_p75:.1f}]")
    report_lines.append(f"    90% CI: [{cross_p05:.1f}, {cross_p95:.1f}]")
    report_lines.append("")
    report_lines.append("  解读: Q=1 交叉标志从 expansion 到 renewal 的制度拐点。")
    report_lines.append(f"  在口径+参数双重不确定性下，拐点的 90% 可信区间为")
    report_lines.append(f"  [{cross_p05:.1f}, {cross_p95:.1f}]，中位数 {cross_median:.1f}。")

report_text = "\n".join(report_lines)
OUT_REPORT.write_text(report_text, encoding='utf-8')
print(f"  报告 -> {OUT_REPORT}")

# ============================================================
# 可视化
# ============================================================

print("\n生成图表...")

plt.rcParams['font.family'] = ['Arial']
plt.rcParams['font.size'] = 10

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.subplots_adjust(hspace=0.32, wspace=0.25, top=0.93, bottom=0.07, left=0.07, right=0.95)

years_plot = np.array(list(YEARS))

# --- (a) V1 原始 vs V1_adj 三情景 ---
ax = axes[0, 0]
ax.plot(years_plot, out_df['V1_original_100m'] / 10000, 'k-', lw=2.5, label='V1 original')
ax.plot(years_plot, out_df['V1_adj_low_100m'] / 10000, '--', color='#2196F3', lw=1.5,
        label=r'V1$_{adj}$ ($\delta$=1.0%)')
ax.plot(years_plot, out_df['V1_adj_mid_100m'] / 10000, '-', color='#E53935', lw=2,
        label=r'V1$_{adj}$ ($\delta$=1.5%)')
ax.plot(years_plot, out_df['V1_adj_high_100m'] / 10000, '--', color='#FF9800', lw=1.5,
        label=r'V1$_{adj}$ ($\delta$=2.0%)')
ax.fill_between(years_plot,
                out_df['V1_adj_high_100m'] / 10000,
                out_df['V1_adj_low_100m'] / 10000,
                alpha=0.15, color='#E53935')
ax.set_title('(a) V1 Original vs V1$_{adj}$ (Vintage-Depreciated)', fontsize=13, fontweight='bold')
ax.set_ylabel('Trillion CNY', fontsize=11)
ax.legend(fontsize=9, loc='upper left')
ax.grid(True, alpha=0.3)

# 右轴: 折价百分比
ax2 = ax.twinx()
ax2.plot(years_plot, out_df['discount_pct_mid'], ':', color='gray', lw=1.5, label='Discount %')
ax2.set_ylabel('Discount %', fontsize=10, color='gray')
ax2.tick_params(axis='y', labelcolor='gray')
ax2.set_ylim(0, 50)

# --- (b) 七口径 Q 时序 ---
ax = axes[0, 1]
colors_7 = ['#E53935', '#1976D2', '#388E3C', '#F57C00', '#7B1FA2', '#00838F', '#5D4037']
for i, col in enumerate(Q_COLS_7):
    lw = 2.5 if col == 'Q_V1adjK2' else 1.2
    ls = '-' if col == 'Q_V1adjK2' else '--'
    alpha = 1.0 if col == 'Q_V1adjK2' else 0.6
    ax.plot(years_plot, out_df[col], ls, color=colors_7[i], lw=lw, alpha=alpha, label=col)

ax.axhline(1, color='black', ls=':', lw=1, alpha=0.5)
ax.set_title('(b) Seven Calibrations of Urban Q', fontsize=13, fontweight='bold')
ax.set_ylabel('Urban Q ratio', fontsize=11)
ax.legend(fontsize=7.5, loc='upper right', ncol=2)
ax.grid(True, alpha=0.3)

# --- (c) 加权 Q + 蒙特卡洛不确定性带 ---
ax = axes[1, 0]

# 90% CI 带
ax.fill_between(years_plot, q_p05, q_p95, alpha=0.12, color='#1976D2', label='90% CI (param+calibration)')
# 50% CI 带
ax.fill_between(years_plot, q_p25, q_p75, alpha=0.25, color='#1976D2', label='50% CI')
# 中位数
ax.plot(years_plot, q_median, '-', color='#1976D2', lw=2.5, label='MC median')
# 确定性加权
ax.plot(years_plot, out_df['Q_weighted'], '--', color='#E53935', lw=1.5, label='Deterministic weighted')
# Q=1 线
ax.axhline(1, color='black', ls=':', lw=1.5, alpha=0.7)

# Q=1 交叉区间
if n_crossing > 10:
    ax.axvspan(cross_p05, cross_p95, alpha=0.15, color='#FF9800', label=f'Q=1 crossing 90% CI')
    ax.axvline(cross_median, color='#FF9800', ls='--', lw=1.5, alpha=0.7)

ax.set_title('(c) Weighted Urban Q with Uncertainty Band', fontsize=13, fontweight='bold')
ax.set_ylabel('Urban Q ratio', fontsize=11)
ax.legend(fontsize=8, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_ylim(0, max(q_p95) * 1.1)

# --- (d) Q=1 交叉年份分布 ---
ax = axes[1, 1]
if n_crossing > 30:
    ax.hist(mc_q1_crossing, bins=30, color='#1976D2', alpha=0.7, edgecolor='white', density=True)
    ax.axvline(cross_median, color='#E53935', ls='-', lw=2, label=f'Median: {cross_median:.1f}')
    ax.axvline(cross_p05, color='#FF9800', ls='--', lw=1.5, label=f'90% CI: [{cross_p05:.1f}, {cross_p95:.1f}]')
    ax.axvline(cross_p95, color='#FF9800', ls='--', lw=1.5)
    ax.axvline(det_crossing, color='green', ls=':', lw=2, label=f'Deterministic: {det_crossing:.1f}')

    # 添加 KDE
    if len(mc_q1_crossing) > 50:
        try:
            kde = stats.gaussian_kde(mc_q1_crossing)
            x_kde = np.linspace(mc_q1_crossing.min() - 1, mc_q1_crossing.max() + 1, 200)
            ax.plot(x_kde, kde(x_kde), '-', color='#E53935', lw=1.5, alpha=0.5)
        except Exception:
            pass

    ax.set_title('(d) Distribution of Q=1 Crossing Year', fontsize=13, fontweight='bold')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Density', fontsize=11)
    ax.legend(fontsize=9)
else:
    ax.text(0.5, 0.5, f'Insufficient Q=1 crossings\n({n_crossing}/{N_SIM} simulations)',
            ha='center', va='center', fontsize=14, transform=ax.transAxes)
    ax.set_title('(d) Distribution of Q=1 Crossing Year', fontsize=13, fontweight='bold')

ax.grid(True, alpha=0.3)

for ax_row in axes:
    for a in ax_row:
        a.set_xlabel('Year', fontsize=10)

fig.suptitle('China Urban Q: Vintage-Adjusted V1 and Calibration Uncertainty',
             fontsize=14, fontweight='bold', y=0.97)

fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight')
print(f"  图表 -> {OUT_FIG}")

plt.close()

# ============================================================
# 摘要
# ============================================================

print("\n" + "=" * 70)
print("完成! 摘要")
print("=" * 70)
print(f"\n  V1_adj (delta=1.5%) 相对 V1 折价:")
print(f"    2010: {out_df.loc[2010, 'discount_pct_mid']:.1f}%")
print(f"    2020: {out_df.loc[2020, 'discount_pct_mid']:.1f}%")
print(f"    2024: {out_df.loc[2024, 'discount_pct_mid']:.1f}%")
print(f"\n  加权 Q (确定性):")
print(f"    2020: {out_df.loc[2020, 'Q_weighted']:.4f}")
print(f"    2024: {out_df.loc[2024, 'Q_weighted']:.4f}")
print(f"\n  Q=1 交叉 (确定性): {det_crossing:.1f}")
if n_crossing > 10:
    print(f"  Q=1 交叉 (MC 90% CI): [{cross_p05:.1f}, {cross_p95:.1f}]")
print(f"\n  输出文件:")
print(f"    {OUT_CSV}")
print(f"    {OUT_REPORT}")
print(f"    {OUT_FIG}")
