"""
37_carbon_dimension.py
========================
目的：为 Urban Q 论文增加碳排放维度，回应审稿人意见：
     "过度建设 = 无社会价值回报的碳排放"

核心逻辑：
  - Q < 1 意味着建设资本存量 K 超过均衡值 K*
  - 过度投资 = K - K* (当 Q < 1 时) 或 OCR > 1 的部分
  - 过度投资 x 碳排放强度 = 过度建设的碳成本

分析内容：
  Part A: 中国国家级过度建设碳成本（2000-2024 时序）
  Part B: 城市级过度建设碳分布（248城截面）
  Part C: 全球视角（CPR 较高国家的过度建设碳排放估算）
  Part D: 可视化

输入数据：
  - china_q_adjusted.csv — 中国国家级 Q 与 K 时序
  - china_city_real_window.csv — 城市面板（含 OCR）
  - global_q_revised_panel.csv — 全球面板（含 CPR）

输出：
  - carbon_dimension_report.txt — 分析报告
  - fig_carbon.png — 综合图表

依赖包：pandas, numpy, matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import textwrap
import warnings

warnings.filterwarnings('ignore')

# ============================================================
# 0. 路径设置与碳排放参数
# ============================================================
BASE = Path('/Users/andy/Desktop/Claude/urban-q-phase-transition')
DATA = BASE / '02-data' / 'processed'
MODELS = BASE / '03-analysis' / 'models'
FIGS = BASE / '04-figures' / 'drafts'

# 碳排放强度参数（文献来源标注）
CARBON = {
    # --- 中国参数 ---
    # 单位：tCO2/万元建设投资（2020年不变价）
    # 来源：中国建筑节能协会《中国建筑能耗与碳排放研究报告(2022)》
    'china_per_10k_yuan': 0.65,

    # 单位：tCO2/m2 新建建筑（含隐含碳 + 运营碳前10年折现）
    # 来源：IEA, Global Status Report for Buildings and Construction (2023)
    'china_per_m2': 1.8,

    # --- 全球参数 ---
    # 单位：tCO2/m2 建筑面积（全球平均）
    # 来源：UNEP GlobalABC, 2023 Global Status Report for Buildings and Construction
    'global_per_m2': 0.6,

    # --- 中国年度总碳排放（GtCO2）---
    # 来源：Global Carbon Budget 2023; 含能源+工业过程
    'china_total_annual_GtCO2': {
        2000: 3.4, 2001: 3.5, 2002: 3.7, 2003: 4.1, 2004: 4.7,
        2005: 5.4, 2006: 5.9, 2007: 6.3, 2008: 6.5, 2009: 6.8,
        2010: 7.5, 2011: 8.1, 2012: 8.5, 2013: 8.9, 2014: 9.0,
        2015: 9.0, 2016: 9.1, 2017: 9.3, 2018: 9.6, 2019: 9.9,
        2020: 10.0, 2021: 10.7, 2022: 10.9, 2023: 11.5, 2024: 11.6,
    },

    # 建筑部门占全球碳排放比例
    # 来源：UNEP GlobalABC (2023)
    'global_building_pct': 0.37,

    # 全球年度总碳排放 (GtCO2, 2023)
    # 来源：Global Carbon Budget 2023
    'global_total_annual_GtCO2': 37.4,
}

report_lines = []
def log(msg=''):
    report_lines.append(msg)
    print(msg)


# ============================================================
# Part A: 中国国家级过度建设碳成本
# ============================================================
log('=' * 70)
log('Part A: 中国国家级过度建设碳成本 (2000-2024)')
log('=' * 70)

# 读取国家级 Q 数据
df_q = pd.read_csv(MODELS / 'china_q_adjusted.csv')

# 关键列：
#   K2_100m — 建设资本存量（亿元）
#   Q_weighted — 加权综合 Q 值
#   Q_mc_median — Monte Carlo 中位 Q
#   V1_adj_mid_100m — 调整后市场价值

# 使用 Q_weighted 作为主指标
df_q['Q_main'] = df_q['Q_weighted']

# 计算均衡资本存量 K*：当 Q=1 时的 K 值
# K* = V / 1 = V（当 Q = V/K = 1 → K* = V）
# 实际使用: K* = V1_adj_mid（调整后市场价值）
df_q['Kstar_100m'] = df_q['V1_adj_mid_100m']

# 过度投资 = max(0, K - K*)
# 注意：当 Q < 1 时才存在过度投资
df_q['excess_K_100m'] = np.maximum(0, df_q['K2_100m'] - df_q['Kstar_100m'])

# 增量过度投资（年度新增）：用 K 的年度增量中的过度部分
# 首先计算 K 的年度增量（即当年新增投资形成的资本）
df_q['delta_K_100m'] = df_q['K2_100m'].diff()

# 过度投资的年度增量
df_q['delta_excess_K_100m'] = df_q['excess_K_100m'].diff()
# 第一个有过度投资的年份，增量 = 存量本身
first_excess_idx = df_q[df_q['excess_K_100m'] > 0].index
if len(first_excess_idx) > 0:
    fi = first_excess_idx[0]
    if pd.isna(df_q.loc[fi, 'delta_excess_K_100m']) or df_q.loc[fi, 'delta_excess_K_100m'] == 0:
        df_q.loc[fi, 'delta_excess_K_100m'] = df_q.loc[fi, 'excess_K_100m']

# 方法1：基于过度投资金额 × 碳强度
# 每年新增过度投资（亿元）→ 万元 → × 碳强度
# 亿元 = 10000 万元，所以 delta_excess_K_100m * 10000 = 万元
intensity = CARBON['china_per_10k_yuan']
df_q['annual_excess_carbon_Mt'] = np.maximum(0, df_q['delta_excess_K_100m']) * 10000 * intensity / 1e6
# 单位换算：tCO2 / 1e6 = MtCO2

# 累计过度碳排放
df_q['cumulative_excess_carbon_Mt'] = df_q['annual_excess_carbon_Mt'].cumsum()

# 与中国年度总排放对比
df_q['china_total_GtCO2'] = df_q['year'].map(CARBON['china_total_annual_GtCO2'])
df_q['excess_pct_of_total'] = (
    df_q['annual_excess_carbon_Mt'] / (df_q['china_total_GtCO2'] * 1000) * 100
)  # MtCO2 vs GtCO2*1000 = MtCO2

# 筛选 2000-2024
mask_a = df_q['year'].between(2000, 2024)
df_a = df_q[mask_a].copy()

log(f'\n碳排放强度参数：{intensity} tCO2/万元建设投资')
log(f'来源：中国建筑节能协会《中国建筑能耗与碳排放研究报告(2022)》\n')

log(f'{"年份":>6} {"Q_weighted":>10} {"K(亿元)":>14} {"K*(亿元)":>14} '
    f'{"过度K(亿元)":>14} {"年度碳排(Mt)":>14} {"累计碳排(Mt)":>14} {"占总排放%":>10}')
log('-' * 100)

for _, r in df_a.iterrows():
    yr = int(r['year'])
    log(f'{yr:>6} {r["Q_main"]:>10.3f} {r["K2_100m"]:>14,.0f} '
        f'{r["Kstar_100m"]:>14,.0f} {r["excess_K_100m"]:>14,.0f} '
        f'{r["annual_excess_carbon_Mt"]:>14.1f} '
        f'{r["cumulative_excess_carbon_Mt"]:>14.1f} '
        f'{r["excess_pct_of_total"]:>10.2f}')

# 汇总统计
total_excess_carbon = df_a['cumulative_excess_carbon_Mt'].iloc[-1]
peak_year = df_a.loc[df_a['annual_excess_carbon_Mt'].idxmax()]
q_below_1_year = df_a[df_a['Q_main'] < 1].iloc[0]['year'] if len(df_a[df_a['Q_main'] < 1]) > 0 else 'N/A'

log(f'\n--- 汇总 ---')
log(f'Q 首次低于 1 的年份：{int(q_below_1_year) if isinstance(q_below_1_year, (int, float)) else q_below_1_year}')
log(f'累计过度建设碳排放 (2000-2024)：{total_excess_carbon:,.0f} MtCO2 = {total_excess_carbon/1000:.2f} GtCO2')
log(f'年度峰值：{int(peak_year["year"])} 年，{peak_year["annual_excess_carbon_Mt"]:.0f} MtCO2')
log(f'峰值年占中国总排放比例：{peak_year["excess_pct_of_total"]:.2f}%')

# 计算近年平均占比
recent = df_a[df_a['year'].between(2015, 2024)]
avg_pct = recent['excess_pct_of_total'].mean()
log(f'2015-2024 年均占中国总排放比例：{avg_pct:.2f}%')


# ============================================================
# Part B: 城市级过度建设碳分布
# ============================================================
log('\n' + '=' * 70)
log('Part B: 城市级过度建设碳分布 (248城截面)')
log('=' * 70)

df_city = pd.read_csv(DATA / 'china_city_real_window.csv')

# OCR_w1 = K / K* (Overcapitalization Ratio)
# 过度投资 = max(0, K - K*) = max(0, OCR-1) * K*
# K_100m 是实际资本存量，Kstar_100m 是均衡值
df_city['excess_K_100m'] = np.maximum(0, df_city['K_100m'] - df_city['Kstar_100m'])

# 碳排放：过度投资金额 × 碳强度
# 注意：城市截面数据是多年窗口均值，代表"存量"概念
# 此处估算的是"过度存量对应的累计碳排放"
df_city['excess_carbon_Mt'] = df_city['excess_K_100m'] * 10000 * intensity / 1e6

# 仅保留 OCR > 1 的城市
df_over = df_city[df_city['OCR_w1'] > 1].copy()
n_over = len(df_over)
n_total = len(df_city)

log(f'\nOCR > 1 的城市数量：{n_over} / {n_total} ({n_over/n_total*100:.1f}%)')
log(f'过度建设城市总碳排放：{df_over["excess_carbon_Mt"].sum():,.0f} MtCO2')

# 按城市等级汇总
log('\n--- 按城市等级汇总 ---')
tier_agg = df_city.groupby('city_tier').agg(
    n_cities=('city', 'count'),
    n_overcap=('OCR_w1', lambda x: (x > 1).sum()),
    total_excess_carbon=('excess_carbon_Mt', 'sum'),
    mean_OCR=('OCR_w1', 'mean'),
).reset_index()
tier_agg['pct_overcap'] = tier_agg['n_overcap'] / tier_agg['n_cities'] * 100

log(f'{"等级":<12} {"城市数":>6} {"过度建设数":>10} {"占比%":>8} '
    f'{"累计碳排(Mt)":>14} {"平均OCR":>10}')
log('-' * 65)
for _, r in tier_agg.iterrows():
    log(f'{r["city_tier"]:<12} {r["n_cities"]:>6} {r["n_overcap"]:>10} '
        f'{r["pct_overcap"]:>8.1f} {r["total_excess_carbon"]:>14,.0f} '
        f'{r["mean_OCR"]:>10.3f}')

# 按区域汇总
log('\n--- 按区域汇总 ---')
region_agg = df_city.groupby('region4').agg(
    n_cities=('city', 'count'),
    n_overcap=('OCR_w1', lambda x: (x > 1).sum()),
    total_excess_carbon=('excess_carbon_Mt', 'sum'),
    mean_OCR=('OCR_w1', 'mean'),
).reset_index()

log(f'{"区域":<8} {"城市数":>6} {"过度建设数":>10} {"累计碳排(Mt)":>14} {"平均OCR":>10}')
log('-' * 55)
for _, r in region_agg.iterrows():
    log(f'{r["region4"]:<8} {r["n_cities"]:>6} {r["n_overcap"]:>10} '
        f'{r["total_excess_carbon"]:>14,.0f} {r["mean_OCR"]:>10.3f}')

# Top 10 碳浪费最大的城市
log('\n--- Top 10 过度建设碳排放最大的城市 ---')
top10 = df_city.nlargest(10, 'excess_carbon_Mt')
log(f'{"排名":>4} {"城市":<10} {"等级":<10} {"区域":<6} '
    f'{"OCR":>8} {"过度K(亿元)":>14} {"碳排放(Mt)":>12}')
log('-' * 70)
for i, (_, r) in enumerate(top10.iterrows(), 1):
    log(f'{i:>4} {r["city"]:<10} {r["city_tier"]:<10} {r["region4"]:<6} '
        f'{r["OCR_w1"]:>8.3f} {r["excess_K_100m"]:>14,.0f} '
        f'{r["excess_carbon_Mt"]:>12,.1f}')


# ============================================================
# Part C: 全球视角
# ============================================================
log('\n' + '=' * 70)
log('Part C: 全球视角 — 过度建设的碳排放数量级估算')
log('=' * 70)

df_global = pd.read_csv(DATA / 'global_q_revised_panel.csv')

# 使用 CPR (Capital-to-Price Ratio) 或 MUQ 作为过度建设指标
# CPR > 某阈值 → 可能过度建设
# 使用最近可用年份
recent_years = df_global[df_global['year'].between(2015, 2022)].copy()

# 按国家取最近年份
latest = recent_years.sort_values('year', ascending=False).groupby('country_code').first().reset_index()

# 需要 GFCF 数据
latest = latest.dropna(subset=['gfcf_current_usd', 'CPR'])

# CPR > 1.5 视为可能过度建设（CPR = K/V，类似 1/Q）
# 当 CPR > 1 时，K > V，即 Q < 1
cpr_threshold = 1.5
overbuilt = latest[latest['CPR'] > cpr_threshold].copy()

log(f'\nCPR > {cpr_threshold} 的国家数量：{len(overbuilt)} / {len(latest)}')

if len(overbuilt) > 0:
    # 估算过度投资部分：excess_fraction = 1 - 1/CPR（过度部分占总投资的比例）
    overbuilt['excess_fraction'] = 1 - 1 / overbuilt['CPR']
    overbuilt['excess_gfcf_usd'] = overbuilt['gfcf_current_usd'] * overbuilt['excess_fraction']

    # 粗略估算碳排放：假设 GFCF 中建筑投资占 50-60%
    building_share = 0.55
    # 全球平均碳强度：约 300 tCO2/百万美元建筑投资（UNEP 估算）
    global_carbon_per_m_usd = 300  # tCO2/百万美元

    overbuilt['excess_carbon_Mt'] = (
        overbuilt['excess_gfcf_usd'] / 1e6  # 转为百万美元
        * building_share
        * global_carbon_per_m_usd
        / 1e6  # tCO2 → MtCO2
    )

    total_global_excess = overbuilt['excess_carbon_Mt'].sum()
    log(f'这些国家过度建设年度碳排放估算：{total_global_excess:,.0f} MtCO2')

    global_building_carbon = CARBON['global_total_annual_GtCO2'] * 1000 * CARBON['global_building_pct']
    log(f'全球建筑部门年度碳排放：{global_building_carbon:,.0f} MtCO2')
    log(f'过度建设占全球建筑碳排放：{total_global_excess/global_building_carbon*100:.1f}%')

    # Top 10 国家
    log(f'\n--- CPR > {cpr_threshold} 的 Top 10 国家（按过度碳排放排序）---')
    top10_g = overbuilt.nlargest(10, 'excess_carbon_Mt')
    log(f'{"国家":<25} {"CPR":>8} {"GFCF(亿$)":>12} {"过度碳排(Mt)":>14}')
    log('-' * 65)
    for _, r in top10_g.iterrows():
        log(f'{r["country_name"]:<25} {r["CPR"]:>8.2f} '
            f'{r["gfcf_current_usd"]/1e8:>12,.1f} '
            f'{r["excess_carbon_Mt"]:>14.1f}')
else:
    log(f'未找到 CPR > {cpr_threshold} 的国家，放宽阈值到 1.2')
    overbuilt = latest[latest['CPR'] > 1.2].copy()
    if len(overbuilt) > 0:
        overbuilt['excess_fraction'] = 1 - 1 / overbuilt['CPR']
        overbuilt['excess_gfcf_usd'] = overbuilt['gfcf_current_usd'] * overbuilt['excess_fraction']
        building_share = 0.55
        global_carbon_per_m_usd = 300
        overbuilt['excess_carbon_Mt'] = (
            overbuilt['excess_gfcf_usd'] / 1e6 * building_share
            * global_carbon_per_m_usd / 1e6
        )
        total_global_excess = overbuilt['excess_carbon_Mt'].sum()
        log(f'CPR > 1.2 的国家数量：{len(overbuilt)}')
        log(f'这些国家过度建设年度碳排放估算：{total_global_excess:,.0f} MtCO2')

        top10_g = overbuilt.nlargest(10, 'excess_carbon_Mt')
        log(f'\n--- Top 10 国家 ---')
        log(f'{"国家":<25} {"CPR":>8} {"GFCF(亿$)":>12} {"过度碳排(Mt)":>14}')
        log('-' * 65)
        for _, r in top10_g.iterrows():
            log(f'{r["country_name"]:<25} {r["CPR"]:>8.2f} '
                f'{r["gfcf_current_usd"]/1e8:>12,.1f} '
                f'{r["excess_carbon_Mt"]:>14.1f}')

# 中国在全球语境中的定位
log('\n--- 中国在全球过度建设碳排放中的角色 ---')
china_latest = latest[latest['country_code'] == 'CHN']
if len(china_latest) > 0:
    china_cpr = china_latest['CPR'].values[0]
    china_gfcf = china_latest['gfcf_current_usd'].values[0]
    log(f'中国 CPR: {china_cpr:.2f}')
    log(f'中国 GFCF: {china_gfcf/1e12:.2f} 万亿美元')

# 数量级对比
log('\n--- 数量级对比框架 ---')
global_bldg_total = CARBON['global_total_annual_GtCO2'] * CARBON['global_building_pct']
log(f'全球建筑部门年碳排放：约 {global_bldg_total:.1f} GtCO2 (全球 {CARBON["global_total_annual_GtCO2"]} Gt x {CARBON["global_building_pct"]*100:.0f}%)')
log(f'中国 2023 年过度建设碳排放估算：{df_a.iloc[-2]["annual_excess_carbon_Mt"]:.0f} MtCO2 (基于 Q 框架)')
if total_excess_carbon > 0:
    log(f'中国 2000-2024 累计过度建设碳排放：{total_excess_carbon/1000:.2f} GtCO2')
    log(f'  → 相当于全球建筑碳排放 {total_excess_carbon/1000/global_bldg_total:.1f} 年的排放量')


# ============================================================
# Part D: 可视化
# ============================================================
log('\n' + '=' * 70)
log('Part D: 生成可视化')
log('=' * 70)

plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
})
# 尝试使用中文字体
try:
    plt.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti SC', 'sans-serif']
except:
    pass

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Carbon Dimension of Urban Overcapitalization',
             fontsize=14, fontweight='bold', y=0.98)

# --- Panel A: 中国国家级过度碳排放时序 ---
ax1 = axes[0, 0]
ax1_right = ax1.twinx()

years = df_a['year'].values
annual_carbon = df_a['annual_excess_carbon_Mt'].values
q_vals = df_a['Q_main'].values

# 柱状图：年度过度碳排放
colors_bar = ['#2196F3' if q >= 1 else '#E53935' for q in q_vals]
ax1.bar(years, annual_carbon, color=colors_bar, alpha=0.7, width=0.8,
        label='Annual excess CO$_2$ (Mt)')

# 折线图：Q 值
ax1_right.plot(years, q_vals, 'k-o', markersize=3, linewidth=1.5,
               label='Urban Q (weighted)')
ax1_right.axhline(y=1, color='gray', linestyle='--', alpha=0.6, linewidth=0.8)

ax1.set_xlabel('Year')
ax1.set_ylabel('Excess CO$_2$ Emissions (MtCO$_2$)')
ax1_right.set_ylabel('Urban Q')
ax1.set_title('A. China: Annual Excess Construction Carbon Cost')

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_right.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

# --- Panel B: 累计碳排放 + 占总排放比例 ---
ax2 = axes[0, 1]
ax2_right = ax2.twinx()

ax2.fill_between(years, df_a['cumulative_excess_carbon_Mt'].values,
                 alpha=0.3, color='#E53935')
ax2.plot(years, df_a['cumulative_excess_carbon_Mt'].values,
         color='#E53935', linewidth=2, label='Cumulative excess CO$_2$ (Mt)')

pct_vals = df_a['excess_pct_of_total'].values
ax2_right.plot(years, pct_vals, 'b--', linewidth=1.5,
               label='% of China total emissions')

ax2.set_xlabel('Year')
ax2.set_ylabel('Cumulative CO$_2$ (MtCO$_2$)')
ax2_right.set_ylabel('% of China Total Emissions')
ax2.set_title('B. Cumulative Excess Carbon & Share of Total')

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_right.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

# --- Panel C: 城市级碳浪费 Top 20 ---
ax3 = axes[1, 0]
top20 = df_city.nlargest(20, 'excess_carbon_Mt')
# 按碳排放从大到小排列
top20_sorted = top20.sort_values('excess_carbon_Mt', ascending=True)
cities = top20_sorted['city'].values
carbons = top20_sorted['excess_carbon_Mt'].values
ocrs = top20_sorted['OCR_w1'].values

# 颜色编码：按 OCR 程度
colors_c = []
for ocr in ocrs:
    if ocr > 2.0:
        colors_c.append('#B71C1C')  # 深红
    elif ocr > 1.5:
        colors_c.append('#E53935')  # 红
    elif ocr > 1.0:
        colors_c.append('#FF8A65')  # 橙
    else:
        colors_c.append('#66BB6A')  # 绿

ax3.barh(range(len(cities)), carbons, color=colors_c, alpha=0.8)
ax3.set_yticks(range(len(cities)))
ax3.set_yticklabels(cities, fontsize=7)
ax3.set_xlabel('Excess CO$_2$ (MtCO$_2$)')
ax3.set_title('C. Top 20 Cities by Excess Construction Carbon')

# 添加 OCR 标注
for i, (c, ocr) in enumerate(zip(carbons, ocrs)):
    if c > 0:
        ax3.text(c + max(carbons) * 0.02, i, f'OCR={ocr:.2f}',
                 va='center', fontsize=6, color='gray')

# --- Panel D: 区域碳排放分布 ---
ax4 = axes[1, 1]

# 按区域和等级交叉汇总
cross = df_city.groupby(['region4', 'city_tier'])['excess_carbon_Mt'].sum().unstack(fill_value=0)
# 确保列顺序
tier_order = ['一线', '二线', '三线及以下']
available_tiers = [t for t in tier_order if t in cross.columns]
cross = cross[available_tiers]

region_order = ['东部', '中部', '西部', '东北']
available_regions = [r for r in region_order if r in cross.index]
cross = cross.loc[available_regions]

x = np.arange(len(available_regions))
width = 0.25
colors_tier = ['#1565C0', '#F57C00', '#7B1FA2']

for i, tier in enumerate(available_tiers):
    ax4.bar(x + i * width, cross[tier].values, width,
            label=tier, color=colors_tier[i], alpha=0.8)

ax4.set_xticks(x + width)
ax4.set_xticklabels(available_regions)
ax4.set_ylabel('Excess CO$_2$ (MtCO$_2$)')
ax4.set_title('D. Excess Carbon by Region and City Tier')
ax4.legend(fontsize=8)

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig_path = FIGS / 'fig_carbon.png'
plt.savefig(fig_path, bbox_inches='tight')
plt.close()
log(f'\n图表已保存：{fig_path}')


# ============================================================
# 关键发现摘要
# ============================================================
log('\n' + '=' * 70)
log('关键发现摘要（供论文 Discussion 使用）')
log('=' * 70)

log(textwrap.dedent(f'''
1. 碳排放规模：
   - 中国 2000-2024 年累计过度建设碳排放约 {total_excess_carbon/1000:.1f} GtCO2
   - 峰值年份 {int(peak_year["year"])}，年度过度碳排放约 {peak_year["annual_excess_carbon_Mt"]:.0f} MtCO2
   - 占中国年度总排放的 {avg_pct:.1f}%（2015-2024 均值）

2. 空间分布：
   - {n_over}/{n_total} ({n_over/n_total*100:.0f}%) 城市存在过度建设
   - 过度建设碳排放高度集中于少数城市
   - Top 10 城市占总过度碳排放的 {top10["excess_carbon_Mt"].sum()/df_over["excess_carbon_Mt"].sum()*100:.0f}%

3. 政策含义：
   - Urban Q 框架提供了一个量化"碳浪费"的方法
   - Q < 1 区间的建设投资 = 无社会价值回报的碳排放
   - 城市更新（存量优化）vs 新建扩张（增量碳排放）的碳效率差异
   - 过度建设的碳成本应纳入城市投资决策框架

4. 方法论说明：
   - 碳强度采用行业公认数值（中国建筑节能协会、IEA、UNEP）
   - 估算为保守下界：仅含建设过程碳排放，未含过度建设的运营碳排放
   - 全球估算仅为数量级参考，受数据可得性限制
'''))


# ============================================================
# 保存报告
# ============================================================
report_path = MODELS / 'carbon_dimension_report.txt'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
log(f'\n报告已保存：{report_path}')

print('\n[完成] 37_carbon_dimension.py 执行成功。')
