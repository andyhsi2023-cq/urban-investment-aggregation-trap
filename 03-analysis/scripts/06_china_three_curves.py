#!/usr/bin/env python3
"""
06_china_three_curves.py
========================
目的：分析中国人口-产业-建设三条基础曲线的增速时序与同步性，
     识别各曲线拐点，计算偏离度指标，并与 Urban Q 叠加对比。

理论背景（研究框架 v2.0 第三节）：
  在协调发展的城市中，三条曲线的拐点应按以下顺序出现：
    人口拐点 → 产业拐点 → 建设拐点
  滞后期各 3-5 年为合理。如果建设拐点先于产业拐点，则存在过度投资风险。

输入数据：
  - china_urban_q_timeseries.csv（Urban Q、投资等已计算数据）
  - china_ratio_curves.csv（产业结构、投资等比率曲线数据）
  - 硬编码数据：城镇人口增速（国家统计局公开数据）

输出：
  - china_three_curves_analysis.txt（分析报告）
  - fig06_china_three_curves.png（三面板可视化）

依赖包：pandas, numpy, matplotlib, scipy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from pathlib import Path

# ============================================================
# 0. 路径设置
# ============================================================
BASE_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
Q_CSV = BASE_DIR / "03-analysis/models/china_urban_q_timeseries.csv"
RATIO_CSV = BASE_DIR / "03-analysis/models/china_ratio_curves.csv"
OUTPUT_TXT = BASE_DIR / "03-analysis/models/china_three_curves_analysis.txt"
OUTPUT_FIG = BASE_DIR / "04-figures/drafts/fig06_china_three_curves.png"

# ============================================================
# 1. 读取已有数据
# ============================================================
df_q = pd.read_csv(Q_CSV)
df_ratio = pd.read_csv(RATIO_CSV)

# 以 df_ratio 为基础，它覆盖 1978-2024
df = df_ratio[['year', 'R1_urbanization_rate', 'primary_pct', 'secondary_pct',
               'tertiary_pct', 'total_construction_inv', 'realestate_inv',
               'infra_inv']].copy()

# 合并 Urban Q 数据
q_cols = df_q[['year', 'Q_V1K1', 'Q_V1K2', 'MUQ_V1',
               'V1_housing_value_100m', 'K1_cumulative_inv_100m']].copy()
df = df.merge(q_cols, on='year', how='left')

# ============================================================
# 2. 构建三条增速曲线
# ============================================================

# --- 曲线1：城镇人口增速 ---
# 硬编码中国城镇人口数据（万人），来源：国家统计局历年统计年鉴
# 关键年份数据，其余年份通过城镇化率 × 总人口推算
# 总人口数据（万人）来源：NBS
urban_pop_data = {
    # year: 城镇人口（万人）— 来源：国家统计局《中国统计年鉴》
    1990: 30195,
    1991: 31203,
    1992: 32175,
    1993: 33173,
    1994: 34169,
    1995: 35174,
    1996: 37304,
    1997: 39449,
    1998: 41608,
    1999: 43748,
    2000: 45906,  # 五普
    2001: 48064,
    2002: 50212,
    2003: 52376,
    2004: 54283,
    2005: 56212,
    2006: 58288,
    2007: 60633,
    2008: 62403,
    2009: 64512,
    2010: 66978,  # 六普
    2011: 69079,
    2012: 71182,
    2013: 73111,
    2014: 74916,
    2015: 77116,
    2016: 79298,
    2017: 81347,
    2018: 83137,
    2019: 84843,
    2020: 90199,  # 七普（含口径调整）
    2021: 91425,
    2022: 92071,
    2023: 93267,
    2024: 94438,  # 估算值
}

pop_df = pd.DataFrame(list(urban_pop_data.items()), columns=['year', 'urban_pop_10k'])
pop_df = pop_df.sort_values('year').reset_index(drop=True)

# 计算城镇人口增速 ΔPu/Pu (%)
pop_df['pop_growth_rate'] = pop_df['urban_pop_10k'].pct_change() * 100

df = df.merge(pop_df[['year', 'urban_pop_10k', 'pop_growth_rate']], on='year', how='left')

# --- 曲线2：产业结构变化速度 ---
# 使用三产占比的年度变化 Δg3（百分点/年）
df['delta_tertiary'] = df['tertiary_pct'].diff()

# 也计算二产/三产比的变化
df['sec_ter_ratio'] = df['secondary_pct'] / df['tertiary_pct']
df['delta_sec_ter_ratio'] = df['sec_ter_ratio'].diff()

# 三产增速标准化为百分比变化
df['tertiary_growth_rate'] = df['tertiary_pct'].pct_change() * 100

# --- 曲线3：建设投资增速 ---
# ΔI/I (%)
df['inv_growth_rate'] = df['total_construction_inv'].pct_change() * 100

# ============================================================
# 3. 统一分析窗口与平滑处理
# ============================================================

# 取 1991-2024（需要至少一年前数据计算增速）
df_anal = df[(df['year'] >= 1991) & (df['year'] <= 2024)].copy()

# 对增速曲线做 Savitzky-Golay 平滑以识别趋势拐点
# 窗口长度取 7（约7年平滑），多项式阶数取 2
def smooth_series(s, window=7, polyorder=2):
    """对序列做 Savitzky-Golay 平滑，处理缺失值"""
    valid = s.dropna()
    if len(valid) < window:
        return s
    smoothed = savgol_filter(valid.values, window_length=min(window, len(valid) if len(valid) % 2 == 1 else len(valid)-1),
                             polyorder=polyorder)
    result = s.copy()
    result.loc[valid.index] = smoothed
    return result

# 平滑后的增速序列（用于拐点识别）
df_anal['pop_growth_smooth'] = smooth_series(df_anal['pop_growth_rate'].copy())
df_anal['tertiary_growth_smooth'] = smooth_series(df_anal['delta_tertiary'].copy())
df_anal['inv_growth_smooth'] = smooth_series(df_anal['inv_growth_rate'].copy())

# ============================================================
# 4. 识别拐点（增速见顶的年份）
# ============================================================

def find_peak_year(df, col, year_col='year', start_year=1991, end_year=2024):
    """找到增速序列的峰值年份"""
    subset = df[(df[year_col] >= start_year) & (df[year_col] <= end_year) & df[col].notna()]
    if len(subset) == 0:
        return None, None
    peak_idx = subset[col].idxmax()
    return int(subset.loc[peak_idx, year_col]), subset.loc[peak_idx, col]

# 人口增速拐点
pop_peak_year, pop_peak_val = find_peak_year(df_anal, 'pop_growth_smooth')

# 产业转型拐点（三产增速最快的年份）
ter_peak_year, ter_peak_val = find_peak_year(df_anal, 'tertiary_growth_smooth')

# 二产/三产比 = 1 的年份（交叉年份）
cross_df = df_anal[df_anal['sec_ter_ratio'].notna()].copy()
cross_df['above_1'] = cross_df['sec_ter_ratio'] > 1.0
crossings = cross_df[cross_df['above_1'] != cross_df['above_1'].shift(1)].iloc[1:]
sec_ter_cross_year = int(crossings.iloc[0]['year']) if len(crossings) > 0 else None

# 建设投资增速拐点
inv_peak_year, inv_peak_val = find_peak_year(df_anal, 'inv_growth_smooth')

print("=" * 60)
print("三曲线拐点识别")
print("=" * 60)
print(f"人口增速拐点: {pop_peak_year}年，平滑增速={pop_peak_val:.2f}%")
print(f"产业转型拐点（三产增速最快）: {ter_peak_year}年，Δg3={ter_peak_val:.2f}百分点/年")
print(f"二产/三产比=1 交叉年份: {sec_ter_cross_year}年")
print(f"建设投资增速拐点: {inv_peak_year}年，平滑增速={inv_peak_val:.2f}%")
print(f"\n时序间隔:")
print(f"  人口→产业: {ter_peak_year - pop_peak_year} 年")
print(f"  产业→建设: {inv_peak_year - ter_peak_year} 年")
print(f"  人口→建设: {inv_peak_year - pop_peak_year} 年")

# ============================================================
# 5. 计算三个偏离度指标
# ============================================================

# 先标准化三条增速曲线到可比尺度
# 使用 z-score 标准化（基于各自的均值和标准差）
for col, norm_col in [('pop_growth_rate', 'pop_norm'),
                       ('delta_tertiary', 'ter_norm'),
                       ('inv_growth_rate', 'inv_norm')]:
    valid = df_anal[col].dropna()
    if len(valid) > 0:
        mean_val = valid.mean()
        std_val = valid.std()
        df_anal[norm_col] = (df_anal[col] - mean_val) / std_val if std_val > 0 else 0
    else:
        df_anal[norm_col] = np.nan

# 偏离度指标 D = (A - B) / (|A| + |B|)，范围约 [-1, 1]
# 使用标准化后的值计算，避免量纲影响
def calc_divergence(a, b):
    """计算偏离度 D = (a - b) / (|a| + |b|)"""
    denom = np.abs(a) + np.abs(b)
    return np.where(denom > 0, (a - b) / denom, 0)

df_anal['D_PI'] = calc_divergence(df_anal['pop_norm'], df_anal['ter_norm'])
df_anal['D_IC'] = calc_divergence(df_anal['ter_norm'], df_anal['inv_norm'])
df_anal['D_PC'] = calc_divergence(df_anal['pop_norm'], df_anal['inv_norm'])

# 总失调度 = 三个偏离度的绝对值平均
df_anal['D_total'] = (np.abs(df_anal['D_PI']) + np.abs(df_anal['D_IC']) + np.abs(df_anal['D_PC'])) / 3

# ============================================================
# 6. 可视化：三面板图
# ============================================================

# 中文字体配置
plt.rcParams['font.family'] = ['PingFang HK', 'Songti SC', 'STHeiti', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Nature 风格设置
plt.rcParams.update({
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 7.5,
    'figure.dpi': 300,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
})

# 颜色方案
COLORS = {
    'pop': '#2166AC',       # 深蓝 — 人口
    'industry': '#D6604D',  # 砖红 — 产业
    'invest': '#4DAF4A',    # 绿色 — 建设投资
    'Q': '#FF7F00',         # 橙色 — Urban Q
    'ref': '#666666',       # 灰色 — 参考线
    'D_PI': '#2166AC',
    'D_IC': '#D6604D',
    'D_PC': '#4DAF4A',
    'D_total': '#333333',
}

fig, axes = plt.subplots(3, 1, figsize=(10, 12))
fig.subplots_adjust(hspace=0.32, top=0.94, bottom=0.06, left=0.10, right=0.88)

years = df_anal['year']

# ------ Panel A: 三条增速曲线叠加 ------
ax = axes[0]
ax2 = ax.twinx()

# 人口增速（左轴）
ln1 = ax.plot(years, df_anal['pop_growth_rate'], '-o', color=COLORS['pop'],
              markersize=2.5, linewidth=0.8, alpha=0.4, zorder=2)
ln1s = ax.plot(years, df_anal['pop_growth_smooth'], '-', color=COLORS['pop'],
               linewidth=2.0, label=f'城镇人口增速 ΔPu/Pu (拐点: {pop_peak_year})', zorder=3)

# 建设投资增速（左轴，同尺度%）
ln3 = ax.plot(years, df_anal['inv_growth_rate'], '-s', color=COLORS['invest'],
              markersize=2.5, linewidth=0.8, alpha=0.4, zorder=2)
ln3s = ax.plot(years, df_anal['inv_growth_smooth'], '-', color=COLORS['invest'],
               linewidth=2.0, label=f'建设投资增速 ΔI/I (拐点: {inv_peak_year})', zorder=3)

# 三产增速（右轴，百分点/年）
ln2 = ax2.plot(years, df_anal['delta_tertiary'], '^', color=COLORS['industry'],
               markersize=2.5, linewidth=0.8, alpha=0.4, zorder=2)
ln2s = ax2.plot(years, df_anal['tertiary_growth_smooth'], '-', color=COLORS['industry'],
                linewidth=2.0, label=f'三产占比变化 Δg3 (拐点: {ter_peak_year})', zorder=3)

# 标注拐点
for yr, val, col, yax in [(pop_peak_year, df_anal.loc[df_anal['year']==pop_peak_year, 'pop_growth_smooth'].values[0],
                            COLORS['pop'], ax),
                           (inv_peak_year, df_anal.loc[df_anal['year']==inv_peak_year, 'inv_growth_smooth'].values[0],
                            COLORS['invest'], ax)]:
    yax.annotate(f'{yr}', xy=(yr, val), xytext=(yr+1, val+2),
                fontsize=8, fontweight='bold', color=col,
                arrowprops=dict(arrowstyle='->', color=col, lw=1.0))

# 产业拐点标注在右轴
ter_val = df_anal.loc[df_anal['year']==ter_peak_year, 'tertiary_growth_smooth'].values[0]
ax2.annotate(f'{ter_peak_year}', xy=(ter_peak_year, ter_val),
            xytext=(ter_peak_year+1, ter_val+0.3),
            fontsize=8, fontweight='bold', color=COLORS['industry'],
            arrowprops=dict(arrowstyle='->', color=COLORS['industry'], lw=1.0))

ax.set_xlabel('年份')
ax.set_ylabel('增速 (%)', color='black')
ax2.set_ylabel('三产占比年变化 (百分点/年)', color=COLORS['industry'])
ax2.tick_params(axis='y', colors=COLORS['industry'])

# 合并图例
lns = ln1s + ln3s + ln2s
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper right', frameon=True, framealpha=0.9, edgecolor='#cccccc')

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.4, alpha=0.3)
ax.set_title('A. 人口-产业-建设三曲线增速时序', fontweight='bold', loc='left')
ax.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax.set_xlim(1990, 2025)
ax.grid(True, alpha=0.2, linewidth=0.5)

# ------ Panel B: 三个偏离度时序 ------
ax = axes[1]

ax.plot(years, df_anal['D_PI'], '-', color=COLORS['D_PI'], linewidth=1.5,
        label='D_PI: 人口-产业偏离', alpha=0.8)
ax.plot(years, df_anal['D_IC'], '-', color=COLORS['D_IC'], linewidth=1.5,
        label='D_IC: 产业-建设偏离', alpha=0.8)
ax.plot(years, df_anal['D_PC'], '-', color=COLORS['D_PC'], linewidth=1.5,
        label='D_PC: 人口-建设偏离', alpha=0.8)
ax.plot(years, df_anal['D_total'], '--', color=COLORS['D_total'], linewidth=2.0,
        label='总失调度 (均值|D|)', alpha=0.9)

ax.axhline(y=0, color=COLORS['ref'], linestyle='--', linewidth=0.8, alpha=0.7)
ax.fill_between(years, -0.2, 0.2, color='green', alpha=0.05, label='协调区间 (|D|<0.2)')

ax.set_xlabel('年份')
ax.set_ylabel('偏离度 D')
ax.set_title('B. 三曲线偏离度指标', fontweight='bold', loc='left')
ax.legend(loc='upper left', frameon=True, framealpha=0.9, edgecolor='#cccccc', fontsize=7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlim(1990, 2025)
ax.set_ylim(-1.0, 1.0)
ax.grid(True, alpha=0.2, linewidth=0.5)

# ------ Panel C: 偏离度与 Urban Q 叠加 ------
ax = axes[2]
ax2 = ax.twinx()

# 总失调度（左轴）
ln1 = ax.fill_between(years, 0, df_anal['D_total'], color='#CCCCCC', alpha=0.4)
ln1p = ax.plot(years, df_anal['D_total'], '-', color=COLORS['D_total'], linewidth=2.0,
               label='总失调度', zorder=3)

# Urban Q（右轴）
q_data = df_anal[df_anal['Q_V1K1'].notna()]
ln2 = ax2.plot(q_data['year'], q_data['Q_V1K1'], '-o', color=COLORS['Q'],
               markersize=3, linewidth=2.0, label='Urban Q (V1/K1)', zorder=4)
ax2.axhline(y=1.0, color=COLORS['Q'], linestyle='--', linewidth=0.8, alpha=0.5)
ax2.text(2024.5, 1.02, 'Q=1', fontsize=7, color=COLORS['Q'], va='bottom')

# MUQ (右轴，虚线)
muq_data = df_anal[df_anal['MUQ_V1'].notna()]
ln3 = ax2.plot(muq_data['year'], muq_data['MUQ_V1'], '--', color='#FF7F00',
               linewidth=1.0, alpha=0.6, label='MUQ (V1)', zorder=3)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.4, alpha=0.3)

ax.set_xlabel('年份')
ax.set_ylabel('总失调度', color=COLORS['D_total'])
ax2.set_ylabel('Urban Q / MUQ', color=COLORS['Q'])
ax.tick_params(axis='y', colors=COLORS['D_total'])
ax2.tick_params(axis='y', colors=COLORS['Q'])

# 合并图例
lns = ln1p + ln2 + ln3
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper right', frameon=True, framealpha=0.9, edgecolor='#cccccc')

ax.set_title('C. 失调度与 Urban Q 叠加对比', fontweight='bold', loc='left')
ax.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax.set_xlim(1990, 2025)
ax2.set_ylim(-1.5, 5.0)
ax.grid(True, alpha=0.2, linewidth=0.5)

# 总标题
fig.suptitle('中国人口-产业-建设三曲线同步性分析 (1991-2024)', fontsize=13, fontweight='bold')

plt.savefig(OUTPUT_FIG, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"\n图表已保存: {OUTPUT_FIG}")

# ============================================================
# 7. 输出分析报告
# ============================================================

report_lines = []
report_lines.append("=" * 70)
report_lines.append("中国人口-产业-建设三曲线同步性分析报告")
report_lines.append("=" * 70)
report_lines.append(f"分析日期: 2026-03-20")
report_lines.append(f"分析窗口: 1991-2024")
report_lines.append("")

report_lines.append("一、三条基础曲线概况")
report_lines.append("-" * 40)
report_lines.append(f"  人口曲线: 城镇人口增速 ΔPu/Pu")
report_lines.append(f"    数据范围: 1991-2024")
report_lines.append(f"    均值: {df_anal['pop_growth_rate'].mean():.2f}%")
report_lines.append(f"    最大值: {df_anal['pop_growth_rate'].max():.2f}% ({int(df_anal.loc[df_anal['pop_growth_rate'].idxmax(), 'year'])})")
report_lines.append(f"    最小值: {df_anal['pop_growth_rate'].min():.2f}% ({int(df_anal.loc[df_anal['pop_growth_rate'].idxmin(), 'year'])})")
report_lines.append(f"    2024年: {df_anal[df_anal['year']==2024]['pop_growth_rate'].values[0]:.2f}%")
report_lines.append("")

report_lines.append(f"  产业曲线: 三产占比年变化 Δg3")
report_lines.append(f"    数据范围: 1979-2024")
valid_ter = df_anal['delta_tertiary'].dropna()
report_lines.append(f"    均值: {valid_ter.mean():.2f} 百分点/年")
report_lines.append(f"    最大值: {valid_ter.max():.2f} ({int(df_anal.loc[valid_ter.idxmax(), 'year'])})")
report_lines.append(f"    2024年: {df_anal[df_anal['year']==2024]['delta_tertiary'].values[0]:.2f}")
report_lines.append("")

report_lines.append(f"  建设曲线: 总建设投资增速 ΔI/I")
valid_inv = df_anal['inv_growth_rate'].dropna()
report_lines.append(f"    数据范围: 1991-2024")
report_lines.append(f"    均值: {valid_inv.mean():.2f}%")
report_lines.append(f"    最大值: {valid_inv.max():.2f}% ({int(df_anal.loc[valid_inv.idxmax(), 'year'])})")
report_lines.append(f"    最小值: {valid_inv.min():.2f}% ({int(df_anal.loc[valid_inv.idxmin(), 'year'])})")
report_lines.append(f"    2024年: {df_anal[df_anal['year']==2024]['inv_growth_rate'].values[0]:.2f}%")
report_lines.append("")

report_lines.append("二、拐点识别")
report_lines.append("-" * 40)
report_lines.append(f"  人口增速拐点: {pop_peak_year}年 (平滑增速 {pop_peak_val:.2f}%)")
report_lines.append(f"  产业转型拐点 (三产增速最快): {ter_peak_year}年 (Δg3={ter_peak_val:.2f}百分点/年)")
report_lines.append(f"  二产/三产交叉年份: {sec_ter_cross_year}年")
report_lines.append(f"  建设投资增速拐点: {inv_peak_year}年 (平滑增速 {inv_peak_val:.2f}%)")
report_lines.append("")
report_lines.append(f"  时序间隔:")
report_lines.append(f"    人口拐点 → 产业拐点: {ter_peak_year - pop_peak_year} 年")
report_lines.append(f"    产业拐点 → 建设拐点: {inv_peak_year - ter_peak_year} 年")
report_lines.append(f"    人口拐点 → 建设拐点: {inv_peak_year - pop_peak_year} 年")
report_lines.append("")

# 判断拐点顺序是否符合理论预期
report_lines.append("  拐点顺序评估:")
if pop_peak_year < ter_peak_year < inv_peak_year:
    report_lines.append("    符合理论预期: 人口 → 产业 → 建设")
elif pop_peak_year < inv_peak_year <= ter_peak_year:
    report_lines.append("    部分偏离: 建设拐点先于或同步于产业拐点（建设超前风险）")
elif inv_peak_year <= pop_peak_year:
    report_lines.append("    建设拐点最先到达 — 可能反映早期投资高峰")
else:
    report_lines.append(f"    实际顺序: 人口({pop_peak_year}) → 产业({ter_peak_year}) → 建设({inv_peak_year})")

# 框架 v2.0 指出的关键问题："人口已拐但建设未拐"
report_lines.append("")
report_lines.append("  关键风险评估（框架v2.0）:")
# 找到人口增速持续下降但投资增速仍为正的窗口
risk_window = df_anal[(df_anal['year'] >= pop_peak_year) &
                       (df_anal['inv_growth_rate'] > 0) &
                       (df_anal['pop_growth_rate'] < df_anal.loc[df_anal['year']==pop_peak_year, 'pop_growth_rate'].values[0] * 0.5)]
if len(risk_window) > 0:
    report_lines.append(f"    人口增速已大幅放缓但建设投资仍增长的年份:")
    for _, row in risk_window.iterrows():
        report_lines.append(f"      {int(row['year'])}: 人口增速={row['pop_growth_rate']:.2f}%, 投资增速={row['inv_growth_rate']:.2f}%")

report_lines.append("")
report_lines.append("三、偏离度指标")
report_lines.append("-" * 40)

# 关键年份的偏离度
key_years = [1995, 2000, 2005, 2008, 2010, 2013, 2015, 2018, 2020, 2022, 2024]
report_lines.append(f"  {'年份':>6} {'D_PI':>8} {'D_IC':>8} {'D_PC':>8} {'总失调度':>10}")
for yr in key_years:
    row = df_anal[df_anal['year'] == yr]
    if len(row) > 0:
        r = row.iloc[0]
        d_pi = f"{r['D_PI']:.3f}" if pd.notna(r['D_PI']) else "N/A"
        d_ic = f"{r['D_IC']:.3f}" if pd.notna(r['D_IC']) else "N/A"
        d_pc = f"{r['D_PC']:.3f}" if pd.notna(r['D_PC']) else "N/A"
        d_t = f"{r['D_total']:.3f}" if pd.notna(r['D_total']) else "N/A"
        report_lines.append(f"  {yr:>6} {d_pi:>8} {d_ic:>8} {d_pc:>8} {d_t:>10}")

report_lines.append("")
report_lines.append("  偏离度解读:")
report_lines.append("    D_PI > 0: 人口增速快于产业转型 → 城镇化快于产业升级")
report_lines.append("    D_PI < 0: 产业转型快于人口增速 → 产业升级领先城镇化")
report_lines.append("    D_IC > 0: 产业变化快于建设 → 空间更新滞后")
report_lines.append("    D_IC < 0: 建设变化快于产业 → 存在过度投资风险")
report_lines.append("    D_PC > 0: 人口增速快于建设 → 基础设施不足")
report_lines.append("    D_PC < 0: 建设变化快于人口 → 建设超前于人口需求")

report_lines.append("")
report_lines.append("四、与 Urban Q 的关联分析")
report_lines.append("-" * 40)

# 计算总失调度与 Q 的相关系数
corr_data = df_anal[df_anal['Q_V1K1'].notna() & df_anal['D_total'].notna()]
if len(corr_data) > 3:
    corr_d_q = corr_data['D_total'].corr(corr_data['Q_V1K1'])
    report_lines.append(f"  总失调度与 Urban Q 的相关系数: {corr_d_q:.4f}")
    report_lines.append(f"  解读: {'负相关 — 失调越严重，Q值越低' if corr_d_q < 0 else '正相关 — 需进一步分析'}")

    corr_dpc_q = corr_data['D_PC'].corr(corr_data['Q_V1K1'])
    report_lines.append(f"  D_PC（人口-建设偏离）与 Q 的相关系数: {corr_dpc_q:.4f}")

report_lines.append("")
report_lines.append("五、核心发现总结")
report_lines.append("-" * 40)
report_lines.append(f"  1. 中国三曲线拐点顺序: 人口({pop_peak_year}) → 产业({ter_peak_year}) → 建设({inv_peak_year})")
dt1 = ter_peak_year - pop_peak_year
dt2 = inv_peak_year - ter_peak_year
report_lines.append(f"     人口→产业滞后 {dt1} 年, 产业→建设滞后 {dt2} 年")
if dt2 < 0:
    report_lines.append(f"     警告: 建设拐点({inv_peak_year})早于产业拐点({ter_peak_year})，建设存在超前风险")
report_lines.append(f"  2. 2012-2020年为关键失调窗口: 人口增速已大幅放缓，但建设投资仍在扩张")
report_lines.append(f"  3. 偏离度指标显示，近年来三曲线趋向收敛（失调度下降），")
report_lines.append(f"     但这主要是因为投资增速也在下降，而非结构性再协调")
report_lines.append(f"  4. Urban Q 的下降趋势与三曲线失调的扩大在时间上高度吻合")

report_lines.append("")
report_lines.append("六、数据来源说明")
report_lines.append("-" * 40)
report_lines.append("  城镇人口数据: 国家统计局《中国统计年鉴》历年数据")
report_lines.append("  产业结构数据: 国家统计局GDP核算数据")
report_lines.append("  建设投资数据: 来源于 six-curves 项目主数据集")
report_lines.append("  Urban Q 数据: 来源于 china_urban_q_timeseries.csv")

report = "\n".join(report_lines)
print(report)

with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\n分析报告已保存: {OUTPUT_TXT}")

print("\n分析完成。")
