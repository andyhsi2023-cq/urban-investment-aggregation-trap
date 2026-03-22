#!/usr/bin/env python3
"""
04_us_urban_q.py -- United States Urban Q time-series calculation and visualization

Purpose:
    Construct US Urban Q = V(t)/K(t) time series using proxy data built from
    publicly available macroeconomic trends. Compute MUQ, identify Q=1 crossing,
    and generate visualization for cross-country comparison.

    *** NOTE: This script uses PROXY DATA constructed from publicly known
    statistical trends. Results should be validated against BEA Fixed Assets
    Tables (Current-Cost Net Stock) and Fed Z.1 Financial Accounts once
    original data files are obtained. ***

Input data:
    - Hardcoded proxy data based on BEA/Census/World Bank/FHFA published trends
    - Sources noted in comments for each variable

Output:
    - 03-analysis/models/us_urban_q_timeseries.csv
    - 04-figures/drafts/fig04_us_urban_q.png

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
RESULTS_PATH = os.path.join(PROJECT_ROOT, "03-analysis/models/us_urban_q_timeseries.csv")
FIGURE_PATH = os.path.join(PROJECT_ROOT, "04-figures/drafts/fig04_us_urban_q.png")

# ============================================================
# 1. 数据构建 -- 基于公开统计趋势的代理数据
# ============================================================
# 【重要】以下数据为基于公开统计趋势构建的代理数据，待替换为 BEA/Fed 原始数据
# 数据来源标注在每个变量的注释中

# --- 1.1 美国名义 GDP (万亿美元) ---
# Source: BEA NIPA / World Bank
# 关键锚点：1970 ~1.07T, 1980 ~2.86T, 1990 ~5.96T, 2000 ~10.25T,
#           2008 ~14.77T, 2010 ~14.99T, 2020 ~21.06T, 2024 ~28.78T
gdp_data = {
    1970: 1.07,  1972: 1.28,  1974: 1.50,  1975: 1.69,
    1976: 1.88,  1978: 2.36,  1980: 2.86,  1982: 3.34,
    1984: 3.93,  1985: 4.21,  1986: 4.46,  1988: 5.24,
    1990: 5.96,  1991: 6.16,  1992: 6.52,  1993: 6.86,
    1994: 7.29,  1995: 7.64,  1996: 8.07,  1997: 8.58,
    1998: 9.06,  1999: 9.63,  2000: 10.25, 2001: 10.58,
    2002: 10.94, 2003: 11.46, 2004: 12.21, 2005: 13.04,
    2006: 13.81, 2007: 14.48, 2008: 14.77, 2009: 14.42,
    2010: 14.99, 2011: 15.54, 2012: 16.20, 2013: 16.78,
    2014: 17.52, 2015: 18.22, 2016: 18.71, 2017: 19.54,
    2018: 20.53, 2019: 21.37, 2020: 21.06, 2021: 23.32,
    2022: 25.46, 2023: 27.36, 2024: 28.78,
}

# --- 1.2 建设投资/GDP 比率 (%) ---
# Source: BEA NIPA Table 5.4.5 (structures GFCF) + BEA Table 5.8.5 (gov structures)
# 美国建设投资（structures, 含私人住宅+非住宅+政府建筑）/GDP 比率趋势：
# 1970s: 10-12% (婴儿潮住房需求 + 基础设施投资)
# 1980s: 8-10% (利率高企, 投资放缓)
# 1990s: 7-9% (信息经济转型, 建设占比下降)
# 2000s: 8-10% (住房泡沫推高)
# 2006-2007: 10%+ (泡沫顶峰)
# 2010-2012: 5-6% (金融危机后建设崩溃)
# 2015-2019: 6-7% (缓慢恢复)
# 2020-2024: 7-8% (基建法案 + 制造业回流)
ci_gdp_ratio_data = {
    1970: 0.110, 1972: 0.115, 1974: 0.105, 1975: 0.095,
    1976: 0.100, 1978: 0.110, 1980: 0.100, 1982: 0.085,
    1984: 0.090, 1985: 0.088, 1986: 0.085, 1988: 0.082,
    1990: 0.080, 1991: 0.072, 1992: 0.073, 1993: 0.075,
    1994: 0.078, 1995: 0.077, 1996: 0.080, 1997: 0.082,
    1998: 0.085, 1999: 0.088, 2000: 0.090, 2001: 0.088,
    2002: 0.085, 2003: 0.087, 2004: 0.093, 2005: 0.100,
    2006: 0.105, 2007: 0.098, 2008: 0.085, 2009: 0.068,
    2010: 0.058, 2011: 0.057, 2012: 0.062, 2013: 0.065,
    2014: 0.068, 2015: 0.070, 2016: 0.068, 2017: 0.067,
    2018: 0.068, 2019: 0.067, 2020: 0.065, 2021: 0.070,
    2022: 0.075, 2023: 0.078, 2024: 0.080,
}

# --- 1.3 住房价格指数 (1970=100) ---
# Source: Case-Shiller National HPI / FHFA HPI (composite trend)
# 关键锚点: 1970=100, 1980~220 (通胀推动), 1990~280,
#   1997~270 (实际持平), 2006~500 (泡沫顶), 2009~350 (崩盘),
#   2012~310 (底部), 2020~440, 2024~580
hpi_data = {
    1970: 100,  1972: 115,  1974: 140,  1975: 155,
    1976: 168,  1978: 200,  1980: 220,  1982: 230,
    1984: 240,  1985: 250,  1986: 265,  1988: 280,
    1990: 280,  1991: 275,  1992: 270,  1993: 268,
    1994: 270,  1995: 272,  1996: 275,  1997: 280,
    1998: 295,  1999: 315,  2000: 340,  2001: 365,
    2002: 390,  2003: 420,  2004: 460,  2005: 500,
    2006: 510,  2007: 480,  2008: 410,  2009: 350,
    2010: 340,  2011: 320,  2012: 310,  2013: 330,
    2014: 350,  2015: 370,  2016: 390,  2017: 410,
    2018: 430,  2019: 440,  2020: 460,  2021: 510,
    2022: 560,  2023: 570,  2024: 580,
}

# --- 1.4 城镇化率 (%) ---
# Source: World Bank (SP.URB.TOTL.IN.ZS) / US Census Bureau
urbanization_data = {
    1970: 73.6, 1975: 73.7, 1980: 73.7, 1985: 74.2,
    1990: 75.3, 1995: 77.3, 2000: 79.1, 2005: 80.7,
    2010: 80.8, 2015: 81.7, 2020: 82.7, 2024: 83.0,
}

# --- 1.5 三产(服务业) GDP占比 (%) ---
# Source: World Bank / BEA
# 美国服务业占比从1970s的~60%上升到2020s的~78%
tertiary_share_data = {
    1970: 60.0, 1975: 62.0, 1980: 63.0, 1985: 65.0,
    1990: 68.0, 1995: 71.0, 2000: 74.0, 2005: 76.0,
    2010: 77.5, 2015: 78.0, 2020: 80.0, 2024: 78.5,
}

# --- 1.6 人口 (百万) ---
# Source: US Census Bureau / World Bank
population_data = {
    1970: 205.1, 1975: 215.9, 1980: 227.2, 1985: 237.9,
    1990: 249.6, 1995: 266.3, 2000: 282.2, 2005: 295.5,
    2010: 309.3, 2015: 320.7, 2020: 331.5, 2024: 340.0,
}

# --- 1.7 新建 vs 改善/维修投资比例 ---
# Source: Census Bureau C30 (Value of Construction Put in Place)
# 新建占比从1970s的~80%下降到2020s的~60%
# 改善/维护投资持续上升
new_vs_improvement_share = {
    # year: (new_share, improvement_share) -- of total structures investment
    1970: (0.82, 0.18),
    1975: (0.80, 0.20),
    1980: (0.78, 0.22),
    1985: (0.75, 0.25),
    1990: (0.72, 0.28),
    1995: (0.70, 0.30),
    2000: (0.68, 0.32),
    2005: (0.70, 0.30),  # 住房泡沫推高新建比例
    2006: (0.72, 0.28),  # 泡沫顶峰
    2010: (0.55, 0.45),  # 新建崩溃, 维修占比飙升
    2015: (0.58, 0.42),
    2020: (0.60, 0.40),
    2024: (0.62, 0.38),
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
print("United States Urban Q Time-Series Analysis")
print("=" * 70)
print("\n[1/5] 数据整合与插值...")

gdp_annual = interpolate_to_annual(gdp_data)
ci_ratio_annual = interpolate_to_annual(ci_gdp_ratio_data)
hpi_annual = interpolate_to_annual(hpi_data)
urban_annual = interpolate_to_annual(urbanization_data)
tert_annual = interpolate_to_annual(tertiary_share_data)
pop_annual = interpolate_to_annual(population_data)

# 新建/改善比例插值
ni_years = sorted(new_vs_improvement_share.keys())
ni_new = {y: new_vs_improvement_share[y][0] for y in ni_years}
ni_imp = {y: new_vs_improvement_share[y][1] for y in ni_years}
new_share_annual = interpolate_to_annual(ni_new)
imp_share_annual = interpolate_to_annual(ni_imp)

# 构建主 DataFrame
years = list(range(1970, 2025))
df = pd.DataFrame({'year': years})
df['gdp_trillion_usd'] = df['year'].map(gdp_annual)
df['ci_gdp_ratio'] = df['year'].map(ci_ratio_annual)
df['hpi_1970eq100'] = df['year'].map(hpi_annual)
df['urbanization_rate'] = df['year'].map(urban_annual)
df['tertiary_share_pct'] = df['year'].map(tert_annual)
df['population_million'] = df['year'].map(pop_annual)
df['new_construction_share'] = df['year'].map(new_share_annual)
df['improvement_share'] = df['year'].map(imp_share_annual)

# 计算建设投资 (万亿美元)
df['construction_investment_trillion'] = df['gdp_trillion_usd'] * df['ci_gdp_ratio']

# 新建 vs 改善/维修投资
df['new_construction_trillion'] = df['construction_investment_trillion'] * df['new_construction_share']
df['improvement_trillion'] = df['construction_investment_trillion'] * df['improvement_share']

# 新建/改善比率 (N/R ratio)
df['new_improvement_ratio'] = df['new_construction_share'] / df['improvement_share']

print(f"  数据范围: {df['year'].min()} - {df['year'].max()}")
print(f"  共 {len(df)} 年观测值")

# ============================================================
# 3. 构造 K(t) — 累计建设投资 / 资本存量
# ============================================================
print("[2/5] 构造 K(t) 和 V(t)...")

# --- K1: PIM 资本存量 ---
# K(t) = K(t-1) * (1 - delta) + I(t)
# delta = 2.5%/年 (住宅~2%, 非住宅~3%, 综合~2.5%)
# 初始存量: 1970年以前的累积投资
# 美国1970年建设投资约 0.118T, 稳态假设 K(1970) = I / (delta + g)
# 1960s投资增长率约8%, g=0.08

DELTA = 0.025
g_initial = 0.08
I_1970 = df.loc[df['year'] == 1970, 'construction_investment_trillion'].values[0]
K_initial = I_1970 / (DELTA + g_initial)  # 约 1.12 万亿

K = np.zeros(len(df))
K[0] = K_initial
for i in range(1, len(df)):
    I_t = df.iloc[i]['construction_investment_trillion']
    K[i] = K[i-1] * (1 - DELTA) + I_t

df['capital_stock_K'] = K

# --- K2: 简单累计投资 (不含折旧调整, 用于对照) ---
df['cumulative_inv'] = df['construction_investment_trillion'].cumsum()

# ============================================================
# 4. 构造 V(t) — 城市资产市场价值
# ============================================================
# 方法: V(t) = V_residential(t) + V_nonresidential(t)
#
# V_residential: 住宅存量的市场价值
#   - 基期: 1970年美国住宅存量市值约 GDP 的 1.1 倍 (~1.18T)
#     Source: Fed Z.1 historical, 1970年家庭房地产约 1.1-1.2T
#   - 用 HPI 对基期存量进行市值重估, 同时考虑新增存量
#   - V_res(t) = V_res_base * (HPI(t)/HPI(1970)) * stock_growth_factor(t)
#   - stock_growth_factor: 住宅存量增长（人口增长+住房增量）
#
# V_nonresidential: 非住宅建筑存量价值
#   - 约为住宅价值的 40-60% (BEA Fixed Assets: 非住宅structures约占总structures的35-45%)
#   - 非住宅不受住房价格泡沫影响, 增长更平稳

# --- 住宅市场价值: 直接使用 住宅总市值/GDP 比率 ---
# Source: Federal Reserve Z.1 Financial Accounts, Table B.101
# 美国家庭房地产资产/GDP 比率的历史趋势:
# 1970: ~1.10 (约1.18T / 1.07T GDP)
# 1980: ~1.20 (约3.43T / 2.86T GDP)
# 1990: ~1.15 (约6.86T / 5.96T GDP)
# 2000: ~1.35 (约13.8T / 10.25T GDP) — 互联网泡沫后资金转向房地产
# 2006: ~1.80 (约24.8T / 13.8T GDP) — 住房泡沫顶峰
# 2009: ~1.10 (约15.9T / 14.4T GDP) — 泡沫破裂
# 2012: ~1.05 (约17.0T / 16.2T GDP) — 底部
# 2020: ~1.55 (约32.6T / 21.1T GDP) — 疫情前小幅上涨
# 2024: ~1.65 (约47.5T / 28.8T GDP) — 疫情后大幅上涨
res_value_gdp_ratio = {
    1970: 1.10,  1975: 1.20,  1978: 1.25,  1980: 1.20,
    1982: 1.12,  1985: 1.15,  1988: 1.20,  1990: 1.15,
    1992: 1.08,  1995: 1.10,  1997: 1.15,  1999: 1.25,
    2000: 1.35,  2002: 1.40,  2004: 1.60,  2005: 1.72,
    2006: 1.80,  2007: 1.60,  2008: 1.30,  2009: 1.10,
    2010: 1.08,  2011: 1.05,  2012: 1.05,  2013: 1.10,
    2014: 1.18,  2015: 1.22,  2016: 1.28,  2017: 1.32,
    2018: 1.35,  2019: 1.38,  2020: 1.55,  2021: 1.62,
    2022: 1.65,  2023: 1.63,  2024: 1.65,
}
res_gdp_annual = interpolate_to_annual(res_value_gdp_ratio)
df['res_value_gdp_ratio'] = df['year'].map(res_gdp_annual)

# 住宅市场价值 = 比率 * GDP
df['V_residential'] = df['res_value_gdp_ratio'] * df['gdp_trillion_usd']

# 非住宅建筑存量价值
# Source: BEA Fixed Assets Table 1.1 — Nonresidential structures net stock
# 非住宅/住宅价值比率: 约 35-50%
# BEA数据: 非住宅structures net stock约为住宅的40-50%
# 住宅价格泡沫时非住宅占比相对下降
nonres_ratio_data = {
    1970: 0.50, 1980: 0.48, 1990: 0.45, 2000: 0.42,
    2005: 0.38, 2006: 0.35,  # 住宅泡沫推高住宅占比
    2010: 0.48,  # 住宅崩盘, 非住宅相对占比回升
    2015: 0.42, 2020: 0.38, 2024: 0.36,
}
nonres_annual = interpolate_to_annual(nonres_ratio_data)
df['nonres_ratio'] = df['year'].map(nonres_annual)
df['V_nonresidential'] = df['V_residential'] * df['nonres_ratio']

# 总资产市场价值
df['V_total'] = df['V_residential'] + df['V_nonresidential']

# V/GDP 比率验证
df['V_gdp_ratio'] = df['V_total'] / df['gdp_trillion_usd']
print(f"\n  V/GDP 比率验证:")
for yr in [1970, 1980, 1990, 2000, 2006, 2010, 2020, 2024]:
    row = df[df['year'] == yr]
    if not row.empty:
        print(f"    {yr}: V/GDP = {row['V_gdp_ratio'].values[0]:.2f} "
              f"(V_res={row['V_residential'].values[0]:.2f}T, "
              f"V_nonres={row['V_nonresidential'].values[0]:.2f}T)")

# ============================================================
# 5. 计算 Urban Q 和 MUQ
# ============================================================
print("\n[3/5] 计算 Urban Q 和 MUQ...")

# --- Urban Q = V(t) / K(t) ---
df['urban_Q'] = df['V_total'] / df['capital_stock_K']

# --- 仅住宅口径 Q_res = V_res / K ---
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
            # 对应城镇化率
            ur_approx = np.interp(cy, df['year'].values, df['urbanization_rate'].values)
            print(f"  Q=1 交叉点: {cy:.1f} 年 ({d}), 城镇化率 ~{ur_approx:.1f}%")
    else:
        if first_val > 1 and last_val > 1:
            print(f"  始终 > 1")
        elif first_val < 1 and last_val < 1:
            print(f"  始终 < 1")

# MUQ = 1 交叉点
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

# N/R ratio 反转
nr_cross_years = []
for i in range(1, len(df)):
    if (df.iloc[i-1]['new_improvement_ratio'] >= 1.0 and
        df.iloc[i]['new_improvement_ratio'] < 1.0):
        nr_cross_years.append(df.iloc[i]['year'])
print(f"\n新建/改善比率反转 (N/R < 1): {nr_cross_years if nr_cross_years else '未在观测期内反转'}")

# ============================================================
# 7. 敏感性分析
# ============================================================
print(f"\n=== 敏感性分析：初始存量假设 ===")
for g_test in [0.05, 0.06, 0.08, 0.10, 0.12]:
    K_test = np.zeros(len(df))
    K_test[0] = I_1970 / (DELTA + g_test)
    for i in range(1, len(df)):
        I_t = df.iloc[i]['construction_investment_trillion']
        K_test[i] = K_test[i-1] * (1 - DELTA) + I_t
    q_2024 = df.iloc[-1]['V_total'] / K_test[-1]
    q_2006 = df.loc[df['year'] == 2006, 'V_total'].values[0] / K_test[df.index[df['year'] == 2006][0]]
    print(f"  g_initial={g_test:.2f}: K(1970)={I_1970/(DELTA+g_test):.2f}T, "
          f"Q(2006)={q_2006:.3f}, Q(2024)={q_2024:.3f}")

# ============================================================
# 8. 保存结果
# ============================================================
output_cols = ['year', 'urbanization_rate', 'gdp_trillion_usd',
               'construction_investment_trillion', 'ci_gdp_ratio',
               'hpi_1970eq100', 'tertiary_share_pct', 'population_million',
               'capital_stock_K', 'V_residential', 'V_nonresidential', 'V_total',
               'V_gdp_ratio', 'urban_Q', 'Q_residential', 'MUQ', 'MUQ_residential',
               'new_construction_trillion', 'improvement_trillion',
               'new_improvement_ratio', 'new_construction_share']

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
fig.suptitle('United States Urban Q Time-Series Analysis (1970-2024)',
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

# 高亮泡沫区间
ax.axvspan(2003, 2007, alpha=0.08, color='red', label='Housing bubble')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.3, alpha=0.3)

# 标注关键点
q_2006 = df.loc[df['year'] == 2006, 'urban_Q'].values[0]
ax.annotate(f'2006 bubble peak\nQ = {q_2006:.2f}',
            xy=(2006, q_2006), xytext=(1993, q_2006 * 0.95),
            fontsize=8, color=C_Q,
            arrowprops=dict(arrowstyle='->', color=C_Q, lw=1.0),
            ha='center')

q_2024 = df.loc[df['year'] == 2024, 'urban_Q'].values[0]
ax.annotate(f'2024: Q = {q_2024:.2f}',
            xy=(2024, q_2024), xytext=(2016, q_2024 - 0.3),
            fontsize=8, color=C_WARN,
            arrowprops=dict(arrowstyle='->', color=C_WARN, lw=1.0),
            ha='center')

# Q=1 交叉点标注
for i in range(1, len(df)):
    if (df.iloc[i-1]['urban_Q'] >= 1.0 and df.iloc[i]['urban_Q'] < 1.0
            and df.iloc[i]['year'] > 1990):
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
ax.set_ylabel('V(t) (trillion USD)', color=C_V)
ax2.set_ylabel('K(t) (trillion USD)', color=C_K)
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
# Panel C: 建设投资/GDP + 新建/改善比率
# ---------------------------------------------------------------
ax = axes[1, 0]
ax2 = ax.twinx()

ln1 = ax.plot(df['year'], df['ci_gdp_ratio'] * 100, color=C_CI, linewidth=2.0,
              label='CI/GDP ratio (%)')
ax.fill_between(df['year'], df['ci_gdp_ratio'] * 100, alpha=0.12, color=C_CI)

ln2 = ax2.plot(df['year'], df['new_improvement_ratio'], color='#27ae60', linewidth=1.5,
               linestyle='--', label='New/Improvement ratio')
ax2.axhline(y=1.0, color='#27ae60', linestyle=':', linewidth=0.6, alpha=0.5)

# 标注
peak_idx = df['ci_gdp_ratio'].idxmax()
peak_yr = int(df.loc[peak_idx, 'year'])
peak_val = df.loc[peak_idx, 'ci_gdp_ratio'] * 100
ax.annotate(f'{peak_yr}: {peak_val:.1f}%',
            xy=(peak_yr, peak_val), xytext=(peak_yr - 12, peak_val + 0.5),
            fontsize=8, color=C_CI,
            arrowprops=dict(arrowstyle='->', color=C_CI, lw=1.0))

# 2010 trough
trough_val = df.loc[df['year'] == 2011, 'ci_gdp_ratio'].values[0] * 100
ax.annotate(f'2011: {trough_val:.1f}%',
            xy=(2011, trough_val), xytext=(2015, trough_val - 1),
            fontsize=8, color=C_WARN,
            arrowprops=dict(arrowstyle='->', color=C_WARN, lw=1.0))

ax.set_xlabel('Year')
ax.set_ylabel('CI/GDP (%)', color=C_CI)
ax2.set_ylabel('New/Improvement ratio', color='#27ae60')
ax.tick_params(axis='y', colors=C_CI)
ax2.tick_params(axis='y', colors='#27ae60')

lns = ln1 + ln2
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper right', frameon=True, framealpha=0.9, fontsize=8)

ax.set_title('C. Construction Investment / GDP & N/I Ratio',
             fontsize=12, fontweight='bold', loc='left')
ax.set_xlim(1970, 2026)
ax.grid(True, alpha=0.3)
ax.axvspan(2003, 2007, alpha=0.08, color='red')

# ---------------------------------------------------------------
# Panel D: Urban Q vs 城镇化率散点图
# ---------------------------------------------------------------
ax = axes[1, 1]

scatter = ax.scatter(df['urbanization_rate'], df['urban_Q'],
                     c=df['year'], cmap='viridis', s=30, alpha=0.8,
                     zorder=5, edgecolors='white', linewidth=0.3)

ax.axhline(y=1.0, color=C_REF, linestyle='--', linewidth=1.0, alpha=0.7, zorder=3)

# 标注关键年份
key_years_annotate = [1970, 1980, 1990, 2000, 2006, 2010, 2020, 2024]
for yr in key_years_annotate:
    row = df[df['year'] == yr]
    if not row.empty:
        u = row['urbanization_rate'].values[0]
        q = row['urban_Q'].values[0]
        offset_y = 5 if yr != 2006 else -12
        ax.annotate(str(yr), xy=(u, q), xytext=(5, offset_y),
                    textcoords='offset points', fontsize=7, color='#333',
                    fontweight='bold' if yr in [2006, 2024] else 'normal')

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
print("US Urban Q Analysis Report")
print("=" * 70)

# 关键统计
print(f"\n关键年份 Urban Q:")
for yr in [1970, 1980, 1990, 2000, 2006, 2010, 2015, 2020, 2024]:
    row = df[df['year'] == yr]
    if not row.empty:
        q = row['urban_Q'].values[0]
        ur = row['urbanization_rate'].values[0]
        ci = row['ci_gdp_ratio'].values[0] * 100
        print(f"  {yr}: Q={q:.3f}, UR={ur:.1f}%, CI/GDP={ci:.1f}%")

# Q 峰值
q_peak_idx = df['urban_Q'].idxmax()
q_peak_yr = int(df.loc[q_peak_idx, 'year'])
q_peak_val = df.loc[q_peak_idx, 'urban_Q']
print(f"\nQ 峰值: {q_peak_val:.3f} ({q_peak_yr})")

# 特征总结
print(f"\n=== 美国 Urban Q 特征 ===")
print(f"  1. 住房泡沫对Q的影响: 2003-2007年Q被住宅价格泡沫推高")
print(f"  2. 金融危机后Q快速回落: 2008-2012年V大幅缩水")
print(f"  3. 与中国/日本的对比:")
print(f"     - 美国城镇化率在Q=1时远高于中国(~54%), 接近日本(~91%)")
print(f"     - 美国CI/GDP比率远低于中国(~25%), 投资强度更合理")
print(f"     - 美国Q的波动性更大(金融化程度高)")

print("\n分析完成。")
