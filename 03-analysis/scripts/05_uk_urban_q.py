#!/usr/bin/env python3
"""
05_uk_urban_q.py -- United Kingdom Urban Q time-series calculation and visualization

Purpose:
    Construct UK Urban Q = V(t)/K(t) time series using proxy data built from
    publicly available macroeconomic trends. Compute MUQ, identify Q=1 crossing,
    and generate visualization for cross-country comparison.

    *** NOTE: This script uses PROXY DATA constructed from publicly known
    statistical trends. Results should be validated against ONS National Balance
    Sheet (Table 10.1), ONS Blue Book capital stock estimates, and Bank of
    England housing wealth data once original data files are obtained. ***

Input data:
    - Hardcoded proxy data based on ONS/World Bank/Nationwide HPI published trends
    - Sources noted in comments for each variable

Output:
    - 03-analysis/models/uk_urban_q_timeseries.csv
    - 04-figures/drafts/fig05_uk_urban_q.png

Dependencies:
    pandas, numpy, matplotlib, scipy

Author: data-analyst
Date: 2026-03-20
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.interpolate import interp1d
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 0. 路径设置
# ============================================================
PROJECT_ROOT = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
RESULTS_PATH = os.path.join(PROJECT_ROOT, "03-analysis/models/uk_urban_q_timeseries.csv")
FIGURE_PATH = os.path.join(PROJECT_ROOT, "04-figures/drafts/fig05_uk_urban_q.png")

# ============================================================
# 1. 数据构建 -- 基于公开统计趋势的代理数据
# ============================================================
# 【重要】以下数据为基于公开统计趋势构建的代理数据，待替换为 ONS/BoE 原始数据
# 数据来源标注在每个变量的注释中

# --- 1.1 英国名义 GDP (万亿英镑) ---
# Source: ONS Blue Book / World Bank
# 关键锚点: 1970 ~0.052T, 1980 ~0.231T, 1990 ~0.567T, 2000 ~0.987T,
#           2008 ~1.485T, 2010 ~1.555T, 2020 ~1.954T, 2024 ~2.720T
gdp_data = {
    1970: 0.052,  1972: 0.064,  1974: 0.082,  1975: 0.105,
    1976: 0.125,  1978: 0.167,  1980: 0.231,  1982: 0.276,
    1984: 0.318,  1985: 0.350,  1986: 0.380,  1988: 0.448,
    1990: 0.567,  1991: 0.586,  1992: 0.610,  1993: 0.639,
    1994: 0.672,  1995: 0.710,  1996: 0.752,  1997: 0.800,
    1998: 0.843,  1999: 0.883,  2000: 0.987,  2001: 1.012,
    2002: 1.057,  2003: 1.117,  2004: 1.184,  2005: 1.253,
    2006: 1.328,  2007: 1.404,  2008: 1.485,  2009: 1.459,
    2010: 1.555,  2011: 1.618,  2012: 1.666,  2013: 1.732,
    2014: 1.822,  2015: 1.892,  2016: 1.966,  2017: 2.038,
    2018: 2.108,  2019: 2.173,  2020: 1.954,  2021: 2.187,
    2022: 2.390,  2023: 2.590,  2024: 2.720,
}

# --- 1.2 建设投资/GDP 比率 (%) ---
# Source: ONS GFCF by asset type / OECD
# 英国建设投资/GDP 比率趋势:
# 1970s: 7-8% (战后建设尾声)
# 1980s: 6-8% (撒切尔改革, PFI起步)
# 1988-1990: 8%+ (房地产繁荣)
# 1990s衰退后: 5-6%
# 2000s: 6-7% (布莱尔时代)
# 2008-2012: 5-6% (金融危机后建设低迷)
# 2015-2024: 6-7%
ci_gdp_ratio_data = {
    1970: 0.075, 1972: 0.078, 1974: 0.072, 1975: 0.070,
    1976: 0.068, 1978: 0.065, 1980: 0.065, 1982: 0.060,
    1984: 0.062, 1985: 0.063, 1986: 0.065, 1988: 0.078,
    1989: 0.082, 1990: 0.080, 1991: 0.070, 1992: 0.062,
    1993: 0.058, 1994: 0.060, 1995: 0.060, 1996: 0.062,
    1997: 0.063, 1998: 0.065, 1999: 0.065, 2000: 0.065,
    2001: 0.063, 2002: 0.065, 2003: 0.068, 2004: 0.070,
    2005: 0.072, 2006: 0.073, 2007: 0.073, 2008: 0.068,
    2009: 0.060, 2010: 0.058, 2011: 0.060, 2012: 0.060,
    2013: 0.063, 2014: 0.067, 2015: 0.068, 2016: 0.068,
    2017: 0.067, 2018: 0.068, 2019: 0.067, 2020: 0.058,
    2021: 0.065, 2022: 0.070, 2023: 0.070, 2024: 0.068,
}

# --- 1.3 住房价格指数 (1970=100) ---
# Source: Nationwide House Price Index / ONS HPI
# 英国房价经历了几轮大幅上涨:
# 1970=100, 1973 ~200 (巴伯繁荣), 1977 ~250 (调整后),
# 1988 ~650 (劳森繁荣), 1993 ~500 (衰退),
# 2007 ~2200 (信贷繁荣), 2009 ~1700 (金融危机),
# 2024 ~3200
hpi_data = {
    1970: 100,   1971: 120,   1972: 160,   1973: 210,
    1974: 200,   1975: 210,   1976: 220,   1977: 240,
    1978: 270,   1979: 340,   1980: 370,   1981: 380,
    1982: 380,   1983: 420,   1984: 450,   1985: 480,
    1986: 540,   1987: 630,   1988: 750,   1989: 800,
    1990: 760,   1991: 700,   1992: 650,   1993: 630,
    1994: 640,   1995: 640,   1996: 660,   1997: 700,
    1998: 750,   1999: 830,   2000: 900,   2001: 960,
    2002: 1120,  2003: 1280,  2004: 1420,  2005: 1500,
    2006: 1600,  2007: 1700,  2008: 1500,  2009: 1400,
    2010: 1480,  2011: 1460,  2012: 1480,  2013: 1520,
    2014: 1680,  2015: 1800,  2016: 1920,  2017: 2000,
    2018: 2060,  2019: 2080,  2020: 2120,  2021: 2380,
    2022: 2650,  2023: 2700,  2024: 2750,
}

# --- 1.4 城镇化率 (%) ---
# Source: World Bank (SP.URB.TOTL.IN.ZS) / ONS
# 英国城镇化率很高且变化缓慢
urbanization_data = {
    1970: 77.1, 1975: 78.1, 1980: 78.5, 1985: 78.4,
    1990: 78.1, 1995: 78.5, 2000: 79.0, 2005: 79.7,
    2010: 80.6, 2015: 82.0, 2020: 83.6, 2024: 84.0,
}

# --- 1.5 三产(服务业) GDP占比 (%) ---
# Source: World Bank / ONS
# 英国服务业占比全球最高之一: 1970s ~55%, 2020s ~80%
tertiary_share_data = {
    1970: 55.0, 1975: 56.0, 1980: 57.0, 1985: 60.0,
    1990: 63.0, 1995: 67.0, 2000: 71.0, 2005: 75.0,
    2010: 78.0, 2015: 79.0, 2020: 80.0, 2024: 80.5,
}

# --- 1.6 人口 (百万) ---
# Source: ONS / World Bank
population_data = {
    1970: 55.6, 1975: 56.2, 1980: 56.3, 1985: 56.5,
    1990: 57.2, 1995: 58.0, 2000: 58.9, 2005: 60.4,
    2010: 62.8, 2015: 65.1, 2020: 67.1, 2024: 68.3,
}

# --- 1.7 住宅房地产总市值/GDP 比率 ---
# Source: BoE Financial Stability Reports / Savills Research / ONS National Balance Sheet
# 英国住宅房地产总市值/GDP 比率:
# 1970s: ~1.2-1.5 (战后住房存量, 价格相对合理)
# 1980s: 1.5-2.5 (撒切尔Right to Buy推动)
# 1990s: 2.0-2.5 (含负资产期)
# 2007: ~4.5 (信贷繁荣顶峰)
# 2009: ~3.5 (回调)
# 2024: ~4.5
# 这个比率直接用于构造 V_residential
res_value_gdp_ratio = {
    1970: 1.20,  1973: 1.60,  1975: 1.30,  1978: 1.40,
    1980: 1.50,  1983: 1.55,  1985: 1.60,  1988: 2.30,
    1989: 2.50,  1990: 2.30,  1991: 2.00,  1993: 1.80,
    1995: 1.80,  1997: 1.90,  1999: 2.10,  2000: 2.20,
    2002: 2.70,  2004: 3.50,  2005: 3.70,  2006: 3.90,
    2007: 4.20,  2008: 3.60,  2009: 3.30,  2010: 3.50,
    2011: 3.40,  2012: 3.40,  2013: 3.50,  2014: 3.80,
    2015: 4.00,  2016: 4.10,  2017: 4.20,  2018: 4.20,
    2019: 4.10,  2020: 4.30,  2021: 4.50,  2022: 4.40,
    2023: 4.30,  2024: 4.30,
}

# --- 1.8 新建 vs 维修/翻新比例 ---
# Source: ONS Output in Construction / RICS
# 英国建设产出中新建与维修翻新的比例:
# 1970s: 新建~70%, 维修~30%
# 到2020s: 新建~55%, 维修~45%
# 英国由于住房存量老旧（大量战前房屋），维修翻新占比较高
new_vs_repair_share = {
    1970: (0.72, 0.28),
    1975: (0.70, 0.30),
    1980: (0.65, 0.35),
    1985: (0.63, 0.37),
    1990: (0.65, 0.35),  # 建设繁荣推高新建
    1993: (0.55, 0.45),  # 衰退期新建下降
    1995: (0.57, 0.43),
    2000: (0.58, 0.42),
    2005: (0.60, 0.40),  # 信贷繁荣
    2007: (0.60, 0.40),
    2010: (0.52, 0.48),  # 金融危机后新建崩溃
    2012: (0.50, 0.50),  # 接近反转
    2015: (0.53, 0.47),
    2020: (0.52, 0.48),
    2024: (0.55, 0.45),
}


# ============================================================
# 2. 插值为年度序列
# ============================================================

def interpolate_to_annual(data_dict, start_year=1970, end_year=2024, kind='linear'):
    """将稀疏数据点插值为连续年度序列"""
    years = sorted(data_dict.keys())
    values = [data_dict[y] for y in years]
    start = max(start_year, min(years))
    end = min(end_year, max(years))
    f = interp1d(years, values, kind=kind, fill_value='extrapolate')
    annual_years = np.arange(start, end + 1)
    annual_values = f(annual_years)
    return dict(zip(annual_years.astype(int), annual_values))

print("=" * 70)
print("United Kingdom Urban Q Time-Series Analysis")
print("=" * 70)
print("\n[1/5] 数据整合与插值...")

gdp_annual = interpolate_to_annual(gdp_data)
ci_ratio_annual = interpolate_to_annual(ci_gdp_ratio_data)
hpi_annual = interpolate_to_annual(hpi_data)
urban_annual = interpolate_to_annual(urbanization_data)
tert_annual = interpolate_to_annual(tertiary_share_data)
pop_annual = interpolate_to_annual(population_data)
res_gdp_annual = interpolate_to_annual(res_value_gdp_ratio)

# 新建/维修比例插值
nr_years = sorted(new_vs_repair_share.keys())
nr_new = {y: new_vs_repair_share[y][0] for y in nr_years}
nr_rep = {y: new_vs_repair_share[y][1] for y in nr_years}
new_share_annual = interpolate_to_annual(nr_new)
rep_share_annual = interpolate_to_annual(nr_rep)

# 构建主 DataFrame
years = list(range(1970, 2025))
df = pd.DataFrame({'year': years})
df['gdp_trillion_gbp'] = df['year'].map(gdp_annual)
df['ci_gdp_ratio'] = df['year'].map(ci_ratio_annual)
df['hpi_1970eq100'] = df['year'].map(hpi_annual)
df['urbanization_rate'] = df['year'].map(urban_annual)
df['tertiary_share_pct'] = df['year'].map(tert_annual)
df['population_million'] = df['year'].map(pop_annual)
df['res_value_gdp_ratio'] = df['year'].map(res_gdp_annual)
df['new_construction_share'] = df['year'].map(new_share_annual)
df['repair_share'] = df['year'].map(rep_share_annual)

# 计算建设投资 (万亿英镑)
df['construction_investment_trillion'] = df['gdp_trillion_gbp'] * df['ci_gdp_ratio']

# 新建 vs 维修投资
df['new_construction_trillion'] = df['construction_investment_trillion'] * df['new_construction_share']
df['repair_trillion'] = df['construction_investment_trillion'] * df['repair_share']

# 新建/维修比率 (N/R ratio)
df['new_repair_ratio'] = df['new_construction_share'] / df['repair_share']

print(f"  数据范围: {df['year'].min()} - {df['year'].max()}")
print(f"  共 {len(df)} 年观测值")

# ============================================================
# 3. 构造 K(t) — 资本存量
# ============================================================
print("[2/5] 构造 K(t) 和 V(t)...")

# --- K(t): PIM 资本存量 ---
# K(t) = K(t-1) * (1 - delta) + I(t)
# delta = 2.5%/年
# 初始存量: K(1970) = I(1970) / (delta + g)
# 1960s英国投资增长率约6%

DELTA = 0.025
g_initial = 0.06
I_1970 = df.loc[df['year'] == 1970, 'construction_investment_trillion'].values[0]
K_initial = I_1970 / (DELTA + g_initial)

K = np.zeros(len(df))
K[0] = K_initial
for i in range(1, len(df)):
    I_t = df.iloc[i]['construction_investment_trillion']
    K[i] = K[i-1] * (1 - DELTA) + I_t

df['capital_stock_K'] = K

# ============================================================
# 4. 构造 V(t) — 城市资产市场价值
# ============================================================
# 方法: V(t) = V_residential(t) + V_nonresidential(t)
#
# V_residential: 直接使用 住宅总市值/GDP 比率 * GDP
#   - 这个比率由 BoE/ONS 多方验证, 是英国最可靠的房地产价值指标
#   - 2024年英国住宅总市值约 8-9 万亿英镑 (Savills estimates)
#
# V_nonresidential: 非住宅建筑存量价值
#   - 约为住宅价值的 40-50%
#   - Source: ONS National Balance Sheet AN.112

df['V_residential'] = df['res_value_gdp_ratio'] * df['gdp_trillion_gbp']

# 非住宅/住宅价值比率: 英国非住宅占比约 40-50%
# 金融危机后住宅价格飙升使该比率下降
nonres_ratio_data = {
    1970: 0.50, 1980: 0.48, 1990: 0.45, 2000: 0.42,
    2005: 0.40, 2007: 0.38, 2010: 0.45,  # 住宅缩水, 非住宅相对回升
    2015: 0.40, 2020: 0.38, 2024: 0.38,
}
nonres_annual = interpolate_to_annual(nonres_ratio_data)
df['nonres_ratio'] = df['year'].map(nonres_annual)
df['V_nonresidential'] = df['V_residential'] * df['nonres_ratio']

# 总资产市场价值
df['V_total'] = df['V_residential'] + df['V_nonresidential']

# V/GDP 比率验证
df['V_gdp_ratio'] = df['V_total'] / df['gdp_trillion_gbp']
print(f"\n  V/GDP 比率验证:")
for yr in [1970, 1980, 1990, 2000, 2007, 2010, 2020, 2024]:
    row = df[df['year'] == yr]
    if not row.empty:
        print(f"    {yr}: V/GDP = {row['V_gdp_ratio'].values[0]:.2f} "
              f"(V_res={row['V_residential'].values[0]:.3f}T, "
              f"V_nonres={row['V_nonresidential'].values[0]:.3f}T)")

# ============================================================
# 5. 计算 Urban Q 和 MUQ
# ============================================================
print("\n[3/5] 计算 Urban Q 和 MUQ...")

# --- Urban Q = V(t) / K(t) ---
df['urban_Q'] = df['V_total'] / df['capital_stock_K']

# --- 仅住宅口径 Q_res ---
df['Q_residential'] = df['V_residential'] / df['capital_stock_K']

# --- 边际 Urban Q: MUQ = deltaV / I(t) ---
df['delta_V'] = df['V_total'].diff()
df['MUQ'] = df['delta_V'] / df['construction_investment_trillion']

# --- 住宅 MUQ ---
df['delta_V_res'] = df['V_residential'].diff()
df['MUQ_residential'] = df['delta_V_res'] / df['construction_investment_trillion']

# ============================================================
# 6. 识别关键转折点
# ============================================================
print("[4/5] 分析关键转折点...")

print("\n" + "=" * 60)
print("关键转折点分析")
print("=" * 60)

# Q = 1 交叉点
for q_col, label in [('urban_Q', 'Urban Q (total)'), ('Q_residential', 'Q (residential)')]:
    crossings = []
    vals = df[['year', q_col]].dropna()
    for i in range(1, len(vals)):
        prev_val = vals.iloc[i-1][q_col]
        curr_val = vals.iloc[i][q_col]
        if (prev_val - 1) * (curr_val - 1) < 0:
            y1, y2 = vals.iloc[i-1]['year'], vals.iloc[i]['year']
            frac = (1 - prev_val) / (curr_val - prev_val)
            cross_year = y1 + frac * (y2 - y1)
            direction = "下穿" if prev_val > 1 else "上穿"
            crossings.append((cross_year, direction))

    first_val = vals.iloc[0][q_col]
    last_val = vals.iloc[-1][q_col]
    print(f"\n{label}:")
    print(f"  起始值 ({int(vals.iloc[0]['year'])}): {first_val:.3f}")
    print(f"  终止值 ({int(vals.iloc[-1]['year'])}): {last_val:.3f}")
    if crossings:
        for cy, d in crossings:
            ur_approx = np.interp(cy, df['year'].values, df['urbanization_rate'].values)
            print(f"  Q=1 交叉点: {cy:.1f} 年 ({d}), 城镇化率 ~{ur_approx:.1f}%")
    else:
        if first_val > 1 and last_val > 1:
            print(f"  始终 > 1 — 英国Q从未降到1以下")
        elif first_val < 1 and last_val < 1:
            print(f"  始终 < 1")

# MUQ 分析
for muq_col, label in [('MUQ', 'MUQ (total)'), ('MUQ_residential', 'MUQ (residential)')]:
    crossings = []
    vals = df[['year', muq_col]].dropna()
    for i in range(1, len(vals)):
        prev_val = vals.iloc[i-1][muq_col]
        curr_val = vals.iloc[i][muq_col]
        if (prev_val - 1) * (curr_val - 1) < 0:
            y1, y2 = vals.iloc[i-1]['year'], vals.iloc[i]['year']
            frac = (1 - prev_val) / (curr_val - prev_val)
            cross_year = y1 + frac * (y2 - y1)
            direction = "下穿" if prev_val > 1 else "上穿"
            crossings.append((cross_year, direction))

    print(f"\n{label}:")
    if crossings:
        for cy, d in crossings:
            print(f"  MUQ=1 交叉点: {cy:.1f} 年 ({d})")
    else:
        print(f"  无明确交叉")

# N/R ratio 分析
nr_min_yr = df.loc[df['new_repair_ratio'].idxmin(), 'year']
nr_min_val = df['new_repair_ratio'].min()
print(f"\n新建/维修比率最低点: {nr_min_val:.2f} ({int(nr_min_yr)}年)")
nr_cross = df[df['new_repair_ratio'] < 1.0]
if not nr_cross.empty:
    print(f"  N/R < 1 的年份: {int(nr_cross['year'].min())} - {int(nr_cross['year'].max())}")

# ============================================================
# 7. 敏感性分析
# ============================================================
print(f"\n=== 敏感性分析：初始存量假设 ===")
for g_test in [0.04, 0.05, 0.06, 0.08, 0.10]:
    K_test = np.zeros(len(df))
    K_test[0] = I_1970 / (DELTA + g_test)
    for i in range(1, len(df)):
        I_t = df.iloc[i]['construction_investment_trillion']
        K_test[i] = K_test[i-1] * (1 - DELTA) + I_t
    q_2024 = df.iloc[-1]['V_total'] / K_test[-1]
    q_2007 = df.loc[df['year'] == 2007, 'V_total'].values[0] / K_test[df.index[df['year'] == 2007][0]]
    print(f"  g_initial={g_test:.2f}: K(1970)={I_1970/(DELTA+g_test):.3f}T, "
          f"Q(2007)={q_2007:.3f}, Q(2024)={q_2024:.3f}")

print(f"\n=== 敏感性分析：折旧率 ===")
for delta_test in [0.020, 0.025, 0.030, 0.035]:
    K_test = np.zeros(len(df))
    K_test[0] = I_1970 / (delta_test + g_initial)
    for i in range(1, len(df)):
        I_t = df.iloc[i]['construction_investment_trillion']
        K_test[i] = K_test[i-1] * (1 - delta_test) + I_t
    q_2024 = df.iloc[-1]['V_total'] / K_test[-1]
    print(f"  delta={delta_test:.3f}: K(2024)={K_test[-1]:.3f}T, Q(2024)={q_2024:.3f}")

# ============================================================
# 8. 保存结果
# ============================================================
output_cols = ['year', 'urbanization_rate', 'gdp_trillion_gbp',
               'construction_investment_trillion', 'ci_gdp_ratio',
               'hpi_1970eq100', 'tertiary_share_pct', 'population_million',
               'capital_stock_K', 'V_residential', 'V_nonresidential', 'V_total',
               'V_gdp_ratio', 'res_value_gdp_ratio',
               'urban_Q', 'Q_residential', 'MUQ', 'MUQ_residential',
               'new_construction_trillion', 'repair_trillion',
               'new_repair_ratio', 'new_construction_share']

df[output_cols].to_csv(RESULTS_PATH, index=False, float_format='%.4f')
print(f"\n结果已保存: {RESULTS_PATH}")

# ============================================================
# 9. 可视化 -- 2x2 面板图
# ============================================================
print("[5/5] 生成图表...")

# 设置字体 (macOS)
plt.rcParams['font.family'] = 'Heiti TC'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('United Kingdom Urban Q Time-Series Analysis (1970-2024)',
             fontsize=16, fontweight='bold', y=0.98)

# 颜色方案
C_Q = '#2c3e50'
C_MUQ = '#e74c3c'
C_V = '#2166AC'
C_K = '#B2182B'
C_CI = '#2980b9'
C_WARN = '#c0392b'
C_REF = '#666666'

# ---------------------------------------------------------------
# Panel A: Urban Q 时序
# ---------------------------------------------------------------
ax = axes[0, 0]
ax.plot(df['year'], df['urban_Q'], color=C_Q, linewidth=2.0,
        label='Average Q (total)', zorder=5)
ax.plot(df['year'], df['Q_residential'], color=C_CI, linewidth=1.2,
        alpha=0.7, linestyle='--', label='Q (residential only)', zorder=4)

# MUQ
mask_muq = df['MUQ'].notna()
ax.plot(df.loc[mask_muq, 'year'], df.loc[mask_muq, 'MUQ'],
        color=C_MUQ, linewidth=1.0, alpha=0.5, label='Marginal Q (MUQ)', zorder=3)

# Q=1 参考线
ax.axhline(y=1.0, color=C_REF, linestyle='--', linewidth=0.8, alpha=0.7)
ax.text(2025.5, 1.02, 'Q = 1', fontsize=8, color=C_REF, va='bottom')

# 高亮繁荣区间
ax.axvspan(1986, 1990, alpha=0.06, color='red', label='Lawson boom')
ax.axvspan(2003, 2007, alpha=0.06, color='orange', label='Credit boom')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.3, alpha=0.3)

# 标注关键点
q_2007 = df.loc[df['year'] == 2007, 'urban_Q'].values[0]
ax.annotate(f'2007 credit boom\nQ = {q_2007:.2f}',
            xy=(2007, q_2007), xytext=(1995, q_2007 * 0.85),
            fontsize=8, color=C_Q,
            arrowprops=dict(arrowstyle='->', color=C_Q, lw=1.0),
            ha='center')

q_2024 = df.loc[df['year'] == 2024, 'urban_Q'].values[0]
ax.annotate(f'2024: Q = {q_2024:.2f}',
            xy=(2024, q_2024), xytext=(2016, q_2024 + 0.5),
            fontsize=8, color=C_Q,
            arrowprops=dict(arrowstyle='->', color=C_Q, lw=1.0),
            ha='center')

# Q=1 交叉点标注
for i in range(1, len(df)):
    if (df.iloc[i-1]['urban_Q'] >= 1.0 and df.iloc[i]['urban_Q'] < 1.0
            and df.iloc[i]['year'] > 1980):
        yr1 = df.iloc[i-1]['year']
        q1 = df.iloc[i-1]['urban_Q']
        q2 = df.iloc[i]['urban_Q']
        yr_cross = yr1 + (1.0 - q1) / (q2 - q1)
        ax.annotate(f'{yr_cross:.0f}: Q < 1',
                    xy=(yr_cross, 1.0), xytext=(yr_cross + 3, 0.6),
                    fontsize=8, color=C_WARN, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=C_WARN, lw=1.0),
                    ha='center')
        break

ax.set_xlim(1970, 2026)
ax.set_ylabel('Urban Q')
ax.set_title('A. Urban Q = V(t)/K(t)', fontsize=12, fontweight='bold', loc='left')
ax.legend(loc='upper left', fontsize=7.5, framealpha=0.9)
ax.grid(True, alpha=0.3)

# ---------------------------------------------------------------
# Panel B: V(t) 和 K(t) 双轴图
# ---------------------------------------------------------------
ax = axes[0, 1]
ax2 = ax.twinx()

ln1 = ax.plot(df['year'], df['V_total'], '-', color=C_V, linewidth=2.0,
              label='V(t): Total asset value', zorder=5)
ln1b = ax.plot(df['year'], df['V_residential'], '--', color=C_V, linewidth=1.0,
               alpha=0.6, label='V_res: Residential only', zorder=4)
ln2 = ax2.plot(df['year'], df['capital_stock_K'], '-', color=C_K, linewidth=2.0,
               label='K(t): PIM capital stock', zorder=5)

ax.set_xlabel('Year')
ax.set_ylabel('V(t) (trillion GBP)', color=C_V)
ax2.set_ylabel('K(t) (trillion GBP)', color=C_K)
ax.tick_params(axis='y', colors=C_V)
ax2.tick_params(axis='y', colors=C_K)

lns = ln1 + ln1b + ln2
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper left', frameon=True, framealpha=0.9, fontsize=8)

ax.set_title('B. Asset Value V(t) vs Capital Stock K(t)',
             fontsize=12, fontweight='bold', loc='left')
ax.set_xlim(1970, 2026)
ax.grid(True, alpha=0.3)

# ---------------------------------------------------------------
# Panel C: 建设投资/GDP + 新建/维修比率
# ---------------------------------------------------------------
ax = axes[1, 0]
ax2 = ax.twinx()

ln1 = ax.plot(df['year'], df['ci_gdp_ratio'] * 100, color=C_CI, linewidth=2.0,
              label='CI/GDP ratio (%)')
ax.fill_between(df['year'], df['ci_gdp_ratio'] * 100, alpha=0.12, color=C_CI)

ln2 = ax2.plot(df['year'], df['new_repair_ratio'], color='#27ae60', linewidth=1.5,
               linestyle='--', label='New/Repair ratio')
ax2.axhline(y=1.0, color='#27ae60', linestyle=':', linewidth=0.6, alpha=0.5)

# 标注
peak_idx = df['ci_gdp_ratio'].idxmax()
peak_yr = int(df.loc[peak_idx, 'year'])
peak_val = df.loc[peak_idx, 'ci_gdp_ratio'] * 100
ax.annotate(f'{peak_yr}: {peak_val:.1f}%',
            xy=(peak_yr, peak_val), xytext=(peak_yr - 10, peak_val + 0.5),
            fontsize=8, color=C_CI,
            arrowprops=dict(arrowstyle='->', color=C_CI, lw=1.0))

ax.set_xlabel('Year')
ax.set_ylabel('CI/GDP (%)', color=C_CI)
ax2.set_ylabel('New/Repair ratio', color='#27ae60')
ax.tick_params(axis='y', colors=C_CI)
ax2.tick_params(axis='y', colors='#27ae60')

lns = ln1 + ln2
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper right', frameon=True, framealpha=0.9, fontsize=8)

ax.set_title('C. Construction Investment / GDP & N/R Ratio',
             fontsize=12, fontweight='bold', loc='left')
ax.set_xlim(1970, 2026)
ax.grid(True, alpha=0.3)
ax.axvspan(1986, 1990, alpha=0.06, color='red')
ax.axvspan(2003, 2007, alpha=0.06, color='orange')

# ---------------------------------------------------------------
# Panel D: Urban Q vs 城镇化率散点图
# ---------------------------------------------------------------
ax = axes[1, 1]

scatter = ax.scatter(df['urbanization_rate'], df['urban_Q'],
                     c=df['year'], cmap='viridis', s=30, alpha=0.8,
                     zorder=5, edgecolors='white', linewidth=0.3)

ax.axhline(y=1.0, color=C_REF, linestyle='--', linewidth=1.0, alpha=0.7, zorder=3)

# 标注关键年份
key_years_annotate = [1970, 1980, 1990, 2000, 2007, 2010, 2020, 2024]
for yr in key_years_annotate:
    row = df[df['year'] == yr]
    if not row.empty:
        u = row['urbanization_rate'].values[0]
        q = row['urban_Q'].values[0]
        offset_y = 5 if yr != 2007 else -12
        ax.annotate(str(yr), xy=(u, q), xytext=(5, offset_y),
                    textcoords='offset points', fontsize=7, color='#333',
                    fontweight='bold' if yr in [2007, 2024] else 'normal')

cbar = plt.colorbar(scatter, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label('Year', fontsize=9)

ax.set_xlabel('Urbanization rate (%)')
ax.set_ylabel('Urban Q')
ax.set_title('D. Urban Q vs Urbanization Rate',
             fontsize=12, fontweight='bold', loc='left')
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(FIGURE_PATH, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  图表已保存: {FIGURE_PATH}")

# ============================================================
# 10. 分析报告
# ============================================================
print("\n" + "=" * 70)
print("UK Urban Q Analysis Report")
print("=" * 70)

# 关键统计
print(f"\n关键年份 Urban Q:")
for yr in [1970, 1980, 1990, 2000, 2007, 2010, 2015, 2020, 2024]:
    row = df[df['year'] == yr]
    if not row.empty:
        q = row['urban_Q'].values[0]
        ur = row['urbanization_rate'].values[0]
        ci = row['ci_gdp_ratio'].values[0] * 100
        vg = row['V_gdp_ratio'].values[0]
        print(f"  {yr}: Q={q:.3f}, UR={ur:.1f}%, CI/GDP={ci:.1f}%, V/GDP={vg:.2f}")

# Q 峰值
q_peak_idx = df['urban_Q'].idxmax()
q_peak_yr = int(df.loc[q_peak_idx, 'year'])
q_peak_val = df.loc[q_peak_idx, 'urban_Q']
print(f"\nQ 峰值: {q_peak_val:.3f} ({q_peak_yr})")

# 特征总结
print(f"\n=== 英国 Urban Q 特征 ===")
print(f"  1. 英国是'永久Q>1'的特殊案例:")
print(f"     - 土地供给极度稀缺（绿带政策 Green Belt, 规划限制）")
print(f"     - 住房供给持续不足, 推动价格长期上涨")
print(f"     - 金融自由化 (1980s+) 放大资产价格")
print(f"  2. 与中国/日本的关键差异:")
print(f"     - 英国CI/GDP仅6-8%, 远低于中国25%和日本18%")
print(f"     - 低投资强度 = K增长缓慢, V/K比率不易下降")
print(f"     - 英国的'相变'可能体现为MUQ<1而非Q<1")
print(f"  3. 政策含义:")
print(f"     - Q持续>>1 意味着建设投资持续不足")
print(f"     - 英国住房危机(housing crisis)本质是Urban Q过高")
print(f"     - 这是一个'供给侧锁定'的案例, 与中国的'投资过度'形成对偶")

print("\n分析完成。")
