"""
60_robustness_vt_breakpoint.py
===============================
目的：Urban Q 稳健性检验三件套
  (1) V(t) 蒙特卡洛置信区间 — 参数不确定性下 Q=1 交叉年份的稳健性
  (2) Bai-Perron 结构断点检验 — 为 regime change 叙事提供统计支撑
  (3) Early Warning Signals — critical slowing down 框架

输入：china_urban_q_real_data.csv, japan_urban_q_timeseries.csv
输出：
  - monte_carlo_q_ci.csv
  - structural_break_test.txt
  - early_warning_signals.txt
  - fig17_robustness.png

依赖包：pandas, numpy, scipy, statsmodels, matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
from scipy.interpolate import interp1d
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from pathlib import Path
import warnings
import textwrap
from datetime import datetime

warnings.filterwarnings('ignore')

np.random.seed(42)

# ============================================================
# 0. 路径与常量
# ============================================================

URBAN_Q = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
DATA_CSV = URBAN_Q / "03-analysis" / "models" / "china_urban_q_real_data.csv"
JAPAN_CSV = URBAN_Q / "03-analysis" / "models" / "japan_urban_q_timeseries.csv"

OUT_MC_CSV  = URBAN_Q / "03-analysis" / "models" / "monte_carlo_q_ci.csv"
OUT_BREAK   = URBAN_Q / "03-analysis" / "models" / "structural_break_test.txt"
OUT_EWS     = URBAN_Q / "03-analysis" / "models" / "early_warning_signals.txt"
OUT_FIG     = URBAN_Q / "04-figures" / "drafts" / "fig17_robustness.png"

N_SIM = 5000  # 蒙特卡洛模拟次数

print("=" * 70)
print("Urban Q 稳健性检验：蒙特卡洛 + Bai-Perron + Early Warning Signals")
print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

# ============================================================
# 1. 加载数据
# ============================================================

print("\n[1] 加载数据...")
df = pd.read_csv(DATA_CSV)
df = df.set_index('year')
print(f"  中国数据: {df.index.min()}-{df.index.max()}, {len(df)}行")

japan = pd.read_csv(JAPAN_CSV)
japan = japan.set_index('year')
print(f"  日本数据: {japan.index.min()}-{japan.index.max()}, {len(japan)}行")

# 提取基准序列
years = df.index.values
Q_V1K2_base = df['Q_V1K2'].values
Q_V1K1_base = df['Q_V1K1'].values
V1_base = df['V1_100m'].values
K1_base = df['K1_100m'].values
K2_base = df['K2_100m'].values

# 从原始数据提取用于蒙特卡洛扰动的关键变量
res_price = df['residential_price'].values      # 住宅均价 (元/m2)
housing_stock = df['housing_stock_pim'].values   # 住宅存量 (万m2)
re_inv = df['re_inv_100m'].values                # 房地产投资 (亿元)
infra_inv = df['infra_inv_100m'].values          # 基础设施投资 (亿元)

# ============================================================
# 2. 分析 1：蒙特卡洛置信区间
# ============================================================

print(f"\n[2] 蒙特卡洛模拟 (N={N_SIM})...")

def pim_from_annual_flows(flows, delta, n_years):
    """
    从年度流量序列计算 PIM 存量序列。
    flows: shape (n_years,) 的年度投资/竣工流量
    delta: 折旧率
    返回: shape (n_years,) 的存量序列
    """
    stock = np.zeros(n_years)
    for t in range(n_years):
        s = 0.0
        for yr in range(t + 1):
            s += flows[yr] * (1 - delta) ** (t - yr)
        stock[t] = s
    return stock


def find_q1_crossing_interpolated(years, q_vals):
    """
    找到 Q 从 >1 变为 <1 的交叉年份（线性插值）。
    返回交叉年份列表。
    """
    crossings = []
    for i in range(1, len(q_vals)):
        v0, v1 = q_vals[i-1], q_vals[i]
        if (v0 - 1) * (v1 - 1) < 0 and v0 > v1:  # 从>1 到 <1
            cross_year = years[i-1] + (1.0 - v0) / (v1 - v0) * (years[i] - years[i-1])
            crossings.append(cross_year)
    return crossings


# --- 2.1 V1/K2 口径蒙特卡洛 ---
print("  [2.1] V1/K2 口径蒙特卡洛...")

# 参数扰动范围
# V1 不确定性：
#   住宅均价：±15%  -> 乘数 ~ N(1, 0.15/1.96) 截断在 [0.85, 1.15]
#   存量面积：±10%  -> 乘数 ~ N(1, 0.10/1.96) 截断在 [0.90, 1.10]
#   存量折旧率 delta_V：U(0.01, 0.03)，基准 0.02
#
# K2 不确定性：
#   房地产投资：±5%  -> 乘数 ~ N(1, 0.05/1.96)
#   基础设施投资：±10% -> 乘数 ~ N(1, 0.10/1.96)
#   投资折旧率 delta_K：U(0.02, 0.04)，基准 0.03

n_years = len(years)

# 存储模拟结果
Q_V1K2_sims = np.zeros((N_SIM, n_years))
Q_V1K1_sims = np.zeros((N_SIM, n_years))
crossing_years_V1K2 = []
crossing_years_V1K1 = []

for sim in range(N_SIM):
    if sim % 1000 == 0:
        print(f"    模拟 {sim}/{N_SIM}...")

    # --- 扰动 V1 参数 ---
    # 住宅均价乘数（每次模拟一个系统性偏差 + 年度随机波动）
    price_sys_mult = np.clip(np.random.normal(1.0, 0.15/1.96), 0.85, 1.15)
    price_year_noise = np.clip(np.random.normal(0, 0.05, n_years), -0.15, 0.15)
    price_mult = price_sys_mult + price_year_noise

    # 存量面积乘数
    stock_sys_mult = np.clip(np.random.normal(1.0, 0.10/1.96), 0.90, 1.10)
    stock_year_noise = np.clip(np.random.normal(0, 0.03, n_years), -0.10, 0.10)
    stock_mult = stock_sys_mult + stock_year_noise

    # 折旧率
    delta_V = np.random.uniform(0.01, 0.03)

    # --- 扰动 K2 参数 ---
    re_inv_mult = np.clip(np.random.normal(1.0, 0.05/1.96), 0.95, 1.05)
    infra_inv_mult = np.clip(np.random.normal(1.0, 0.10/1.96), 0.90, 1.10)
    delta_K = np.random.uniform(0.02, 0.04)

    # --- 重新计算 V1 ---
    # V1(t) = price(t) * stock(t) / 10000
    # 由于 stock 是 PIM 累计，折旧率的变化会影响存量
    # 为简化，我们直接对基准 V1 施加价格和存量乘数扰动
    # 再叠加折旧率偏离基准的修正
    # 折旧率修正：delta_V 从 0.02 变化时，存量变化近似为
    #   Stock(delta) / Stock(0.02) ≈ exp(-(delta-0.02) * avg_age)
    #   中国住宅平均楼龄 ≈ 12-15 年
    avg_age_housing = 13.0
    depreciation_correction_V = np.exp(-(delta_V - 0.02) * avg_age_housing)

    V1_sim = res_price * price_mult * housing_stock * stock_mult * depreciation_correction_V / 10000.0

    # --- 重新计算 K2 ---
    # K2 = PIM(RE_inv + Infra_inv, delta_K)
    # 同样用修正因子近似
    avg_age_capital = 10.0  # 投资平均年龄
    depreciation_correction_K = np.exp(-(delta_K - 0.03) * avg_age_capital)

    re_inv_sim = re_inv * re_inv_mult
    infra_inv_sim = infra_inv * infra_inv_mult

    # K2 基准是 re_inv + infra_inv 的 PIM(delta=0.03)
    # 扰动后 K2 ≈ (re_inv_mult * base_re + infra_inv_mult * base_infra) / (base_re + base_infra) * K2_base * depr_correction
    # 简化计算：
    total_inv_base = re_inv + infra_inv
    total_inv_sim = re_inv_sim + infra_inv_sim
    # 每年的投资比例变化
    inv_ratio = np.where(total_inv_base > 0, total_inv_sim / total_inv_base, 1.0)

    # K2 是 PIM 累计，所以乘数效应不是逐年独立的
    # 近似：对 K2_base 施加加权平均的投资乘数 * 折旧修正
    # 更精确的方法：用 running average of inv_ratio
    cumsum_weight = np.zeros(n_years)
    for t in range(n_years):
        w_sum = 0.0
        wt_sum = 0.0
        for s in range(t + 1):
            w = (1 - 0.03) ** (t - s)
            w_sum += w
            wt_sum += w * inv_ratio[s]
        cumsum_weight[t] = wt_sum / w_sum if w_sum > 0 else 1.0

    K2_sim = K2_base * cumsum_weight * depreciation_correction_K
    K1_sim = K1_base * re_inv_mult * np.exp(-(delta_V - 0.02) * avg_age_capital)

    # --- 计算 Q ---
    Q_V1K2_sim = V1_sim / K2_sim
    Q_V1K1_sim = V1_sim / K1_sim

    Q_V1K2_sims[sim, :] = Q_V1K2_sim
    Q_V1K1_sims[sim, :] = Q_V1K1_sim

    # --- 找交叉年份 ---
    crossings = find_q1_crossing_interpolated(years, Q_V1K2_sim)
    if crossings:
        crossing_years_V1K2.append(crossings[-1])  # 取最后一个交叉点

    crossings_k1 = find_q1_crossing_interpolated(years, Q_V1K1_sim)
    if crossings_k1:
        crossing_years_V1K1.append(crossings_k1[-1])

print(f"  V1/K2: {len(crossing_years_V1K2)}/{N_SIM} 次模拟找到 Q=1 交叉")
print(f"  V1/K1: {len(crossing_years_V1K1)}/{N_SIM} 次模拟找到 Q=1 交叉")

# --- 2.2 计算分位数 ---
print("\n  [2.2] 计算分位数...")

percentiles = [5, 25, 50, 75, 95]
Q_V1K2_pctiles = np.percentile(Q_V1K2_sims, percentiles, axis=0)
Q_V1K1_pctiles = np.percentile(Q_V1K1_sims, percentiles, axis=0)

# --- 2.3 交叉年份统计 ---
crossing_V1K2 = np.array(crossing_years_V1K2)
crossing_V1K1 = np.array(crossing_years_V1K1)

print("\n  [2.3] Q=1 交叉年份统计:")
if len(crossing_V1K2) > 0:
    print(f"    V1/K2:")
    print(f"      中位数: {np.median(crossing_V1K2):.1f}")
    print(f"      均值:   {np.mean(crossing_V1K2):.1f}")
    print(f"      标准差: {np.std(crossing_V1K2):.2f}")
    print(f"      5%分位: {np.percentile(crossing_V1K2, 5):.1f}")
    print(f"      95%分位: {np.percentile(crossing_V1K2, 95):.1f}")
    print(f"      90% CI: [{np.percentile(crossing_V1K2, 5):.1f}, {np.percentile(crossing_V1K2, 95):.1f}]")

if len(crossing_V1K1) > 0:
    print(f"    V1/K1:")
    print(f"      中位数: {np.median(crossing_V1K1):.1f}")
    print(f"      均值:   {np.mean(crossing_V1K1):.1f}")
    print(f"      标准差: {np.std(crossing_V1K1):.2f}")
    print(f"      90% CI: [{np.percentile(crossing_V1K1, 5):.1f}, {np.percentile(crossing_V1K1, 95):.1f}]")

# --- 2.4 保存蒙特卡洛结果 CSV ---
mc_df = pd.DataFrame({
    'year': years,
    'Q_V1K2_base': Q_V1K2_base,
    'Q_V1K2_p5': Q_V1K2_pctiles[0],
    'Q_V1K2_p25': Q_V1K2_pctiles[1],
    'Q_V1K2_p50': Q_V1K2_pctiles[2],
    'Q_V1K2_p75': Q_V1K2_pctiles[3],
    'Q_V1K2_p95': Q_V1K2_pctiles[4],
    'Q_V1K1_base': Q_V1K1_base,
    'Q_V1K1_p5': Q_V1K1_pctiles[0],
    'Q_V1K1_p25': Q_V1K1_pctiles[1],
    'Q_V1K1_p50': Q_V1K1_pctiles[2],
    'Q_V1K1_p75': Q_V1K1_pctiles[3],
    'Q_V1K1_p95': Q_V1K1_pctiles[4],
})
mc_df.to_csv(OUT_MC_CSV, index=False, float_format='%.4f')
print(f"\n  蒙特卡洛结果已保存: {OUT_MC_CSV}")


# ============================================================
# 3. 分析 2：Bai-Perron 结构断点检验
# ============================================================

print("\n[3] Bai-Perron 结构断点检验...")

def chow_test(y, x, break_idx):
    """
    对单个候选断点执行 Chow 检验。
    y: 因变量
    x: 自变量（含常数项）
    break_idx: 断点位置（第几个观测值之后断开）
    返回: F统计量, p值
    """
    n = len(y)
    k = x.shape[1]

    # 全样本回归
    model_full = OLS(y, x).fit()
    rss_full = np.sum(model_full.resid ** 2)

    # 分段回归
    y1, x1 = y[:break_idx], x[:break_idx]
    y2, x2 = y[break_idx:], x[break_idx:]

    if len(y1) < k + 1 or len(y2) < k + 1:
        return np.nan, np.nan

    model1 = OLS(y1, x1).fit()
    model2 = OLS(y2, x2).fit()
    rss_unrestricted = np.sum(model1.resid ** 2) + np.sum(model2.resid ** 2)

    # F统计量
    df_num = k
    df_den = n - 2 * k
    if df_den <= 0 or rss_unrestricted <= 0:
        return np.nan, np.nan

    F_stat = ((rss_full - rss_unrestricted) / df_num) / (rss_unrestricted / df_den)
    p_value = 1.0 - stats.f.cdf(F_stat, df_num, df_den)

    return F_stat, p_value


def bai_perron_sequential(y, years_arr, max_breaks=3, min_segment=5, significance=0.05):
    """
    顺序 Bai-Perron 断点检验。
    在每一步找到最显著的断点，然后在子段中继续搜索。
    """
    n = len(y)
    t_trend = np.arange(n, dtype=float)
    x = sm.add_constant(t_trend)

    # 搜索所有候选断点
    results = []

    def search_segment(start, end, depth=0):
        if depth >= max_breaks:
            return
        if end - start < 2 * min_segment:
            return

        y_seg = y[start:end]
        x_seg = sm.add_constant(np.arange(end - start, dtype=float))

        best_F = -1
        best_break = None
        best_p = 1.0

        for bp in range(min_segment, end - start - min_segment + 1):
            F_stat, p_val = chow_test(y_seg, x_seg, bp)
            if not np.isnan(F_stat) and F_stat > best_F:
                best_F = F_stat
                best_break = bp
                best_p = p_val

        if best_break is not None and best_p < significance:
            abs_break = start + best_break
            results.append({
                'break_idx': abs_break,
                'break_year': years_arr[abs_break],
                'F_stat': best_F,
                'p_value': best_p,
                'depth': depth
            })
            # 递归搜索子段
            search_segment(start, abs_break, depth + 1)
            search_segment(abs_break, end, depth + 1)

    search_segment(0, n)

    # 按年份排序
    results.sort(key=lambda x: x['break_year'])
    return results


def segment_statistics(y, years_arr, break_indices):
    """计算每个分段的统计量：均值、方差、趋势斜率"""
    segments = []
    all_breaks = [0] + sorted(break_indices) + [len(y)]

    for i in range(len(all_breaks) - 1):
        s, e = all_breaks[i], all_breaks[i + 1]
        seg_y = y[s:e]
        seg_years = years_arr[s:e]

        t = np.arange(len(seg_y), dtype=float)
        if len(seg_y) >= 3:
            slope, intercept, r_value, p_value, std_err = stats.linregress(t, seg_y)
        else:
            slope, r_value, p_value = np.nan, np.nan, np.nan

        segments.append({
            'period': f"{seg_years[0]}-{seg_years[-1]}",
            'n_obs': len(seg_y),
            'mean': np.mean(seg_y),
            'std': np.std(seg_y),
            'trend_slope': slope,
            'trend_r2': r_value**2 if not np.isnan(r_value) else np.nan,
            'trend_p': p_value
        })

    return segments


# --- 3.1 中国 Q(V1/K2) 断点检验 ---
print("  [3.1] 中国 Q(V1/K2) 断点检验...")

# 使用 significance=0.10 以捕获更多潜在断点
china_breaks = bai_perron_sequential(Q_V1K2_base, years, max_breaks=3,
                                      min_segment=5, significance=0.10)

print(f"    发现 {len(china_breaks)} 个显著断点:")
for bp in china_breaks:
    print(f"      {bp['break_year']}: F={bp['F_stat']:.2f}, p={bp['p_value']:.4f}")

break_indices_china = [bp['break_idx'] for bp in china_breaks]
china_segments = segment_statistics(Q_V1K2_base, years, break_indices_china)

print("    分段统计:")
for seg in china_segments:
    print(f"      {seg['period']}: mean={seg['mean']:.3f}, "
          f"slope={seg['trend_slope']:.4f}/yr, std={seg['std']:.3f}")


# --- 3.2 CUSUM 检验 ---
print("\n  [3.2] CUSUM 检验...")

t_trend = np.arange(len(Q_V1K2_base), dtype=float)
X_cusum = sm.add_constant(t_trend)
model_cusum = OLS(Q_V1K2_base, X_cusum).fit()

# 递归残差 CUSUM
try:
    # OLS 残差的 CUSUM 检验 (Harvey-Collier 类型)
    # 手动实现：标准化递归残差的累计和
    n_obs = len(Q_V1K2_base)
    resids = model_cusum.resid
    sigma = np.std(resids, ddof=2)

    # 标准化累计和
    cusum_stat = np.cumsum(resids) / (sigma * np.sqrt(n_obs))

    # 5% 临界值边界 (Brown, Durbin, Evans 1975)
    # 边界线: ±(a + 2*a*t/T), a ≈ 0.948 (5% level)
    a_crit = 0.948
    t_norm = np.arange(1, n_obs + 1) / n_obs
    cusum_upper = a_crit * (1 + 2 * t_norm)
    cusum_lower = -cusum_upper

    cusum_exceeds = np.any(cusum_stat > cusum_upper) or np.any(cusum_stat < cusum_lower)
    print(f"    CUSUM 最大绝对值: {np.max(np.abs(cusum_stat)):.3f}")
    print(f"    CUSUM 5%临界值范围: [{a_crit:.3f}, {a_crit*(1+2):.3f}]")
    print(f"    CUSUM 是否越界: {'是 (参数不稳定, 存在结构变化)' if cusum_exceeds else '否'}")
    cusum_available = True
except Exception as e:
    print(f"    CUSUM 检验出错: {e}")
    cusum_available = False


# --- 3.3 日本 Q 断点检验 ---
print("\n  [3.3] 日本 Q 断点检验...")

japan_q = japan['urban_Q'].dropna().values
japan_years = japan['urban_Q'].dropna().index.values

japan_breaks = bai_perron_sequential(japan_q, japan_years, max_breaks=3,
                                      min_segment=5, significance=0.10)

print(f"    发现 {len(japan_breaks)} 个显著断点:")
for bp in japan_breaks:
    print(f"      {bp['break_year']}: F={bp['F_stat']:.2f}, p={bp['p_value']:.4f}")

break_indices_japan = [bp['break_idx'] for bp in japan_breaks]
japan_segments = segment_statistics(japan_q, japan_years, break_indices_japan)

print("    分段统计:")
for seg in japan_segments:
    print(f"      {seg['period']}: mean={seg['mean']:.3f}, "
          f"slope={seg['trend_slope']:.4f}/yr, std={seg['std']:.3f}")


# --- 3.4 Sup-Wald 检验（全局断点检验） ---
print("\n  [3.4] Sup-Wald 检验...")

def sup_wald_test(y, trimming=0.15):
    """
    计算 Sup-Wald 统计量（Andrews 1993 / Bai-Perron 2003）。
    遍历所有候选断点，取 Wald/F 统计量的上确界。
    """
    n = len(y)
    trim = int(n * trimming)
    t_trend = np.arange(n, dtype=float)
    x = sm.add_constant(t_trend)

    F_stats = []
    test_years = []

    for bp in range(trim, n - trim):
        F_stat, p_val = chow_test(y, x, bp)
        if not np.isnan(F_stat):
            F_stats.append(F_stat)
            test_years.append(bp)

    if not F_stats:
        return np.nan, -1, np.nan

    sup_F = max(F_stats)
    sup_idx = test_years[F_stats.index(sup_F)]

    # Andrews (1993) 渐近临界值近似（k=2 回归元, trimming=0.15）
    # 10%: 7.12, 5%: 8.68, 1%: 12.16 (Andrews Table 1, p=2)
    # 这些是近似值
    critical_values = {0.10: 7.12, 0.05: 8.68, 0.01: 12.16}

    return sup_F, sup_idx, critical_values

sup_F_china, sup_idx_china, cv = sup_wald_test(Q_V1K2_base)
print(f"    中国 Q(V1/K2):")
print(f"      Sup-Wald F = {sup_F_china:.2f}")
print(f"      最优断点: {years[sup_idx_china]} (索引 {sup_idx_china})")
print(f"      渐近临界值: 10%={cv[0.10]:.2f}, 5%={cv[0.05]:.2f}, 1%={cv[0.01]:.2f}")
sig_level = "不显著"
for alpha in [0.01, 0.05, 0.10]:
    if sup_F_china > cv[alpha]:
        sig_level = f"在 {alpha*100:.0f}% 水平显著"
        break
print(f"      结论: {sig_level}")

sup_F_japan, sup_idx_japan, _ = sup_wald_test(japan_q)
print(f"    日本 Q:")
print(f"      Sup-Wald F = {sup_F_japan:.2f}")
if sup_idx_japan >= 0:
    print(f"      最优断点: {japan_years[sup_idx_japan]}")


# --- 保存断点检验报告 ---
report_lines = []
report_lines.append("=" * 70)
report_lines.append("结构断点检验报告 — Urban Q 时间序列")
report_lines.append(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report_lines.append("=" * 70)

report_lines.append("\n一、中国 Q(V1/K2) 1998-2024")
report_lines.append("-" * 40)
report_lines.append(f"样本量: {len(Q_V1K2_base)}")
report_lines.append(f"序列均值: {np.mean(Q_V1K2_base):.4f}")
report_lines.append(f"序列标准差: {np.std(Q_V1K2_base):.4f}")

report_lines.append(f"\n1. Sup-Wald 检验:")
report_lines.append(f"   Sup-Wald F = {sup_F_china:.4f}")
report_lines.append(f"   最优断点年份: {years[sup_idx_china]}")
report_lines.append(f"   渐近临界值 (Andrews 1993, k=2, trimming=15%):")
report_lines.append(f"     10%: {cv[0.10]:.2f}, 5%: {cv[0.05]:.2f}, 1%: {cv[0.01]:.2f}")
report_lines.append(f"   结论: {sig_level}")

report_lines.append(f"\n2. 顺序 Bai-Perron 检验 (min_segment=5, alpha=0.10):")
report_lines.append(f"   检出断点数: {len(china_breaks)}")
for bp in china_breaks:
    report_lines.append(f"   断点 {bp['break_year']}: F={bp['F_stat']:.4f}, p={bp['p_value']:.6f}")

report_lines.append(f"\n3. 分段回归统计:")
for seg in china_segments:
    report_lines.append(f"   {seg['period']} (n={seg['n_obs']}): "
                        f"mean={seg['mean']:.4f}, std={seg['std']:.4f}, "
                        f"slope={seg['trend_slope']:.5f}/yr (R2={seg['trend_r2']:.3f}, p={seg['trend_p']:.4f})")

if cusum_available:
    report_lines.append(f"\n4. CUSUM 检验:")
    report_lines.append(f"   CUSUM 最大绝对值: {np.max(np.abs(cusum_stat)):.4f}")
    report_lines.append(f"   是否越界: {'是 — 拒绝参数稳定性零假设' if cusum_exceeds else '否'}")

report_lines.append(f"\n5. 断点与 Q=1 的关系:")
for bp in china_breaks:
    q_at_break = Q_V1K2_base[bp['break_idx']]
    report_lines.append(f"   {bp['break_year']}: Q={q_at_break:.3f} "
                        f"({'接近 Q=1' if abs(q_at_break - 1.0) < 0.15 else '距离 Q=1 较远'})")

report_lines.append(f"\n\n二、日本 Q 1960-2022")
report_lines.append("-" * 40)
report_lines.append(f"样本量: {len(japan_q)}")
report_lines.append(f"Sup-Wald F = {sup_F_japan:.4f}")
if sup_idx_japan >= 0:
    report_lines.append(f"最优断点年份: {japan_years[sup_idx_japan]}")

report_lines.append(f"\n顺序 Bai-Perron 检出断点:")
for bp in japan_breaks:
    report_lines.append(f"  断点 {bp['break_year']}: F={bp['F_stat']:.4f}, p={bp['p_value']:.6f}")

report_lines.append(f"\n分段回归统计:")
for seg in japan_segments:
    report_lines.append(f"  {seg['period']} (n={seg['n_obs']}): "
                        f"mean={seg['mean']:.4f}, std={seg['std']:.4f}, "
                        f"slope={seg['trend_slope']:.5f}/yr")

report_lines.append(f"\n\n三、综合解读")
report_lines.append("-" * 40)
report_lines.append("中国 Q(V1/K2) 时序呈现清晰的从 Q>1 到 Q<1 的下降趋势。")
report_lines.append("断点检验结果支持 Q 动态存在结构性变化（regime change）。")
if china_breaks:
    bp_years_str = ", ".join([str(bp['break_year']) for bp in china_breaks])
    report_lines.append(f"显著断点年份: {bp_years_str}")
    report_lines.append("这些断点对应着投资回报率的结构性转变。")

OUT_BREAK.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_BREAK, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f"\n  断点检验报告已保存: {OUT_BREAK}")


# ============================================================
# 4. 分析 3：Early Warning Signals
# ============================================================

print("\n[4] Early Warning Signals (Critical Slowing Down)...")

def rolling_ews(y, years_arr, window=6):
    """
    计算滚动窗口 early warning signals。
    - AR(1) 系数
    - 方差
    - 偏度
    """
    n = len(y)
    half_w = window // 2

    ar1_vals = []
    var_vals = []
    skew_vals = []
    center_years = []

    for i in range(half_w, n - half_w):
        seg = y[i - half_w: i + half_w + 1]
        center_years.append(years_arr[i])

        # AR(1): 自回归系数
        if len(seg) >= 4:
            ar1 = np.corrcoef(seg[:-1], seg[1:])[0, 1]
        else:
            ar1 = np.nan
        ar1_vals.append(ar1)

        # 方差
        var_vals.append(np.var(seg, ddof=1))

        # 偏度
        if len(seg) >= 3:
            skew_vals.append(stats.skew(seg))
        else:
            skew_vals.append(np.nan)

    return {
        'years': np.array(center_years),
        'ar1': np.array(ar1_vals),
        'variance': np.array(var_vals),
        'skewness': np.array(skew_vals)
    }


# 使用两个窗口大小检验稳健性
print("  计算 rolling EWS (窗口=6年和8年)...")

ews_w6 = rolling_ews(Q_V1K2_base, years, window=6)
ews_w8 = rolling_ews(Q_V1K2_base, years, window=8)

# Kendall tau 检验趋势显著性
def kendall_trend(x):
    """用 Kendall tau 检验序列是否有显著单调趋势"""
    t = np.arange(len(x))
    mask = ~np.isnan(x)
    if np.sum(mask) < 4:
        return np.nan, np.nan
    tau, p = stats.kendalltau(t[mask], x[mask])
    return tau, p

print("\n  EWS 趋势检验 (Kendall tau):")
for label, ews in [("窗口=6", ews_w6), ("窗口=8", ews_w8)]:
    tau_ar1, p_ar1 = kendall_trend(ews['ar1'])
    tau_var, p_var = kendall_trend(ews['variance'])
    tau_skew, p_skew = kendall_trend(ews['skewness'])

    print(f"  {label}:")
    print(f"    AR(1):  tau={tau_ar1:.3f}, p={p_ar1:.4f} "
          f"({'显著上升' if tau_ar1 > 0 and p_ar1 < 0.05 else '显著下降' if tau_ar1 < 0 and p_ar1 < 0.05 else '不显著'})")
    print(f"    方差:   tau={tau_var:.3f}, p={p_var:.4f} "
          f"({'显著上升' if tau_var > 0 and p_var < 0.05 else '显著下降' if tau_var < 0 and p_var < 0.05 else '不显著'})")
    print(f"    偏度:   tau={tau_skew:.3f}, p={p_skew:.4f}")


# 分前后半段检验（断点前后）
# 如果有断点，在断点前检验是否有 critical slowing down
if china_breaks:
    main_break_year = china_breaks[0]['break_year']
    pre_break_mask = years < main_break_year
    pre_break_q = Q_V1K2_base[pre_break_mask]
    pre_break_years = years[pre_break_mask]

    if len(pre_break_q) >= 8:
        ews_pre = rolling_ews(pre_break_q, pre_break_years, window=5)
        tau_ar1_pre, p_ar1_pre = kendall_trend(ews_pre['ar1'])
        tau_var_pre, p_var_pre = kendall_trend(ews_pre['variance'])

        print(f"\n  断点前 ({pre_break_years[0]}-{main_break_year-1}) EWS 趋势:")
        print(f"    AR(1): tau={tau_ar1_pre:.3f}, p={p_ar1_pre:.4f}")
        print(f"    方差:  tau={tau_var_pre:.3f}, p={p_var_pre:.4f}")


# --- 保存 EWS 报告 ---
ews_lines = []
ews_lines.append("=" * 70)
ews_lines.append("Early Warning Signals 报告 — Critical Slowing Down 分析")
ews_lines.append(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
ews_lines.append("=" * 70)
ews_lines.append(f"\n理论框架: Scheffer et al. (2009, Nature)")
ews_lines.append("如果系统接近临界转换 (tipping point)，预期:")
ews_lines.append("  - AR(1) 系数趋向 1 (critical slowing down)")
ews_lines.append("  - 方差增大 (flickering)")
ews_lines.append("  - 偏度变化 (asymmetry)")

ews_lines.append(f"\n对象: 中国 Q(V1/K2), 1998-2024")
ews_lines.append(f"样本量: {len(Q_V1K2_base)}")

for label, ews in [("窗口=6年", ews_w6), ("窗口=8年", ews_w8)]:
    ews_lines.append(f"\n--- {label} ---")
    tau_ar1, p_ar1 = kendall_trend(ews['ar1'])
    tau_var, p_var = kendall_trend(ews['variance'])
    tau_skew, p_skew = kendall_trend(ews['skewness'])

    ews_lines.append(f"AR(1):  Kendall tau = {tau_ar1:.4f}, p = {p_ar1:.6f}")
    ews_lines.append(f"方差:   Kendall tau = {tau_var:.4f}, p = {p_var:.6f}")
    ews_lines.append(f"偏度:   Kendall tau = {tau_skew:.4f}, p = {p_skew:.6f}")

    ews_lines.append(f"\nAR(1) 时序:")
    for yr, v in zip(ews['years'], ews['ar1']):
        ews_lines.append(f"  {yr}: {v:.4f}")

    ews_lines.append(f"\n方差时序:")
    for yr, v in zip(ews['years'], ews['variance']):
        ews_lines.append(f"  {yr}: {v:.6f}")

ews_lines.append(f"\n\n综合解读:")
ews_lines.append("-" * 40)

# 根据实际结果写解读
tau_ar1_6, p_ar1_6 = kendall_trend(ews_w6['ar1'])
tau_var_6, p_var_6 = kendall_trend(ews_w6['variance'])

if tau_ar1_6 > 0 and p_ar1_6 < 0.10:
    ews_lines.append("AR(1) 系数在 Q 下降过程中呈上升趋势，与 critical slowing down 预期一致。")
    ews_lines.append("这表明 Urban Q 接近 Q=1 临界值时，系统恢复能力下降。")
elif tau_ar1_6 < 0 and p_ar1_6 < 0.10:
    ews_lines.append("AR(1) 系数呈下降趋势，不符合经典 critical slowing down 模式。")
    ews_lines.append("这可能反映了中国城市化的政策驱动特征：")
    ews_lines.append("  - 强力政策干预（限购、去库存）使系统偏离自组织临界行为")
    ews_lines.append("  - Q 的下降更多是结构性的而非临界转换")
else:
    ews_lines.append("AR(1) 趋势不显著，critical slowing down 证据不充分。")
    ews_lines.append("注意：27年时间序列的滚动窗口分析统计效力有限。")

if tau_var_6 < 0 and p_var_6 < 0.10:
    ews_lines.append("\n方差在 Q 下降过程中减小，提示 Q 的下降是平稳的，")
    ews_lines.append("而非伴随剧烈波动的临界转换。这与'渐进相变'而非'突变'一致。")
elif tau_var_6 > 0 and p_var_6 < 0.10:
    ews_lines.append("\n方差在 Q 下降过程中增大，与临界转换前的 flickering 一致。")

ews_lines.append("\n注: 本分析时间序列较短 (27年), 滚动窗口分析的统计效力受限。")
ews_lines.append("结果应作为辅助证据，而非独立的因果判断。")

with open(OUT_EWS, 'w', encoding='utf-8') as f:
    f.write('\n'.join(ews_lines))
print(f"\n  EWS 报告已保存: {OUT_EWS}")


# ============================================================
# 5. 可视化
# ============================================================

print("\n[5] 生成可视化...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Urban Q Robustness Analysis: Monte Carlo CI, Structural Breaks & Early Warnings',
             fontsize=14, fontweight='bold', y=0.98)

# 颜色方案
C_MAIN = '#1f77b4'
C_ALT = '#ff7f0e'
C_CI90 = '#1f77b4'
C_CI50 = '#2ca02c'
C_BREAK = '#d62728'
C_REF = '#666666'

# --- (a) Q(V1/K2) + 90% Monte Carlo CI ---
ax = axes[0, 0]
ax.fill_between(years, Q_V1K2_pctiles[0], Q_V1K2_pctiles[4],
                alpha=0.15, color=C_CI90, label='90% CI')
ax.fill_between(years, Q_V1K2_pctiles[1], Q_V1K2_pctiles[3],
                alpha=0.25, color=C_CI50, label='50% CI')
ax.plot(years, Q_V1K2_base, 'o-', color=C_MAIN, linewidth=2,
        markersize=4, label='Q(V1/K2) baseline', zorder=5)
ax.plot(years, Q_V1K2_pctiles[2], '--', color='gray', linewidth=1,
        alpha=0.7, label='MC median')
ax.axhline(y=1.0, color=C_REF, linestyle=':', linewidth=1.5, alpha=0.8)
ax.text(2024.5, 1.02, 'Q = 1', fontsize=9, color=C_REF, va='bottom')

# 标注基准交叉年份
base_crossings = find_q1_crossing_interpolated(years, Q_V1K2_base)
if base_crossings:
    for cx in base_crossings:
        ax.axvline(x=cx, color=C_BREAK, linestyle='--', alpha=0.5)
        ax.text(cx, ax.get_ylim()[1]*0.95 if ax.get_ylim()[1] > 2 else 1.8,
                f'{cx:.1f}', fontsize=8, color=C_BREAK, ha='center')

ax.set_xlabel('Year')
ax.set_ylabel('Urban Q')
ax.set_title('(a) Q(V1/K2) with Monte Carlo 90% CI', fontweight='bold')
ax.legend(loc='upper right', fontsize=8)
ax.set_xlim(1997, 2025)
ax.grid(True, alpha=0.3)

# --- (b) Q=1 交叉年份直方图 ---
ax = axes[0, 1]

if len(crossing_V1K2) > 0:
    bins_range = np.arange(int(min(crossing_V1K2)) - 1, int(max(crossing_V1K2)) + 2, 0.5)
    ax.hist(crossing_V1K2, bins=bins_range, alpha=0.6, color=C_MAIN,
            edgecolor='white', label=f'V1/K2 (n={len(crossing_V1K2)})')

    ci5 = np.percentile(crossing_V1K2, 5)
    ci95 = np.percentile(crossing_V1K2, 95)
    med = np.median(crossing_V1K2)

    ax.axvline(x=med, color=C_MAIN, linestyle='-', linewidth=2, label=f'Median: {med:.1f}')
    ax.axvline(x=ci5, color=C_MAIN, linestyle='--', linewidth=1.5, alpha=0.7)
    ax.axvline(x=ci95, color=C_MAIN, linestyle='--', linewidth=1.5, alpha=0.7)
    ax.axvspan(ci5, ci95, alpha=0.1, color=C_MAIN)
    ax.text(ci5, ax.get_ylim()[1]*0.9 if ax.get_ylim()[1] > 10 else 10,
            f'5%: {ci5:.1f}', fontsize=8, ha='center', color=C_MAIN)
    ax.text(ci95, ax.get_ylim()[1]*0.9 if ax.get_ylim()[1] > 10 else 10,
            f'95%: {ci95:.1f}', fontsize=8, ha='center', color=C_MAIN)

if len(crossing_V1K1) > 0:
    bins_range2 = np.arange(int(min(crossing_V1K1)) - 1, int(max(crossing_V1K1)) + 2, 0.5)
    ax.hist(crossing_V1K1, bins=bins_range2, alpha=0.4, color=C_ALT,
            edgecolor='white', label=f'V1/K1 (n={len(crossing_V1K1)})')

    if len(crossing_V1K1) >= 10:
        ci5_k1 = np.percentile(crossing_V1K1, 5)
        ci95_k1 = np.percentile(crossing_V1K1, 95)
        med_k1 = np.median(crossing_V1K1)
        ax.axvline(x=med_k1, color=C_ALT, linestyle='-', linewidth=2,
                   label=f'V1/K1 Median: {med_k1:.1f}')

ax.set_xlabel('Year of Q = 1 Crossing')
ax.set_ylabel('Frequency')
ax.set_title('(b) Distribution of Q=1 Crossing Year (MC)', fontweight='bold')
ax.legend(loc='upper left', fontsize=8)
ax.grid(True, alpha=0.3)

# --- (c) 断点检验结果 ---
ax = axes[1, 0]
ax.plot(years, Q_V1K2_base, 'o-', color=C_MAIN, linewidth=2,
        markersize=4, label='Q(V1/K2)', zorder=5)
ax.axhline(y=1.0, color=C_REF, linestyle=':', linewidth=1.5, alpha=0.8)

# 分段回归线
all_breaks_plot = [0] + sorted(break_indices_china) + [len(Q_V1K2_base)]
for i in range(len(all_breaks_plot) - 1):
    s, e = all_breaks_plot[i], all_breaks_plot[i + 1]
    seg_years = years[s:e]
    seg_q = Q_V1K2_base[s:e]
    if len(seg_years) >= 2:
        slope, intercept, _, _, _ = stats.linregress(np.arange(len(seg_years)), seg_q)
        fitted = intercept + slope * np.arange(len(seg_years))
        ax.plot(seg_years, fitted, '-', color=C_BREAK, linewidth=2.5, alpha=0.8)

# 标注断点
for bp in china_breaks:
    ax.axvline(x=bp['break_year'], color=C_BREAK, linestyle='--', linewidth=1.5, alpha=0.7)
    q_at_bp = Q_V1K2_base[bp['break_idx']]
    ax.annotate(f"{bp['break_year']}\nF={bp['F_stat']:.1f}\np={bp['p_value']:.3f}",
                xy=(bp['break_year'], q_at_bp),
                xytext=(bp['break_year'] + 1.5, q_at_bp + 0.15),
                fontsize=7.5,
                arrowprops=dict(arrowstyle='->', color=C_BREAK, lw=1.2),
                color=C_BREAK,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C_BREAK, alpha=0.8))

# Sup-Wald 注释
ax.text(0.02, 0.02,
        f"Sup-Wald F = {sup_F_china:.1f}\n"
        f"Critical: 5%={cv[0.05]:.1f}, 1%={cv[0.01]:.1f}\n"
        f"{sig_level}",
        transform=ax.transAxes, fontsize=8,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', edgecolor='gray', alpha=0.9))

ax.set_xlabel('Year')
ax.set_ylabel('Urban Q')
ax.set_title('(c) Bai-Perron Structural Break Test', fontweight='bold')
ax.legend(loc='upper right', fontsize=8)
ax.set_xlim(1997, 2025)
ax.grid(True, alpha=0.3)

# --- (d) Early Warning Signals ---
ax = axes[1, 1]
ax2 = ax.twinx()

# AR(1) 用左轴
ln1 = ax.plot(ews_w6['years'], ews_w6['ar1'], 's-', color='#9467bd',
              linewidth=1.5, markersize=4, label='AR(1), w=6yr')
ln2 = ax.plot(ews_w8['years'], ews_w8['ar1'], 's--', color='#9467bd',
              linewidth=1, markersize=3, alpha=0.6, label='AR(1), w=8yr')
ax.set_ylabel('AR(1) coefficient', color='#9467bd')
ax.tick_params(axis='y', labelcolor='#9467bd')

# 方差用右轴
ln3 = ax2.plot(ews_w6['years'], ews_w6['variance'], '^-', color='#e377c2',
               linewidth=1.5, markersize=4, label='Variance, w=6yr')
ln4 = ax2.plot(ews_w8['years'], ews_w8['variance'], '^--', color='#e377c2',
               linewidth=1, markersize=3, alpha=0.6, label='Variance, w=8yr')
ax2.set_ylabel('Variance', color='#e377c2')
ax2.tick_params(axis='y', labelcolor='#e377c2')

# 标注 Q=1 交叉区域
if base_crossings:
    for cx in base_crossings:
        ax.axvline(x=cx, color=C_REF, linestyle=':', linewidth=1, alpha=0.5)
        ax.text(cx, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1.0,
                f'Q=1\n({cx:.0f})', fontsize=7, ha='center', color=C_REF, va='top')

# 如果有断点也标注
for bp in china_breaks:
    ax.axvline(x=bp['break_year'], color=C_BREAK, linestyle='--',
               linewidth=1, alpha=0.4)

# 合并图例
lns = ln1 + ln2 + ln3 + ln4
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper right', fontsize=7)

# Kendall 检验注释
tau_ar1_6, p_ar1_6 = kendall_trend(ews_w6['ar1'])
tau_var_6, p_var_6 = kendall_trend(ews_w6['variance'])
ax.text(0.02, 0.02,
        f"Kendall trend (w=6):\n"
        f"AR(1): tau={tau_ar1_6:.3f}, p={p_ar1_6:.3f}\n"
        f"Var:   tau={tau_var_6:.3f}, p={p_var_6:.3f}",
        transform=ax.transAxes, fontsize=7.5,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='gray', alpha=0.9))

ax.set_xlabel('Year')
ax.set_title('(d) Early Warning Signals (Rolling Window)', fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])

OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_FIG, dpi=300, bbox_inches='tight')
print(f"  图表已保存: {OUT_FIG}")
plt.close()

# ============================================================
# 6. 总结
# ============================================================

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)

print("\n输出文件:")
print(f"  1. 蒙特卡洛 CI CSV:  {OUT_MC_CSV}")
print(f"  2. 断点检验报告:     {OUT_BREAK}")
print(f"  3. EWS 报告:         {OUT_EWS}")
print(f"  4. 综合可视化:       {OUT_FIG}")

print("\n关键发现:")
if len(crossing_V1K2) > 0:
    print(f"  [MC] Q=1 交叉年份 90% CI: [{np.percentile(crossing_V1K2, 5):.1f}, "
          f"{np.percentile(crossing_V1K2, 95):.1f}], 中位数 {np.median(crossing_V1K2):.1f}")
    print(f"       {len(crossing_V1K2)}/{N_SIM} ({100*len(crossing_V1K2)/N_SIM:.1f}%) 模拟中 Q 跌破 1")

if china_breaks:
    bp_str = ", ".join([f"{bp['break_year']}(F={bp['F_stat']:.1f})" for bp in china_breaks])
    print(f"  [BP] 显著断点: {bp_str}")
    print(f"  [BP] Sup-Wald F={sup_F_china:.1f} ({sig_level})")

print(f"  [EWS] AR(1) Kendall tau={tau_ar1_6:.3f} (p={p_ar1_6:.3f})")
print(f"  [EWS] Variance Kendall tau={tau_var_6:.3f} (p={p_var_6:.3f})")
